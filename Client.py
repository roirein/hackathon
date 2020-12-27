from socket import *
import struct
from pynput.keyboard import Listener
import tkinter as tk


class Client:

    def __init__(self, name):
        self.name = name
        self.udp_client_Socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_client_Socket = socket(AF_INET, SOCK_STREAM)


    def look_for_server(self):
        print("Client started, listening for offer requests...")
        host = gethostname()
        self.udp_client_Socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udp_client_Socket.bind((host, 13117))
        magic_cookie = 4276993775
        msg = 0
        while msg != magic_cookie:
            data,adrr = self.udp_client_Socket.recvfrom(1024)
            data = struct.unpack("Ibh", data)
            print("Received offer from " + adrr[0] + " ,attempting to connect...")
            if data[0] == magic_cookie:
                msg = magic_cookie
            else:
                print("connection failed, trying again")
        self.udp_client_Socket.close()
        return data

    def connect_to_server(self, address):
        try:
            self.tcp_client_Socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.tcp_client_Socket.connect(('127.0.0.1', address))
            self.tcp_client_Socket.send(str.encode(self.name + "\n"))
            print("connection achived in port " + str(address))
        except:
            print("connection failed")

    def communictae_with_server(self):
        msg = self.tcp_client_Socket.recv(1024)
        msg = msg.decode(encoding="utf-8")
        print(msg)
        root = tk.Tk()
        root.bind_all("<Key>",self.on_press)
        while True:
            try:
                with Listener(on_press=self.on_press) as listener:
                    listener.join()
            except:
                pass

    def on_press(self,key):
        self.tcp_client_Socket.send(str.encode(str(key)))

c = Client("Santa Claus")
addr = c.look_for_server()[2]
c.connect_to_server(addr)
c.communictae_with_server()
