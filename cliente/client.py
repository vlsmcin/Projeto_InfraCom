from socket import *

serverName = 'localhost'

serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

file = open('./arquivos_para_enviar/ex.txt', 'r')
fileContent = file.read()
file.close()

clientSocket.sendto(fileContent.encode(), (serverName, serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

print(modifiedMessage.decode())

clientSocket.close()