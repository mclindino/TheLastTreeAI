# -*- coding: utf-8 -*-
import random
import copy
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret!'
# app.config['DEBUG'] = True

socketio = SocketIO(app)

class Animal:
	land = 2
	fruits = 0

class Land:
	def __init__(self,trees):
		self.seeds = 0
		self.plants = 0
		self.trees = trees

class Game:
	NUMGOALS = 8
	NUMPLAYERS = 2
	animals = []
	lands = []
	goals = []
	player = 0
	ended = False
	movements = 0
	last_rule = 0
	last_animal = 0
	last_land = 0
	previous_land = 0

    # Initialize the board.
	def init_board(self,numplayers):
		self.NUMGOALS = 8
		self.NUMPLAYERS = numplayers
		self.animals = [Animal(),Animal(),Animal(),Animal()]
		self.lands = [Land(0),Land(0),Land(1),Land(0),Land(0)]
		availableGoals = []
		for g in range(self.NUMGOALS):
			availableGoals.append(10+g)
		random.shuffle(availableGoals)
		self.goals = []
		self.goals.extend(availableGoals[0:self.NUMPLAYERS])
		self.player = 0
		self.ended = False
		self.movements = 0
		self.last_rule = 0
		self.last_animal = 0
		self.last_land = 0
		self.previous_land = 0

	def get_info(self, info, num):
		if infoID=='land': #which land the animal[num] is at?
			return self.animals[num].land
		elif infoID=='fruit': #how much fruits does the animal[num] have?
			return self.animals[num].fruits
		elif infoID=='seed': #how much seeds at land[num]?
			return self.lands[num].seeds
		elif infoID=='plant': #how much plants at land[num]?
			return self.lands[num].plants
		elif infoID=='tree': #how much trees at land[num]?
			return self.lands[num].trees
		else:
			return -1
	
	def preview_board(self, modifications):
		newAnimals = copy.deepcopy(self.animals)
		newLands = copy.deepcopy(self.lands)
		for modification in (modifications):
			if modification[0]=='land':
				newAnimals[modification[1]].land = modification[2]
			elif modification[0]=='fruit':
				newAnimals[modification[1]].fruits = modification[2]
			elif modification[0]=='seed':
				newLands[modification[1]].seeds = modification[2]
			elif modification[0]=='plant':
				newLands[modification[1]].plants = modification[2]
			elif modification[0]=='tree':
				newLands[modification[1]].trees = modification[2]
			else:
				return None
		return (newAnimals,newLands)
	
	def preview_move(self, player, rule, animal, land):
		if rule == 0: #move (displace an animal to an adjacent land)
			if self.animals[animal].land+1 == land or self.animals[animal].land-1 == land:
				if self.last_rule==0 and self.last_animal==animal and self.last_land==self.animals[animal].land and self.previous_land==land:
					return None #(-5, "Can't reverse last action")
				else:
					return self.preview_board([('land',animal,land)])
			else:
				return None #(-3.0, "Invalid move, input land is not adjacent to the land of input animal")
		elif rule == 1: #gather (create a fruit picking it from a tree)
			if self.lands[self.animals[animal].land].trees > 0:
				return self.preview_board([('fruit',animal,self.animals[animal].fruits+1)])
			else:			
				return None #(-3.1, "Invalid move, not enough trees")
		elif rule == 2: #eat (destroy a fruit and spit out its seed)
			if self.animals[animal].fruits > 0:
				return self.preview_board([('fruit',animal,self.animals[animal].fruits-1),('seed',self.animals[animal].land,self.lands[self.animals[animal].land].seeds+1)])
			else:
				return None # (-3.2, "Invalid move,  not enough fruits")
		elif rule == 3: #plant (create a plant by planting a seed)
			if self.lands[self.animals[animal].land].seeds > 0:
				return self.preview_board([('seed',self.animals[animal].land,self.lands[self.animals[animal].land].seeds-1),('plant',self.animals[animal].land,self.lands[self.animals[animal].land].plants+1)])
			else:
				return None # (-3.3, "Invalid move,  not enough seeds")
		elif rule == 4: #fertilize (create a tree by fertilizing a plant with a fruit)
			if self.lands[self.animals[animal].land].plants > 0:
				if self.animals[animal].fruits > 0:
					return self.preview_board([('fruit',animal,self.animals[animal].fruits-1),('plant',self.animals[animal].land,self.lands[self.animals[animal].land].plants-1),('tree',self.animals[animal].land,self.lands[self.animals[animal].land].trees+1)])
				else:
					return None # (-3.2, "Invalid move,  not enough fruits")
			else:
				return None # (-3.4, "Invalid move,  not enough plants")
		elif rule == 5: #devour (destroy 2 fruits)
			if self.animals[animal].fruits > 1:
				return self.preview_board([('fruit',animal,self.animals[animal].fruits-2)])
			else:
				return None # (-3.2, "Invalid move, not enough fruits")
		elif rule == 10: #the fruit king (an animal with 5+ fruits is the only one with fruits)
			if self.goals[player] == rule:
				if self.animals[animal].fruits > 4:
					if self.animals[animal].fruits == self.animals[0].fruits+self.animals[1].fruits+self.animals[2].fruits+self.animals[3].fruits:
	            				return (self.animals,self.lands)
					else:
						return None # (-3.8, "Invalid move, too much fruits")
				else:
					return None # (-3.2, "Invalid move, not enough fruits")
			else:
				return None # (-4, "Not your goal")
		elif rule == 11: #grove symmetry (all self.lands have the same amount of trees)
			if self.goals[player] == rule:
				if self.lands[0].trees==self.lands[1].trees and self.lands[0].trees==self.lands[2].trees and self.lands[0].trees==self.lands[3].trees and self.lands[0].trees==self.lands[4].trees:
					return (self.animals,self.lands)
				else:
					return None # (-3.6, "Invalid move, all numbers should be equal")
			else:
				return None # (-4, "Not your goal")
		elif rule == 12: #ecosystem (the same amount (>0) of fruits, seeds, plants and trees in one place/animal)
			if self.goals[player] == rule:
				if self.animals[animal].fruits == self.lands[self.animals[animal].land].plants and self.animals[animal].fruits == self.lands[self.animals[animal].land].seeds and self.animals[animal].fruits == self.lands[self.animals[animal].land].trees:
					if self.animals[animal].fruits > 0:
	            				return (self.animals,self.lands)
					else:
						return None # (-3.2, "Invalid move, not enough fruits")
				else:
					return None # (-3.6, "Invalid move, all numbers should be equal")
			else:
				return None # (-4, "Not your goal")
		elif rule == 13: #orchard (all self.animals are in self.lands with as much trees as their fruits)
			if self.goals[player] == rule:
				if self.animals[0].fruits==self.lands[self.animals[0].land].trees and self.animals[1].fruits==self.lands[self.animals[1].land].trees and self.animals[2].fruits==self.lands[self.animals[2].land].trees and self.animals[3].fruits==self.lands[self.animals[3].land].trees:
	            			return (self.animals,self.lands)
				else:
					return None # (-3.6, "Invalid move, all numbers should be equal")
			else:
				return None # (-4, "Not your goal")
		elif rule == 14: #plant valley (an animal at a land with no plants that is between adjacent self.lands with the same amount of plants >0)
			if self.goals[player] == rule:
				if self.lands[self.animals[animal].land].plants == 0:
					if self.animals[animal].land > 0 and self.animals[animal].land < 4:
						if self.lands[self.animals[animal].land+1].plants > 0:
							if self.lands[self.animals[animal].land+1].plants==self.lands[self.animals[animal].land-1].plants:
	            						return (self.animals,self.lands)
							else:
								return None # (-3.6, "Invalid move, all numbers should be equal")
						else:
							return None # (-3.4, "Invalid move, not enough plants")
					else:
						return None # (-3.7, "Invalid move, not enough self.lands")
				else:
					return None # (-3.8, "Invalid move, too much fruits")
			else:
				return None # (-4, "Not your goal")
		elif rule == 15: #chicken farm (all self.lands have seeds)
			if self.goals[player] == rule:
				if self.lands[0].seeds > 0 and self.lands[1].seeds > 0 and self.lands[2].seeds > 0 and self.lands[3].seeds > 0 and self.lands[4].seeds > 0:
        	    			return (self.animals,self.lands)
				else:
					return None # (-3.3, "Invalid move, not enough seeds")
			else:
				return None # (-4, "Not your goal")
		elif rule == 16: #jungle hierarchy (all self.animals have different numbers of fruits)
			if self.goals[player] == rule:
				if self.animals[0].fruits != self.animals[1].fruits and self.animals[0].fruits != self.animals[2].fruits and self.animals[0].fruits != self.animals[3].fruits and self.animals[1].fruits != self.animals[2].fruits and self.animals[1].fruits != self.animals[3].fruits and self.animals[2].fruits != self.animals[3].fruits:
        	    			return (self.animals,self.lands)
				else:
					return None # (-3.9, "Invalid move, all numbers should be different")
			else:
				return None # (-4, "Not your goal")
		elif rule == 17: #treehouse party (all self.animals together at a land that has 4+ trees)
			if self.goals[player] == rule:
				if self.animals[0].land == self.animals[1].land and self.animals[0].land == self.animals[2].land and self.animals[0].land == self.animals[3].land:
					if self.lands[self.animals[0].land].trees > 4:
        	    				return (self.animals,self.lands)
					else:
						return None # (-3.1, "Invalid move, not enough trees")
				else:
					return None # (-3.6, "Invalid move, all numbers should be equal")
			else:
				return None # (-4, "Not your goal")
		# Add self.goals here
		#elif rule == 18: #goal name (goal description)
		#	if self.goals[player] == rule:
		#		if goal condition:
		#			return (self.animals,self.lands)
		#		else:
		#			return None # (errorID, "Invalid move, error message")
		#	else:
		#		return None # (-4, "Not your goal")
		else:
			return None # (-4, "Invalid rule")
	
	
    # Returns a list of moves that would be successful at the current state of the board
	def get_available_moves(self,player):
		moves = []
		for animal in range(len(self.animals)):
			for land in range(len(self.lands)):
				for rule in range(6):
					if self.preview_move(player,rule,animal,land)!= None:
						moves.append((rule,animal,land))
				if self.preview_move(player,self.goals[player],animal,land)!=None:
					moves.append((self.goals[player],animal,land))
		return moves

    # Returns a list of all possible boards from the current
	def get_available_boards(self,player):
		boards = []
		for animal in range(len(self.animals)):
			for land in range(len(self.lands)):
				for rule in range(6):
					newboard = self.preview_move(player,rule,animal,land)
					if newboard != None:
						boards.append(newboard)
				winboard = self.preview_move(player,self.goals[player],animal,land)
				if winboard!=None:
					boards.append(winboard)
		return boards

	def take_turn(self):
		self.player = (self.player+1)%self.NUMPLAYERS
	        return self.player

	def setposition(self, animal, land):
		self.animals[animal].land = land
		socketio.emit('move', {'animal': '#animal-' + str(animal), 'land' : '#land-' + str(land) + '-animal-' + str(animal)}, namespace='/socket')

	def addfruit(self, animal, num):
		self.animals[animal].fruits += num
		socketio.emit('setnum', {'element': '#animal-' + str(animal) + '-fruits', 'num' : self.animals[animal].fruits}, namespace='/socket')

	def addseed(self, land, num):
		self.lands[land].seeds += num
		socketio.emit('setnum', {'element': '#land-' + str(land) + '-seeds', 'num' : self.lands[land].seeds}, namespace='/socket')

	def addplant(self, land, num):
		self.lands[land].plants += num
		socketio.emit('setnum', {'element': '#land-' + str(land) + '-plants', 'num' : self.lands[land].plants}, namespace='/socket')

	def addtree(self, land, num):
		self.lands[land].trees += num
		socketio.emit('setnum', {'element': '#land-' + str(land) + '-trees', 'num' : self.lands[land].trees}, namespace='/socket')

	def make_move(self, player, rule, animal, land):
	        if self.ended:
	            return (-1, "Game is over")

	        if player != self.player:
	            return (-2, "Not your turn")

	        if self.preview_move(player,rule,animal,land) == None:
	            return (-3, "Invalid move")

		if rule == 0: #move (displace an animal to an adjacent land)
			self.previous_land = land
			self.setposition(animal,land)
		elif rule == 1: #gather (create a fruit picking it from a tree)
			self.addfruit(animal,1)
		elif rule == 2: #eat (destroy a fruit and spit out its seed)
			self.addfruit(animal,-1)
			self.addseed(self.animals[animal].land,1)
		elif rule == 3: #plant (create a plant by planting a seed)
			self.addseed(self.animals[animal].land,-1)
			self.addplant(self.animals[animal].land,1)
		elif rule == 4: #fertilize (create a tree by fertilizing a plant with a fruit)
			self.addfruit(animal,-1)
			self.addplant(self.animals[animal].land,-1)
			self.addtree(self.animals[animal].land,1)
		elif rule == 5: #devour (destroy 2 fruits)
			self.addfruit(animal,-2)
		elif rule >= 10 and rule <= self.NUMGOALS+9: #self.goals
	            	self.ended = True
			self.player = -1
	            	return (0, "%d wins" % player)

	        self.last_rule = rule
	        self.last_animal = animal
	        self.last_land = land

	        self.movements += 1
		self.take_turn()

	        return (1, "Successful Move")


###### SERVER ######

game = Game()
game.init_board(2)


@app.route("/minhavez")
def minhavez():
	player = int(q['player'][0])
    
	if request.args.get('format') == "json":
		if game.player != player:
			return jsonify("-1")
		else:
			return jsonify("1")
	else:
		if game.player != player:
			return "-1"
		else:
			return "1"
    
@app.route("/jogador")
def jogador():
	if request.args.get('format') == "json":
		if game.ended:
			return jsonify("0")
		else:
			return jsonify(game.player)
	else:
		if game.ended:
			return "0"
		else:
			return str(game.player)


@app.route("/tabuleiro")
def tabuleiro():
	if request.args.get('format') == "json":
		return jsonify((game.animals,game.lands))
	else:
		return str((game.animals,game.lands))
        

@app.route("/movimentos")
def movimentos():
	player = int(request.args.get('player'))
	if request.args.get('format') == "json":
		return jsonify(game.get_available_moves(player))
	else:
		return str(game.get_available_moves(player))


@app.route("/num_movimentos")
def num_movimentos():
	if request.args.get('format') == "json":
		return jsonify(game.movements)
	else:
		return str(game.movements)


@app.route("/ultima_jogada")
def ultima_jogada():
	if request.args.get('format') == "json":
		return jsonify((game.last_rule, game.last_animal, game.last_land))
	else:
		return str((game.last_rule, game.last_animal, game.last_land))


@app.route("/reiniciar")
def reiniciar():
	numplayers = int(request.args.get('numplayers'))
	game.init_board(numplayers)

	if request.args.get('format') == "json":
        	return jsonify("reiniciado")
	else:
        	return "reiniciado"


@app.route("/move")
def move():
	rule = int(request.args.get('rule'))
	animal = int(request.args.get('animal'))
	land = int(request.args.get('land'))
	player = int(request.args.get('player'))
	r = game.make_move(player, rule, animal, land)
	
	socketio.emit('update', namespace='/socket')

	if request.args.get('format') == "json":
		return jsonify(r)
	else:
		return str(r)


@app.route("/")
def index():
	return render_template('visualizador.html')


@socketio.on('connect', namespace='/socket')
def socketConnected():
	# need visibility of the global thread object
	socketio.emit('update', namespace='/socket')
	print('Client connected')


PORT_NUMBER = 8080

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=PORT_NUMBER)
