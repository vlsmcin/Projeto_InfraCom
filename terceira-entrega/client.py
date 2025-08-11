'''
Lógica Geral Cliente:

1. Inicialização
    - O cliente cria um socket TCP e tenta se conectar ao servidor usando o IP e porta configurados.
    - O usuário fornece login para identificação no chat.

2. Estabelecendo comunicação
    - Após a conexão ser aceita pelo servidor, o cliente pode enviar comandos (ex.: ver usuarios no chat).
    - Inicia uma thread dedicada para receber mensagens do servidor continuamente.
    - O loop principal cuida do envio de mensagens e comandos.

3. Enviando mensagens e comandos
    - O cliente envia pacotes formatados ao servidor, que podem incluir:
        - Mensagens de chat para todos
        - Comando para listar usuários conectados
        - Solicitações para adicionar/remover amigos
        - Participar de votação de banimento
        - Comando para sair do chat

4. Recebendo mensagens
    - A thread receptora fica em loop aguardando mensagens do servidor.
    - As mensagens recebidas podem ser:
        - Textos enviados por outros clientes
        - Confirmações ou erros para ações solicitadas
        - Atualizações de listas (amigos, usuários conectados)
        - Avisos de votação ou banimento

5. Encerramento
    - O cliente pode encerrar a conexão manualmente enviando um comando de saída.
    - Caso o servidor encerre a conexão (ex.: banimento), o cliente encerra o programa.
'''

import os, json
from fsm import *   # Importa funções de transmissão/recepção implementadas no módulo fsm
import threading

# Configuração inicial do cliente
serverName = 'localhost'  # Endereço do servidor
serverPort = 12000        # Porta padrão para se conectar ao servidor

# Controle de conexão
isConnected = False
isConnected_lock = threading.Lock()  # Lock para evitar condições de corrida

login = ""  # Nome de usuário do cliente

# Função para dividir mensagens em blocos menores para transmissão (máx. 1020 bytes cada)
def splitMessage(texto, tamanho=1020):
    return [texto[i:i+tamanho].encode() for i in range(0, len(texto), tamanho)]

# Função responsável por enviar comandos e mensagens para o servidor
def send(clientSocket):
    global isConnected
    global serverPort
    global login
    msg = str(input())  # Lê comando ou mensagem do usuário

    match msg:  # Avalia o comando digitado pelo cliente
        
        # Comando para entrar no chat
        case s if  s.startswith(":HI"): 
            with isConnected_lock:
                if not isConnected:
                    login = msg[4:]  # Captura o login enviado pelo usuário
                    # Envia comando ":HI" seguido do login para o servidor
                    FSM_transmissor([b":HI", login.encode()], clientSocket, (serverName, serverPort))

                    pkt, _ = FSM_receptor(clientSocket)  # Recebe resposta do servidor

                    if pkt[0].decode() == "ERROR":
                        print(pkt[1].decode())  # Mensagem de erro
                    elif pkt[0].decode() == "OK":
                        isConnected = True
                        newPort = int.from_bytes(pkt[1], byteorder='big')  # Nova porta para comunicação
                        serverPort = newPort
                        print("Você entrou na sala de chat")
                        # Inicia thread para receber mensagens de forma assíncrona
                        t1 = threading.Thread(target=receive)
                        t1.start()
                else:    
                    print("Você já está conectado")
                return
            
        # Comando para sair do chat
        case s if s.startswith(":BYE"):
            FSM_transmissor([b":BYE"], clientSocket, (serverName, serverPort))

            pkt, _ = FSM_receptor(clientSocket)
        
            if pkt[0].decode() == "ERROR":
                print(pkt[1].decode())
            elif pkt[0].decode() == "OK":
                with isConnected_lock:
                    isConnected = False
                print("Você saiu da sala de chat")
                os._exit(0)  # Encerra o programa
                
        # Comando para votar no banimento de um usuário
        case s if s.startswith(":BAN"):
            loginBan = msg[5:]
            FSM_transmissor([b":BAN", loginBan.encode()], clientSocket, (serverName, serverPort))

            pkt, _ = FSM_receptor(clientSocket)

            if pkt[0].decode() == "ERROR":
                print(pkt[1].decode())
            elif pkt[0].decode() == "OK":
                print(f'Voto para banir {loginBan} computado.')
                
        # Lista usuários conectados
        case s if s.startswith(":LIST"):
            FSM_transmissor([b':LIST'], clientSocket, (serverName, serverPort))
            
            pkt, _ = FSM_receptor(clientSocket)
            msg = [i.decode() for i in pkt] # Remontagem da mensagem contendo lista de clientes
            msg = ''.join(msg)

            clientList: dict = json.loads(msg) # Transforma string no formato de dicionario

            print("Nome | IP:PORTA")
            for k,v in clientList.items():
                print(f"{k} : {v[0]}:{v[1]}") # Itera sobre dicionario da lista de usuarios, printando seu conteudo

        # Adiciona amigo
        case s if s.startswith(":ADDF"):
            friendLogin = msg[6:]
            FSM_transmissor([b":ADDF", friendLogin.encode()], clientSocket, (serverName, serverPort))

            pkt, _ = FSM_receptor(clientSocket)

            if pkt[0].decode() == "ERROR":
                print("ERRO:", pkt[1].decode())
            elif pkt[0].decode() == "OK":
                print(f'{friendLogin} foi adicionado a sua lista de amigos.')
                
        # Remove amigo
        case s if s.startswith(":RMVF"):
            friendLogin = msg[6:]
            FSM_transmissor([b":RMVF", friendLogin.encode()], clientSocket, (serverName, serverPort))

            pkt, _ = FSM_receptor(clientSocket)

            if pkt[0].decode() == "OK":
                print(f"Removido {friendLogin} da sua lista de amigos")
            elif pkt[0].decode() == "ERROR":
                print("ERROR: ",pkt[1].decode())
                
        # Lista de amigos
        case s if s.startswith(":FLIST"):
            FSM_transmissor([b":FLIST"], clientSocket, (serverName, serverPort))

            pkt, _ = FSM_receptor(clientSocket)

            msg = [i.decode() for i in pkt]
            msg = ''.join(msg)
            
            print("Amigos")
            friendList = json.loads(msg)
            for i in friendList:
                print(i)

        # Caso padrão: envia mensagem para o chat
        case _:
            if msg != "": # Previne mensagens vazias
                splitedMessage = splitMessage(msg) # Divide mensagem em blocos menores para transmissao
                FSM_transmissor(splitedMessage, clientSocket, (serverName, serverPort))

    return

# Função que recebe mensagens do servidor em uma thread separada
# Essa thread é inicializada quando o comando de :HI eh bem sucedido
# Alem disso, sao utilizadas duas portas especificas por cliente, sendo uma para enviar (ex: 12002) e uma para receber (ex: 12001) mensagens do servidor
def receive():
    global isConnected
    global login
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', serverPort-1))  # Porta de recepção (serverPort - 1)
    
    while True:
        with isConnected_lock:
            isConnectedCopy = isConnected # Cópia da variavel isConnect para nao travar o mutex por muito tempo
            
        if isConnectedCopy:
            pkt, _  = FSM_receptor(clientSocket)
            msg = [i.decode() for i in pkt] # Remontagem da mensagem
            msg = ''.join(msg) 
            if msg.startswith(f"{login} foi banido."): # Verifica se o cliente foi banido
                print("Voce foi banido do chat.")
                os._exit(0)  # Finaliza o cliente
            else:
                print(msg) # Caso não seja uma mensagem de ban, printa a mensagem do chat no terminal do cliente
        else:
            return # Caso isConnected seja false, encerra a thread de escuta de mensagens

# Ponto de entrada do cliente
if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    while True:
        send(clientSocket)
