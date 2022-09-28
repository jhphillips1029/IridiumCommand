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

This is the live-ish temperature plotter for MSGC BOREALIS HASP 2021 for showing the effects of cutdown commands in near real-time.
"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import widgets.Widget as Widget
from widgets.Widget import _create_rounded_rectangle
import requests
import re
import io
import numpy as np
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from time import strftime
from PIL import Image,ImageTk
import traceback
    
class HASP(Widget.Widget):
    '''
    A widget for tracking the temperature activity of multiple cutdown units during testing on LSU's HASP balloon flight
    '''

    def __init__(self,master,x,y,m_W,m_H,w=300,h=300):
        '''
        The initialization function
        
        Parameters:
        self         (Widget): Required for object functions
        master (WidgetSocket): The widget socket
        x               (int): The x-coordinate of the top-left corner
        y               (int): The y-coordinate of the top-left corner
        m_W             (int): The width of the main application window
        m_H             (int): The height of the main application window
        w               (int): The width of the widget
        h               (int): The height of the widget
        
        Returns:
        None
        '''
    
        # Use parent class constructor for basic things and add ability to create rounded rectangle
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h,bg='black')
        tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle
        
        # Initialize variable and set constants and aliases
        self.img_oW,self.img_oH = int(0.5*w),int(h)
        self.img_w,self.img_h = self.img_oW,self.img_oH
        self.data = None
        self.copy_of_image = None
        self.n_brds = 8
        self.names_ = {'float':'t1',
                       'xbee':'t3',
                       'msp':'t2'
                      }
        
        # Add canvas
        self.canvas = tk.Canvas(self,width=w,height=h,bg='black',bd=0,highlightthickness=0)
        self.add_comp(self.canvas,0,0,w,h)
        
        # Add image frame
        self.img_frame = tk.Frame(self,width=self.img_oW,height=self.img_oH)
        self.add_comp(self.img_frame,0,0,self.img_oW,self.img_oH)
        
        # Get today's date
        self.today = strftime('%m-%d-%y')

        # Variables related to data collection
        self.list_url = 'https://laspace.lsu.edu/hasp/groups/2021/data/data.php?pname=Payload_11&py=2021'
        self.window = 500
        self.label = tk.Label(self.img_frame,bg='black',anchor='nw')
        self.label.pack(fill=tk.BOTH)
        
        # Set labels
        self.X_temp_block = int(self.w*0.5)+60
        self.Y_temp_block = 55
        self.add_comp(tk.Label(self,
                               text='Average Floating Temperature:',
                               font=('Arial',10),
                               anchor='w',
                               fg=self.master.colors['pale yellow'],
                               bg='black'
                              ),
                      self.X_temp_block-5,self.Y_temp_block-25,180,20)
        
        self.temp_avg_str = 'Board {:1d} Avg: {:9.4f} \u00B0C'
        self.temp_avg_block_index_start = len(self.components)
        for i in range(self.n_brds):
            label = tk.Label(self,
                             text=self.temp_avg_str.format(i+1,0),
                             font=('Arial',10),
                             anchor='w',
                             bg='black',
                             fg=self.master.colors['pale yellow']
                            )
            self.add_comp(label,self.X_temp_block,self.Y_temp_block+i*25,160,20)

        self.add_comp(tk.Label(self,
                               text='Maximum Floating Temperature:',
                               font=('Arial',10),
                               anchor='w',
                               fg=self.master.colors['pale yellow'],
                               bg='black'
                              ),
                      self.X_temp_block+210,self.Y_temp_block-25,180,20)
        
        self.temp_max_str = 'Board {:1d} Max: {:6.1f} \u00B0C'
        self.temp_max_block_index_start = len(self.components)
        for i in range(self.n_brds):
            label = tk.Label(self,
                             text=self.temp_max_str.format(i+1,0),
                             font=('Arial',10),
                             anchor='w',
                             bg='black',
                             fg=self.master.colors['pale yellow']
                            )
            self.add_comp(label,self.X_temp_block+215,self.Y_temp_block+i*25,160,20)
            
        self.cutdown_label_text = 'Detected Cutdowns\n'
        offset = 0 if self.n_brds==8 else 1
        for i in range(int(np.ceil(self.n_brds/2))):
            self.cutdown_label_text += 'B{boards['+str(i)+']:1d} (XB) {temps['+str(i)+']:{formats['+str(i)+']:}}\tB{boards['+str(i+4+(1 if offset else 0))+']:1d} (XB) {temps['+str(i+4+(1 if offset else 0))+']:{formats['+str(i+4+(1 if offset else 0))+']:}}\tB{boards['+str(i+8+(0 if offset else 0))+']:1d} (MSP) {temps['+str(i+8+(0 if offset else 0))+']:{formats['+str(i+8+(0 if offset else 0))+']:}}\tB{boards['+str(i+12+(2 if offset else 0))+']:1d} (MSP) {temps['+str(i+12+(2 if offset else 0))+']:{formats['+str(i+12+(2 if offset else 0))+']:}}\n'
        self.cutdown_label_index = len(self.components)
        self.add_comp(tk.Label(self,
                               text=self.detect_cutdowns(),
                               font=('Arial',12),
                               anchor='w',
                               fg=self.master.colors['pale yellow'],
                               bg='black'
                              ),
                      0.5*w+10,280,0.5*self.w-30,self.h-300)

        self.link_partials = []
        self.update_data()
        
        
    def detect_cutdowns(self):
        '''
        Detects whether or not individual boards have attempted to cut down by measuring the difference in maximum and average temperatures
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        str: A prewritten string filled in with all cutdown detection information using string formatting
        '''
        
        if self.data is None:
            formats = ['6s']*(2*self.n_brds)
            boards = [i+1 for i in list(range(self.n_brds))+list(range(self.n_brds))]
            temps = ['-']*(2*self.n_brds)
        else:
            boards = []
            formats = []
            temps = []
            for header in [self.names_['xbee'],self.names_['msp']]:
                for board in set(self.data['brd']):
                    boards.append(int(board))
                    if self.data[self.data['brd']==board][header][-self.window:].max() > self.data[self.data['brd']==board][self.names_['float']][-self.window:].max()+3:
                        formats.append('6.1f')
                        temps.append(self.data[self.data['brd']==board][header][-self.window:].max())
                    else:
                        formats.append('6s')
                        temps.append('-')
        
        boards+=[1]*10
        formats+=['6s']*10
        temps+=['']*10
        
        #print('{}:{}\n{}:{}\n{}:{}'.format('temps',len(temps),'formats',len(formats),'boards',len(boards)))
        
        return self.cutdown_label_text.format(formats=formats,boards=boards,temps=temps)
        
        
    def gen_plt(self):
        '''
        Generates the plots showing the tail of all the data points for each sensor; plots divided into sensor locations on boards
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
    
        self.fig,axs = plt.subplots(ncols=2,nrows=2)
        
        for board in set(self.data['brd']):
            axs[1][1].plot([0],[0],label='B{}'.format(int(board)))
        axs[1][1].axis('off')
        axs[1][1].legend(loc='center')
        
        for i,header in enumerate(['t1','t2','t3']):
            ax_1,ax_2 = [int(char) for char in bin(i)[2:].zfill(2)]
            
            window = self.window if self.window < len(self.data) else len(self.data)
            start = len(self.data[header])-len(set(self.data['brd']))*self.window
            stop  = len(self.data[header])
            if 'time' in self.data.keys():
                first_index = list(set(self.data['brd']))[0]
                start,stop = list(self.data[self.data['brd']==first_index]['time'][-window:])[0],list(self.data[self.data['brd']==first_index]['time'][-window:])[-1]
            axs[ax_1][ax_2].plot([start,stop],[0,0],'k')
            titles = {self.names_['xbee']:'XBee Cutdown',self.names_['float']:'Floating',self.names_['msp']:'MSP430 Cutdown'}
            axs[ax_1][ax_2].set_title(titles[header])
            if 'time' in self.data.keys():
                axs[ax_1][ax_2].set_xlabel('Time Since Startup (ms)')
            else:
                axs[ax_1][ax_2].set_xlabel('Position')
            axs[ax_1][ax_2].set_ylabel('Temp (C)')
            
            for board in set(self.data['brd']):
                if 'time' in self.data.keys():
                    axs[ax_1][ax_2].plot(self.data[self.data['brd']==board]['time'][-self.window:],self.data[self.data['brd']==board][header][-self.window:])
                else:
                    axs[ax_1][ax_2].plot(self.data[self.data['brd']==board][header][-self.window:])
        self.fig.tight_layout()
        
        
    def update_data(self):
        '''
        Gets newest data from HASP websited, if available
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
    
        #print('Updating HASP...')
        self.today = strftime('%m-%d-%y')
        req = requests.get(self.list_url)
        webpage = req.text

        regex_str = '<a href=Payload_[0-9]{2}\/sp[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}.raw>sp[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}.raw</a>'
        hrefs = re.findall(regex_str,webpage)
        link_partials = [href.split('href=')[-1].split('>sp')[0] for href in hrefs]

        dates = [link.split('/')[-1].replace('.raw','')[5:13] for link in link_partials]
        #if self.today not in dates:
        dummy = list(set(dates))
        dummy.sort()
        self.today = dummy[-1]
        link_partials = [link_partials[i] for i in range(len(link_partials)) if dates[i]==self.today]
        
        if len(link_partials)!=len(self.link_partials):
            self.link_partials += link_partials[len(self.link_partials):]
            self.link_partials.sort()
            self.master.log('New HASP data received.','DEBUG')
        else:
            self.after(3000,self.update_data)
            return
        
        raw = {}
        self.url_partial = 'https://laspace.lsu.edu/hasp/groups/2021/data/'
        def thread_func(url,id_num,raw):
            #print('Thread {} starting...'.format(id_num))
            raw[str(id_num)]=requests.get(url).text
            #print('Thread {} finishing'.format(id_num))
    
            return;

        N = 15
        for i in range(0,int(np.ceil(len(self.link_partials)/N)*N),N):
            #print('Block {}'.format(int(i/N)+1))
            threads = []
            for j in range(N):
                if i+j<len(self.link_partials):
                    #print('{}\t'.format(i+j)+self.link_partials[i+j])
                    threads.append(threading.Thread(target=thread_func,args=(self.url_partial+self.link_partials[i+j],i+j,raw,)))
                    threads[-1].start()
            for t in threads:
                t.join()
           
        self.raw = ''.join([raw[key] for key in [str(i) for i in range(len(raw.keys()))]])
        self.raw = self.raw.split('Loading /flash/main.mpy...\r\nRunning bytecode...\r\n')[-1]
        lines = self.raw.split('\r\n')
        my_list = [[num for num in line.split(',')] for line in lines if len(line)>=19]
        my_list = [[float(num) if self.is_float(num) else 0 for num in line] for line in my_list if len(line)==len(my_list[0])]
        
        if len(my_list)==0:
            self.link_partials = []
            return;
        
        columns = None
        if len(my_list[0])==5:
            columns = ['time','brd','t1','t2','t3']
        else:
            columns = ['brd','t1','t2','t3']
        #self.data = pd.DataFrame(data=my_list,columns=columns)
        #=============For Purposes of Presentation#=============
        self.data = pd.DataFrame(data=my_list[:50000-4*500+250],columns=columns)
        
        self.data = self.data[self.data['brd']>0].reindex()
        if 'time' in self.data.keys():
            self.data = self.data[self.data['time']>0].reindex()
        
        for board in set(self.data['brd']):
            for t in ['t1','t2','t3']:
                if self.data[self.data['brd']==board][t][-self.window:].max() > self.data[t][-self.window:].mean()+20:
                    # TODO - remove any output that is too large
                    pass
                    
        
        self.gen_plt()
        self.gen_img()
        self.update_labels()
        
        self.after(3000,self.update_data)
        
        
    def is_float(self,num):
        '''
        Determines if the number is capable of being cast as a float type variable
        
        Parameters:
        self (Widget): Required for object functions
        num     (var): A variable
        
        Returns:
        bool: whether or not the variable can be cast as floating point number
        '''
        
        try:
            float(num)
            return True
        except:
            return False
        
        
    def _update_data(self):
        '''
        Wrapper for update_data
        '''
        
        #thread = threading.Thread(target=self.update_data)
        #thread.start()
        #self.after(3000,self._update_data)
        self.update_data()
        
        
    def update_labels(self):
        '''
        Updates all temperature and cutdown triggered labels
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
    
        for i,board in enumerate(set(self.data['brd'])):
            self.components[self.temp_avg_block_index_start+i][0].configure(text=self.temp_avg_str.format(int(board),self.data[self.data['brd']==board][self.names_['float']][-self.window:].mean()))
            
        for i,board in enumerate(set(self.data['brd'])):
            self.components[self.temp_max_block_index_start+i][0].configure(text=self.temp_max_str.format(int(board),self.data[self.data['brd']==board][self.names_['float']][-self.window:].max()))
            
        self.components[self.cutdown_label_index][0].configure(text=self.detect_cutdowns())
        
        
    def gen_img(self):
        '''
        Generates an image from the plot generated and updates the image label on the screen
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
    
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
        
        
    def autocrop_image(self,image,border=0):
        '''
        Crop image automatically to its content
        
        Parameters:
        self (Widget): Required for object functions
        image (Image): The image to be cropped
        border  (int): The extra border to include with the cropped image
        
        Returns:
        Image: The cropped image
        '''
    
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
        
        
    def redraw(self,w,h):
        '''
        The redraw function to update graphical elements in game loop
        '''
    
        self.img_w,self.img_h = int(self.img_oW/self.m_W*w), int(self.img_oH/self.m_H*h)
        self.image = self.copy_of_image.resize((self.img_w,self.img_h))
        self.photo = ImageTk.PhotoImage(self.image)
        self.label.config(image = self.photo)
        self.label.image = self.photo #avoid garbage collection

