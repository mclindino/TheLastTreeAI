import DiBotDre as bot

simulatedGame = bot.Game()
simulatedGame.init_board(2)

firstBoard = simulatedGame

decisionTree = bot.tree((0,0,0))
decisionTree.setChildren(moviments)

for possibleMovimentsOpponent in decisionTree.children:
    rule = int(possibleMovimentsOpponent.moviment[0])
    animal = int(possibleMovimentsOpponent.moviment[1])
    land = int(possibleMovimentsOpponent[2])

    simulatedGame.make_move(player, rule, animal, land)

    moviments = simulatedGame.get_available_moves(oppenent)

