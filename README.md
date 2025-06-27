## Objetivo

(2,0 pontos) Implementação de comunicação UDP utilizando a biblioteca Socket na linguagem Python, com envio e devolução de arquivo (o arquivo deve ser enviado pelo cliente, armazenado no servidor e devolvido ao cliente) em pacotes de até 1024 bytes (buffer_size). Não é necessária a implementação de transferência confiável nessa etapa, somente na etapa 2.

- Nessa entrega se deve implementar o envio e devolução de arquivos, reforçando que o envio de strings não é suficiente. Sugerimos que testem o programa para ao menos dois tipos de arquivos, como por exemplo um .txt e uma imagem. 
- É necessário a alteração do nome do arquivo antes da devolução ao cliente para demonstrar o funcionamento correto do código.

#### Requisitos do vídeo dela

- Estabelecer conexão
- Mandar arquivos de formatos diferentes (txt, mp4, png)
- Ter um diretório com os dados a serem enviados (cliente)
- Servidor deve guardar os dados recebidos em um folder com nome diferente
- Servidor armazena e depois reenvia para o cliente que também armazenará com outro nome
- Mandar o projeto no classroom compactado, deixar no github mas mandar compactado
- Deixar o projeto bem documentado e comentado, documentado pode ser pelo readme eu acredito
- Documentar também o que fez, a linha de raciocínio etc