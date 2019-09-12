Um motor, servidor, cliente e visualizador para jogar The Last Tree feito em Python 3.

## Requerimentos
* Python 3
* Flask
* Flask-SocketIO

## Instalando Requisitos
pip install -r requirements.txt

## Executando

```
./python server.py
```

Use um navegador para acessar o endereço `http://localhost:8080/visualizador.html`. (ou `http://0.0.0.0:8080/`)

## Cliente

Um cliente que faz jogadas aleatórias está disponível (`random_client.py`). Para utilizá-lo, rode o servidor e execute o cliente passando como parâmetro o número do jogador (0 ou 1). Pode-se rodar dois clientes simultaneamente, cada um com um número de jogador.

## API

A API ainda está em desenvolvimento. Estão disponíveis funcionalidades básicas, que são acessadas por http.

* `/jogador`. Retorna o número do jogador de quem é a vez de jogar. Retorna -1 se o jogo acabou e o oponente venceu.
* `/tabuleiro`. Retorna o estado atual do tabuleiro, na forma de tupla de listas: animais e terrenos, onde cada animal tem um atributo land que indica onde ele está e um fruits que indica seu número de frutas; e cada terreno tem três atributos para indicar as quantidades de sementes, plantas e árvores, respectivamente, seeds, plants e trees.
* `/move?player=P&rule=R&animal=A&land=L`. Aplica a regra R no animal A e terreno L. Para a definição do match o animal é prioritário, se tiver terrenos que podem ser inferidos pela localização do animal, eles serão. O terreno L é para quando é necessário definir um lugar específico além do lugar onde o animal está (como em mover, especifica-se o animal e o lugar para onde ir). Retorna uma tupla `(erro, msg)`. Se `erro<0`, `msg` conterá o erro ocorrido. Se `erro==0`, o movimento feito encerrou o jogo e o cliente venceu.
* `/reiniciar?numplayers=N`. Reinicia o jogo com N jogadores, limpando o tabuleiro.
* `/ultima_jogada`. Retorna a última jogada realizada no formato de tupla de inteiros representando, respectivamente regra, animal alvo e terreno alvo.
* `/movimentos?player=P`. Retorna uma lista de jogadas válidas (regra,animal,terreno) que o jogador P pode realizar.
* `/num_movimentos`. Retorna o número de movimentos realizados desde o início do jogo.