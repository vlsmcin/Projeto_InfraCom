import os
from math import ceil
from fsm import *

serverName = 'localhost'
serverPort = 12000

def send(clientSocket):
    msg = input()

    if msg.startswith(":HI"):
        login = msg[3:]
        FSM_transmissor([b"HI", login.encode()], clientSocket, (serverName, serverPort))

        pkt, _ = FSM_receptor(clientSocket)

        if pkt[0].decode() == "ERROR":
            print(pkt[1].decode())
        elif pkt[0].decode() == "OK":
            newPort = int.from_bytes(pkt[1], byteorder='big')
            print("Nova porta:", newPort)


    return

def receive(clientSocket):
    return

if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    send(clientSocket)
    receive(clientSocket)

    clientSocket.close()
