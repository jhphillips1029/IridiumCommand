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

This is the main program file. Enjoy.
"""

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import filedialog
    from tkinter import messagebox
except ImportError:
    import Tkinter as tk
    import Tkinter.ttk as ttk
    from Tkinter import filedialog
    from Tkinter import messagebox
from functools import partial
from time import strftime
import glob
import os
import os.path
from PIL import Image, ImageTk, ImageGrab
import traceback
import threading
import sys
import serial

# Setup a color theme    
colors = {
           'grey':'#848484',
         'yellow':'#ffce63',
    'pale yellow':'#f6ef95',
         'purple':'#9c639c',
           'pink':'#ce9cce',
         'orange':'#ff9c00',
            'red':'#ce6363',
      'pale blue':'#99ccff'
}
MASTER_COLORS = colors.copy()
# Variables for use
HEIGHT,WIDTH = 800,1200
height,width = HEIGHT,WIDTH
buttons = []
btn_coords = {}
labels = {}
active_frame = 0
time_str = 'Before'
frames = []
alert_ring_show = False


# For creating the rounded rectangles that are so iconic to this theme
def _create_rounded_rectangle(self,x1,y1,x2,y2,radius,**kwargs):

    """
    For creating the rounded rectangle that are so iconic to this theme
    
    Parameters:
    self     (tk Canvas): Required for object functions
    x1             (int): The x-coordinate of the first corner of the rectangle
    y1             (int): The y-coordinate of the first corner of the rectangle
    x2             (int): The x-coordinate of the second corner of the rectangle, opposite the first corner
    y2             (int): The y-coordinate of the second corner of the rectangle, opposite the first corner
    radius         (int): The radius of the corners of the rounded rectangle
    **kwargs       (var): Additional parameters passed to the function create_polygon
    
    Returns:
    UnT: The rounded rectangle
    """
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
tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle


def set_frame(num):
    """
    Show the active widget and hide all others
    
    Parameters:
    num (int): The index for which widget is active
    
    Returns:
    None
    """

    global active_frame
    
    active_frame = num
        
    draw_layout(width,height)
        
    [frames[i].hide() if i!=active_frame else frames[i].show(width,height) for i in range(len(frames))]
    

def draw_layout(w,h):
    """
    Draws the various graphical garnishings for the theme.
    
    Parameters:
    w (int): The width of the window
    h (int): The height of the window
    
    Returns:
    None
    """

    global buttons,colors,MASTER_COLORS
    canvas.delete("all")
    canvas.config(width=w,height=h)
    
    if socket_frame.alerting:
        for key in colors.keys():
            colors[key] = socket_frame.alert_color
        socket_frame.colors = colors
    else:
        colors = MASTER_COLORS.copy()
        socket_frame.colors = colors
    
    # Upper Divider
    canvas.create_rounded_rectangle(          0,  0,w,250/HEIGHT*h,100,fill=colors['pink'],outline='')
    canvas.create_rounded_rectangle(100/WIDTH*w,  0,w,220/HEIGHT*h, 30,         fill='black',outline='')
    canvas.create_rectangle(          0,           0,          w,180/HEIGHT*h,         fill='black',outline='')
    canvas.create_rectangle(          0,           0,100/WIDTH*w,175/HEIGHT*h,fill=colors['yellow'],outline='')
    canvas.create_rectangle(180/WIDTH*w,           0,          w,250/HEIGHT*h,         fill='black',outline='')
    canvas.create_rectangle(185/WIDTH*w,220/HEIGHT*h,340/WIDTH*w,250/HEIGHT*h,fill=colors['purple'],outline='')
    canvas.create_rectangle(345/WIDTH*w,220/HEIGHT*h,650/WIDTH*w,250/HEIGHT*h,fill=colors['purple'],outline='')
    canvas.create_rectangle(655/WIDTH*w,220/HEIGHT*h,          w,250/HEIGHT*h,fill=colors['purple'],outline='')

    # Lower Divider
    canvas.create_rounded_rectangle(          0,255/HEIGHT*h,w,h,100,fill=colors['pale yellow'],outline='')
    canvas.create_rounded_rectangle(100/WIDTH*w,285/HEIGHT*h,w,h, 30,         fill='black',outline='')
    canvas.create_rectangle(180/WIDTH*w,255/HEIGHT*h,          w,              h,         fill='black',outline='')
    canvas.create_rectangle(          0,325/HEIGHT*h,          w,              h,         fill='black',outline='')
    canvas.create_rectangle(185/WIDTH*w,255/HEIGHT*h,340/WIDTH*w,285/HEIGHT*h,fill=colors['purple'],outline='')
    canvas.create_rectangle(345/WIDTH*w,255/HEIGHT*h,650/WIDTH*w,285/HEIGHT*h,fill=colors['purple'],outline='')
    canvas.create_rectangle(655/WIDTH*w,255/HEIGHT*h,          w,285/HEIGHT*h,fill=colors['purple'],outline='')
    
    # Widget Selector Bar
    for i in range(num_frames):
        passive = 'black' if socket_frame.alerting else colors['grey']
        ind_color = passive if i!= active_frame else colors['red']
        canvas.create_rounded_rectangle(0,(330+45*i)/HEIGHT*height,135/WIDTH*width,(370+45*i)/HEIGHT*height,(45)/HEIGHT*height,fill=ind_color,outline='')
        canvas.create_rectangle(0,(330+45*i)/HEIGHT*height,105/WIDTH*width,(370+45*i)/HEIGHT*height,fill='black',outline='')
    canvas.create_rectangle(0,(330+45*num_frames)/HEIGHT*h,100/WIDTH*w,h,fill=colors['grey'],outline='')
    
    # Labels
    for i,label in enumerate(labels.keys()):
        label_color = colors[label_colors[i]]
        label.configure(font=('Verdana',int(labels[label][2]/HEIGHT*h),'bold'),
                        fg=label_color)
        label.place(x=labels[label][0]/WIDTH*w,y=labels[label][1]/HEIGHT*h)
    
    # Buttons
    for i,btn in enumerate(buttons):
        btn_color = colors[btn_colors[i%len(btn_colors)]]
        btn.configure(font=('Verdana',int(9/HEIGHT*h),'bold'),
                      bg=btn_color,
                      activebackground=btn_color)
        btn.place(x=btn_coords[btn][0]/WIDTH*w,
                  y=btn_coords[btn][1]/HEIGHT*h,
                  height=int(btn_coords[btn][2]/HEIGHT*height),
                  width=int(btn_coords[btn][3]/WIDTH*width)
                 )

    # Log window        
    log_window.configure(font=('Courier New',int(log_window_nums[-1]/HEIGHT*h)))
    log_window.place(x=log_window_nums[0]/WIDTH*w,
                     y=log_window_nums[1]/HEIGHT*h,
                     width=log_window_nums[2]/WIDTH*width,
                     height=log_window_nums[3]/HEIGHT*height)
        
        
def time():
    """
    Gets the current system time and updates the graphical display of the time
    
    Parameters:
    None
    
    Returns:
    None
    """

    global time_str
    time_str = strftime('%Y-%m-%d %H:%M:%S')
    time_label.config(text=time_str)
    time_label.after(1000, time)
    socket_frame.time_str = time_str


def close_shortcut(event):
    """
    Updates all frames of intent to close and closes application
    
    Parameters:
    event (???): I don't know what this is but it's necessary
    
    Returns:
    None
    """
    
    for frame in frames:
        frame._close()
        
    socket_frame.log_file.close()
        
    root.destroy()
    
    
def alert_ring():
    """
    Updates the colored ring around the widget socket for alerts
    
    Parameters:
    None
    
    Returns:
    None
    """

    global alert_ring_show
    draw_layout(width,height)
    if alert_ring_show and socket_frame.alerting:
        canvas.create_rounded_rectangle(165/WIDTH*width,
                                        310/HEIGHT*height,
                                        (WIDTH-10)/WIDTH*width,
                                        (HEIGHT-10)/HEIGHT*height,
                                        100/HEIGHT*height,
                                        fill=socket_frame.alert_color)
        canvas.create_rounded_rectangle(175/WIDTH*width,
                                        320/HEIGHT*height,
                                        (WIDTH-20)/WIDTH*width,
                                        (HEIGHT-20)/HEIGHT*height,
                                        50/HEIGHT*height,
                                        fill='black')
                         
    alert_ring_show = not(alert_ring_show)               
    if socket_frame.alerting:
        socket_frame.after(500,alert_ring)


# Wrapper for other methods of closing the window
def _close_shortcut():
    """
    Wrapper method for close_shortcut
    
    Parameters:
    None
    
    Returns:
    None
    """

    close_shortcut(None)
    
    
def resize(event):
    """
    Handles main window resize events and resizes all loaded widgets
    
    Parameters:
    event (???): Still don't know what this is
    
    Returns:
    None
    """

    global width,height
    if event=='dummy_resize' or str(event.widget)=='.':
        if event=='dummy_resize' or ((width != event.width) and (height != event.height)):
            if event!='dummy_resize':
                width,height = event.width,event.height
            
            draw_layout(width,height)
            
            socket_frame.place(x=socket_frame_coords[0]/WIDTH*width,
                               y=socket_frame_coords[1]/HEIGHT*height,
                               width=socket_frame_coords[2]/WIDTH*width,
                               height=socket_frame_coords[3]/HEIGHT*height)
            socket_frame.width,socket_frame.height = width,height
            
            for frame in frames:
                try:
                    frame.resize(width,height)
                except:
                    socket_frame.log('{} failed to resize.'.format(str(frame).split('.!')[-1].capitalize()),'ERROR')
            set_frame(active_frame)
            
            image = img_copy.resize((int(logo_w/WIDTH*width),int(logo_h/HEIGHT*height)))
            tk_image = ImageTk.PhotoImage(img_copy)
            logo_label.configure(image=tk_image)
            logo_label.image=tk_image
            logo_label.place(x=(WIDTH-logo_w-30)/WIDTH*width,y=50/HEIGHT*height)
            
            
# The frame used as a socket for all the widgets
class WidgetSocket(tk.Frame):
    """
    The socket for all individual sockets to slot into. Handles various updates
    """

    def __init__(self,master,x,y,w,h):
        """
        The socket initialization function
        
        Parameters:
        self     (Widget): Required for object functions
        master (tk.Frame): The Tkinter frame the socket has been inserted into
        x           (int): The x-coordinate of the top-left corner
        y           (int): The y-coordinate of the top-left corner
        w           (int): The width of the socket
        h           (int): The height of the socket
        
        Returns:
        None
        """
    
        super().__init__(master,width=w,height=h)
        self.place(x=x,y=y)
        
        self.init_log()
        
        self.colors = MASTER_COLORS.copy()
        self.time_str = time_str
        self.width,self.height = WIDTH,HEIGHT
        
        self.alert_colors = ['green',
                             'blue',
                             'yellow',
                             'red',
                            ]
        
        self.profile = None
        self.frames = []
        self.alert_level = 0
        self.alerting = False
        
        
    def init_log(self):
        """
        Initializes the log file and deletes old ones if over limit
        
        Parameters:
        self (???): Required for object functions
        
        Returns:
        None
        """
    
        files = glob.glob('logs/*.log')
        for file in files:
            with open(file,'r') as f:
                if f.readlines() == []:
                    os.remove(file)
        files = glob.glob('logs/*.log')
                    
        files.sort()
        num_files = len(files)
        num_files_allowed = 20
        
        if os.path.isfile('logs/prefs.txt'):
            with open('logs/prefs.txt','r') as f:
                line = f.readline().strip()
                if line.isnumeric():
                    num_files_allowed = int(line)
        num_files_allowed-=1
            
        if num_files>num_files_allowed:
            for file in files[:num_files-num_files_allowed]:
                os.remove(file)
            
        self.log_file = open('logs/{}.log'.format(strftime('%Y%m%d%H%M%S')),'w')
        self.log_lines = []
        
        
    def log(self,msg,lvl='INFO'):
        """
        Logs a message to both the log file and the log window
        
        Parameters:
        self (???): Required for object functions
        msg  (str): The message to be logged.
        lvl  (str): The level delimiter for the logged message; default is 'INFO'
        
        Returns:
        None
        """
    
        self.log_file.write('{}:{}$ {}\r\n'.format(strftime('%Y-%m-%d %H:%M:%S'),lvl,msg))
        self.log_lines.append('{}:{}$ {}\r\n'.format(strftime('%H:%M:%S'),lvl,msg))
        self.log_file.flush()
        
        
    def set_profile(self,profile):
        """
        Sets the command profile for the main application and updates all loaded widgets with profile
        
        Parameters:
        self     (???): Required for object functions
        profile (dict): Dictionary loaded from command profile JSON file
        
        Returns:
        None
        """
    
        self.log('profile \'{}\' set'.format(profile['name']))
        self.profile = profile
        for frame in self.frames:
            try:
                frame._set_profile(profile)
                threading.Thread(target=frame._set_profile,args=(profile,)).start()
                #frame._set_profile(profile)
            except:
                self.log('Profile not set for {}'.format(str(frame).split('.!')[-1].capitalize()),'ERROR')
            
            
    def set_alert(self,level):
        """
        Sets the alert level for the main application
        
        Parameters:
        self  (???): Required for object functions
        level (int): The alert level to be set; lower level is higher alert
        
        Returns:
        None
        """
        
        level+=1
        self.alert_level = level
        self.alerting = self.alert_level>0
        if self.alerting:
            self.log('{} Alert activated.'.format(self.alert_colors[level-1].capitalize()))
        else:
            self.log('Alert cancelled.')
        alert_ring_show = True
        self.alert_color = self.alert_colors[self.alert_level-1]
        resize('dummy_resize')
        alert_ring()
        
        for frame in self.frames:
            try:
                frame._set_alert(level-1)
            except: pass
            
    def list_serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
        
        
class Splash(tk.Toplevel):
    """
    The splash screen for loading.
    """
    
    def __init__(self,parent):
        """
        The initialization function
        
        Parameters:
        self   (???): Required for object functions
        parent (???): The main application window
        
        Returns:
        None
        """

        tk.Toplevel.__init__(self,parent,bg='black')
        self.title('ICC')
        self.geometry('{}x{}'.format(200,150))
        self.dots = 3
    
        image = Image.open('images/logo.png')
        img_copy= image.copy()
        image = img_copy.resize((int(image.width*125/image.height),125))
        tk_image = ImageTk.PhotoImage(image)
        logo_label = tk.Label(self,image=tk_image,bg='black')
        logo_label.image = tk_image
        logo_w,logo_h = image.width,image.height
        logo_label.pack()
        
        self.label = tk.Label(self,
                              text='Loading...',
                              font=('Verdana',18),
                              fg=colors['pale yellow'],
                              bg='black'
                             )
        self.label.pack()
        
        self.update()
        
        
def update_log_window():
    """
    A function to update the log window with all new log data
    
    Parameters:
    None
    
    Returns:
    None
    """

    log_window.configure(text='')
    len_longest_line = 0
    for line in socket_frame.log_lines:
        if len(line)>len_longest_line:
            len_longest_line=len(line.strip())
    
    for line in socket_frame.log_lines:
        log_window.configure(text=log_window.cget('text')+line.strip().ljust(len_longest_line)+'\n',
                             fg=colors[label_colors[2]])
    
    log_window.after(1000,update_log_window)
    
    
def my_func(event):
    """
    A secret surprise! Oh my!
    
    Parameters:
    event (???): Nope. Still don't know.
    
    Returns:
    None
    """
    
    messagebox.showinfo('Info Box','Created by God himself.')
        
if __name__=='__main__':
    # Create the main window with predefined geometry
    root = tk.Tk()
    root.withdraw()
    splash = Splash(root)
    root.geometry('{}x{}'.format(WIDTH,HEIGHT))
    root.title('Iridium Command Center')
    
    # Add key bindings
    root.bind('<Control-Key-q>',close_shortcut)
    root.protocol("WM_DELETE_WINDOW",_close_shortcut)
    root.bind("<Configure>",resize)
    root.bind('<Alt-p>',my_func)

    # Create drawing canvas
    canvas = tk.Canvas(root,width=WIDTH,height=HEIGHT,borderwidth=0,highlightthickness=0,bg='black')
    canvas.place(x=0,y=0)
    
    # Create the widget socket
    socket_frame_coords = [185,330,WIDTH-185-30,HEIGHT-330-30]
    socket_frame = WidgetSocket(root,*socket_frame_coords)
    socket_frame.log('Started widget socket frame...',lvl='DEBUG')

    # Importing and setting up widgets using an implicit import method (I know, "implicit = bad" and all, but it works well)
    modules = [f for f in glob.glob('widgets/*/') if f.split('/')[-2] not in ['__pycache__','Utility']]
    modules = [mod.replace('\\','/') for mod in modules]   # for the shit operating system known as Windows.
    modules = [f+f.split('/')[-2] for f in modules]
    try:
        # Determine if there are widgets to ignore
        with open('widgets/.ignore','r') as f:
            ignores = ['widgets/'+line.strip()+'/'+line.strip() for line in f.readlines() if line[0]!='#' and line.strip()!='']
            _modules = modules.copy()
            modules = [modules[i] for i in range(len(modules)) if modules[i]!='widgets/Widget.py' and modules[i] not in ignores]
            for mod in _modules:
                if mod in ignores:
                    socket_frame.log('Ignoring {}'.format(mod),lvl='DEBUG')
            
    except Exception as e:
        # If unable to find use widgets/.ignore, load all but abstract widget class
        modules = [modules[i] for i in range(len(modules)) if modules[i]!='widgets/Widget.py']
    num_frames = len(modules)

    # Import all modules found above
    for module in modules:
        try:
            _import = __import__(module.replace('/','.'),fromlist=['*'])
            globals()[module.split('/')[-1].replace('.py','')] = _import
            locals()[module.split('/')[-1].replace('.py','')] = _import
            socket_frame.log('Successfully loaded {}.'.format(module),lvl='DEBUG')
        except Exception as e:
            socket_frame.log('Failed to load {}.'.format(module),lvl='DEBUG')
            socket_frame.log(str(e),lvl='ERROR')
            traceback.print_exc()
    
    # Instantiate all modules imported
    succ_mod = []
    while True:
        break_me = True
        for frame in frames:
            frame.destroy()
        frames = []
        
        for _module in modules:
            try:
                module = _module.split('/')[-1].replace('.py','')
                frame = getattr(globals()[module],module)(socket_frame,0,0,WIDTH,HEIGHT,w=socket_frame_coords[2],h=socket_frame_coords[3])
                frames.append(frame)
                socket_frame.log('Successfully instantiated {}'.format(module),lvl='DEBUG')
                succ_mod.append(_module)
                break_me = break_me and True
            except Exception as e:
                socket_frame.log('Failed to instantiate {}'.format(module),lvl='ERROR')
                socket_frame.log(str(e),lvl='ERROR')
                break_me = break_me and False
                traceback.print_exc()
                
        modules = succ_mod.copy()
                
        if break_me:
            break
    
    # Reorganize the widgets so the three primary widgets are at the top and in order
    ui = list(range(len(frames)))
    ci = []
    primary_widgets = ['Overview','Tracker','Profiles']
    for k in primary_widgets:
        ci.append(modules.index('widgets/{0}/{0}'.format(k.replace(' ','_'))))
    mi = [ui[i] for i in range(len(ui)) if ui[i] not in ci]
    ci = ci+mi
    
    # Add all the widgets to the widget socket
    frames = [frames[i] for i in ci]
    socket_frame.frames = frames
    num_frames = len(frames)
    
    # Add selectors for all widgets
    btn_colors = ['yellow','pink','orange','pale blue','purple']
    for i in range(num_frames):
        btn = tk.Button(root,
                        text=modules[ci[i]].split('/')[-1].replace('.py','').replace('_',' '),
                        command=partial(set_frame,i),
                        font=('Verdana',int(9/HEIGHT*height),'bold'),
                        anchor='se',
                        highlightthickness=0,
                        bd=0,
                        relief='flat',
                        bg=colors[btn_colors[i%len(btn_colors)]],
                        activebackground=colors[btn_colors[i%len(btn_colors)]]
                       )
        buttons.append(btn)
        btn_coords[btn]=(0,330+45*i,40,100)
    
    # Add various labels
    # Title label
    label_colors = ['yellow','pale blue','pale yellow']
    title_label = tk.Label(text='Iridium Command Center',fg=colors[label_colors[0]],bg='black')
    labels[title_label] = [500,50,24]
    
    # System time label
    time_label = tk.Label(text='',fg=colors[label_colors[1]],bg='black')
    labels[time_label] = [550,100,18]
    time()
    
    # Log window
    log_window_nums = [110,10,350,200,8]
    log_window = tk.Label(root,anchor='sw',bg='black',fg=colors[label_colors[2]])
    update_log_window()
    
    # Logo
    image = Image.open('images/logo.png')
    img_copy = image.copy()
    image = img_copy.resize((int(image.width*125/image.height),125))
    tk_image = ImageTk.PhotoImage(image)
    logo_label = tk.Label(root,image=tk_image,bg='black')
    logo_label.image = tk_image
    logo_w,logo_h = image.width,image.height
    logo_label.place(x=WIDTH-logo_w-30,y=50)
    
    # Prepare main window for display
    root.update()
    [frames[i].hide() if i!=active_frame else frames[i].show(width,height) for i in range(len(frames))]
    draw_layout(WIDTH,HEIGHT)
    
    # Close splash screen
    socket_frame.log('Starting GUI...',lvl='DEBUG')
    splash.destroy()
    root.deiconify()
    
    # Start main window
    root.update()
    if root.winfo_screenwidth()<WIDTH:
        r = root.winfo_screenwidth()/WIDTH
        w,h = int(WIDTH*r),int(HEIGHT*r)
        root.geometry('{}x{}'.format(w,h))
    if root.winfo_screenheight()<HEIGHT:
        r = root.winfo_screenheight()/HEIGHT
        w,h = int(WIDTH*r),int(HEIGHT*r)
        root.geometry('{}x{}'.format(w,h))
        
    root.mainloop()
