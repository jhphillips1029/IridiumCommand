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

This widget uses Map.py in conjunction with Ronnel's scraper to download data from Sierra's website in order to render a map tracking the balloon's progress.
"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import io
import widgets.Widget as Widget
from widgets.Widget import _create_rounded_rectangle
import widgets.Balloon_Coordinates as BC
import pandas as pd
import requests
from threading import Thread
import widgets.Map as Map
import numpy as np
from functools import partial


class Tracker(Widget.Widget):
    def __init__(self,master,x,y,m_W,m_H,w,h):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h,bg='black')
        tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle
        
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,bg='black')
        self.add_comp(self.canvas,0,0,w,h)
        
        self.Map = Map.Map(self,0,0,w,h,0.5*w,1.0*h)
        
        self.bc = None
        self.data = {'latitude':self.Map.DEFAULT_center_pt[0],
                     'longitude':self.Map.DEFAULT_center_pt[1]}
        
        self.coord_label = tk.Label(self,text='Coordinates:',font=('Arial',18,'bold'),fg=self.master.colors['pale yellow'],bg='black',anchor='w')
        self.add_comp(self.coord_label,0.5*self.w+130,20,155,20)
        
        self.latlon_label = tk.Label(self,text='Lat: {:9.4f}\nLon: {:9.4f}'.format(*self.Map.center_pt),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(self.latlon_label,0.5*self.w+135,40,100,30)
        
        self.elev_label = tk.Label(self,text='Altitude:',font=('Arial',18,'bold'),fg=self.master.colors['pale yellow'],bg='black',anchor='w')
        self.add_comp(self.elev_label,0.5*self.w+130,85,155,20)
        
        self.alt_label = tk.Label(self,text='Alt: {} m'.format(self.Map.DEFAULT_elev),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(self.alt_label,0.5*self.w+135,105,100,15)
        
        self.buttons = []
        x_coords = [40,10,40,70,40,40]
        y_coords = [50,80,110,80,170,200]
        symbols = ['\u2191','\u2190','\u2193','\u2192','+','-']
        cmds = [partial(self.move_map,c) for c in ['up','right','down','left','in','out']]
        for x,y,s,c in zip(x_coords,y_coords,symbols,cmds):
            button = tk.Button(self,
                               text=s,
                               command=c,
                               highlightthickness=0,
                               bd=0,
                               relief='flat',
                               bg=self.master.colors['yellow'],
                               activebackground=self.master.colors['yellow'])
            self.buttons.append(button)
            self.add_comp(button,0.5*self.w+x,y,25,25)
        
        self.redraw(m_W,m_H)
        
    def redraw(self,w,h):
        # All the pretty little ponies
        self.canvas.delete('all')
        self.canvas.create_rounded_rectangle(0,
                                             0,
                                             (0.5*self.w+100)/self.m_W*w,
                                             self.h/self.m_H*h,100/self.m_H*h,
                                             fill=self.master.colors['grey'],
                                             outline='')
        self.canvas.create_rectangle(0,
                                     0,
                                     (0.5*self.w+5)/self.m_W*w,
                                     self.h/self.m_H*h,
                                     fill='black',
                                     outline='')
        self.canvas.create_rounded_rectangle((0.5*self.w+110)/self.m_W*w,
                                             0,
                                             (0.5*self.w+310)/self.m_W*w,
                                             self.h/self.m_H*h,100/self.m_H*h,
                                             fill=self.master.colors['pale blue'],
                                             outline='')
        self.canvas.create_rectangle((0.5*self.w+110)/self.m_W*w,
                                     (self.h*0.15)/self.m_H*h,
                                     (0.5*self.w+310)/self.m_W*w,
                                     (self.h*0.85)/self.m_H*h,
                                     fill='black',
                                     outline='')
        self.canvas.create_rectangle((0.5*self.w+110)/self.m_W*w,
                                     (self.h*0.15+5)/self.m_H*h,
                                     (0.5*self.w+310)/self.m_W*w,
                                     (self.h*0.85-5)/self.m_H*h,
                                     fill=self.master.colors['pink'],
                                     outline='')
        self.canvas.create_rounded_rectangle((0.5*self.w+115)/self.m_W*w,
                                             5/self.m_H*h,
                                             (0.5*self.w+305)/self.m_W*w,
                                             (self.h-5)/self.m_H*h,
                                             90/self.m_H*h,
                                             fill='black',
                                             outline='')
                                             
        # Actually deal with resizing
        self.coord_label.configure(font=('Arial',int(18/self.m_H*h),'bold'))
        self.latlon_label.configure(font=('Arial',int(10/self.m_H*h)))
        self.elev_label.configure(font=('Arial',int(18/self.m_H*h),'bold'))
        self.alt_label.configure(font=('Arial',int(10/self.m_H*h)))
        
        for btn in self.buttons:
            btn.configure(font=('Arial',int(18/self.m_H*h)))
        
        self.Map.resize((self.w)/self.m_W*w,(self.h)/self.m_H*h)
        
        
    def move_map(self,ind):
        # Threading to prevent freezing in main thread
        t1 = Thread(target=self._move_map,args=(ind,))
        t1.start()
    
    
    def _move_map(self,ind):
        cntr = list(self.Map.center_pt)
        zoom = self.Map.zoom
        
        if ind=='left':
            cntr[1]+=zoom
        elif ind=='right':
            cntr[1]-=zoom
        elif ind=='up':
            cntr[0]+=zoom
        elif ind=='down':
            cntr[0]-=zoom
        elif ind=='in':
            zoom-=0.25*zoom
        elif ind=='out':
            zoom+=0.75*zoom
            
        self.Map.gen_plt(self.data['longitude'],
                         self.data['latitude'],
                         center_pt=cntr,
                         zoom=zoom)
        self.Map.gen_img()
        
        return;   # kill thread on finish
        
        
    def _update_coords(self,clear):
        if self.bc is None:
            pass
        else:
            try:
                urlData = requests.get("https://borealis.rci.montana.edu/flight?uid={}&format=csv".format(self.bc.uid)).content
                data = pd.read_csv(io.StringIO(urlData.decode('UTF-8')))
            except:
                data = self.data
            if data.shape==self.data.shape:
                pass   # self.master.log('No new data',lvl='DEBUG')
            else:
                self.data = data
                self.master.log('New data received',lvl='DEBUG')
                
                spread = np.array(self.data[['latitude','longitude']].max()) - np.array(self.data[['latitude','longitude']].min())
                zoom = (np.sqrt(sum(spread**2))/10**1)**0.5
                
                self.Map.gen_plt(self.data['longitude'], self.data['latitude'],zoom=zoom)
                self.Map.gen_img()
                
                self.latlon_label.configure(text='Lat: {:9.4f}\nLon: {:9.4f}'.format(list(self.data['latitude'])[-1],list(self.data['longitude'])[-1]))
                self.alt_label.configure(text='Alt: {:7.2f} m'.format(list(self.data['altitude'])[-1]))
                
                self.master.log('Payload @ ({:9.4f},{:9.4f})|{:7.2f} m'.format(list(self.data['latitude'])[-1],list(self.data['longitude'])[-1],list(self.data['altitude'])[-1]))
                
        
        self.after(5000,self.update_coords)
        return;   # kill thread on finish
        

    def update_coords(self,clear=False):
        # Threading to prevent freezing in main thread
        t1 = Thread(target=self._update_coords,args=(clear,))
        t1.start()
        
        
    def set_profile(self):
        self.bc = BC.Balloon_Coordinates(self.master.profile['imei'])
        self.data = pd.DataFrame()
        self.update_coords(clear=True)

