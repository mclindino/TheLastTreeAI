import Biblioteca as bot
import urllib.request
import sys
import time
from server import Game
import random

simulateGame = Game()
simulateGame.init_board(2)

auxSimulateGame = Game()
auxSimulateGame.init_board(2)

auxSimulateGame_2 = Game()
auxSimulateGame_2.init_board(2)

if len(sys.argv) == 1:
    print('Especificar numero do jogador 0 ou 1')
    quit()

host = 'http://localhost:8080'
player = int(sys.argv[1])
done = False

while not done:
    turn = int(urllib.request.urlopen('%s/jogador' % host).read())

    if turn == -1:
        print('I lose.')
        done = True
    
    if turn == player:
        if turn == 1:
            opponent = 0
        else:
            opponent = 1
        
        moviments = eval(urllib.request.urlopen('%s/movimentos?player=%d' % (host,player)).read())
        goal = eval(urllib.request.urlopen('%s/goals?player=%s' % (host, player)).read())

        print('\n\nCalculando Minimax...')
        minimax = bot.tree((0,0,0))

        i = 0
        for possibleMoviments in moviments:
            auxSimulateGame = simulateGame

            rule = int(possibleMoviments[0])
            animal = int(possibleMoviments[1])
            land = int(possibleMoviments[2])

            minimax.setChildren([(rule, animal, land)] )
            
            auxSimulateGame.make_move(opponent, rule, animal, land)

            auxMinimax = minimax.getChildren()[i]
            opponentMoviments = auxSimulateGame.get_available_moves(opponent)

            k = 0
            for possibleOpponentMoviments in opponentMoviments:

                auxSimulateGame_2 = auxSimulateGame

                rule = int(possibleOpponentMoviments[0])
                animal = int(possibleOpponentMoviments[1])
                land = int(possibleOpponentMoviments[2])

                auxMinimax.setChildren([(rule, animal, land)])

                auxSimulateGame_2.make_move(player, rule, animal, land)

                #print('Movimento: {} \t Arvore: {}'.format(possibleOpponentMoviments, auxMinimax.getChildren()[k].getMoviment()))
                auxMinimax_2 = auxMinimax.getChildren()[k]

                playerMoviments = auxSimulateGame_2.get_available_moves(player)

                for possiblePlayerMoviments in playerMoviments:

                    rule = int(possiblePlayerMoviments[0])
                    animal = int(possiblePlayerMoviments[1])
                    land = int(possiblePlayerMoviments[2])

                    auxMinimax_2.setChildren([(rule, animal, land)])

                k += 1
            i += 1
        
        # for children in minimax.getChildren():
        #     print('Moviment: {}\t Score: {}'.format(children.getMoviment(), children.getScore()))
        #     for grandchildren in children.getChildren():
        #         print('Moviment: {}\t Score: {}'.format(grandchildren.getMoviment(), grandchildren.getScore()))
        #         for grandgrandchildren in grandchildren.getChildren():
        #             print('Moviment: {}\t Score: {}'.format(grandgrandchildren.getMoviment(), grandgrandchildren.getScore()))
        
        opponentMoves = eval(urllib.request.urlopen('%s/ultima_jogada' % host).read())
        simulateGame.make_move(opponent, int(opponentMoves[0]), int(opponentMoves[1]), int(opponentMoves[2]))
        bot.calculateMinimax(minimax, simulateGame, goal)

        best = minimax.bestScore()
        print('Goal: ' + str(goal))
        print('Best Move: ' + str(best))

        resp = urllib.request.urlopen("%s/move?player=%d&rule=%d&animal=%d&land=%d" % (host,player,best[0],best[1],best[2]))
        simulateGame.make_move(player, int(best[0]), int(best[1]), int(best[2]))
        msg = eval(resp.read())
        
        if msg[0]==0:
            print("I win")
            done = True
        if msg[0]<0:
            raise Exception(msg[1])
    
    time.sleep(1)



