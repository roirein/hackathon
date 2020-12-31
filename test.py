import socket
import sys
import ipaddress
import msvcrt
import time
from colorama import Fore
from colorama import Style
from colorama import init
import scapy.all
import socket
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

init()

#print(scapy.all.get_if_addr())
print(scapy.all.get_if_addr(socket.gethostname()))
print(f'This is{Fore.GREEN} color{Style.RESET_ALL}!')