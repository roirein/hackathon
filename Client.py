import select
import time
import os
import threading
from socket import *
import struct
import colorama
#from msvcrt import getch
#from msvcrt import kbhit
import os
import _thread
import multiprocessing

# Windows
if os.name == 'nt':
    import msvcrt
    import sys

# Posix (Linux, OS X)
else:
    import fcntl
    import sys
    import select
    from multiprocessing import process
    import tty
    import getch
    import termios


class Client:

    def __init__(self, name):
        self.name = name
        #self.udp_client_Socket = socket(AF_INET, SOCK_DGRAM)
        #self.tcp_client_Socket = socket(AF_INET, SOCK_STREAM)
        print("Client started, listening for offer requests...")
        self.input = None
        colorama.init()

    def look_for_server(self):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_socket.bind(('', 13117))
        magic_cookie = 4276993775
        msg = 0
        while msg != magic_cookie:
            data,adrr = udp_socket.recvfrom(1024)
            try:
                data = struct.unpack("Ibh", data)
            except:
                continue
            print(f'{colorama.Fore.LIGHTYELLOW_EX}Received offer from " + adrr[0] + " ,attempting to connect...')
            if data[0] == magic_cookie:
                msg = magic_cookie
            else:
                print(f'{colorama.Fore.RED}connection failed, trying again')
        udp_socket.close()
        return data[2], adrr[0]

    def connect_to_server(self, address):
        try:
            tcp_Socket = socket(AF_INET, SOCK_STREAM)
            tcp_Socket .setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            tcp_Socket .connect((address[1], address[0]))
            tcp_Socket .send(str.encode(self.name + "\n"))
            return tcp_Socket
        except:
            print(colorama.Fore.RED+"connection failed")

    def communicate_with_server(self, socket):
        try:
            msg = socket.recv(1024)
        except:
            print(colorama.Fore.RED+"connection lost, listening for offer requests...")
            try:
                socket.close()
                return
            except:
                return
        msg = msg.decode(encoding="utf-8")
        print(msg)
        #self.tcp_client_Socket.settimeout(0.001)
        t_end = time.time() + 10
        stop = 0.5
        while time.time() < t_end:
            if os.name == 'nt':
                try:
                    if msvcrt.kbhit():
                        key = msvcrt.getch()
                        socket.send(str.encode(key.decode(encoding='utf-8')))

                except Exception as e:
                    print("connection lost, listening for offer requests...")
                    return
            else:
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    tty.setcbreak(sys.stdin.fileno())
                    if self.isData():
                        c = sys.stdin.read(1)
                        socket.send(str.encode(c))
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        try:
            msg = socket.recv(1024)
        except:
            print(f'{colorama.Fore.RED}connection lost, listening for offer requests...')
            socket.close()
            return
        msg = msg.decode(encoding="utf-8")
        print(f'{colorama.Fore.CYAN}' + msg)
        socket.close()
        print("Server disconnected, listening for offer requests...")

    def isData(self):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    @staticmethod
    def send_message(socket):
        try:
            key = getch.getch()
            socket.send(str.encode(key))
        except:
            pass




def run_client(client):
    while True:
        addr = client.look_for_server()
        s = client.connect_to_server(addr)
        client.communicate_with_server(s)


c = Client("STUXNET")
run_client(c)
