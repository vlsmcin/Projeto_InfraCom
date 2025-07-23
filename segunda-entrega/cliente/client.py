from socket import *
import os, sys
from math import ceil
from fsm import *

# Dados do servidor (porta e ip)
serverName = 'localhost'

serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)

fileName = 'ex.txt'  

# Ler partes do arquivo (1024 bytes) para dividir no pacote
# Manda primeiro o nome do arquivo e depois manda o arquivo
with open(f'./arquivos_para_enviar/{fileName}', 'rb') as f:
    # Conta quantos pacotes tem a serem enviados, dividindo cada pacote em 1024 bytes
    packagesCount = ceil(os.path.getsize(f'./arquivos_para_enviar/{fileName}') / 1024)
    # Manda o nome e quantidade de pacotes
    FSM_transmissor([fileName.encode(), packagesCount.to_bytes(4, byteorder='big')],clientSocket, (serverName, serverPort))
    fileContent = f.read(1020)#1024

    # Continua no loop até não ter mais o que ler
    dados = []
    while fileContent:
        dados.append(fileContent)
        fileContent = f.read(1020)
    FSM_transmissor(dados, clientSocket, (serverName, serverPort))


print('Message successfully sent')

# Recebe o nome do arquivo do servidor

pkt_fileName, serverAddress = FSM_receptor(clientSocket)
filename = 'received_' + pkt_fileName[0].decode()

data, clientAddress = FSM_receptor(clientSocket)

for i in data:
    with open(f'./arquivos_recebidos_cliente/{filename}', 'ab') as f:
        f.write(i)

print("Arquivo recebido")

clientSocket.close()


