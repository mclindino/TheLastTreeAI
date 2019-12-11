import DiBotDre as bot
import urllib.request
import sys
import time
from server import Game
import random

simulateGame = Game()
simulateGame.init_board(2)

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

        minimax = bot.tree((0,0,0))

        for possibleMoviments in moviments:
            rule = int(possibleMoviments[0])
            animal = int(possibleMoviments[1])
            land = int(possibleMoviments[2])

            minimax.setChildren([(rule, animal, land)] )
            #newAnimal, newLand = simulateGame.preview_move(player, rule, animal, land)
        
        for children in minimax.getChildren():
            print(children.getMoviment())
        
        opponentMoves = eval(urllib.request.urlopen('%s/ultima_jogada' % host).read())
        simulateGame.make_move(opponent, int(opponentMoves[0]), int(opponentMoves[1]), int(opponentMoves[2]))
        bot.calculateMinimax(minimax, simulateGame, goal)

        best = minimax.bestScore()
        print('Goal: ' + str(goal))
        print('Best Move: ' + str(best))

        resp = urllib.request.urlopen("%s/move?player=%d&rule=%d&animal=%d&land=%d" % (host,player,best[0],best[1],best[2]))
        msg = eval(resp.read())
        
        if msg[0]==0:
            print("I win")
            done = True
        if msg[0]<0:
            raise Exception(msg[1])
    
    time.sleep(1)



