import os
import threading, queue
from datetime import datetime
from fsm import *

serverPort = 12000
clientList = {"SERVIDOR":('', serverPort)} #   "login" : (ip,porta)
clientList_lock = threading.Lock()

msgQueue = queue.Queue(maxsize=50)

def splitMessage(texto, tamanho=1020):
    return [texto[i:i+tamanho].encode() for i in range(0, len(texto), tamanho)]

def receiveMsgClient(clientIP, newPort):
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', newPort))

    clientAddress = (clientIP, newPort)

    while True:
        pkt, realClientAddress = FSM_receptor(serverSocket) # get dynamic client port # TO DO: fix this
        
        if pkt[0].decode() == "BYE":
            clientName = ""
            with clientList_lock:
                clientName = [cltName for cltName, cltAdress in clientList.items() if cltAdress == clientAddress]
            clientList.pop(clientName[0])
            print(f"Cliente {clientName[0]} pediu para sair da sala")
            FSM_transmissor([b"OK"], serverSocket, realClientAddress)
            return
        else:
            clientName = ""
            msg = [i.decode() for i in pkt]
            msg = ''.join(msg)
            with clientList_lock:
                clientName = [cltName for cltName, cltAdress in clientList.items() if cltAdress == clientAddress]
            message = f'{clientAddress[0]}:{clientAddress[1]}/~{clientName[0]}: <{msg}> <{datetime.now().strftime("%H:%M:%S, %d/%m/%Y")}>'
            print(message)
            splitedMessage = splitMessage(message)
            msgQueue.put(splitedMessage)

def broadcast():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    
    while True:
        if msgQueue.qsize() > 0:
            msg = msgQueue.get()
            clientList_copy = {}
            with clientList_lock:
                clientList_copy = clientList.copy()

            clientList_copy.pop("SERVIDOR")

            for k,v in clientList_copy.items():
                FSM_transmissor(msg, serverSocket, (v[0],v[1]-1)) # Same IP but Port -1

if __name__ == '__main__':
    # Inicialização do servidor, tendo a porta, o ip e tipo (UDP)    
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    
    print ('The server is ready to receive')

    t0 = threading.Thread(target=broadcast)
    t0.start()

    while True:
        pkt, clientAdress = FSM_receptor(serverSocket)
        
        if pkt[0].decode() == "HI":
            clientLogin = pkt[1].decode()
            if clientLogin not in clientList.keys():
                lastKey, lastValue = list(clientList.items())[-1]
                newPort = lastValue[1] + 2
                clientList[clientLogin] = (clientAdress[0], newPort)
                print("Login recebido:", clientLogin)
                FSM_transmissor([b"OK", newPort.to_bytes(4, byteorder='big')], serverSocket, clientAdress)
                # create thread receber mensagem
                t1 = threading.Thread(target=receiveMsgClient, args=(clientAdress[0], newPort))
                t1.start()
                #t1.join()
                
            else:
                errorMessage = "Erro: ja existe um cliente com esse login na sala"
                FSM_transmissor([b"ERROR", errorMessage.encode()], serverSocket, clientAdress)
