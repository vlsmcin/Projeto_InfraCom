from socket import *
import os, sys

#sys.path.append(os.path.abspath("../"))

#import utils

from fsm import *


# Inicialização do servidor, tendo a porta, o ip e tipo (UDP)
serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('', serverPort))

print ('The server is ready to receive')

metadata = True
# Variável para contar quantos pacotes foram enviados
loopCount = 0
        
def process_packet(data, filename):
    with open(f'./arquivos_recebidos_servidor/{filename}', 'ab') as f:
        f.write(data)


# Loop infinito que o servidor executa esperando pacotes
while True:
    # Lê o inicialmente o nome do arquivo e setta metadata para False, indicando que agora de fato
    # É o arquivo que está sendo enviado
    packageCount:int = 0
    filename = ""
    if metadata:
        pkt_fileName: Packets
        pkt_fileName, clientAddress = FSM_receptor(serverSocket)
        filename = pkt_fileName.data[0].decode()
        metadata = False
        name, extension = os.path.splitext(filename)
        file_count = 1
        # Verifica se o arquivo já existe, e se existir, incrementa o contador para criar um nome único
        while os.path.exists(f'./arquivos_recebidos_servidor/archived_{name}' + f'_{file_count}' + extension):
            file_count += 1
        filename = 'archived_' + name + f'_{file_count}' + extension
        # Recebe informações da quantidade de pacotes para determinar parada
        packageCountEncoded = pkt_fileName.data[1]
        packageCount = int.from_bytes(packageCountEncoded, byteorder='big')
        
    message, clientAddress = serverSocket.recvfrom(1024)
    modifiedMessage = message
    loopCount += 1

    # Abre (ou cria) o arquivo no modo append binário e escreve o bloco de dados
    # Está no modo append para cada pacote incrementar as informações do arquivo
    with open(f'./arquivos_recebidos_servidor/{filename}', 'ab') as f:
        f.write(modifiedMessage)

    # Se o tamanho do pacote recebido for menor que 1024 bytes, indica que é o último pacote
    if loopCount >= packageCount:
        # Reinicia a quantidade de pacotes para um novo cliente
        loopCount = 0
        serverSocket.sendto(filename.encode(), clientAddress)
        # Abre o arquivo salvo no modo leitura binária e envia seu conteúdo de volta ao cliente em blocos de 1024 bytes
        with open(f'./arquivos_recebidos_servidor/{filename}', 'rb') as f:
            returnMessage = f.read(1024)
            while returnMessage:
                serverSocket.sendto(returnMessage, clientAddress)
                returnMessage = f.read(1024)
        metadata = True #Flag de controle para saber quando deve ler o nome de um arquivo
