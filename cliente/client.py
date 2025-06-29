from socket import *

serverName = 'localhost'

serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

fileName = 'santa.png'

if fileName.endswith('.png'):
    file = open('./arquivos_para_enviar/santa.png', 'rb')
    fileContent = file.read()
    file.close()
    clientSocket.sendto(fileContent, (serverName, serverPort))

else: 
    file = open('./arquivos_para_enviar/ex.txt', 'r')
    fileContent = file.read()
    file.close()
    clientSocket.sendto(fileContent.encode(), (serverName, serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

print('Message successfully sent')

clientSocket.close()