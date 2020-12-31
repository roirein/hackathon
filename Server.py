from socket import *
import time
from threading import *
import struct
import colorama
import scapy.all

class Server:

    def __init__(self):
        '''constructor for the server that initalize the the
        data structures for the game'''
        self.clients = []
        self.group1 = {}
        self.score1 = 0
        self.score2 = 0
        self.group2 = {}
        ips = ["172.1.0.33","172.99.0.33",scapy.all.get_if_addr(scapy.all.conf.iface)]
        for i in range(len(ips)):
            print(str(i+1) + " " + ips[i])
        n = input("enter your ip: ")
        while n != '1' and n != '2' and n != '3':
            n = input("enter your ip: ")
        self.my_ip = ips[int(n) - 1]
        colorama.init()
        print(f'{colorama.Fore.GREEN}Server started,listening on IP address ' + self.my_ip)


    def spread_the_message(self):
        '''method for broadcasting offers to join the game
        using udp packets'''
        dest_port = 13117
        source_port = 12000
        cookie = 0xfeedbeef
        offer = 0x2
        port_hexa = 0x2ee1
        broadcast_ip = ""
        if self.my_ip.startswith("172.1"):
            broadcast_ip = "172.1.255.255"
        elif self.my_ip.startswith("172.99"):
            broadcast_ip = "172.99.255.255"
        else:
            broadcast_ip = "255.255.255.255"
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind((self.my_ip, source_port))
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        t_end = time.time() + 10
        message = struct.pack('Ibh',cookie, offer, port_hexa)
        while time.time() < t_end:
            udp_socket.sendto(message, (broadcast_ip, dest_port))
            time.sleep(1)
        udp_socket.close()

    def accept_clients(self, tcp_socket):
        '''method for accepting clients that recived the
        offer for join the game'''
        t_end = time.time() + 10
        while time.time() < t_end:
            try:
                connection, addr = tcp_socket.accept()
                self.add_new_client(connection, addr)
            except:
                continue

    def add_new_client(self, client, addr):
        '''adding new client for the game'''
        client.settimeout(10)
        name = client.recv(1024)
        name = name.decode(encoding='utf-8')
        self.clients.append([name, client, addr])

    def communicate_with_client(self, client):
        '''method for communicate with the clients during the game,
        send messages to the client about the game and recives the pressed keys
        from the clients and count them for their group during the game'''
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
            print(f'{colorama.Fore.RED}connection lost')
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
                return

    def server_main_func(self):
        '''method that manage the server, using all the functions above
        and arrange the game groups and starts the threads for wach client'''
        dest_port = 12001
        flag = False
        clients = []
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
        '''reset the class field after a game over'''
        self.clients.clear()
        self.group1.clear()
        self.group2.clear()
        self.score1 = 0
        self.score2 = 0


def run_server(server):
    '''driver code for the server'''
    while True:
        server.server_main_func()
        time.sleep(1)


server = Server()
run_server(server)

