import os
from fsm import *
import threading

serverName = 'localhost'
serverPort = 12000

isConnected = False
isConnected_lock = threading.Lock()

def splitMessage(texto, tamanho=1020):
    return [texto[i:i+tamanho].encode() for i in range(0, len(texto), tamanho)]

def send(clientSocket):
    global isConnected
    global serverPort
    msg = str(input())

    # Join chat session
    if msg.startswith(":HI"): 
        with isConnected_lock:
            if not isConnected:
                login = msg[4:] # Message format: ":HI <login>"
                FSM_transmissor([b"HI", login.encode()], clientSocket, (serverName, serverPort))

                pkt, _ = FSM_receptor(clientSocket)

                if pkt[0].decode() == "ERROR":
                    print(pkt[1].decode())
                elif pkt[0].decode() == "OK":
                    isConnected = True
                    newPort = int.from_bytes(pkt[1], byteorder='big')
                    serverPort = newPort # client will talk with server by new port
                    print("Você entrou na sala de chat")
                    print("Nova porta:", newPort)
                    t1 = threading.Thread(target=receive)
                    t1.start()
            else:    
                print("Você já está conectado")
            return
    # Exit chat session
    elif msg.startswith(":BYE"):
  
        FSM_transmissor([b"BYE"], clientSocket, (serverName, serverPort))

        pkt, _ = FSM_receptor(clientSocket)
     
        if pkt[0].decode() == "ERROR":
            print(pkt[1].decode())
        elif pkt[0].decode() == "OK":
            with isConnected_lock:
                isConnected = False
            serverPort = 12000 # client will talk with server by new port
            print("Você saiu da sala de chat")
    else:
        splitedMessage = splitMessage(msg)
        FSM_transmissor(splitedMessage, clientSocket, (serverName, serverPort))


    return

def receive():
    global isConnected
    while True:
        with isConnected_lock:
            if isConnected:
                clientSocket = socket(AF_INET, SOCK_DGRAM)
                clientSocket.bind(('', serverPort-1))

                pkt, _  = FSM_receptor(clientSocket)
                msg = [i.decode() for i in pkt]
                msg = ''.join(msg)
                print(msg)
            else:
                return

if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    while True:
        send(clientSocket)
