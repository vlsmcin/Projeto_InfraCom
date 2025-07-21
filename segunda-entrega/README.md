## Objetivo

(3,5 pontos) Simulação de transferência confiável, segundo o canal de transmissão confiável RDT3.0, apresentado na disciplina e presente no Kurose, utilizando-se do código resultado da etapa anterior (envio de arquivos de tipos diferentes, entrega e devolução dos mesmos). A cada passo executado do algoritmo, em tempo de execução, deve ser printado na linha de comando, de modo a se ter compreensão do que está acontecendo. Para o teste do algoritmo, deve ser simulado um gerador de perdas de pacotes aleatórios, ocasionando timeout no transmissor para tais pacotes, com o intuito de demonstrar a eficiência do RDT3.0 implementado.

A implementação deverá ser realizada conforme os requisitos a seguir:

- O socket UDP de cada cliente e do servidor deverá contar com transmissão confiável, implementada em camada de aplicação segundo o RDT3.0 que consta no livro “Redes de Computadores e a Internet” do Kurose.

- Obs.: O RDT3.0 apresentado pelo Kurose utiliza um checksum. Entretanto, para esse projeto não é necessário a implementação do checksum, pois o UDP já realiza essa função (e antes do UDP também há um checksum na camada de enlace).


#### Instruções de execução

- Utilizar dois terminais, um para o cliente e outro para o servidor
- Inicializar primeiro o servidor seguindo os passos:
    - Navegar para o diretório servidor -> `cd servidor`
    - Executar (No linux, trocar python por python3 -> `python server.py`
- No terminal do cliente:
    - Navegar para o diretório cliente -> `cd cliente`
    - Caso queira adicionar um arquivo para mandar, fazer upload na pasta arquivos_para_enviar
    - Para escolher o arquivo a ser enviado, alterar a linha 10 do arquivo client.py, especificando a string com nome do arquivo, que está sendo atribuida a variável filename
    - Executar (No linux, trocar python por python3) -> `python client.py`
 
#### Integrantes

- Daniel Silvestre de França e Souza
- João Pedro Barbosa Marins
- Marcelo Arcoverde Neves Britto de Rezende
- Rafael Paz Fernandes
- Vinícius Lima Sá de Melo
