
import urllib.request
import sys
import time
from server import Game
import random

simulated_game = Game()
simulated_game.init_board(2)

def minimax2_0(tree, objetivo):
    for children_uno in tree.getChildren():
        _max = -10000
        
        if(len(children_uno.getChildren()) == 0):
            return 
        
        for children_duno in children_uno.getChildren():
            _min = 10000

            if(len(children_duno.getChildren()) == 0):
                return 

            for children_trino in children_duno.getChildren():
                children_trino.setScore(avaliation(objetivo, children_trino.getValue()))
                if children_trino.getScore() < _min:
                    _min = children_trino.getScore()
            children_duno.setScore(_min)
            if children_duno.getScore() > _max:
                _max = children_duno.getScore()
        children_uno.setScore(_max)


class tree:
    def __init__(self, value):
        self.score = 2
        self.value = value
        self.children = []

    def getValue(self):
        return self.value
    
    def getChildren(self):
        return self.children
    
    def setChildren(self, moviments):
        for i in range(len(moviments)):
            self.children.append(tree(moviments[i]))

    def setScore(self, score):
        self.score = score
    
    def getScore(self):
        return self.score

def avaliation(objetivo, movimento):
    rule = movimento[0]
    animal = movimento[1]
    land = movimento[2]

    score = 0

    if objetivo == 12:
        quantity = simulated_game.lands[land].trees
        if simulated_game.lands[land].trees > 0:
            if simulated_game.lands[land].plants == quantity:
                if simulated_game.lands[land].seeds == quantity:
                    if rule == 1:
                        score += 5
                    else:
                        score += 2
                else:
                    if rule == 2:
                        score += 4
                    else:
                        score += 1
            else:
                if rule == 3:
                    score += 3
                elif rule == 2:
                    score += 2
                else:
                    score += 1
        else:
            score += 1

    elif objetivo == 14:
        quantityTrees = simulated_game.lands[land].trees
        quantityFruits = simulated_game.animals[animal].fruits
        if quantityTrees == 0:
            score += 2
        if quantityFruits == 0:
            score += 2
        if simulated_game.lands[land - 1].trees:
            if simulated_game.lands[land + 1].trees:
                if simulated_game.lands[land - 1].trees == simulated_game.lands[land + 1].trees:
                    score += 3
        if (rule != 5) or (rule != 1):
            score += 1

    elif objetivo == 16:
        currentFruits = simulated_game.animals[animal].fruits
        if rule == 1:
            for animal1 in simulated_game.animals:
                if (currentFruits + 1) != animal1.fruits:
                    score += 2
                else:
                    score += 1

    elif objetivo == 17:
        trees = simulated_game.lands[land].trees
        if trees >= 4:
            score += 3
        for animal1 in simulated_game.animals:
            if land == animal1.land:
                score += 2
    
    return score
        
if len(sys.argv)==1:
    print("Voce deve especificar o numero do jogador (0 ou 1)\n\nExemplo:    ./random_client.py 0")
    quit()

# Alterar se utilizar outro host
host = "http://localhost:8080"

player = int(sys.argv[1])

done = False
while not done:
    # Pergunta quem eh o jogador
    resp = urllib.request.urlopen("%s/jogador" % host)
    player_turn = int(resp.read())

    # Se jogador == -1, o jogo acabou e o cliente perdeu
    if player_turn==-1:
        print("I lose.")
        done = True

    # Se for a vez do jogador
    if player_turn==player:
        if player_turn == 1:
            opponent = 0 
        else:
            opponent = 1
        megaTree = tree((0,0,0))

        # Pega os movimentos possiveis
        resp = urllib.request.urlopen("%s/movimentos?player=%d" % (host,player))
        movimentos = eval(resp.read())

        objetivo = eval(urllib.request.urlopen('%s/goals?player=%s' % (host, player)).read())
        megaTree.setChildren(movimentos)

        for possible_moviments in megaTree.getChildren():
            rule = int(possible_moviments.value[0])
            animal = int(possible_moviments.value[1])
            land = int(possible_moviments.value[2])
            simulated_game.make_move(player_turn, rule, animal, land)
            movimentos = simulated_game.get_available_moves(opponent)
            
            if(len(movimentos) == 0):
                break

            possible_moviments.setChildren(movimentos)

            for possible_moviments_le_two in possible_moviments.getChildren():
                rule = int(possible_moviments_le_two.value[0])
                animal = int(possible_moviments_le_two.value[1])
                land = int(possible_moviments_le_two.value[2])
                simulated_game.make_move(player_turn, rule, animal, land)
                
                movimentos = simulated_game.get_available_moves(player_turn)
                
                if(len(movimentos) == 0):
                    break
                
                possible_moviments_le_two.setChildren(movimentos)

        minimax2_0(megaTree, objetivo)

        melhor = -1
        for elemento in megaTree.getChildren():
            if elemento.getScore() > melhor:
                melhor = elemento.getScore()

        list_melhores = []
        for i in megaTree.getChildren():
            for j in i.getChildren():
                for k in j.getChildren():
                    if k.getScore() == melhor:
                        list_melhores.append(k.getValue())

        resp = urllib.request.urlopen("%s/movimentos?player=%d" % (host,player))
        movimentos = eval(resp.read())
        conseguiu = False
        while(not conseguiu):
            movimento_escolhido = list_melhores[random.randrange(0, (len(list_melhores)-1))]
            if movimento_escolhido in movimentos:
                conseguiu = True

        movimento = movimento_escolhido
        # Executa o movimento
        resp = urllib.request.urlopen("%s/move?player=%d&rule=%d&animal=%d&land=%d" % (host,player,movimento[0],movimento[1],movimento[2]))
        msg = eval(resp.read())
        
        # Se com o movimento o jogo acabou, o cliente venceu
        if msg[0]==0:
            print("I win")
            done = True
        if msg[0]<0:
            raise Exception(msg[1])
    
    # Descansa um pouco para nao inundar o servidor com requisicoes
    time.sleep(1)