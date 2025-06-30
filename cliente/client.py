from socket import *

serverName = 'localhost'

serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

fileName = 'nautico.jpg'

packagesCount = 0
with open(f'./arquivos_para_enviar/{fileName}', 'rb') as f:
    fileContent = f.read(1024)
    while fileContent:
        clientSocket.sendto(fileContent, (serverName, serverPort))
        packagesCount+=1
        fileContent = f.read(1024)


print('Message successfully sent')

for i in range(packagesCount):
    modifiedMessage, serverAddress = clientSocket.recvfrom(1024)

    with open(f'./arquivos_recebidos_cliente/{fileName}', 'ab') as f:
        f.write(modifiedMessage)

clientSocket.close()
