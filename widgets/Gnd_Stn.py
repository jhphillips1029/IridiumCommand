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

This is a port for the ground station gui developed by Matthew Clutter in order to run in it as a widget in the ICC.
"""


try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import widgets.Widget as Widget
    
class Gnd_Stn(Widget.Widget):
    '''
    This serves as a starting point for integrating Matthew's ground station GUI
    
    TODO:
    * Create graphical components in this file
    * Link graphical components in this file to functions in Matthew's program
    * (?) Sync graphical theme?
    '''

    def __init__(self,master,x,y,m_W,m_H,w=300,h=300):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h)
        
        self.X_B1,self.Y_B1 = 0,0
        self.add_comp(tk.Button(self,
                                text='Potato',
                                font=('Arial',10)
                               ),
                      self.X_B1,self.Y_B1,100,100)
        
        
    def redraw(self,w,h):
        pass

