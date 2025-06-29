from socket import *

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('localhost', serverPort))

print ('The server is ready to receive')

while True:
    message, clientAddress = serverSocket.recvfrom(1024)

    print(message.isascii())
    
    modifiedMessage = message

    file = open('./arquivos_recebidos_servidor/teste.txt', 'ab')
    file.write(modifiedMessage)
    file.close()
    
    serverSocket.sendto(modifiedMessage, clientAddress)
