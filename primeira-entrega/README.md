## Objetivo

(2,0 pontos) Implementação de comunicação UDP utilizando a biblioteca Socket na linguagem Python, com envio e devolução de arquivo (o arquivo deve ser enviado pelo cliente, armazenado no servidor e devolvido ao cliente) em pacotes de até 1024 bytes (buffer_size). Não é necessária a implementação de transferência confiável nessa etapa, somente na etapa 2.

- Nessa entrega se deve implementar o envio e devolução de arquivos, reforçando que o envio de strings não é suficiente. Sugerimos que testem o programa para ao menos dois tipos de arquivos, como por exemplo um .txt e uma imagem. 
- É necessário a alteração do nome do arquivo antes da devolução ao cliente para demonstrar o funcionamento correto do código.

#### Instruções de execução

- Utilizar dois terminais, um para o cliente e outro para o servidor
- Inicializar primeiro o servidor seguindo os passos:
    - Navegar para o diretório servidor -> `cd servidor`
    - Executar (No linux, trocar python por python3 -> `python server.py`
- No terminal do cliente:
    - Navegar para o diretório cliente -> `cd cliente`
    - Caso queira adicionar um arquivo para mandar, fazer upload na pasta arquivos_para_enviar
    - Para escolher o arquivo a ser enviado, alterar a linha 10 do arquivo client.py, especificando a string com nome do arquivo, que está sendo atribuindo a variável filename
    - Executar (No linux, trocar python por python3) -> `python client.py`
 
#### Integrantes

- Daniel Silvestre de França e Souza
- João Pedro Barbosa Marins
- Marcelo Arcoverde Neves Britto de Rezende
- Rafael Paz Fernandes
- Vinícius Lima Sá de Melo
