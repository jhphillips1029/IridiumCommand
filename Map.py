try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import io
from urllib.request import urlopen, Request
from PIL import Image


class Map(tk.Frame):
    
    
    def __init__(self,master,center_pt,elev,zoom=0.001):
        tk.Frame.__init__(self,master)
        
        
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
        osm_img = cimgt.OSM()
        
        self.fig = plt.figure(figsize=(15,15))
        self.ax = plt.subplot(2,1,1,projection=osm_img.crs)
        
        extent = [center_pt[1]-(zoom*2.0),center_pt[1]+(zoom*2.0),center_pt[0]-zoom,center_pt[0]+zoom]
        self.ax.set_extent(extent)
        
        scale = np.ceil(-np.sqrt(2)*np.log(np.divide(zoom,350.0)))
        scale = (scale<20) and scale or 19
        self.ax.add_image(osm_img, int(scale))
        
        self.flight_path = self.ax.plot([center_pt[1]],[center_pt[0]],'ro',transform=ccrs.Geodetic())
        
        self.canvas = FigureCanvasTkAgg(self.fig,master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        
        self.pack()
        
        
    def plot(self,*args,**kwargs):
        line = self.ax.plot(*args,transform=ccrs.Geodetic(),**kwargs)
        self.Lines.append(line)
        self.canvas.draw()
