import os
from math import ceil
from fsm import *


def send(fileName, clientSocket, Perda_de_Pacote):
    with open(f'./arquivos_para_enviar/{fileName}', 'rb') as f:
        packagesCount = ceil(os.path.getsize(f'./arquivos_para_enviar/{fileName}') / 1020)
        FSM_transmissor([fileName.encode(), packagesCount.to_bytes(4, byteorder='big')], clientSocket,
                        (serverName, serverPort), Perda_de_Pacote)
        fileContent = f.read(1020)
        dados = []
        while fileContent:
            dados.append(fileContent)
            fileContent = f.read(1020)
        FSM_transmissor(dados, clientSocket, (serverName, serverPort), Perda_de_Pacote)

    print(f'Arquivo {fileName} enviado para o servidor')


def receive(clientSocket):
    pkt_fileName, serverAddress = FSM_receptor(clientSocket)
    filename = 'received_' + pkt_fileName[0].decode()

    data, clientAddress = FSM_receptor(clientSocket)

    for i in data:
        with open(f'./arquivos_recebidos_cliente/{filename}', 'ab') as f:
            f.write(i)

    print(f"Arquivo {filename} recebido")


if __name__ == '__main__':
    # Dados do servidor (porta e ip)
    serverName = 'localhost'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    fileName = 'nautico.jpg'

    send(fileName, clientSocket, True)
    receive(clientSocket)

    clientSocket.close()
