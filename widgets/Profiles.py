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

This widget manages the balloon profiles. Profiles are stored as jsons, and contain data for the name of the flight, the imei for the flight, and the command aliases for the flight.
"""

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    from Tkinter import filedialog
import widgets.Widget as Widget
from widgets.Widget import _create_rounded_rectangle
import json
import glob
    
class Profiles(Widget.Widget):
    def __init__(self,master,x,y,m_W,m_H,w=300,h=300):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h,bg='black')
        tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle
        
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,bg='black')
        self.add_comp(self.canvas,0,0,w,h)
        
        self.labels = []
        for i in range(8):
            label = tk.Label(self,
                             text=bin(i)[2:].zfill(3),
                             fg=self.master.colors['pale yellow'],
                             bg='black')
            self.labels.append(label)
            self.add_comp(label,115,145+25*i,50,20)
        for i in range(8):
            label = tk.Label(self,
                             text='Not set',
                             anchor='w',
                             fg=self.master.colors['pale yellow'],
                             bg='black')
            self.labels.append(label)
            self.add_comp(label,165,145+25*i,150,20)
            
        label = tk.Label(self,
                         text='Name: Not yet selected',
                         anchor='w',
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.labels.append(label)
        self.add_comp(label,115,95,250,20)
        
        label = tk.Label(self,
                         text='IMEI: Not set',
                         anchor='w',
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.labels.append(label)
        self.add_comp(label,115,120,250,20)
        
        self.entries = []
        for i in range(8):
            label = tk.Label(self,
                             text=bin(i)[2:].zfill(3),
                             fg=self.master.colors['pale yellow'],
                             bg='black')
            self.labels.append(label)
            self.add_comp(label,715,145+25*i,50,20)
        for i in range(8):
            placeholder = tk.StringVar(self,value=bin(i)[2:].zfill(3))
            entry = tk.Entry(self,
                             textvariable=placeholder,
                             fg=self.master.colors['pale yellow'],
                             bg='black')
            self.entries.append(entry)
            self.add_comp(entry,765,145+25*i,150,20)
            
        label = tk.Label(self,
                         text='Name:',
                         anchor='w',
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.labels.append(label)
        self.add_comp(label,715,95,50,20)
        
        label = tk.Label(self,
                         text='IMEI:',
                         anchor='w',
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.labels.append(label)
        self.add_comp(label,715,120,50,20)
            
        placeholder = tk.StringVar(self,value='Name')
        entry = tk.Entry(self,
                         textvariable=placeholder,
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.entries.append(entry)
        self.add_comp(entry,765,95,200,20)
        
        placeholder = tk.StringVar(self,value='IMEI')
        entry = tk.Entry(self,
                         textvariable=placeholder,
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.entries.append(entry)
        self.add_comp(entry,765,120,200,20)
        
        self.load_profile = tk.Button(self,
                                      text='Load Profile',
                                      command=self.load_profile,
                                      anchor='se',
                                      highlightthickness=0,
                                      bd=0,
                                      relief='flat',
                                      bg=self.master.colors['orange'],
                                      activebackground=self.master.colors['orange'])
        self.add_comp(self.load_profile,120,self.h-60,100,30)
        
        self.save_new = tk.Button(self,
                                  text='Save New',
                                  command=lambda:self.save_profile(False),
                                  anchor='se',
                                  highlightthickness=0,
                                  bd=0,
                                  relief='flat',
                                  bg=self.master.colors['orange'],
                                  activebackground=self.master.colors['orange'])
        self.add_comp(self.save_new,700,self.h-60,100,30)
        
        self.overwrite = tk.Button(self,
                                  text='Overwrite',
                                  command=lambda:self.save_profile(True),
                                  anchor='se',
                                  highlightthickness=0,
                                  bd=0,
                                  relief='flat',
                                  bg=self.master.colors['orange'],
                                  activebackground=self.master.colors['orange'])
        self.add_comp(self.overwrite,805,self.h-60,100,30)
        
        self.redraw(m_W,m_H)
        
        
    def redraw(self,w,h):
        self.canvas.delete('all')
        
        # Actually deal with resizing
        for label in self.labels:
            label.configure(font=('Arial',int(10/self.m_H*h)))
            
        self.load_profile.configure(font=('Arial',int(10/self.m_H*h)))
        
        # All the pretty little ponies
        self.canvas.create_rounded_rectangle(0,0,(self.w/2-2.5)/self.m_W*w,self.h/self.m_H*h,100/self.m_H*h,fill=self.master.colors['grey'],outline='')
        self.canvas.create_rounded_rectangle((self.w/2+2.5)/self.m_W*w,0,self.w/self.m_W*w,self.h/self.m_H*h,100/self.m_H*h,fill=self.master.colors['grey'],outline='')
        
        self.canvas.create_rectangle(0,0,(self.w/4)/self.m_W*w,self.h/self.m_H*h,fill=self.master.colors['grey'],outline='')
        self.canvas.create_rectangle((self.w/4*3)/self.m_W*w,0,self.w/self.m_W*w,self.h/self.m_H*h,fill=self.master.colors['grey'],outline='')
        
        self.canvas.create_rounded_rectangle(30/self.m_W*w,10/self.m_H*h,(self.w/2-2.5-100)/self.m_W*w,(self.h-10)/self.m_H*h,30/self.m_H*h,fill='black',outline='')
        self.canvas.create_rounded_rectangle((self.w/2+2.5+100)/self.m_W*w,10/self.m_H*h,(self.w-30)/self.m_W*w,(self.h-10)/self.m_H*h,30/self.m_H*h,fill='black',outline='')
        
        self.canvas.create_rectangle(0,30/self.m_H*h,(self.w/4)/self.m_W*w,(self.h-30)/self.m_H*h,fill='black',outline='')
        self.canvas.create_rectangle((self.w/4*3)/self.m_W*w,30/self.m_H*h,self.w/self.m_W*w,(self.h-30)/self.m_H*h,fill='black',outline='')
        
        
    def save_profile(self,overwrite):
        aliases = [entry.get() for entry in self.entries[:-2]]
        name = self.entries[-2].get()
        imei = self.entries[-1].get()
        
        if not overwrite:
            files = glob.glob('profiles/*.json')
            if 'profiles/{}.json'.format(name) in files:
                counter = 1
                while 'profiles/{}.json'.format(name) in files:
                    name = '{} ({}).json'.format(name.split('({})'.format(counter-1))[0],counter)
                    counter+=1
                    
            name = name.replace('.json','')
            new_profile = {'name':name,
                           'imei':imei,
                           'commands':{aliases[i]:bin(i)[2:].zfill(3) for i in range(len(aliases))}
                          }
            
            with open('profiles/{}.json'.format(name),'w') as f:
                json.dump(new_profile, f)
        else:
            name = name.replace('.json','')
            new_profile = {'name':name,
                           'imei':imei,
                           'commands':{aliases[i]:bin(i)[2:].zfill(3) for i in range(len(aliases))}
                          }
            with open('profiles/{}.json'.format(name),'w') as f:
                json.dump(new_profile, f)
        self.load_json('profiles/{}.json'.format(name))
        
        
    def load_profile(self):
        f = filedialog.askopenfilename(initialdir='profiles/')
        self.load_json(f)
        
        
    def load_json(self,fname):
        with open(fname,'r') as f:
            data = json.load(f)
            self.master.set_profile(data)
            
            
    def set_profile(self):
        self.profile = self.master.profile
        for i,lbl in enumerate(self.labels[8:16]):
            lbl.configure(text=list(self.profile['commands'].keys())[i])
        for i,entry in enumerate(self.entries[:-2]):
            placeholder = tk.StringVar(self,value=list(self.profile['commands'].keys())[i])
            entry.configure(textvariable=placeholder)
            
        self.labels[16].configure(text='Name: {}'.format(self.profile['name']))
        self.labels[17].configure(text='IMEI: {}'.format(self.profile['imei']))
        
        placeholder=tk.StringVar(self,value=self.profile['name'])
        self.entries[-2].configure(textvariable=placeholder)
        placeholder=tk.StringVar(self,value=self.profile['imei'])
        self.entries[-1].configure(textvariable=placeholder)

