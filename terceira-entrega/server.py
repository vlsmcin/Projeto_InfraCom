'''
Lógica Geral Servidor:

1. Inicialização
    - O servidor cria um socket TCP e começa a escutar em um IP e porta definidos.
    - Ele mantém listas/estruturas para armazenar:
        - Clientes conectados (clientList)
        - Informações temporárias, como votacoes banimento
        - Eventuais listas de amizades.
2. Aceitando conexões
    - Sempre que um cliente tenta se conectar, o servidor aceita a conexão e cria uma thread dedicada para aquele cliente.
    - Essa thread cuida exclusivamente da troca de mensagens entre servidor e aquele cliente.
3. Recebendo e processando mensagens
    - O servidor fica em loop ouvindo as mensagens do cliente.
    - Cada mensagem recebida pode representar:
        - Pedido de conexão
        - Comando para ver lista de usuários no chat
        - Pedidos referentes a lista de amigos
        - Votacao de banimento
        - Comando para sair do chat
4. Sincronização e segurança
    - Para evitar problemas quando várias threads acessam a mesma lista de clientes, o servidor usa clientList_lock para controlar a escrita/leitura.
    - Quando um cliente se desconecta ou é banido, o servidor remove ele da lista.
'''


import threading, queue
import os, json
from datetime import datetime
from fsm import *  # Importa funções de transmissão/recepção implementadas no módulo fsm

# Configuração inicial do servidor
serverPort = 12000
clientList = {"SERVIDOR":('', serverPort)}  # Lista de clientes conectados no formato: "login" : (ip, porta)
banVotes = {}         # Armazena votos de banimento: {login: (votantes)}
friendshipList = {}   # Armazena listas de amigos de cada cliente

# Locks para evitar condicoes de corrida
clientList_lock = threading.Lock()
banVotes_lock = threading.Lock()
friendshipList_lock = threading.Lock()

# Fila para armazenar mensagens que serão enviadas para todos (broadcast)
msgQueue = queue.Queue(maxsize=50)

# Função para dividir mensagens longas em blocos de 1020 bytes
def splitMessage(texto, tamanho=1020):
    return [texto[i:i+tamanho].encode() for i in range(0, len(texto), tamanho)]

# Thread que recebe e processa mensagens de um cliente específico
def receiveMsgClient(clientIP, newPort):
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', newPort))  # Porta exclusiva para esse cliente

    # Obtém o login do cliente com base no IP e porta
    clientAddress = (clientIP, newPort)
    clientName_a = []
    with clientList_lock:
        clientName_a = [cltName for cltName, cltAddress in clientList.items() if cltAddress == clientAddress]
    clientName = clientName_a[0]

    while True:
        pkt, realClientAddress = FSM_receptor(serverSocket)  # Recebe mensagem do cliente

        match pkt[0].decode():
            
            # Cliente saindo do chat
            case ":BYE":
                clientList.pop(clientName)
                print(f"Cliente {clientName} pediu para sair da sala")
                FSM_transmissor([b"OK"], serverSocket, realClientAddress)
                return
            
            # Votação de banimento
            case ":BAN":
                login = pkt[1].decode()
                loginExists = True
                with clientList_lock:
                    if clientList.get(login, None) == None:
                        loginExists = False
                        
                if not loginExists:
                    FSM_transmissor([b"ERROR",f"{login} não está no chat.".encode()], serverSocket, realClientAddress)
                else:
                    with banVotes_lock:
                        computedVotes = banVotes.get(login, ())
                        # Se o cliente ainda não votou para banir este usuário
                        if clientName not in computedVotes:
                            banVotes[login] = banVotes.get(login, ()) + (clientName,)
                            
                            votesCount = len(banVotes[login])
                            requiredVotes = ((len(clientList)-1)//2) + 1  # Maioria simples

                            msgQueue.put(f"[{login}] ban {votesCount}/{requiredVotes}")

                            # Se votos atingirem o necessário, usuário é banido
                            if votesCount == requiredVotes:
                                banVotes[login] = ()
                                message = f"{login} foi banido."
                                msgQueue.put(message)
                                banIp, banPort = "", 0
                                with clientList_lock:
                                    banIp, banPort = clientList.pop(login)
                                # Notifica cliente banido diretamente
                                FSM_transmissor([message.encode()], serverSocket, (banIp, banPort-1))

                            message = [b"OK"]
                        else:
                            message = [b"ERROR",f"{clientName} ja havia votado para banir {login}.".encode()]
                    FSM_transmissor(message, serverSocket, realClientAddress)
                    
            # Lista de clientes conectados
            case ":LIST":
                clientListCopy = {}
                with clientList_lock:
                    clientListCopy = clientList.copy()
                
                clientListCopy.pop("SERVIDOR")  # Remove o próprio servidor da lista
                clientListJSON_list = splitMessage(json.dumps(clientListCopy))

                FSM_transmissor(clientListJSON_list, serverSocket, realClientAddress)
                
            # Adiciona amigo
            case ":ADDF":
                login = pkt[1].decode()               # login do usuário que o cliente quer adicionar
                loginExists = True
                with clientList_lock:                 # verifica se o usuário existe na lista de clientes
                    if clientList.get(login, None) == None:
                        loginExists = False
                        
                if not loginExists:
                    # Se o login não existe no chat, responde com ERROR + mensagem
                    FSM_transmissor([b"ERROR",f"{login} não está no chat.".encode()], serverSocket, realClientAddress)
                else:
                    message = []
                    with friendshipList_lock:       # entra na região crítica das amizades
                        # obtém a lista de amigos do remetente (clientName) — se não existir, usa lista vazia
                        friendList = friendshipList.get(clientName, [])
                        if login not in friendList:
                            # adiciona o login na lista de amigos do remetente
                            friendshipList[clientName] = friendshipList.get(clientName, []) + [login]
                            message = [b"OK"]        # confirma sucesso
                        else:
                            # já estava na lista de amigos
                            message = [b"ERROR",f"{login} ja esta na sua lista de amigos".encode()]
                    # envia resposta (OK ou ERROR) para o cliente que pediu a operação
                    FSM_transmissor(message, serverSocket, realClientAddress)
                    
            # Remove amigo
            case ":RMVF":
                login = pkt[1].decode()               # login do usuário que se deseja remover dos amigos
                loginExists = True 
                with clientList_lock:                 # verifica se esse login está conectado
                    if clientList.get(login, None) == None:
                        loginExists = False
                        
                if not loginExists:
                    # erro: não é possível remover quem não está no chat
                    FSM_transmissor([b"ERROR",f"{login} não está no chat.".encode()], serverSocket, realClientAddress)
                else:
                    message = []
                    with friendshipList_lock:       # região crítica para modificar friendshipList
                        friendList = friendshipList.get(clientName, [])
                        if login in friendList:
                            # remove o login da lista de amigos do remetente
                            friendshipList[clientName].remove(login)
                            message = [b"OK"]
                        else:
                            # erro: o login não estava na lista de amigos
                            message = [b"ERROR",f"{login} nao esta na sua lista de amigos".encode()]
                    # envia resposta ao cliente
                    FSM_transmissor(message, serverSocket, realClientAddress)       

            # Lista de amigos
            case ":FLIST":            
                with friendshipList_lock:
                    # obtém a lista de amigos do clientName (padrão: lista vazia)
                    friendshipListCopy = friendshipList.get(clientName, [])
                    # converte para JSON e divide em blocos para envio via FSM_transmissor
                    friendshipListCopy = splitMessage(json.dumps(friendshipListCopy))
                    FSM_transmissor(friendshipListCopy, serverSocket, realClientAddress)

            # Mensagem comum enviada ao chat (qualquer outra coisa)
            case _:
                # reconstrói a mensagem a partir dos fragmentos recebidos (pkt é lista de bytes)
                msg = [i.decode() for i in pkt]
                msg = ''.join(msg)
                # formata a mensagem com ip:porta do cliente, login, conteúdo e timestamp
                message = f'{clientAddress[0]}:{clientAddress[1]}/~{clientName}: {msg} <{datetime.now().strftime("%H:%M:%S, %d/%m/%Y")}>'
                print(message)  # loga no terminal do servidor para auditoria/debug
                msgQueue.put(message)  # coloca a mensagem na fila de broadcast para envio a todos

# Thread responsável por enviar mensagens para todos os clientes
def broadcast():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    
    while True:
        if msgQueue.qsize() > 0:
            msg = msgQueue.get()
            msgBackup = msg
            clientListCopy = {}
            with clientList_lock:
                clientListCopy = clientList.copy()

            clientListCopy.pop("SERVIDOR")

            for k,v in clientListCopy.items():
                msg = msgBackup
                # Marca mensagem como [AMIGO] caso o remetente esteja na lista de amigos do receptor
                msgEdit = msg.split('/~')
                if len(msgEdit) > 1:
                    login = msgEdit[1].split(':')[0]
                    with friendshipList_lock:
                        friendList = friendshipList.get(k, [])
                        if login in friendList:
                            msg = msgEdit[0] + "/~ [AMIGO] " + msgEdit[1]
                            
                # Envia mensagem pela porta (v[1] - 1), que é usada para recepção
                FSM_transmissor(splitMessage(msg), serverSocket, (v[0],v[1]-1))

# Ponto de entrada do servidor
if __name__ == '__main__':
    # Inicialização do servidor UDP
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    
    print ('The server is ready to receive')

    # Thread de envio de mensagens
    t0 = threading.Thread(target=broadcast)
    t0.start()

    # Loop principal para aceitar conexões
    while True:
        pkt, clientAddress = FSM_receptor(serverSocket)
        
        # Pedido de conexão de um cliente
        if pkt[0].decode() == ":HI":
            clientLogin = pkt[1].decode()
            if clientLogin not in clientList.keys():
                # Define nova porta para este cliente (+2 em relação à última)
                lastKey, lastValue = list(clientList.items())[-1]
                newPort = lastValue[1] + 2
                clientList[clientLogin] = (clientAddress[0], newPort)
                print("Login recebido:", clientLogin)
                FSM_transmissor([b"OK", newPort.to_bytes(4, byteorder='big')], serverSocket, clientAddress)
                msgQueue.put(f'{clientLogin} entrou na sala.')  # Notifica entrada no chat
                # Cria thread para gerenciar comunicação com este cliente
                t1 = threading.Thread(target=receiveMsgClient, args=(clientAddress[0], newPort))
                t1.start()
            else:
                # Login já existe na sala
                errorMessage = "Erro: ja existe um cliente com esse login na sala"
                FSM_transmissor([b"ERROR", errorMessage.encode()], serverSocket, clientAddress)
