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

This is a demo "Hello, World!" widget. It creates a label and a button and prints "Hello, World!" to the log everytime the button is pressed.
"""

# Import statements
try:
    import tkinter as tk   # for python3
except ImportError:
    import Tkinter as tk   # for python2
import widgets.Widget as Widget   # required
    
class Demo(Widget.Widget):   # extends Widget class
    def __init__(self,master,x,y,m_W,m_H,w=300,h=300):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h)
        #print(1/0)   # Uncomment this line to watch the main app work around add-on import errors!
        
        # Use the self.add_comp() function to add components to the widget's registry of components so that it can be resized with the window
        self.add_comp(tk.Button(self,command=self.demo_button),100,100,100,100)
        self.add_comp(tk.Label(self,text='Hello, World!',font=('Arial',10)),0,0,100,30)
        
        
    def redraw(self,w,h):
        # There are components with text, so we must deal with their resizing
        # self.redraw() is called (if it exists) whenever the app is resized
        self.components[0][0].configure(font=('Arial',int(10/self.m_H*h)))
        
        
    def demo_button(self):
        # Print "Hello, World!" to the log
        self.master.log('Hello, World!',lvl='DEMO')

