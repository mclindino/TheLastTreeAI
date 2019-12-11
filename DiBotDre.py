import random

def heuristics(board, goal, moviment):
    rule = int(moviment[0])
    animal = int(moviment[1])
    land = int(moviment[2])
    score = 0

    if goal == 12:
        quantity = board.lands[land].trees
        if quantity > 0:
            if board.lands[land].plants == quantity:
                if board.lands[land].seeds == quantity:
                    if board.animals[animal].fruits > quantity:
                        if rule == 5:
                            score += 50
                    else:
                        if rule == 1:
                            score += 50
                if board.lands[land].seeds < quantity:
                    if board.animals[animal].fruits > 0:
                        if rule == 2:
                            score += 30
                    else:
                        if rule == 1:
                            score += 20
                else:
                    if rule == 3:
                        score += 10
                
                if rule == 0:
                    score += 5

            elif board.lands[land].plants < quantity:
                if board.lands[land].seeds > 0:
                    if rule == 3:
                        score += 30
                if board.animals[animal].fruits > 0:
                    if rule == 2:
                        score += 20
                if rule == 0:
                    score += 5
            else:
                if rule == 4:
                    score += 30
            
        else:
            if board.lands[land].plants > 0:
                if rule == 4:
                    score += 30
            if board.lands[land].seeds > 0:
                if rule == 3:
                    score += 20
            if board.animals[animal].fruits > 0:
                if rule == 2:
                    score += 10
            if rule == 0:
                score += 5
    
    elif goal == 14:
        quantityTrees = board.lands[land].trees
        quantityFruits = board.animals[animal].fruits
        if quantityTrees == 0:
            score += 20
        if quantityFruits == 0:
            score += 20
        if board.lands[land - 1].trees:
            if board.lands[land + 1].trees:
                if board.lands[land - 1].trees == board.lands[land + 1].trees:
                    score += 30
        if (rule != 5) or (rule != 1):
            score += 10

    elif goal == 16:
        currentFruit = board.animals[animal].fruits
        if currentFruit > 0:
            for animals in board.animals:
                if currentFruit == animals.fruits:
                    if (currentFruit + 1) == board.animals[animal].fruits:
                        if rule == 5:
                            score += 50
                        else:
                            score += 10
                    else:
                        if rule == 1:
                            score += 50
                        else:
                            score += 10
                else:
                    if (rule != 5) or (rule != 1):
                        score += 10
        else:
            if rule == 1:
                score += 50
            else:
                score += 10
    
    elif goal == 17:
        quantityTrees = 0
        i = 0
        for nTrees in board.lands:
            if nTrees.trees > quantityTrees:
                quantityTrees = nTrees.trees
                bestLand = i
            i += 1
        if board.lands[bestLand].trees >= 4:
            if rule == 0:
                score += 100
            else:
                score += 10
        else:
            if land == bestLand:
                if rule > 0 and rule < 5:
                    score += 20
                else:
                    score += 5
            else:
                if rule < 5:
                    score += 10

    return score

class tree:
    def __init__(self, value):
        self.score = 0
        self.moviment = value
        self.children = []

    def getMoviment(self):
        return self.moviment

    def setChildren(self, moviments):
        for i in range(len(moviments)):
            self.children.append(tree(moviments[i]))
    
    def bestScore(self):
        bestValue = 0
        bestMoviment = []
        for moviments in self.children:
            if moviments.score > bestValue:
                #bestMoviment = moviments.getMoviment()
                bestValue = moviments.score
        
        for moviments in self.children:
            if moviments.score == bestValue:
                bestMoviment.append(moviments.getMoviment())
        
        return bestMoviment[random.randrange(0, (len(bestMoviment)-1))]

    def getChildren(self):
        return self.children

    def setScore(self, score):
        self.score = score

def calculateMinimax(tree, board, goal):
    for moviments in tree.getChildren():
        moviments.setScore(heuristics(board, goal, moviments.moviment))
#def completeTree(moviment):