from socket import *
import time
from threading import *
import struct
import colorama
import scapy.all

class Server:

    def __init__(self):
        self.clients = []
        self.group1 = {}
        self.score1 = 0
        self.score2 = 0
        self.group2 = {}
        self.my_ip = scapy.all.get_if_addr(scapy.all.conf.iface)
        colorama.init()
        print(f'{colorama.Fore.GREEN}Server started,listening on IP address ' + self.my_ip)


    def spread_the_message(self):
        dest_port = 13117
        source_port = 12000
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind((self.my_ip, source_port))
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        t_end = time.time() + 10
        message = struct.pack('Ibh', 0xfeedbeef, 0x2, 0x2ee1)
        while time.time() < t_end:
            udp_socket.sendto(message, ("255.255.255.255", dest_port))
            time.sleep(1)
        udp_socket.close()

    def accept_clients(self, tcp_socket):
        t_end = time.time() + 10
        while time.time() < t_end:
            try:
                connection, addr = tcp_socket.accept()
                self.add_new_client(connection, addr)
            except:
                continue

    def add_new_client(self, client, addr):
        client.settimeout(10)
        name = client.recv(1024)
        name = name.decode(encoding='utf-8')
        self.clients.append([name, client, addr])

    def communicate_with_client(self, client):
        mutex = Lock()
        respond = f'{colorama.Fore.LIGHTMAGENTA_EX}Welcome to Keyboard Spamming Battle Royale.\n'
        respond += "Group 1:\n==\n"
        for i in self.group1:
            respond += self.group1[i]
        respond += "Group 2:\n==\n"
        for i in self.group2:
            respond += self.group2[i]
        respond += "\nStart pressing keys on your keyboard as fast as you can!!\n"
        try:
            client.send(str.encode(respond))
        except:
            print(f'{colorama.Fore.GREEN}connection lost')
            return
        start = time.time()
        while time.time() < start + 10:
            try:
                msg = client.recv(1024).decode(encoding='utf-8')
                if msg is not None:
                    if client in self.group1:
                        mutex.acquire()
                        self.score1 += 1
                        mutex.release()
                    if client in self.group2:
                        mutex.acquire()
                        self.score2 += 1
                        mutex.release()
            except:
                print(f'{colorama.Fore.GREEN}connection lost')
                return

    def server_main_func(self):
        dest_port = 12001
        flag = False
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        tcp_socket.bind((self.my_ip, dest_port))
        tcp_socket.listen(100)
        tcp_socket.settimeout(1)
        while not flag:
            t1 = Timer(0.1, self.spread_the_message)
            t2 = Timer(0.1, self.accept_clients, args=(tcp_socket,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            if len(self.clients) > 0:
                flag = True
                tcp_socket.close()
                tcp_socket = socket(AF_INET, SOCK_STREAM)
                tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                tcp_socket.bind((self.my_ip, dest_port))
                tcp_socket.listen(100)
                tcp_socket.settimeout(1)
        for c in range(len(self.clients)):
            if c % 2 == 0:
                self.group1[self.clients[c][1]] = self.clients[c][0]
            else:
                self.group2[self.clients[c][1]] = self.clients[c][0]
        clients = []
        for i in self.clients:
            clients.append(Timer(0.1, self.communicate_with_client, args=(i[1],)))
        for i in clients:
            i.start()
        for i in clients:
            i.join()
        message = "Game Over!\n"
        winners = ""
        message += "Group 1 typed in " + str(self.score1) + " characters. Group 2 typed in " + str(self.score2) +\
                   " characters.\n"
        if self.score1 > self.score2:
            message += "Group 1 wins!\n\n"
            for i in self.group1:
                winners += self.group1[i]
        if self.score1 < self.score2:
            message += "Group 2 wins!\n\n"
            for i in self.group2:
                winners += self.group2[i]
        message += "Congratulations to the winners:\n"
        message += "==\n"
        message += winners
        for i in self.clients:
            try:
                i[1].send(str.encode(message))
            except:
                print("client is not available")
        tcp_socket.close()
        print("Game over, sending out offer requests...")
        self.reset()

    def reset(self):
        self.clients.clear()
        self.group1.clear()
        self.group2.clear()
        self.score1 = 0
        self.score2 = 0


def run_server(server):
    while True:
        server.server_main_func()
        time.sleep(1)


server = Server()
run_server(server)

