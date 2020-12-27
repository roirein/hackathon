from socket import *
import time
from threading import *
import sys
import struct


class Server:

    def __init__(self):
        self.udp_server_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.clients = []
        self.group1 = {}
        self.score1 = 0
        self.score2 = 0
        self.group2 = {}
        self.server_name = "Jesus Christ"

    def spread_the_message(self):
        print("Server started,listening on IP address " + gethostbyname(gethostname()))
        self.udp_server_socket.bind(('', 12000))
        self.udp_server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        t_end = time.time() + 10
        message = struct.pack('Ibh', 0xfeedbeef, 0x2, 0x2ee1)
        while time.time() < t_end:
            self.udp_server_socket.sendto(message, ("<broadcast>", 13117))
            time.sleep(1)
        self.udp_server_socket.close()
        print("finished broadcast")

    def accept_clients(self):
        print("ready to accept clients")
        self.tcp_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.tcp_server_socket.bind(('', 12001))
        self.tcp_server_socket.listen(100)
        self.tcp_server_socket.settimeout(1)
        t_end = time.time() + 10
        while time.time() < t_end:
            try:
                connection, addr = self.tcp_server_socket.accept()
                self.add_new_client(connection,addr)
            except:
                pass
        print("finished accept clients")

    def add_new_client(self, client,addr):
        name = client.recv(1024)
        name = name.decode(encoding='utf-8')
        self.clients.append([name, client, addr])

    def communicate_with_client(self,client):
        client.settimeout(1)
        respond = "Welcome to Keyboard Spamming Battle Royale.\n"
        respond += "Group 1:\n==\n"
        for i in self.group1:
            respond += self.group1[i]
        respond += "Group 2:\n==\n"
        for i in self.group2:
            respond += self.group2[i]
        client.send(str.encode(respond))
        mutex = Lock()
        start = time.time()
        while time.time() < start + 10:
            try:
                msg = (client.recv(1024)).decode(encoding='utf-8')
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
                pass
        print("game over,calculating results")


    def run_server(self):
        t1 = Timer(0.1,self.spread_the_message)
        t2 = Timer(0.1,self.accept_clients)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
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
        print(str(self.score1),str(self.score2))


server = Server()
server.run_server()

