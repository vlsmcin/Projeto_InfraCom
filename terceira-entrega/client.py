import os, json
from fsm import *
import threading

serverName = 'localhost'
serverPort = 12000

isConnected = False
isConnected_lock = threading.Lock()

login = ""

def splitMessage(texto, tamanho=1020):
    return [texto[i:i+tamanho].encode() for i in range(0, len(texto), tamanho)]

def send(clientSocket):
    global isConnected
    global serverPort
    global login
    msg = str(input())

    # Join chat session
    if msg.startswith(":HI"): 
        with isConnected_lock:
            if not isConnected:
                login = msg[4:] # Message format: ":HI <login>"
                FSM_transmissor([b"HI", login.encode()], clientSocket, (serverName, serverPort))

                pkt, _ = FSM_receptor(clientSocket)

                if pkt[0].decode() == "ERROR":
                    print(pkt[1].decode())
                elif pkt[0].decode() == "OK":
                    isConnected = True
                    newPort = int.from_bytes(pkt[1], byteorder='big')
                    serverPort = newPort # client will talk with server by new port
                    print("Você entrou na sala de chat")
                    t1 = threading.Thread(target=receive)
                    t1.start()
            else:    
                print("Você já está conectado")
            return
    # Exit chat session
    elif msg.startswith(":BYE"):
        FSM_transmissor([b"BYE"], clientSocket, (serverName, serverPort))

        pkt, _ = FSM_receptor(clientSocket)
     
        if pkt[0].decode() == "ERROR":
            print(pkt[1].decode())
        elif pkt[0].decode() == "OK":
            with isConnected_lock:
                isConnected = False
            serverPort = 12000 # client will talk with server by new port
            print("Você saiu da sala de chat")
    elif msg.startswith(":BAN"):
        loginBan = msg[5:] # Message format: ":BAN <login>"
        FSM_transmissor([b"BAN", loginBan.encode()], clientSocket, (serverName, serverPort))

        pkt, _ = FSM_receptor(clientSocket)

        if pkt[0].decode() == "ERROR":
            print(pkt[1].decode())
        elif pkt[0].decode() == "OK":
            print(f'Voto para banir {loginBan} computado.')
    elif msg.startswith(":LIST"):
        FSM_transmissor([b'LIST'], clientSocket, (serverName, serverPort))
        
        pkt, _ = FSM_receptor(clientSocket)

        msg = [i.decode() for i in pkt]
        msg = ''.join(msg)

        clientList: dict = json.loads(msg)

        print("Nome | IP:PORTA")
        for k,v in clientList.items():
            print(f"{k} : {v[0]}:{v[1]}")

    elif msg.startswith(":ADDF"):
        friendLogin = msg[6:]
        FSM_transmissor([b"ADDF", friendLogin.encode()], clientSocket, (serverName, serverPort))

        pkt, _ = FSM_receptor(clientSocket)

        if pkt[0].decode() == "ERROR":
            print("ERRO:", pkt[1].decode())
        elif pkt[0].decode() == "OK":
            print(f'{friendLogin} foi adicionado a sua lista de amigos.')
    elif msg.startswith(":RMVF"):
        friendLogin = msg[6:]
        FSM_transmissor([b"RMVF", friendLogin.encode()], clientSocket, (serverName, serverPort))

        pkt, _ = FSM_receptor(clientSocket)

        if pkt[0].decode() == "OK":
            print(f"Removido {friendLogin} da sua lista de amigos")
        elif pkt[0].decode() == "ERROR":
            print("ERROR: ",pkt[1].decode())
    elif msg.startswith(":FLIST"):
        FSM_transmissor([b"FLIST"], clientSocket, (serverName, serverPort))

        pkt, _ = FSM_receptor(clientSocket)

        msg = [i.decode() for i in pkt]
        msg = ''.join(msg)

        clientList = json.loads(msg)

        print("Amigos")
        for i in clientList:
            print(i)

    else:
        if msg != "":
            splitedMessage = splitMessage(msg)
            FSM_transmissor(splitedMessage, clientSocket, (serverName, serverPort))


    return

def receive():
    global isConnected
    global login
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', serverPort-1))
    
    while True:
        with isConnected_lock:
            isConnectedCopy = isConnected
            
        if isConnectedCopy:
            pkt, _  = FSM_receptor(clientSocket)
            msg = [i.decode() for i in pkt]
            msg = ''.join(msg)
            if msg.startswith(f"{login} foi banido."):
                print("Voce foi banido do chat.")
                isConnected = False
                os._exit(0) # Ends the program
            else:
                print(msg)
        else:
            return

if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    while True:
        send(clientSocket)
