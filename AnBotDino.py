import urllib.request
import sys
import time
from server import Game
from minimax import MiniMax

simulated_game = Game()
simulated_game.init_board(2)

class tree:
    def __init__(self, value):
        self.score = 0
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
    rule = movimento.value[0]
    animal = movimento.value[1]
    land = movimento.value[2]

    score = 0

    if objetivo == 10:
        # best_animal = animal[0]
        # for animal in animals:
        #     if animal.fruits > best_animal.fruits:
        #         best_animal = animal
        # if land[best_animal.land].tree >= 1:

        score += simulated_game.animals[animal].fruits * 2
        if simulated_game.lands[land].trees >= 1:
            score += 2
            if rule == 1:
                score += 2
            else:
                score += 1
        else:
            if rule == 4:
                score += 2
            else:
                score += 1
        
        return score
    
    elif objetivo == 11:
        if simulated_game.lands[land].trees > 0:
            if animal.fruits > 0:
                if rule == 0:
                    score += 2
                else:
                    score += 1
            else:
                if rule == 1:
                    score += 2
                else:
                    score += 1
        else:
            if rule != 5:
                score += rule / 2
        
        return score
    
    elif objetivo == 12:
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

        return score
    
    #elif objetivo == 13:

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

            possible_moviments.setChildren(movimentos)

            for possible_moviments_le_two in possible_moviments.getChildren():
                rule = int(possible_moviments_le_two.value[0])
                animal = int(possible_moviments_le_two.value[1])
                land = int(possible_moviments_le_two.value[2])
                simulated_game.make_move(player_turn, rule, animal, land)
                
                movimentos = simulated_game.get_available_moves(player_turn)
                possible_moviments_le_two.setChildren(movimentos)

                for possible_moviments_le_three in possible_moviments_le_two.getChildren():
                    possible_moviments_le_three.setScore(avaliation(objetivo, possible_moviments_le_three))
        
        minimax_try = MiniMax(megaTree)
        minimax_try.minimax(megaTree)
        # print(megaTree.value)
        # for i in megaTree.getChildren():
        #     print('\t' + str(i.value))
        #     for j in i.getChildren():
        #         print('\t\t' + str(j.value))
        #         for k in j.getChildren():
        #             print('\t\t\t' + str(k.value))

        # Escolhe um movimento aleatoriamente
        #movimento = random.choice(movimentos)
        
        # Executa o movimento
        #resp = urllib.request.urlopen("%s/move?player=%d&rule=%d&animal=%d&land=%d" % (host,player,movimento[0],movimento[1],movimento[2]))
        #msg = eval(resp.read())
        
        # Se com o movimento o jogo acabou, o cliente venceu
        if msg[0]==0:
            print("I win")
            done = True
        if msg[0]<0:
            raise Exception(msg[1])
    
    # Descansa um pouco para nao inundar o servidor com requisicoes
    time.sleep(1)