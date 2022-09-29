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

This widget takes environmental and geophysical data to calculate the pressure differential in the helium tanks necessary to fill the balloon.
"""


try:
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import simpledialog
except ImportError:
    import Tkinter as tk
    from Tkinter import messagebox
    from Tkinter import simpledialog
import widgets.Utility.Widget as Widget
from widgets.Utility.Widget import _create_rounded_rectangle
import numpy as np
import serial
import json
    
class Filling(Widget.Widget):
    '''
    The Filling widget calculates parameters for filling the balloon and launch
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
        
        self.canvas = tk.Canvas(self,width=w,height=h,bg='black',borderwidth=0,highlightthickness=0)
        self.add_comp(self.canvas,0,0,w,h)
        
        # Thermodynamic curve fit coefficients
        c_0 =  0.99999683
        c_1 = -0.0090826951
        c_2 =  7.8736169e-5
        c_3 = -6.1117958e-7
        c_4 =  4.3884187e-9
        c_5 = -2.9883885e-11
        c_6 =  2.1874425e-13
        c_7 = -1.7892321e-15
        c_8 =  1.1112018e-17
        c_9 = -3.0994571e-20
        self.c_vals = [c_0,c_1,c_2,c_3,c_4,c_5,c_6,c_7,c_8,c_9]
        self.e_so = 6.1078
        
        # Field variables
        self.C_drags = {'latex':lambda m: 0.3572-0.04725*m,
                        'zero pressure':lambda m: 0.68
                       }
        
        self.entry_names = ['Helium Purity',
                            'Tank Volume',
                            'Balloon Type',
                            'Balloon Mass',
                            'Payload Mass',
                            'Lift Ratio',
                            'Ground Elev',
                            'Amb Pressure',
                            'Amb Temperature',
                            'Rel Humidity',
                            'Safety Factor'
                           ]
        self.entry_dflts = [97,
                            43.42,
                            'latex',
                            1600,
                            12,
                            0.29,
                            4659.4,
                            1015.1,
                            23.3333,
                            45,
                            1.155
                           ]
        self.entry_units = [['%'],
                            ['L','m3','cu','ci','gal','cc'],
                            ['-'],
                            ['g','kg','lbs','oz'],
                            ['lbs','oz','g','kg'],
                            ['-'],
                            ['m','km','ft','mi'],
                            ['mbar','kPa','mm Hg','bar','Pa','psi','in Hg'],
                            ['C','F','K','R'],
                            ['%'],
                            ['-']
                           ]
        self.entry_convs = [[lambda x: 0.01*x],
                            [lambda x: 0.001*x,
                             lambda x: x,
                             lambda x: 0.0283168*x,
                             lambda x: 1.63871e-5*x,
                             lambda x: 0.00378541*x,
                             lambda x: 1.0e-6*x],
                            [lambda x: x],
                            [lambda x: x/1000,
                             lambda x: x,
                             lambda x: 0.453592*x,
                             lambda x: 0.0283495*x],
                            [lambda x: 0.453592*x,
                             lambda x: 0.0283495*x,
                             lambda x: x/1000,
                             lambda x: x],
                            [lambda x: x],
                            [lambda x: x,
                             lambda x: 1000*x,
                             lambda x: 0.3048*x,
                             lambda x: 1609.34*x],
                            [lambda x: 100*x,
                             lambda x: 1000*x,
                             lambda x: 133.322*x,
                             lambda x: 100000*x,
                             lambda x: x,
                             lambda x: 6894.76*x,
                             lambda x: 3386.39*x],
                            [lambda x: x+273.15,
                             lambda x: (x-32)*5/9+273.15,
                             lambda x: x,
                             lambda x: 5/9*x],
                            [lambda x: 0.01*x],
                            [lambda x: x]
                           ]
                      
        X = 50
        Y = 55
        h = 20
        self.X_block,self.Y_block = X,Y
        self.entry_string_vars = []
        self.units_string_vars = []
        self.input_block_comp_index_start = len(self.components)
        for i in range(len(self.entry_names)):
            self.entry_string_vars.append(tk.StringVar(self,
                value='{}'.format(self.entry_dflts[i])))
            self.units_string_vars.append(tk.StringVar(self,
                value='{}'.format(self.entry_units[i][0])))
            self.add_comp(tk.Label(self,
                                   text=self.entry_names[i],
                                   font=('Verdana',9),
                                   bg='black',
                                   fg=self.master.colors['pale yellow']),
                          X,Y+(h+5)*i,115,h)
            self.add_comp(tk.Entry(self,
                                   font=('Verdana',9),
                                   textvariable=self.entry_string_vars[-1],
                                   bg='black',
                                   fg=self.master.colors['pale yellow']),
                          X+120,Y+(h+5)*i,100,h)
            om = tk.OptionMenu(self,
                               self.units_string_vars[-1],
                               *self.entry_units[i])
            om.configure(font=('Verdana',9),
                         bg='black',
                         fg=self.master.colors['pale yellow'],
                         activebackground='black',
                         activeforeground=self.master.colors['pale yellow'],
                         anchor='se',
                         highlightthickness=0,
                         bd=0,
                         relief='flat'
                        )
            self.add_comp(om,X+225,Y+(h+5)*i,70,h)
            
        self.add_comp(tk.Button(self,
                                text='Calculate',
                                font=('Verdana',9,'bold'),
                                command=self.calculate_fill,
                                bg=self.master.colors['red'],
                                activebackground=self.master.colors['red'],
                                anchor='se',
                                highlightthickness=0,
                                bd=0,
                                relief='flat'),
                      X+100,Y+20+(h+5)*len(self.entry_names),100,h+10)
                      
        self.output_text = ['Outputs:',
                            ' P_req: {:12.6f} MPa',
                            '        {:12.6f} psi',
                            ' v_asc: {:12.6f} m/s',
                            '        {:12.6f} mph',
                            'L_neck: {:12.6f} g',
                            '        {:12.6f} lbs',
                            ' V_bln: {:12.6f} m^3',
                            '        {:12.6f} cf',
                            ' D_bln: {:12.6f} m',
                            '        {:12.6f} ft'
                           ]
        self.output_block_index_start = len(self.components)
        self.max_line_count = max([len(line) for line in self.output_text])
        output_str = '\n'.join([line+''.join([' ']*(self.max_line_count-len(line))) for line in self.output_text]).format(*[0]*(len(self.output_text)-1))
        for i,line in enumerate(output_str.split('\n')):
            self.add_comp(tk.Label(self,
                                   text=line,
                                   font=('Verdana',9),
                                   anchor='nw',
                                   bg='black',
                                   fg=self.master.colors['pale yellow']
                                  ),
                          X+590,Y+i*(h+5),175,h)
                          
        self.add_comp(tk.Button(self,
                                text='Profile Fill',
                                font=('Verdana',9),
                                command=self.profile_fill,
                                bg=self.master.colors['orange'],
                                activebackground=self.master.colors['orange'],
                                anchor='se',
                                highlightthickness=0,
                                bd=0,
                                relief='flat'
                               ),
                      X+400,Y,100,30)
                          
        self.add_comp(tk.Button(self,
                                text='Serial Fill',
                                font=('Verdana',9),
                                command=self.serial_fill,
                                bg=self.master.colors['orange'],
                                activebackground=self.master.colors['orange'],
                                anchor='se',
                                highlightthickness=0,
                                bd=0,
                                relief='flat'
                               ),
                      X+400,Y+55,100,30)
                      
        self.redraw(m_W,m_H)
        
        
    def profile_fill(self):
        '''
        Fill in field values from values in command profile JSON
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
    
        keys = list(self.master.profile.keys())
        terms = ['Helium Purity',
                 'Tank Volume',
                 'Balloon Type',
                 'Balloon Mass',
                 'Payload Mass',
                 'Lift Ratio',
                 'Ground Elev',
                 'Safety Factor'
                ]
        for term in terms:
            if term in keys:
                i_start = self.input_block_comp_index_start
                n = self.entry_names.index(term)
                self.components[i_start+n*3+1][0].configure(textvariable=tk.StringVar(self,value=self.master.profile[term]))
                
                
    def set_profile(self):
        '''
        Automatically fills applicable fields when profile loaded
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
        self.profile_fill()
        
        
    def serial_fill(self):
        '''
        TODO: Complete ability to fill fields from serial by gathering ambient temperature, pressure, and humidity from Weather St. Rev 2 as well as pressure altitude
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
        
        #messagebox.showinfo('Serial Fill','Serial Fill is currently under development. Please enter the values manually for the time being.')
        
        ports = self.master.list_serial_ports()
        
        index = 0
        if ports:
            if len(ports)>1:
                index = simpledialog.askinteger('Title','Please choose:\n    {}'.format('\n    '.join(['{:2d}: {}'.format(i,p) for i,p in enumerate(ports)])),parent=self)
        else:
            return
            
        PORT = ports[index]
        RATE = 9600
        ser = serial.Serial()
        ser.port = PORT
        ser.baudrate = RATE
        ser.setDTR(False)
        ser.timeout = 2
        ser.open()
        
        for i in range(2):
            line = ser.readline().decode().strip()
            if line and line[0]=='{':
                me_dict = json.loads(line.replace('hPa','mbar'))
        
        '''
        self.master.log('Ambient Temp:  {:.2f} *C'.format(me_dict['T'][0]),lvl='DEBUG')
        self.master.log('Ambient Press: {:.2f} mbar'.format(me_dict['P'][0]),lvl='DEBUG')
        self.master.log('Rel Humidity:  {:.2f} %'.format(me_dict['h'][0]),lvl='DEBUG')
        self.master.log('Pressure Alt:  {:.2f} m'.format(me_dict['H'][0]),lvl='DEBUG')
        '''
        
        keys = list(me_dict.keys())
        terms = {'P':'Amb Pressure',
                 'T':'Amb Temperature',
                 'h':'Rel Humidity',
                 'H':'Ground Elev'
                }
        for term in terms:
            if term in keys:
                i_start = self.input_block_comp_index_start
                n = self.entry_names.index(terms[term])
                self.components[i_start+n*3+1][0].configure(textvariable=tk.StringVar(self,value=me_dict[term][0]))
                      
    def calculate_fill(self):
        '''
        Calculate balloon fill and launch parameters; equations and method improved from flight director's spreadsheet
        
        Parameters:
        self (Widget): Required for object functions
        
        Returns:
        None
        '''
    
        N = 3
        start = self.input_block_comp_index_start
        stops = self.input_block_comp_index_start+N*len(self.entry_names)
        fill_vars = {}
        for i in range(start,stops,N):
            i_label = i
            i_entry = i+1
            i_drpdn = i+2
            i_step  = int(i%len(N*self.entry_names)/N)
            
            unit = self.units_string_vars[i_step].get()
            func = self.entry_convs[i_step][self.entry_units[i_step].index(unit)]
            inpt = self.components[i_entry][0].get()
            
            output = None
            try:
                output = func(float(inpt))
            except:
                output = func(inpt)
            fill_vars[self.entry_names[i_step]]=output
            
        a = 6.1121
        b = 18.678
        c = 257.14
        d = 234.5
        gamma_m = lambda T,H: np.log(H/100*np.exp((b-T/d)*(T/(c+T))))
        g_m = gamma_m(fill_vars['Amb Temperature']-273.15,fill_vars['Rel Humidity']*100)
        T_dp = c*g_m/(b-g_m)
        
        f_den = fill_vars['Helium Purity'] + (1-fill_vars['Helium Purity'])*29/4.02
        C_drag = self.C_drags[fill_vars['Balloon Type']](fill_vars['Payload Mass']) if fill_vars['Balloon Type'] in self.C_drags.keys() else self.C_drags[list(self.C_drags.keys())[0]](fill_vars['Payload Mass'])
        L_gross = fill_vars['Balloon Mass'] + (1+fill_vars['Lift Ratio'])*fill_vars['Payload Mass']
        rho_He = ((1/2077)*(101.29/(288.19-0.00649*fill_vars['Ground Elev']))*((288.19-0.00649*fill_vars['Ground Elev'])/288.08)**(5.256)*1000)*f_den
        
        def _P_exp(T,i):
            if self.c_vals[i]==self.c_vals[-1]:
                return self.c_vals[i]
            return self.c_vals[i] + T*_P_exp(T,i+1)
        def P_exp(T):
            return _P_exp(T,0)
        P = P_exp(T_dp)
        Es_OVER_Pv = self.e_so/P**8*100
        
        rho_air = fill_vars['Amb Pressure']/(287.05*fill_vars['Amb Temperature'])*(1-0.378*Es_OVER_Pv/fill_vars['Amb Pressure'])
        
        Delta_P = fill_vars['Safety Factor']*(L_gross*fill_vars['Amb Pressure'])/((rho_air-rho_He)*fill_vars['Tank Volume'])
        V_bln = fill_vars['Tank Volume']*Delta_P/fill_vars['Amb Pressure']
        D_bln = (6*Delta_P*fill_vars['Tank Volume']/(np.pi*fill_vars['Amb Pressure']))**(1/3)
        L_neck = V_bln*(rho_air-rho_He)-fill_vars['Balloon Mass']
        v_asc = np.sqrt(((L_neck-fill_vars['Payload Mass'])*9.81)/((C_drag)*0.125*rho_air*np.pi*D_bln**2))
        
        '''
        print('Inputs:\n'+''.join(['=']*50))
        print('He Pur.: {:7.2f}%'.format(fill_vars['Helium Purity']*100))
        print(' V_tank: {:7.2f} L'.format(fill_vars['Tank Volume']*1000))
        print('Bln Typ: {:4d}'.format(1 if fill_vars['Balloon Type']=='latex' else 0))
        print('  m_bln: {:7.2f} g'.format(fill_vars['Balloon Mass']*1000))
        print('  m_pld: {:7.2f} lbs'.format(fill_vars['Payload Mass']/0.453592))
        print(' L_free: {:7.2f} lbs'.format(fill_vars['Lift Ratio']*fill_vars['Payload Mass']/0.453592))
        print('  P_amb: {:7.2f} mbar'.format(fill_vars['Amb Pressure']/100))
        print('   Elev: {:7.2f} ft'.format(fill_vars['Ground Elev']/0.3048))
        print('Dew pt.: {:7.2f} C'.format(T_dp))
        print('  T_amb: {:7.2f} C'.format(fill_vars['Amb Temperature']-273.15))

        print('\n\n\nOutputs:\n'+''.join(['=']*50))
        print('\u0394P_req: {:11.6f} MPa'.format(Delta_P/1.0e6))
        print('        {:11.6f} psi'.format(0.000145038*Delta_P))
        print(' v_asc: {:11.6f} m/s'.format(v_asc))
        print('L_neck: {:11.6f} kg'.format(L_neck))
        print()
        print(' V_bln: {:11.6f} m^3'.format(V_bln))
        print(' D_bln: {:11.6f} m'.format(D_bln))
        '''
        
        output_vars = [Delta_P/1.0e6,
                       0.000145038*Delta_P,
                       v_asc,
                       v_asc*2.23694,
                       L_neck*1000,
                       L_neck*2.20462,
                       V_bln,
                       V_bln*35.3147,
                       D_bln,
                       D_bln*3.28084]
        output_str = '\n'.join([line+''.join([' ']*(self.max_line_count-len(line))) for line in self.output_text]).format(*output_vars)
        for i,line in enumerate(output_str.split('\n')):
            self.components[self.output_block_index_start+i][0].configure(text=line)
        
        
    def redraw(self,w,h):
        '''
        Add all the thematic graphical embellishments
        
        Parameters:
        self (Widget): Required for object functions
        w       (int): Width of master window
        h       (int): Height of master window
        
        Returns:
        None
        '''
    
        self.canvas.delete('all')
    
        for off in [0,590]:
            self.canvas.create_rounded_rectangle((self.X_block-15+off)/self.m_W*w,
                                                 (self.Y_block-15)/self.m_H*h,
                                                 (self.X_block+310+off)/self.m_W*w,
                                                 (self.Y_block+345)/self.m_H*h,
                                                 30/self.m_H*h,
                                                 fill=self.master.colors['pale blue'],
                                                 outline='')
            self.canvas.create_rounded_rectangle((self.X_block-10+off)/self.m_W*w,
                                                 (self.Y_block-10)/self.m_H*h,
                                                 (self.X_block+305+off)/self.m_W*w,
                                                 (self.Y_block+340)/self.m_H*h,
                                                 30/self.m_H*h,
                                                 fill='black',
                                                 outline='')
            self.canvas.create_rectangle((self.X_block-15+off)/self.m_W*w,
                                         (self.Y_block)/self.m_H*h,
                                         (self.X_block+310+off)/self.m_W*w,
                                         (self.Y_block+295)/self.m_H*h,
                                         fill='black',
                                         outline='')
            self.canvas.create_rectangle((self.X_block-15+off)/self.m_W*w,
                                         (self.Y_block+5)/self.m_H*h,
                                         (self.X_block+310+off)/self.m_W*w,
                                         (self.Y_block+290)/self.m_H*h,
                                         fill=self.master.colors['pink'],
                                         outline='')
            self.canvas.create_rectangle((self.X_block-10+off)/self.m_W*w,
                                         (self.Y_block+5)/self.m_H*h,
                                         (self.X_block+305+off)/self.m_W*w,
                                         (self.Y_block+290)/self.m_H*h,
                                         fill='black',
                                         outline='')

