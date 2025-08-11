## Objetivo
### Chat de sala única com paradigma cliente-servidor

(4,5 pontos) Implementação do chat, exibido por linha de comando. Apesar do reaproveitamento das etapas anteriores, o histórico da execução dos algoritmos não deve ser exibido nessa etapa, apenas a aplicação como descrita nesse documento e mantendo o uso do rdt3.0. 


#### Instruções de execução

- Utilizar dois terminais, um para o cliente e outro para o servidor
- Inicializar primeiro o servidor seguindo os passos:
    - Executar (No linux, trocar python por python3) -> `python server.py`
- No terminal do cliente:
    - Executar (No linux, trocar python por python3) -> `python client.py`

### Comandos do Chat

- Para entrar na sala ao abrir o cliente
```
:HI <login>
```

- Para sair na sala
```
:BYE
```

- Para visualizar a lista de clientes no Chat
```
:LIST
```

- Para votar no banimento de algum cliente no chat
```
:BAN <login de quem você quer que seja banido>
```

- Para adicionar algum cliente a sua lista de amigos
```
:ADDF <login>
```

- Para remover algum cliente da sua lista de amigos
```
:RMVF <login>
```

- Para visualizar sua lista de amigos
```
:FLIST
```

#### Comandos Úteis

Caso esteja recebendo um erro indicando que a porta já está ocupada, você pode utilizar os seguintes comandos no Linux para identificar e liberar a porta:

```bash
sudo lsof -i :12000
```

Este comando listará os processos que estão escutando ou usando a porta especificada, mostrando o PID do programa.

```bash
kill [PID]
```

Substitua [PID] pelo número do processo que você obteve no comando anterior.

#### Integrantes

- Daniel Silvestre de França e Souza
- João Pedro Barbosa Marins
- Marcelo Arcoverde Neves Britto de Rezende
- Rafael Paz Fernandes
- Vinícius Lima Sá de Melo
