from socket import *
from enum import Enum

class receptor_States(Enum):
    Wait_0 = 0
    Wait_1 = 1

class transmissor_States(Enum):
    Wait_0_above = 0
    Wait_0_ACK = 1
    Wait_1_above = 2
    Wait_1_ACK = 3

class Packets:
    def __init__(self, data, seq_number):
        self.data = data
        self.seq_number = seq_number


def FSM_receptor(filename, socket, address):
    state = receptor_States.Wait_0
    data = []

    while True:
        match state:
            case receptor_States.Wait_0:
                socket.settimeout(5)

                try:
                    p:Packets = socket.recvfrom(1024)
                except socket.timeout:
                    socket.settimeout(None)
                    return data

                socket.settimeout(None)

                # R0: Wait for 0 from below -> Wait for 1 from below
                if p.seq_number == 0: 
                    data.append(p.data)
                    send_p = Packets(seq_number=0, data= b"ACK")
                    socket.sendto(send_p, address)
                    state = receptor_States.Wait_1
                # R3: Wait for 0 from below -> Wait for 0 from below
                else:
                    send_p = Packets(seq_number=1, data= b"ACK")
                    socket.sendto(send_p, address)
                    state = receptor_States.Wait_0
                
            case receptor_States.Wait_1:
                socket.settimeout(5)

                try:
                    p:Packets = socket.recvfrom(1024)
                except socket.timeout:
                    socket.settimeout(None)
                    return data

                socket.settimeout(None)

                # R2: Wait for 1 from below -> Wait for 0 from below
                if p.seq_number == 1:
                    data.append(p.data)
                    send_p = Packets(seq_number=1, data= b"ACK")
                    socket.sendto(send_p, address)
                    state = receptor_States.Wait_0
                # R1: Wait for 1 from below -> Wait for 1 from below
                else:
                    send_p = Packets(seq_number=0, data= b"ACK")
                    socket.sendto(send_p, address)
                    state = receptor_States.Wait_1


def FSM_transmissor(fileName, socket, address):
    state = transmissor_States.Wait_0_above
    p:Packets
    
    with open(f'./arquivos_para_enviar/{fileName}', 'rb') as f:
        while True:
            match state:
                case transmissor_States.Wait_0_above:
                    # S0: Wait for call 0 from above -> Wait for ACK0
                    p = Packets(data=f.read(1020),seq_number=0)
                    socket.sendto(p, address)
                    socket.settimeout(1)
                    state = transmissor_States.Wait_0_ACK

                case transmissor_States.Wait_0_ACK:
                    # S3: Wait for ACK0 -> Wait for call 1 from above
                    try:
                        rcv_p:Packets = socket.recvfrom(1024)
                        
                        if rcv_p.seq_number == 0:
                            socket.settimeout(None)
                            state = transmissor_States.Wait_1_above
                    # S2: Wait for ACK0 -> Wait for ACK0
                    except socket.timeout: 
                        socket.sendto(p, address)
                        socket.settimeout(1)
                        state = transmissor_States.Wait_0_ACK

                case transmissor_States.Wait_1_above:
                    # S5: Wait for call 1 from above -> Wait for ACK1
                    p = Packets(f.read(1020),1)
                    socket.sendto(p, address)
                    socket.settimeout(1)
                    state = transmissor_States.Wait_1_ACK

                case transmissor_States.Wait_1_ACK:
                    # S8: Wait for ACK1 -> Wait for call 0 from above 
                    try:
                        rcv_p:Packets = socket.recvfrom(1024)
                        
                        if rcv_p.seq_number == 1:
                            socket.settimeout(None)
                            state = transmissor_States.Wait_0_above
                    # S7: Wait for ACK1 -> Wait for ACK1
                    except socket.timeout: 
                        socket.sendto(p, address)
                        socket.settimeout(1)
                        state = transmissor_States.Wait_1_ACK