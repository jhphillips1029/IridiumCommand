# TKinter imports
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

# General imports
import Emailer
import json

# Known commands
COMMANDS = [
    '000',
    '001',
    '010',
    '011',
    '100',
    '101',
    '110',
    '111'
]
    
def send_iridium_cmd(cmd,imei):
    if cmd not in COMMANDS:
        raise ValueError('Command must be one of the ones defined')
        
    srvc       = Emailer.gmail_authenticate()
    to         = 'data@sbd.iridium.com'
    #to         = 'iridium.msgc@gmail.com'
    subject    = imei
    msg        = ''
    attachment = 'attachments/{}.sbd'.format(cmd)
    
    confirmation = ''
    print("Chosen command: {}".format(cmd))
    print("Chosen IMEI:    {}".format(imei))
    
    return Emailer.send_message(srvc,to,subject,msg,attachments=[attachment])
    
# get the Gmail API service
service = Emailer.gmail_authenticate()

HEIGHT,WIDTH = 600,1000
colors = {
    'grey':'#848484',
    'yellow':'#ffce63',
    'pale yellow':'#f6ef95',
    'purple':'#9c639c',
    'pink':'#ce9cce',
    'orange':'#ff9c00',
    'red':'#ce6363'
}
file = profile = None

root = tk.Tk()
root.title('LCARS')
root.resizable(width=False, height=False)
root.geometry('{}x{}'.format(WIDTH,HEIGHT))

def close_shortcut(event):
    # print('You are attempting to close me!')
    root.destroy()
root.bind('<Control-Key-q>',close_shortcut)

canvas = tk.Canvas(root,width=WIDTH,height=HEIGHT,borderwidth=0,highlightthickness=0,bg='black')
canvas.place(x=0,y=0)

# Define methods for custom shapes
def _create_circle(self,x,y,r,**kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

def _create_circle_arc(self,x,y,r,**kwargs):
    if "start" in kwargs and "end" in kwargs:
        kwargs["extent"] = kwargs["end"] - kwargs["start"]
        del kwargs["end"]
    return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle_arc = _create_circle_arc

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
tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle

# Master Bar
canvas.create_rounded_rectangle(250,50,WIDTH-50,HEIGHT-50,100,fill=colors['grey'],outline='')
canvas.create_rounded_rectangle(10,80,WIDTH-150,HEIGHT-80,30,fill='black',outline='')
canvas.create_rounded_rectangle(50,50,150,80,30,fill=colors['grey'],outline='')
canvas.create_rounded_rectangle(50,HEIGHT-80,150,HEIGHT-50,30,fill=colors['grey'],outline='')
canvas.create_rectangle(100,0,375,HEIGHT,fill='black',outline='')

canvas.create_rectangle(0,100,WIDTH,HEIGHT-100,fill='black',outline='')
canvas.create_rectangle(WIDTH-150,105,WIDTH-50,HEIGHT-305,fill=colors['pink'],outline='')
canvas.create_rectangle(WIDTH-150,HEIGHT-300,WIDTH-50,HEIGHT-255,fill=colors['yellow'],outline='')
canvas.create_rectangle(WIDTH-150,HEIGHT-250,WIDTH-50,HEIGHT-105,fill=colors['yellow'],outline='')

master_label1 = tk.Label(text='Iridium Command',font=('Arial',14,'bold'),fg=colors['yellow'],bg='black')
master_label1.place(x=110,y=55)

def profile_select():
    global file,profile,master_profile_select,radio_buttons,imei_label
    
    file = filedialog.askopenfilename(initialdir='profiles/')
    with open(file) as f:
        profile = json.load(f)
        
    master_profile_select.config(text=profile['name'])
    for button,label in zip(radio_buttons,profile['commands'].keys()):
        button.config(text=label)
        
    imei_label.config(text='IMEI: {}'.format(profile['imei']))

master_profile_select = tk.Button(root,
                                  text='Tap To Select Profile',
                                  font=('Arial',14),
                                  fg=colors['yellow'],
                                  bg='black',
                                  activebackground='black',
                                  activeforeground=colors['yellow'],
                                  highlightthickness=0,
                                  bd=0,
                                  relief='flat',
                                  width=len('Tap to select profile'),
                                  command=profile_select)
master_profile_select.place(x=100,y=HEIGHT-80)

# Sub Bar
canvas.create_rectangle(50,110,200,HEIGHT-110,fill=colors['purple'],outline='')
canvas.create_rounded_rectangle(150,110,WIDTH-180,HEIGHT-110,80,fill=colors['purple'],outline='')
canvas.create_rectangle(0,130,WIDTH-300,HEIGHT-130,fill='black',outline='')
canvas.create_rounded_rectangle(100,120,WIDTH-225,HEIGHT-120,30,fill='black',outline='')

canvas.create_rectangle(WIDTH-225,150,WIDTH-180,HEIGHT-150,fill='black',outline='')
canvas.create_rectangle(WIDTH-225,155,WIDTH-180,HEIGHT-155,fill=colors['pink'],outline='')

# Buttons
def _send_command():
    if profile is not None:
        cmd_num = list(profile['commands'])[v.get()]
        cmd_nam = profile['commands'][list(profile['commands'])[v.get()]]
        msg_con = 'Please confirm the following:\n\nCommand: {} ({})\nIMEI:  {}'.format(cmd_num,cmd_nam,profile['imei'])
        if messagebox.askyesno('Confirm Command',msg_con):
            print("I would normally try to send an email.")
            print("send_iridium_cmd({},{})".format(cmd_nam,profile['imei']))
            print(send_iridium_cmd(cmd_nam,profile['imei']))
        
def _new_profile():
    newWindow = tk.Toplevel(root)
    newWindow.title('New Profile')
    newWindow.geometry('300x300')
    
    new_canvas = tk.Canvas(newWindow,width=300,height=300,borderwidth=0,highlightthickness=0,bg='black')
    new_canvas.place(x=0,y=0)
    
    new_name_label = tk.Label(newWindow,text='Name:',fg=colors['yellow'],bg='black')
    new_name_label.place(x=10,y=10)
    new_name_input = tk.Entry(newWindow,fg=colors['yellow'],bg='black')
    new_name_input.place(x=50,y=10)
    
    new_imei_label = tk.Label(newWindow,text='IMEI:',fg=colors['yellow'],bg='black')
    new_imei_label.place(x=10,y=30)
    new_imei_input = tk.Entry(newWindow,fg=colors['yellow'],bg='black')
    new_imei_input.place(x=50,y=30)
    
    new_commands_label = tk.Label(newWindow,text='Commands:',fg=colors['yellow'],bg='black')
    new_commands_label.place(x=10,y=50)
    command_entries = []
    for i in range(8):
        new_cmd_input = tk.Entry(newWindow,fg=colors['yellow'],bg='black')
        new_cmd_input.place(x=20,y=70+i*20)
        command_entries.append(new_cmd_input)
        new_cmd_label = tk.Label(newWindow,text=bin(i)[2:].zfill(3),fg=colors['yellow'],bg='black')
        new_cmd_label.place(x=200,y=70+i*20)
        
    def _save():
        new_profile = {}
        
        new_profile['name'] = new_name_input.get()
        new_profile['imei'] = new_imei_input.get()
        
        commands = [bin(i)[2:].zfill(3) for i in range(8)]
        aliases = [cmd.get() for cmd in command_entries]
        cmd_alias = {alias:cmd for alias,cmd in zip(aliases,commands)}
        new_profile['commands'] = cmd_alias
        
        filename = new_profile['name']
        path = filedialog.askdirectory(initialdir='profiles/')
        with open(path+'/'+filename+'.json','w') as f:
            #print(path+'/'+filename+'.json\n',new_profile)
            json.dump(new_profile,f)
        newWindow.destroy()
            
    def _cancel():
        newWindow.destroy()
        
    save_btn = tk.Button(newWindow,text='Save',command=_save,fg=colors['yellow'],bg='black')
    save_btn.place(x=10,y=250)
    cancel_btn = tk.Button(newWindow,text='Cancel',command=_cancel,fg=colors['yellow'],bg='black')
    cancel_btn.place(x=200,y=250)
    
def _edit_profile():
    if profile is None:
        return
    
    newWindow = tk.Toplevel(root)
    newWindow.title('New Profile')
    newWindow.geometry('300x300')
    
    new_canvas = tk.Canvas(newWindow,width=300,height=300,borderwidth=0,highlightthickness=0,bg='black')
    new_canvas.place(x=0,y=0)
    
    _name_label = tk.Label(newWindow,text='Name:',fg=colors['yellow'],bg='black')
    _name_label.place(x=10,y=10)
    _name_input = tk.Entry(newWindow,fg=colors['yellow'],bg='black')
    _name_input.insert(0,profile['name'])
    _name_input.place(x=50,y=10)
    
    _imei_label = tk.Label(newWindow,text='IMEI:',fg=colors['yellow'],bg='black')
    _imei_label.place(x=10,y=30)
    _imei_input = tk.Entry(newWindow,fg=colors['yellow'],bg='black')
    _imei_input.insert(0,profile['imei'])
    _imei_input.place(x=50,y=30)
    
    commands_label = tk.Label(newWindow,text='Commands:',fg=colors['yellow'],bg='black')
    commands_label.place(x=10,y=50)
    command_entries = []
    for i in range(8):
        cmd_input = tk.Entry(newWindow,fg=colors['yellow'],bg='black')
        cmd_input.place(x=20,y=70+i*20)
        cmd_input.insert(0,list(profile['commands'].keys())[i])
        command_entries.append(cmd_input)
        cmd_label = tk.Label(newWindow,text=bin(i)[2:].zfill(3),fg=colors['yellow'],bg='black')
        cmd_label.place(x=200,y=70+i*20)
        
    def _save():
        profile['name'] = _name_input.get()
        profile['imei'] = _imei_input.get()
        
        commands = [bin(i)[2:].zfill(3) for i in range(8)]
        aliases = [cmd.get() for cmd in command_entries]
        cmd_alias = {alias:cmd for alias,cmd in zip(aliases,commands)}
        profile['commands'] = cmd_alias
        
        filename = profile['name']
        path = filedialog.askdirectory(initialdir='profiles/')
        with open(path+'/'+filename+'.json','w') as f:
            #print(path+'/'+filename+'.json\n',new_profile)
            json.dump(profile,f)
        newWindow.destroy()
            
    def _cancel():
        newWindow.destroy()
        
    save_btn = tk.Button(newWindow,text='Save',command=_save,fg=colors['yellow'],bg='black')
    save_btn.place(x=10,y=250)
    cancel_btn = tk.Button(newWindow,text='Cancel',command=_cancel,fg=colors['yellow'],bg='black')
    cancel_btn.place(x=200,y=250)

new_profile    = tk.Button(root,
                           text='New Profile',
                           font=('Arial',12,'bold'),
                           anchor='se',
                           command=_new_profile,
                           height=3,
                           width=15,
                           highlightthickness=0,
                           bd=0,
                           relief='flat',
                           bg=colors['pale yellow'],
                           activebackground=colors['pale yellow'])
x,y = 50,150
off = 10
new_profile.place(x=x+off,y=y+off)
new_profile.update()
w,h = new_profile.winfo_width(),new_profile.winfo_height()
canvas.create_rounded_rectangle(x,y,x+w+2*off,y+h+2*off,30,fill=colors['pale yellow'],outline='')

edit_profile   = tk.Button(root,
                           text='Edit Profile',
                           font=('Arial',12,'bold'),
                           anchor='se',
                           command = _edit_profile,
                           height=3,
                           width=15,
                           highlightthickness=0,
                           bd=0,
                           relief='flat',
                           bg=colors['orange'],
                           activebackground=colors['orange'])
x,y = 50,250
off = 10
edit_profile.place(x=x+off,y=y+off)
edit_profile.update()
w,h = edit_profile.winfo_width(),edit_profile.winfo_height()
canvas.create_rounded_rectangle(x,y,x+w+2*off,y+h+2*off,30,fill=colors['orange'],outline='')

send_command   = tk.Button(root,
                           text='Send Command',
                           font=('Arial',12,'bold'),
                           anchor='se',
                           command=_send_command,
                           height=3,
                           width=15,
                           highlightthickness=0,
                           bd=0,
                           relief='flat',
                           bg=colors['red'],
                           activebackground=colors['red'])
x,y = 50,350
off = 10
send_command.place(x=x+off,y=y+off)
send_command.update()
w,h = send_command.winfo_width(),send_command.winfo_height()
canvas.create_rounded_rectangle(x,y,x+w+2*off,y+h+2*off,30,fill=colors['red'],outline='')

# Radio Buttons
v = tk.IntVar()
radio_buttons = []
for i in range(8):
    test = tk.Radiobutton(root,
                          text=bin(i)[2:].zfill(3),
                          font=('Arial',12,'bold'),
                          fg=colors['orange'],
                          activeforeground=colors['orange'],
                          bg='black',
                          activebackground ='black',
                          selectcolor='black',
                          highlightthickness=0,
                          bd=0,
                          variable=v,
                          value=i)
    test.place(x=300,y=150+25*i)
    radio_buttons.append(test)

# Data Labels
prev_cmd_label = tk.Label(text='Prev Cmd: ',fg=colors['yellow'],bg='black',font=('Arial',12,'bold'))
prev_cmd_label.place(x=WIDTH-550,y=150)

imei_label = tk.Label(text='IMEI: ',fg=colors['yellow'],bg='black',font=('Arial',12,'bold'))
imei_label.place(x=WIDTH-550,y=175)

root.mainloop()
