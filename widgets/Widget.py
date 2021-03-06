"""
----------------------------------------------------------------------------
MIT License
Copyright (c) 2022 Joshua H. Phillips
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
----------------------------------------------------------------------------

This is the abstract Widget class. All other widgets must extend this class.
"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
from abc import ABC,abstractmethod

class Widget(tk.Frame):
    '''
    The template for widgets
    '''

    @abstractmethod
    def __init__(self,master,x,y,m_W,m_H,w,h,**kwargs):
        '''
        The initialization function
        
        Parameters:
        self     (Widget): Required for object functions
        master (tk.Frame): The parent frame
        x           (int): The x-coordinate of the top left corner
        y           (int): The y-coordinate of the top left corner
        m_W         (int): The width of the parent frame
        m_H         (int): The height of the parent frame
        w           (int): The width of the widget
        h           (int): The height of the widget
        **kwargs         : Additional parameters
        
        Returns:
        None
        '''
    
        tk.Frame.__init__(self,master,width=w,height=h,**kwargs)
        self.master = master
        self.x,self.y = x,y
        self.m_W,self.m_H = m_W,m_H
        self.w,self.h = w,h
        self.components = []
        self.place(x=x,y=y)


    def resize(self,w,h):
        '''
        Automatically handles effects of window resizing, such as scaling text, enforcing correct colors, etc
        
        Parameters:
        self (Widget): Required for object functions
        w       (int): New width of parent frame
        h       (int): New height of parent frame
        
        Returns:
        None
        '''
    
        self.configure(width=self.w/self.m_W*w,height=self.h/self.m_H*h)
        self.place(x=self.x/self.m_W*w,y=self.y/self.m_H*h)
        
        for cl in self.components:
            cl[0].place(x=cl[1]/self.m_W*w,
                        y=cl[2]/self.m_H*h,
                        width=int(cl[3]/self.m_W*w),
                        height=int(cl[4]/self.m_H*h))
            try:
                font = cl[-1]['font'].split(' ')
                if len(font)<=1:
                    raise ValueError('Ignoring unspecified font')
                font[1] = int(int(font[1])/self.m_H*h)
                cl[0].configure(font=tuple(font))
            except: pass
            for trait in ['background','foreground','activebackground','activeforeground','insertbackground']:
                if trait in cl[-1].keys():
                    cl[0][trait] = self.master.colors[cl[-1][trait]]
        
        if 'redraw' in dir(self):
            # If 'redraw' is an actual function for this widget, call it.
            self.redraw(w,h)


    def show(self,w,h):
        '''
        Shows the widget
        '''
    
        self.place(x=self.x/self.m_W*w,y=self.y/self.m_H*h)
        self.focus_set()


    def hide(self):
        '''
        Hides the widget
        '''
    
        self.place_forget()
        
        
    def add_comp(self,comp,x,y,w,h):
        '''
        Adds components to registery of components; allows for automatic scaling when window resized
        '''
    
        comp_attr = {}
        for trait in ['background','foreground','activebackground','activeforeground','insertbackground','font']:
            try:
                dummy = comp[trait]
                if trait not in ['font']:
                    for key in self.master.colors.keys():
                        if dummy == self.master.colors[key]:
                            comp_attr[trait] = key
                            break
                else:
                    comp_attr[trait] = dummy
            except: pass
        self.components.append([comp,x,y,w,h,comp_attr])
        self.components[-1][0].place(x=x,y=y,width=w,height=h)
        

    def get_comp(self,i):
        '''Getter for components registery'''
        return self.components[i][0]
        
        
    def _close(self):
        '''Wrapper for window close event'''
        if 'close' in dir(self):
            self.close()
            
            
    def _set_alert(self,level):
        '''Set alert level'''
        if 'set_alert' in dir(self):
            self.set_alert(level)
        
        
    def _set_profile(self,profile):
        '''Set flight command profile'''
        if 'set_profile' in dir(self):
            # If 'set_profile' is an actual function in this widget, call it.
            self.set_profile()
            
        return;
        
      
# For creating all the pretty little ponies  
def _create_rounded_rectangle(self,x1,y1,x2,y2,radius,**kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]

    return self.create_polygon(points, **kwargs, smooth=True)

