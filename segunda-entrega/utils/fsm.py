from socket import *
from enum import Enum
import os

class receptor_States(Enum):
    Wait_0 = 0
    Wait_1 = 1

class transmissor_States(Enum):
    Wait_0_above = 0
    Wait_0_ACK = 1
    Wait_1_above = 2
    Wait_1_ACK = 3

class Packets:
    def __init__(self, data, package, seq_number):
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
    i = 0
    p:Packets
    with open(f'./arquivos_para_enviar/{fileName}', 'rb') as f:
        while True:
            match state:
                case transmissor_States.Wait_0_above:
                    p = Packets(f.read(1020),0)
                    socket.sendto(p, address)
                    socket.settimeout(1)
                    state = transmissor_States.Wait_0_ACK

                case transmissor_States.Wait_0_ACK:
                    try:
                        rcv_p = socket.recvfrom(1024)
                        
                        if rcv_p.seq_number == 0:
                            socket.settimeout(None)
                            state = transmissor_States.Wait_1_above
                    except socket.timeout: 
                        socket.sendto(p, address)
                        socket.settimeout(1)
                        state = transmissor_States.Wait_0_ACK

                case transmissor_States.Wait_1_above:
                    p = Packets(f.read(1020),1)
                    socket.sendto(p, address)
                    socket.settimeout(1)
                    state = transmissor_States.Wait_1_ACK

                case transmissor_States.Wait_1_ACK:
                    try:
                        rcv_p = socket.recvfrom(1024)
                        
                        if rcv_p.seq_number == 1:
                            socket.settimeout(None)
                            state = transmissor_States.Wait_0_above
                    except socket.timeout: 
                        socket.sendto(p, address)
                        socket.settimeout(1)
                        state = transmissor_States.Wait_1_ACK

export