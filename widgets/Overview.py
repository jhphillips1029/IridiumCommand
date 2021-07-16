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

This widget sends the commands to the Iridium modem on the balloon via emails to Iridium.
"""

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    import Tkinter as tk
    from Tkinter import messagebox
import widgets.Widget as Widget
from widgets.Widget import _create_rounded_rectangle
from functools import partial
import widgets.Emailer as Emailer

EMAIL_ADDRESS = 'iridium.msgc@gmail.com'

class Overview(Widget.Widget):


    def __init__(self,master,x,y,m_W,m_H,w=300,h=300):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h,bg='black')
        
        self.COMMANDS = [
            '000',
            '001',
            '010',
            '011',
            '100',
            '101',
            '110',
            '111'
        ]
        
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,bg='black')
        self.add_comp(self.canvas,0,0,w,h)
        
        self.active_cmd = 0
        self.btns = []
        for i in range(8):
            self.btns.append(tk.Button(self,
                                    text=str(bin(i)[2:].zfill(3)),
                                    command=partial(self.set_cmd,i),
                                    anchor='se',
                                    highlightthickness=0,
                                    bd=0,
                                    relief='flat',
                                    bg=self.master.colors['yellow'],
                                    activebackground=self.master.colors['yellow']
                                   ))
        for i in range(len(self.btns)):
            self.add_comp(self.btns[i],self.w-100,65+40*i,100,35)
    
        self.send_cmd_btn = tk.Button(self,
                                      text='Send Command',
                                      command=self.send_command,
                                      anchor='se',
                                      highlightthickness=0,
                                      bd=0,
                                      relief='flat',
                                      bg=self.master.colors['red'],
                                      activebackground=self.master.colors['red'])
        self.add_comp(self.send_cmd_btn,505,105,150,50)
        
        self.labels = []
        for i in range(8):
            label = tk.Label(self,
                             text=bin(i)[2:].zfill(3),
                             fg=self.master.colors['pale yellow'],
                             bg='black')
            self.labels.append(label)
            self.add_comp(label,100,100+25*i,50,20)
        for i in range(8):
            label = tk.Label(self,
                             text='Not set',
                             anchor='w',
                             fg=self.master.colors['pale yellow'],
                             bg='black')
            self.labels.append(label)
            self.add_comp(label,155,100+25*i,150,20)
            
        label = tk.Label(self,
                         text='Profile: Select under \'Profiles\'',
                         anchor='w',
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.labels.append(label)
        self.add_comp(label,100,50,250,20)
            
        label = tk.Label(self,
                         text='IMEI: Not set',
                         anchor='w',
                         fg=self.master.colors['pale yellow'],
                         bg='black'
                        )
        self.labels.append(label)
        self.add_comp(label,100,75,250,20)
                          
        self.update()
        tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle
        self.redraw(m_W,m_H)
        
        
    def redraw(self,w,h):
        self.canvas.delete('all')
        
        # Draw all the pretty UI decorations
        self.canvas.create_rounded_rectangle(0,
                                             0,
                                             self.w/self.m_W*w,
                                             self.h/self.m_H*h,
                                             100/self.m_H*h,
                                             fill=self.master.colors['grey'],
                                             outline='')
        self.canvas.create_rounded_rectangle(0,
                                             30/self.m_H*h,
                                             (self.w-100)/self.m_W*w,
                                             (self.h-30)/self.m_H*h,
                                             30/self.m_H*h,
                                             fill='black',
                                             outline='')
        self.canvas.create_rectangle(0,
                                     0,
                                     200/self.m_W*w,
                                     self.h/self.m_H*h,
                                     fill='black',
                                     outline='')
        self.canvas.create_rounded_rectangle(100/self.m_W*w,
                                             0,
                                             300/self.m_W*w,
                                             30/self.m_H*h,
                                             30/self.m_H*h,
                                             fill=self.master.colors['grey'],
                                             outline='')
        self.canvas.create_rounded_rectangle(100/self.m_W*w,
                                             (self.h-30)/self.m_H*h,
                                             300/self.m_W*w,
                                             self.h/self.m_H*h,
                                             30/self.m_H*h,
                                             fill=self.master.colors['grey'],
                                             outline='')
        self.canvas.create_rectangle((self.w-100)/self.m_W*w,
                                     60/self.m_H*h,
                                     self.w/self.m_W*w,
                                     (self.h-55)/self.m_H*h,
                                     fill='black',
                                     outline='')
        
        self.canvas.create_rounded_rectangle(500/self.m_W*w,
                                             100/self.m_H*h,
                                             665/self.m_W*w,
                                             165/self.m_H*h,
                                             30/self.m_H*h,
                                             fill=self.master.colors['red'],
                                             outline='')
        
        # Actually deal with resizing
        self.send_cmd_btn.configure(font=('Arial',int(10/self.m_H*h),'bold'))
        
        for i in range(len(self.btns)):
            ind_color = self.master.colors['red'] if i==self.active_cmd else self.master.colors['grey']
            
            self.btns[i].configure(font=('Arial',int(10/self.m_H*h),'bold'))
            
            self.canvas.create_rounded_rectangle((self.w-130)/self.m_W*w,
                                                 (65+40*i)/self.m_H*h,
                                                 self.w/self.m_W*w,
                                                 (65+40*i+35)/self.m_H*h,
                                                 35/self.m_H*h,
                                                 fill=ind_color,
                                                 outline='')
            self.canvas.create_rectangle((self.w-105)/self.m_W*w,
                                         (65+40*i)/self.m_H*h,
                                         self.w/self.m_W*w,
                                         (65+40*i+35)/self.m_H*h,
                                         fill='black',
                                         outline='')
                                         
        for label in self.labels:
            label.configure(font=('Arial',int(10/self.m_H*h)))
        
                          
    def set_cmd(self,cmd_num):
        self.active_cmd = cmd_num
        self.redraw(self.master.width,self.master.height)
        
        
    def set_profile(self):
        self.profile = self.master.profile
        for i,lbl in enumerate(self.labels[8:-2]):
            lbl.configure(text=list(self.profile['commands'].keys())[i])
            self.btns[i].configure(text=list(self.profile['commands'].keys())[i])
            
        self.labels[-2].configure(text='Profile: {}'.format(self.profile['name']))
        self.labels[-1].configure(text='Profile: {}'.format(self.profile['imei']))
        
        
    def send_command(self):
        if self.master.profile is not None:
            alias = list(self.master.profile['commands'].keys())[self.active_cmd]
            cmd = bin(self.active_cmd)[2:].zfill(3)
            imei = self.master.profile['imei']
            if messagebox.askyesno(title='Confirmation',message='Is this correct:\n\nCmd: {} ({})\nIMEI: {}'.format(alias,cmd,imei)):
                ret = self.send_iridium_cmd(cmd,imei)
                self.master.log('Command ({},{}) sent. ({})'.format(cmd,imei[-4:],ret['labelIds'][0]))
            else:
                self.master.log('Command aborted.')
        else:
            self.master.log('No profile selected!',lvl='DEBUG')
    
    
    def send_iridium_cmd(self,cmd,imei):
        if cmd not in self.COMMANDS:
            raise ValueError('Command must be one of the ones defined')
            
        srvc       = Emailer.gmail_authenticate()
        to         = 'data@sbd.iridium.com'
        subject    = imei
        msg        = ''
        attachment = 'attachments/{}.sbd'.format(cmd)
    
        return Emailer.send_message(srvc,to,subject,msg,attachments=[attachment])
