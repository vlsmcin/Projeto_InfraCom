import os
from socket import *

serverName = 'localhost'

serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

fileName = 'santa.png'

file = open(f'./arquivos_para_enviar/{fileName}', 'rb')

fileContent = file.read(1024)
while fileContent:
    clientSocket.sendto(fileContent, (serverName, serverPort))
    fileContent = file.read(1024)

file.close()

#clientSocket.sendto(fileContent, (serverName, serverPort))

print('Message successfully sent')

modifiedMessage, serverAddress = clientSocket.recvfrom(1024)

file = open(f'./arquivos_recebidos_cliente/{fileName}', 'wb')
file.write(modifiedMessage)
file.close()


clientSocket.close()
