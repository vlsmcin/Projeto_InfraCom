from socket import *
import os, sys
from fsm import *

def receive(serverSocket):
    pkt_fileName, clientAddress = FSM_receptor(serverSocket)
    filename = pkt_fileName[0].decode()
    name, extension = os.path.splitext(filename)
    file_count = 1

    # Verifica se o arquivo já existe, e se existir, incrementa o contador para criar um nome único
    while os.path.exists(f'./arquivos_recebidos_servidor/archived_{name}' + f'_{file_count}' + extension):
        file_count += 1
    filename = 'archived_' + name + f'_{file_count}' + extension
    # Recebe informações da quantidade de pacotes para determinar parada
    packageCountEncoded = pkt_fileName[1]
    packageCount = int.from_bytes(packageCountEncoded, byteorder='big')

    message, clientAddress = FSM_receptor(serverSocket)
    modifiedMessage = message

    for i in modifiedMessage:
        with open(f'./arquivos_recebidos_servidor/{filename}', 'ab') as f:
            f.write(i)

    print(f"Recebeu o arquivo: {filename}")

    return filename, packageCount, clientAddress


def send(filename, packageCount, clientAddress, serverSocket):
    FSM_transmissor([filename.encode(), packageCount.to_bytes(4, byteorder='big')],serverSocket, clientAddress)

    dados = []
    with open(f'./arquivos_recebidos_servidor/{filename}', 'rb') as f:
        fileContent = f.read(1020)#1024

        while fileContent:
            dados.append(fileContent)
            fileContent = f.read(1020)
    FSM_transmissor(dados, serverSocket, clientAddress)

    print(f"Enviou o arquivo: {filename}")


if __name__ == '__main__':
    # Inicialização do servidor, tendo a porta, o ip e tipo (UDP)
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print ('The server is ready to receive')

    while True:
        fileName, packageCount, ClientAddress = receive(serverSocket)
        send(fileName, packageCount, ClientAddress, serverSocket)



