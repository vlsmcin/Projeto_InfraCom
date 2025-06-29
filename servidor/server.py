from socket import *

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('', serverPort))

print ('The server is ready to receive')

while True:
    message, clientAddress = serverSocket.recvfrom(2048)

    print(message.isascii())

    modifiedMessage = message.decode()

    file = open('./arquivos_recebidos_servidor/teste.txt', 'w')
    file.write(modifiedMessage)
    file.close()

    serverSocket.sendto(modifiedMessage, clientAddress)
