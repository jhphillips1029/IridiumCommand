"""
-------------------------------------------------------------------------------
MIT License
Copyright (c) 2021 Joshua H. Phillips
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-------------------------------------------------------------------------------

This is a wrapper class that uses cartopy to create a map, plot data points to it, and render the result in tkinter.
"""

import requests
import io
import shapefile
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from pyproj import Transformer
from geopy.geocoders import Nominatim
import zipfile


def get_cadastral_by_county(county):
    zip_url = 'http://ftpgeoinfo.msl.mt.gov/Data/Spatial/MSDI/Cadastral/Parcels/{0}/{0}_SHP.zip'
    chunk_size = 128
    req = requests.get(zip_url.format(county),stream=True)
    zip_buffer = io.BytesIO()
    for chunk in req.iter_content(chunk_size=chunk_size):
        zip_buffer.write(chunk)
    req.close()
    #print(zip_url.format(county))
        
    zip_buffer.seek(0)
    zipshape = zipfile.ZipFile(zip_buffer)
    dbfname,shpname,shxname = ['{}_Parcels/{}_Parcels.{}'.format(county,county,ext) for ext in ['dbf','shp','shx']]
    shape = shapefile.Reader(shp=io.BytesIO(zipshape.read(shpname)),
                             dbf=io.BytesIO(zipshape.read(dbfname)),
                             shx=io.BytesIO(zipshape.read(shxname))
                            )
    zip_buffer.close()
    
    return shape


def get_county(coord,lon=None):
    if lon is not None:
        coord = (coord,lon)
    
    geolocator = Nominatim(user_agent="ICC")
    loc = geolocator.reverse('{},{}'.format(*coord))
    return loc.raw['address']['county'].replace('County','').strip().replace(' ','').replace('&','')


def check_point_in_shapes(coord,shapes):
    poi = Point(coord)
    i_con = containter = None
    for i,feature in enumerate(shapes.shapeRecords()):
        first = feature.shape.__geo_interface__
        coords = first['coordinates']
        while type(coords[0])==type([]):
            coords = coords[0]
        poly = Polygon(coords)
        if poly.contains(poi):
            i_con = i
            container = coords
            break
    return i_con,container

def get_transformers():
    return Transformer.from_crs('NAD83 / Montana','epsg:4326'),Transformer.from_crs('epsg:4326','NAD83 / Montana')

def gen_owner_dict(i_con,shapes):
    return {key:val for key,val in zip([s[0] for s in shapes.fields[1:]],shapes.records()[i_con])}

