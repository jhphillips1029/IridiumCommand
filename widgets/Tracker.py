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
import urllib
from threading import Thread
import widgets.Map as Map
import numpy as np
from functools import partial


class Tracker(Widget.Widget):
    def __init__(self,master,x,y,m_W,m_H,w,h):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h,bg='black')
        tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle
        
        self.p_0 = 101325
        self.T_0 = 288.16
        self.g = 9.80665
        self.M = 0.02896968
        self.R_0 = 8.314462618
        
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,bg='black')
        self.add_comp(self.canvas,0,0,w,h)
        
        self.Map = Map.Map(self,0,0,w,h,0.5*w,1.0*h)
        
        self.bc = None
        self.data = {'latitude':[self.Map.DEFAULT_center_pt[0]],
                     'longitude':[self.Map.DEFAULT_center_pt[1]],
                     'uid':[0]}
        
        self.titles = []
        self.labels = []
        
        title = tk.Label(self,text='Coordinates:',font=('Arial',18,'bold'),fg=self.master.colors['pale yellow'],bg='black',anchor='w')
        self.add_comp(title,0.5*self.w+130,20,155,25)
        self.titles.append(title)
        
        label = tk.Label(self,text='Lat: {:9.4f}\nLon: {:9.4f}'.format(*self.Map.center_pt),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(label,0.5*self.w+135,40,100,30)
        self.labels.append(label)
        self.latlon_label = label
        
        title = tk.Label(self,text='Altitude:',font=('Arial',18,'bold'),fg=self.master.colors['pale yellow'],bg='black',anchor='w')
        self.add_comp(title,0.5*self.w+130,85,155,25)
        self.titles.append(title)
        
        label = tk.Label(self,text='Alt: {:7.2f} m'.format(self.Map.DEFAULT_elev),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(label,0.5*self.w+135,105,100,15)
        self.labels.append(label)
        self.alt_label = label
        
        label = tk.Label(self,text='Alt: {:7.1f} ft'.format(self.Map.DEFAULT_elev*3.28084),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(label,0.5*self.w+135,120,100,15)
        self.labels.append(label)
        self.altft_label = label
        
        params = {'output':'json','x':self.Map.DEFAULT_center_pt[1],'y':self.Map.DEFAULT_center_pt[0],'units':'Meters'}
        url = r'https://nationalmap.gov/epqs/pqs.php?'
        result = requests.get((url + urllib.parse.urlencode(params)))
        agl = float(result.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']) - self.Map.DEFAULT_elev
        label = tk.Label(self,text='AGL: {:7.2f} m'.format(agl),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(label,0.5*self.w+135,135,100,15)
        self.labels.append(label)
        self.agl_label = label
        
        title = tk.Label(self,text='Velocities:',font=('Arial',18,'bold'),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(title,0.5*self.w+130,165,155,25)
        self.titles.append(title)
        
        label = tk.Label(self,text='Vert: {:7.2f} m/s'.format(0),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(label,0.5*self.w+135,190,125,15)
        self.labels.append(label)
        self.vertvel_label = label
        
        label = tk.Label(self,text='Grnd: {:7.2f} m/s'.format(0),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(label,0.5*self.w+135,205,125,15)
        self.labels.append(label)
        self.grndvel_label = label
        
        p_theory = self.p_0*np.exp(-((self.g*self.Map.DEFAULT_elev*self.M)/(self.T_0*self.R_0)))
        pcntg = 100*(1-p_theory/self.p_0)
        label = tk.Label(self,text='You are above {:6.2f}% of\nthe atmosphere.'.format(pcntg),font=('Arial',10),fg=self.master.colors['pale yellow'],bg='black',anchor='nw')
        self.add_comp(label,0.5*self.w+130,235,155,30)
        self.labels.append(label)
        self.pcntg_label = label
        
        self.buttons = []
        x_coords = [40,10,40,70,40,40]
        y_coords = [50,80,110,80,170,200]
        symbols = ['\u2191','\u2190','\u2193','\u2192','+','-']
        cmds = [partial(self.move_map,c) for c in ['up','right','down','left','in','out']]
        for x,y,s,c in zip(x_coords,y_coords,symbols,cmds):
            button = tk.Button(self,
                               text=s,
                               font=('Arial',18),
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
            return;
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
                if list(self.data['uid'])[-1]!=self.bc.uid:
                    return;
                self.master.log('New data received',lvl='DEBUG')
                
                spread = np.array(self.data[['latitude','longitude']].max()) - np.array(self.data[['latitude','longitude']].min())
                zoom = (np.sqrt(sum(spread**2))/10**1)**0.5
                
                self.Map.gen_plt(self.data['longitude'], self.data['latitude'],zoom=zoom)
                self.Map.gen_img()
                
                self.latlon_label.configure(text='Lat: {:9.4f}\nLon: {:9.4f}'.format(list(self.data['latitude'])[-1],list(self.data['longitude'])[-1]))
                self.alt_label.configure(text='Alt: {:7.2f} m'.format(list(self.data['altitude'])[-1]))
                
                self.altft_label.configure(text='Alt: {:7.1f} ft'.format(list(self.data['altitude'])[-1]*3.28084))
                
                params = {'output':'json','x':list(self.data['longitude'])[-1],'y':list(self.data['latitude'])[-1],'units':'Meters'}
                url = r'https://nationalmap.gov/epqs/pqs.php?'
                result = requests.get((url + urllib.parse.urlencode(params)))
                agl = float(result.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']) - list(self.data['altitude'])[-1]
                self.agl_label.configure(text='AGL: {:7.2f} m'.format(agl))
                
                self.vertvel_label.configure(text='Vert: {:7.2f} m/s'.format(list(self.data['vertical_velocity'])[-1]))
                
                self.grndvel_label.configure(text='Grnd: {:7.2f} m/s'.format(list(self.data['ground_speed'])[-1]))
                
                p_theory = self.p_0*np.exp(-((self.g*list(self.data['altitude'])[-1]*self.M)/(self.T_0*self.R_0)))
                pcntg = 100*(1-p_theory/self.p_0)
                self.pcntg_label.configure(text='You are above {:6.2f}% of\nthe atmosphere.'.format(pcntg))
                
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

