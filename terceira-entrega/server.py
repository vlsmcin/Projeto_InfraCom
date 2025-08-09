import os
from fsm import *

# def receive(serverSocket):
    


# def send(clientAddress, serverSocket):
    


if __name__ == '__main__':
    # Inicialização do servidor, tendo a porta, o ip e tipo (UDP)
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    clientList = {"SERVIDOR":('', serverPort)} #   "login" : (ip,porta)
    print ('The server is ready to receive')

    while True:
        pkt, clientAdress = FSM_receptor(serverSocket)
        
        if pkt[0].decode() == "HI":
            clientLogin = pkt[1].decode()
            if clientLogin not in clientList.keys():
                lastKey, lastValue = list(clientList.items())[-1]
                newPort = lastValue[1] + 1
                clientList[clientLogin] = (clientAdress[0], newPort)
                print("Login recebido:", clientLogin)
                FSM_transmissor([b"OK", newPort.to_bytes(4, byteorder='big')], serverSocket, clientAdress)
                #create thread receber mensagem
            else:
                errorMessage = "Erro: ja existe um cliente com esse login na sala"
                FSM_transmissor([b"ERROR", errorMessage.encode()], serverSocket, clientAdress)
