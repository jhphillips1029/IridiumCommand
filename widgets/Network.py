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

This widget will allow different copies of the ICC to communicate across multiple unique devices.
"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import widgets.Widget as Widget
import socket
import threading
import io
import json
    
class Network(Widget.Widget):
    def __init__(self,master,x,y,m_W,m_H,w=300,h=300):
        Widget.Widget.__init__(self,master,x,y,m_W,m_H,w,h)
        
        self.port = 8080
        self.timeout = 0.1
        self.recv_running = True
        self.process_buffer = None
        self.client_addresses = []
        self.MASTER = False
        
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        self.local_ip = s.getsockname()[0]
        s.close()
        
        self.recv_thread = threading.Thread(target=self.run_recv_sock)
        self.recv_thread.start()
        
        self.add_comp(tk.Label(self,
                               text='New Connection',
                               font=('Arial',10)
                              ),
                      0,0,150,20)
        
        self.ip_entry_comp_index = len(self.components)
        self.add_comp(tk.Entry(self,
                               textvariable=tk.StringVar(self,value='Type an ip address'),
                               font=('Arial',10)
                              ),
                      0,25,150,20)
        
        self.add_comp(tk.Button(self,
                                text='Connect',
                                font=('Arial',10),
                                command=self.connect
                               ),
                      25,50,100,20)
                      
        self.add_comp(tk.Button(self,
                                text='Claim MASTER',
                                font=('Arial',10),
                                command=self.claim_master,
                               ),
                      180,25,150,20)
                      
                      
    def claim_master(self):
        self.MASTER = True
        for addr in self.client_addresses:
            self.send(addr[0],addr[1],'code:self.MASTER=False;print(self.MASTER)')
            
            
    def set_profile(self):
        if self.MASTER:
            try:
                profile_bytes = b'file:'+json.dumps(self.master.profile).encode('utf-8')
                for addr in self.client_addresses:
                    self.send(addr[0],addr[1],profile_bytes,encode=False)
                    self.send(addr[0],addr[1],'code:data=json.loads(self.process_buffer.read().decode("utf-8"));self.master.set_profile(data)')
            except Exception as e:
                print('{}'.format(e))
                
                
    def set_alert(self,level):
        if self.MASTER:
            try:
                for addr in self.client_addresses:
                    self.send(addr[0],addr[1],'code:self.master.set_alert({})'.format(level))
                      
                      
    def connect(self):
        ip_addr,port = self.components[self.ip_entry_comp_index][0].get().split(':')
        port = int(port)
        self.send(ip_addr,port,'{}'.format(self.port))
        
        
    def run_recv_sock(self):
        recv_sock = socket.socket()
        recv_sock.settimeout(self.timeout)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.bind((self.local_ip,self.port))
        recv_sock.listen(5)
        
        try:
            while True:
                c,addr = None,None
                try:
                    c,addr = recv_sock.accept()
                    if addr[0] not in [a[0] for a in self.client_addresses]:
                        c_port = int(c.recv(65535).decode('utf-8'))
                        c.close()
                        c = None
                    
                        self.client_addresses.append((addr[0],c_port))
                        self.send(addr[0],c_port,'{}'.format(self.port))
                except KeyboardInterrupt:
                    raise
                except: pass
        
                if not(self.recv_running):
                    raise KeyboardInterrupt('Fuck you.')
            
                if c is not None:
                    msg = c.recv(65535)
                    self.process(addr[0],[a[1] for a in self.client_addresses if a[0]==addr[0]][0],msg)
                    c.close()
            
        except KeyboardInterrupt:
            recv_sock.shutdown(socket.SHUT_RDWR)
            recv_sock.close()
            
        return
        
        
    def process(self,address,port,message):
        if message[:5]==b'code:':
            try:
                exec(message.decode('utf-8')[5:])
            except Exception as e:
                self.send(address,port,'{}'.format(e))
        elif message[:5]==b'file:':
            self.process_buffer = io.BytesIO(message[5:])
        else:
            print(message.decode('utf-8'))
            
            
    def send(self,address,port,message,encode=True):
        s = socket.socket()
        try:
            s.connect((address,port))
            send_me = message.encode('utf-8') if encode else message
            s.send(send_me)
        finally:
            s.close()
        
        
    def redraw(self,w,h):
        pass
        
        
    def close(self):
        self.recv_running = False
        self.recv_thread.join()

