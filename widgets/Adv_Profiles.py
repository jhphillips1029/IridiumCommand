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
import numpy as np
from itertools import groupby
from operator import itemgetter
import os
    
class Adv_Profiles(Widget.Widget):
    def __init__(self,master,x,y,m_W,m_H,w=300,h=300):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h,bg='black')
        tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle
        
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,bg='black')
        self.add_comp(self.canvas,0,0,w,h)
        
        self.add_comp(tk.Button(self,
                                text='Open Profile',
                                font=('Arial',10,'bold'),
                                command=self.load_profile,
                                anchor='se',
                                highlightthickness=0,
                                bd=0,
                                relief='flat',
                                bg=self.master.colors['orange'],
                                activebackground=self.master.colors['orange']
                               ),
                      150,395,100,30)
        
        self.add_comp(tk.Button(self,
                                text='Save',
                                font=('Arial',10,'bold'),
                                command=self.save_profile,
                                anchor='se',
                                highlightthickness=0,
                                bd=0,
                                relief='flat',
                                bg=self.master.colors['orange'],
                                activebackground=self.master.colors['orange']
                               ),
                      725,395,100,30)
        
        self.disp_label = tk.Label(self,
                                   text='Lorem Ipsum... Blah, blah, blah.',
                                   font=('Arial',10),
                                   anchor='nw',
                                   bg='black',
                                   fg=self.master.colors['pale yellow']
                                  )
        self.add_comp(self.disp_label,50,35,310,350)
        
        self.edit_entry = tk.Text(self,
                                  font=('Arial',10),
                                  bg='black',
                                  fg=self.master.colors['pale yellow'],
                                  insertbackground=self.master.colors['pale yellow']
                                 )
        self.edit_entry.insert(1.0,'Lorem Ipsum... BLah, blah, blah.')
        self.add_comp(self.edit_entry,625,35,310,350)
        
        self.redraw(m_W,m_H)
        
        
    def save_profile(self):
        text = self.edit_entry.get(1.0,'end').rstrip()
        json_dict = self.collect_dict(text)
        name = json_dict['name']
        with open('profiles/{}.json'.format(name),'w') as f:
            json.dump(json_dict,f)
        self.load_json('{}/profiles/{}.json'.format(os.path.dirname(os.path.realpath(__file__))[:-len('/widgets')],name))
        
        
    def collect_dict(self,text):
        ret_dict = {}
    
        lines = np.array([line for line in text.split('\n') if len(line)>0])
        indent_lens = np.array([len(line.split(' : ')[0]) for line in lines])
        part_lens = np.array([len([part for part in line.split(' : ') if len(part)>0]) for line in lines])
    
        levels = list(set(indent_lens))
        levels.sort(reverse=True)
        sub_dicts = [[] for level in levels]
        indices = np.array(range(len(lines)))
        for level in levels:
            sub_indices = indices[indent_lens==level]
            for k,g in groupby(enumerate(sub_indices),lambda ix:ix[0]-ix[1]):
                indexes = list(map(itemgetter(1),g))
                d = {}
                for index in indexes:
                    parts = lines[index].split(' : ')
                    d[parts[0].strip()]=parts[1].strip()
                sub_dicts[levels.index(level)].append(d)
            
        for i in range(len(sub_dicts)-1):
            upper_dict_list = sub_dicts[i+1]
            current_dict_list = sub_dicts[i]
            for j in range(len(current_dict_list)):
                last_key = list(upper_dict_list[j].keys())[-1]
                if len(upper_dict_list[j][last_key])>0:
                    raise ValueError('Someone fucked up indentation.')
                upper_dict_list[j][last_key]=current_dict_list[j]
                
        for sub_dict in sub_dicts[-1]:
            for key in sub_dict.keys():
                ret_dict[key] = sub_dict[key]
                
        return ret_dict
        
        
    def load_profile(self):
        f = filedialog.askopenfilename(initialdir='profiles/')
        self.load_json(f)
        
        
    def load_json(self,fname):
        with open(fname,'r') as f:
            data = json.load(f)
            self.master.set_profile(data)
            
            
    def set_profile(self):
        text = self.disp_dict(self.master.profile)
        lines = text.split('\n')
        max_len = max([len(line) for line in lines])
        lines = [line+' '*(max_len-len(line)) for line in lines]
        self.disp_label.configure(text='\n'.join(lines))
        self.edit_entry.delete(1.0,'end')
        self.edit_entry.insert(1.0,text)
        
        
    def disp_dict(self,my_dict,indent_dist=0):
        lines = []
        if type(my_dict)==type([]):
            my_dict = {str(i):var for i,var in enumerate(my_dict)}
        longest_key_len = max([len(key) for key in my_dict.keys()])
        for key in my_dict.keys():
            lines.append(' '*(longest_key_len-len(key)+indent_dist)+key+' : ')
            if str(type(my_dict[key])).split('\'')[1] in ['dict','list']:
                lines.append('\n')
                lines.append(self.disp_dict(my_dict[key],longest_key_len+indent_dist+3))
            else:
                lines.append(my_dict[key]+'\n')
            
        return ''.join(lines)
        
        
    def redraw(self,w,h):
        self.canvas.delete('all')
        
        # All the pretty little ponies
        self.canvas.create_rounded_rectangle(0,0,(self.w/2-2.5)/self.m_W*w,self.h/self.m_H*h,100/self.m_H*h,fill=self.master.colors['grey'],outline='')
        self.canvas.create_rounded_rectangle((self.w/2+2.5)/self.m_W*w,0,self.w/self.m_W*w,self.h/self.m_H*h,100/self.m_H*h,fill=self.master.colors['grey'],outline='')
        
        self.canvas.create_rectangle(0,0,(self.w/4)/self.m_W*w,self.h/self.m_H*h,fill=self.master.colors['grey'],outline='')
        self.canvas.create_rectangle((self.w/4*3)/self.m_W*w,0,self.w/self.m_W*w,self.h/self.m_H*h,fill=self.master.colors['grey'],outline='')
        
        self.canvas.create_rounded_rectangle(30/self.m_W*w,10/self.m_H*h,(self.w/2-2.5-100)/self.m_W*w,(self.h-10)/self.m_H*h,30/self.m_H*h,fill='black',outline='')
        self.canvas.create_rounded_rectangle((self.w/2+2.5+100)/self.m_W*w,10/self.m_H*h,(self.w-30)/self.m_W*w,(self.h-10)/self.m_H*h,30/self.m_H*h,fill='black',outline='')
        
        self.canvas.create_rectangle(0,30/self.m_H*h,(self.w/4)/self.m_W*w,(self.h-30)/self.m_H*h,fill='black',outline='')
        self.canvas.create_rectangle((self.w/4*3)/self.m_W*w,30/self.m_H*h,self.w/self.m_W*w,(self.h-30)/self.m_H*h,fill='black',outline='')

