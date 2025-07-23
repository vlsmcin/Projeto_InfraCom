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


def FSM_receptor(socket):
    """
Implementação de uma Máquina de Estados Finitos (FSM) para um receptor de dados usando o protocolo stop-and-wait.
Esta função escuta pacotes recebidos em um socket, processa-os de acordo com o estado atual
e envia os reconhecimentos (ACKs) apropriados de volta ao transmissor. Alterna entre esperar por pacotes
com números de sequência 0 e 1, garantindo a transferência confiável dos dados ao lidar com retransmissões e pacotes duplicados.
Args:
socket (socket.socket): O socket UDP utilizado para receber e enviar pacotes.
address (tuple): O endereço do transmissor para o qual os ACKs são enviados.
Returns:
list: Uma lista contendo os payloads de dados recebidos em ordem.
    """
    global addr
    state = receptor_States.Wait_0
    data = []

    while True:
        match state:
            case receptor_States.Wait_0:
                socket.settimeout(5)

                try:
                    p: Packets
                    p, addr = socket.recvfrom(1024)
                except socket.timeout:
                    socket.settimeout(None)
                    return data, addr

                socket.settimeout(None)

                # R0: Wait for 0 from below -> Wait for 1 from below
                if p.seq_number == 0:
                    data.append(p.data)
                    send_p = Packets(seq_number=0, data=b"ACK")
                    socket.sendto(send_p, addr)
                    state = receptor_States.Wait_1
                # R3: Wait for 0 from below -> Wait for 0 from below
                else:
                    send_p = Packets(seq_number=1, data=b"ACK")
                    socket.sendto(send_p, addr)
                    state = receptor_States.Wait_0

            case receptor_States.Wait_1:
                socket.settimeout(5)

                try:
                    p: Packets
                    p, addr = socket.recvfrom(1024)
                except socket.timeout:
                    socket.settimeout(None)
                    return data

                socket.settimeout(None)

                # R2: Wait for 1 from below -> Wait for 0 from below
                if p.seq_number == 1:
                    data.append(p.data)
                    send_p = Packets(seq_number=1, data=b"ACK")
                    socket.sendto(send_p, addr)
                    state = receptor_States.Wait_0
                # R1: Wait for 1 from below -> Wait for 1 from below
                else:
                    send_p = Packets(seq_number=0, data=b"ACK")
                    socket.sendto(send_p, addr)
                    state = receptor_States.Wait_1


def FSM_transmissor(data, socket, address):
    """
Implementa a máquina de estados finitos (FSM) para o lado transmissor de um protocolo stop-and-wait.
Esta função lê um arquivo em modo binário e envia seu conteúdo por um socket utilizando um protocolo
simples de transferência confiável de dados. O protocolo alterna entre dois estados (números de sequência 0 e 1)
para garantir a entrega confiável, aguardando reconhecimentos (ACKs) do receptor antes de prosseguir.
Args:
fileName (str): Nome do arquivo a ser enviado, localizado no diretório './arquivos_para_enviar/'.
socket (socket.socket): O socket UDP utilizado para enviar e receber pacotes.
address (tuple): O endereço (IP, porta) do receptor.
Estados:
- Wait_0_above: Aguarda para enviar um pacote com número de sequência 0.
- Wait_0_ACK: Aguarda o ACK para o pacote com número de sequência 0.
- Wait_1_above: Aguarda para enviar um pacote com número de sequência 1.
- Wait_1_ACK: Aguarda o ACK para o pacote com número de sequência 1.
Comportamento:
- Lê partes do arquivo e as envia como pacotes com números de sequência alternados.
- Aguarda o ACK correspondente para cada pacote antes de enviar o próximo.
- Retransmite o pacote caso o ACK não seja recebido dentro do período de timeout.
- Continua até que todo o arquivo seja enviado.
Nota:
- A função assume a existência de uma classe 'Packets' e de um enum 'transmissor_States' ou similar.
- O socket deve estar configurado para comunicação UDP.
    """
    state = transmissor_States.Wait_0_above
    #p: Packets
    index = 0
    tam_max = len(data)

    while True:
        if index == tam_max: return
        match state:
            case transmissor_States.Wait_0_above:
                # S0: Wait for call 0 from above -> Wait for ACK0
                p = Packets(data=data[index], seq_number=0)
                socket.sendto(p, address)
                socket.settimeout(1)
                state = transmissor_States.Wait_0_ACK

            case transmissor_States.Wait_0_ACK:
                # S3: Wait for ACK0 -> Wait for call 1 from above
                try:
                    rcv_p: Packets = socket.recvfrom(1024)

                    if rcv_p.seq_number == 0:
                        socket.settimeout(None)
                        index += 1
                        state = transmissor_States.Wait_1_above
                # S2: Wait for ACK0 -> Wait for ACK0
                except socket.timeout:
                    p = Packets(data=data[index], seq_number=0)
                    socket.sendto(p, address)
                    socket.settimeout(1)
                    state = transmissor_States.Wait_0_ACK

            case transmissor_States.Wait_1_above:
                # S5: Wait for call 1 from above -> Wait for ACK1
                p = Packets(data[index], 1)
                socket.sendto(p, address)
                socket.settimeout(1)
                state = transmissor_States.Wait_1_ACK

            case transmissor_States.Wait_1_ACK:
                # S8: Wait for ACK1 -> Wait for call 0 from above
                try:
                    rcv_p: Packets = socket.recvfrom(1024)

                    if rcv_p.seq_number == 1:
                        socket.settimeout(None)
                        index += 1
                        state = transmissor_States.Wait_0_above
                # S7: Wait for ACK1 -> Wait for ACK1
                except socket.timeout:
                    p = Packets(data=data[index], seq_number=1)
                    socket.sendto(p, address)
                    socket.settimeout(1)
                    state = transmissor_States.Wait_1_ACK
