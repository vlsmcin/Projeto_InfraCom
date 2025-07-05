from socket import *
import os
from math import ceil

# Dados do servidor (porta e ip)
serverName = 'localhost'

serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

fileName = 'ex2.txt'

# Ler partes do arquivo (1024 bytes) para dividir no pacote
# Manda primeiro o nome do arquivo e depois manda o arquivo
with open(f'./arquivos_para_enviar/{fileName}', 'rb') as f:
    # Conta quantos pacotes tem a serem enviados, dividindo cada pacote em 1024 bytes
    packagesCount = ceil(os.path.getsize(f'./arquivos_para_enviar/{fileName}') / 1024)
    # Manda o nome e quantidade de pacotes
    clientSocket.sendto(fileName.encode(), (serverName, serverPort))
    clientSocket.sendto(packagesCount.to_bytes(4, byteorder='big'), (serverName, serverPort))
    fileContent = f.read(1024)
    # Continua no loop até não ter mais o que ler
    while fileContent:
        # Não precisa ter encode pois lê em binário
        clientSocket.sendto(fileContent, (serverName, serverPort))
        fileContent = f.read(1024)


print('Message successfully sent')

# Recebe o nome do arquivo do servidor
fileName, serverAddress = clientSocket.recvfrom(1024)
fileName = 'received_' + fileName.decode()

for i in range(packagesCount):
    # Lê cada pacote, iterando o número de pacotes que foi contado ao enviar
    modifiedMessage, serverAddress = clientSocket.recvfrom(1024)

    # Arquivo em modo a (append) para adicionar ao final do arquivo os bytes
    with open(f'./arquivos_recebidos_cliente/{fileName}', 'ab') as f:
        f.write(modifiedMessage)

clientSocket.close()
