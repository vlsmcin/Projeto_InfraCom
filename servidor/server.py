from socket import *
import os

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('localhost', serverPort))

print ('The server is ready to receive')

metadata = True

while True:
    if metadata:
        filename, clientAddress = serverSocket.recvfrom(1024)
        metadata = False
        filename = filename.decode()
        name, extension = os.path.splitext(filename)
        file_count = 1
        while os.path.exists(f'./arquivos_recebidos_servidor/{name}' + f'_{file_count}' + extension):
            file_count += 1
        filename = name + f'_{file_count}' + extension
        
    message, clientAddress = serverSocket.recvfrom(1024)
    modifiedMessage = message

    with open(f'./arquivos_recebidos_servidor/{filename}', 'ab') as f:
        f.write(modifiedMessage)

    if len(message) < 1024:
        serverSocket.sendto(filename.encode(), clientAddress)
        with open(f'./arquivos_recebidos_servidor/{filename}', 'rb') as f:
            returnMessage = f.read(1024)
            while returnMessage:
                serverSocket.sendto(returnMessage, clientAddress)
                returnMessage = f.read(1024)
        metadata = True

# Se pedirem múltiplos clientes, criar uma thread ou simplesmente juntar com o ip
# Seria bom a thread, ai manda como parametro pra thread o filename e o ip do cliente