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

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import io
from urllib.request import urlopen, Request
from PIL import Image,ImageTk
import widgets.Widget as Widget


class Map(Widget.Widget):
    def __init__(self,master,x,y,m_W,m_H,w,h):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h,bg='blue')
        self.img_oW,self.img_oH = int(w),int(h)
        self.img_w,self.img_h = int(w),int(h)
        
        self.DEFAULT_center_pt = (45.662947, -111.044888)
        self.DEFAULT_zoom=0.001
        self.DEFAULT_elev = 1500.1
        
        self.center_pt = self.DEFAULT_center_pt
        self.zoom = self.DEFAULT_zoom
        
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,bg='red')
        self.add_comp(self.canvas,0,0,w,h)
        
        # Necessary to be able to retrieve political map data (streets, buildings, names, etc., etc.)
        def image_spoof(self, tile):
            url = self._image_url(tile)
            req = Request(url)
            req.add_header('User-agent','Anaconda 3')
            fh = urlopen(req) 
            im_data = io.BytesIO(fh.read())
            fh.close()
            img = Image.open(im_data)
            img = img.convert(self.desired_tile_form)
            return img, self.tileextent(tile), 'lower'
        cimgt.OSM.get_image = image_spoof
        self.osm_img = cimgt.OSM()
        
        self.gen_plt([self.DEFAULT_center_pt[1]],[self.DEFAULT_center_pt[0]])

        self.label = tk.Label(self,bg='pink',anchor='nw')
        self.label.pack(fill=tk.BOTH)
        self.gen_img()
        
        
    def gen_plt(self,x,y,decorator='ro-',zoom=0.001,center_pt=None,**kwargs):
        if center_pt is None:
            center_pt = (sum(y)/len(y),sum(x)/len(x))
        if zoom<=0:
            zoom = self.DEFAULT_zoom
        self.center_pt = center_pt
        self.zoom = zoom
        
        self.fig = plt.figure(frameon=False)
        self.ax = plt.subplot(111,projection=self.osm_img.crs)
        self.ax.set_axis_off()
        self.fig.patch.set_facecolor('grey')

        extent = [center_pt[1]-(zoom*2.0),center_pt[1]+(zoom*2.0),center_pt[0]-zoom,center_pt[0]+zoom]
        self.ax.set_extent(extent)

        scale = np.ceil(-np.sqrt(2)*np.log(np.divide(zoom,350.0)))
        scale = (scale<20) and scale or 19
        self.ax.add_image(self.osm_img, int(scale))

        self.ax.plot(x,y,decorator,transform=ccrs.Geodetic())
        
        
    def gen_img(self):
        buff = io.BytesIO()
        self.fig.savefig(buff,format='png')
        plt.close(self.fig)
        
        self.image = Image.open(buff)
        self.image = self.autocrop_image(self.image)
        self.image = self.image.resize((self.img_w,self.img_h))
        
        self.copy_of_image = self.image.copy()
        self.photo = ImageTk.PhotoImage(self.image)
        self.label.configure(image=self.photo)
        self.label.image = self.photo
        
        buff.close()
        
        
    def redraw(self,w,h):
        self.img_w,self.img_h = int(self.img_oW/self.m_W*w), int(self.img_oH/self.m_H*h)
        self.image = self.copy_of_image.resize((self.img_w,self.img_h))
        self.photo = ImageTk.PhotoImage(self.image)
        self.label.config(image = self.photo)
        self.label.image = self.photo #avoid garbage collection
        
        
    def autocrop_image(self,image,border=0):
        # Get the bounding box
        bbox = image.getbbox()

        # Crop the image to the contents of the bounding box
        image = image.crop(bbox)

        # Determine the width and height of the cropped image
        (width,height) = image.size
    
        # Add border
        width+=border*2
        height+=border*2
    
        # Create a new image object for the output image
        cropped_image = Image.new("RGBA",(width,height),(0,0,0,0))

        # Paste the cropped image onto the new image
        cropped_image.paste(image,(border, border))

        return cropped_image
        
