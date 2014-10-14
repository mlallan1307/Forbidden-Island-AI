
import random

NUM_PLAYERS = 1
TREASURES = ['The Earth Stone', 'The Statue of the Wind', 'The Crystal of Fire', 'The Ocean\'s Chalice']

"""
TODO:
 enforce hand limit
 implement adventurer type
 implement player init
 run game start and player start actions
"""

class Game_Board():
	"""
	tracks the locations of the 24 tiles and their status (dry, flooded, sunk)
	Includes a 'shuffle' method to generate a random layout for each game
	Includes a 'flip' method for flooding / shoring_up a tile
	includes a 'sink' method for removing a tile from the game
	A data structure  (I think it would be a dictionary in Python) for tile information:
	--ID (zero thru 23)
	--Name
	--Associated_Treasure (if any)
	--Associated_Adventure (if any)
	"""
	def __init__(self):
		self.board = [
			{name: 'Temple of the Moon', status: 'dry', players:[], treasure: 0},
			{name: 'Temple of the Sun',  status: 'dry', players:[], treasure: 0},
			{name: 'Whipering Garden',   status: 'dry', players:[], treasure: 1},
			{name: 'Howling Garden',     status: 'dry', players:[], treasure: 1},
			{name: 'Cave of Embers',     status: 'dry', players:[], treasure: 2},
			{name: 'Cave of Shadows',    status: 'dry', players:[], treasure: 2},
			{name: 'Coral Palace',       status: 'dry', players:[], treasure: 3},
			{name: 'Tidal Palace',       status: 'dry', players:[], treasure: 3},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]},
			{name: '', status: 'dry', players:[]}
		]
		self.board = random.shuffle(self.board)
		self.captured = {0: False, 1: False, 2: False, 3: False}
		self.boardMap = [
			['E','E','T','T','E','E'],
			['E','T','T','T','T','E'],
			['T','T','T','T','T','T'],
			['T','T','T','T','T','T'],
			['E','T','T','T','T','E'],
			['E','E','T','T','E','E'],
		]
		
		tileCount = 0
		for i, row in enumerate(self.boardMap):
			for j, col in enumerate(row):
				if col == 'T':
					self.boardMap[i][j] = tileCount
					self.board[tileCount].row = i
					self.board[tileCount].column = j
	
	
	def flip(self, tile):
		if self.board[tile].status == 'dry':
			self.board[tile].status == 'flooded'
		elif self.board[tile].status == 'flooded':
			self.board[tile].status == 'dry'
		else:
			raise Exception('Tile status not "dry" or "flooded"')
			
			
	def sink(self, tile):
		self.board[tile].status == 'sunk'
		
	def move_player(self, player, tileFrom, tileTo):
		self.board[tileFrom].players.remove(player)
		self.board[tileTo].players.append(player)

		
BOARD = Game_Board()
		
class Card_Deck():
	def check_reshuffle(self)
		tmpDeck = list(self.deck)
		tmpDiscard = list(self.discard)
		if len(self.deck) == 0:
			self.deck = random.shuffle(self.discard)
			self.discard = []


class Flood_Deck(Card_Deck):
	
	def __init__(self):
		self.discard = []
		self.deck = random.shuffle([n for n in range(23)])
	
	
	def draw(self):
		self.check_reshuffle()
		self.lastDraw = self.deck.pop()
		self.discard.append(self.lastDraw)
	
	
	def flood(self):
		self.draw()
		if BOARD.board[self.lastDraw].status == 'dry':
			BOARD.flip(self.lastDraw)
		else:
			BOARD.sink(self.lastDraw)
		
		
	def waters_rise(self):
		self.deck.extend(random.shuffle(self.discard))
		self.discard = []
	

class Treasure_Deck(Card_Deck):
	def __init__(self):
		self.discard = []
		self.deck = []
		for n in range(5):
			self.deck.append({type: 'Treasure', treasure: 0})
		for n in range(5):
			self.deck.append({type: 'Treasure', treasure: 1})
		for n in range(5):
			self.deck.append({type: 'Treasure', treasure: 2})
		for n in range(5):
			self.deck.append({type: 'Treasure', treasure: 3})
		for n in range(3):
			self.deck.append({type: 'Waters Rise!'})
		for n in range(3):
			self.deck.append({type: 'Special', action: 'Helicopter Lift'})
		for n in range(2):
			self.deck.append({type: 'Special', action: 'Sandbags'})
		self.deck = random.shuffle(self.deck)
	
	
	def draw(self):
		self.check_reshuffle()
		self.lastDraw = self.deck.pop()
		return self.lastDraw
		
	def discard(self, cards):
		for card in cards:
			self.discard.append(card)
	

class Player():
	"""
	Tracks Adventurer type and location of player on board and any treasures being carried
	Has method's for:
	--tracking treasure cards in hand
	--can_move (lists possible movement destinations, taking special movement abilities into account)
	--move
	--can_shore_up (lists underwater tiles that player can shore up from current location, or from a passed-in location)
	--shore_up
	--give_card (probably doesn't need a 'can' method, just some error checking in case the A.I tries something illegal)
	--capture_treasure (need 4 of a kind in hand and be on matching tile)
	--draw_card (checks for hand limit; may use a special card to free up space)
	--play_special_card (complex logic here)
	"""
	def __init__(self):
		global NUM_PLAYERS
		self.playerId = NUM_PLAYERS
		NUM_PLAYERS += 1
		self.hand = []
		self.onTile = 0 # need to assign based on adventurer
		
	
	def local_tiles(self):
		r = BOARD.board[self.onTile].row
		c = BOARD.board[self.onTile].column
		tiles = []
		if r > 0 and BOARD.boardMap[r-1][c] != 'E':
			tiles.append(BOARD.boardMap[r-1][c])
		if r < 5 and BOARD.boardMap[r+1][c] != 'E':
			tiles.append(BOARD.boardMap[r+1][c])
		if c > 0 and BOARD.boardMap[r][c-1] != 'E':
			tiles.append(BOARD.boardMap[r][c-1])
		if c < 5 and BOARD.boardMap[r][c+1] != 'E':
			tiles.append(BOARD.boardMap[r][c+1])
		return tiles
		
	def can_move(self):
		tiles = self.local_tiles()
		moves = []
		for tileNum in tiles:
			tile = BOARD.board[tileNum]
			if tile.status != 'sunk':
				moves.append(tileNum)
		return moves
		
		
	def move(self, tileTo):
		BOARD.move(self.playerId, self.onTile, self.tileTo)
		self.onTile = tileTo
	
	
	def can_shore_up(self):
		tiles = self.local_tiles()
		moves = []
		for tileNum in tiles:
			tile = BOARD.board[tileNum]
			if tile.status == 'flooded':
				moves.append(tileNum)
		return moves
		
		
	def shore_up(self, tile):
		BOARD.flip(tile)
		
		
	def give_card(self, player, card):
		if not card in player.hand:
			raise Exception('Error, player cannot give card that is not in their hand')
		player.hand.remove(card)
		self.hand.append(card)
		
		
	def capture_treasure(self, treasure):
		if BOARD.board[self.onTile].status == 'sunk':
			raise Exception('Error cannot capture treasure on sunk tile')
		if not 'treasure' in BOARD.board[self.onTile]:
			raise Exception('Error cannot capture treasure on a non-treasure tile')
		if not BOARD.board[self.onTile].treasure == treasure:
			raise Exception('Error cannot capture {} on this tile'.format(TREASURES[treasure]))
		numCards = 0
		for card in self.hand:
			if 'treasure' in card:
				if card.treasure == treasure
					numCards += 1
		if numCards < 4:
			raise Exception('Error not enough treasure cards')
			
		BOARD.captured[treasure] = True
		numCards = 4
		for card in self.hand:
			if numCards > 0 and 'treasure' in card and card.treasure == treasure:
				self.hand.remove(card)
				numCards -= 1
		
		
class Forbidden_Island():
  def __init__(self, num_players, difficulty):
    self.flood_deck = Flood_Deck()
    self.treasure_deck = Treasure_Deck()
    self.players = []
    for i in range(num_players):
      self.players.append(Player())
'''
Then when we play the game:
game = Forbidden_Island(4, 1)
game.player[0].player_special_card()
'''

if __name__ == '__main__':
		print 'hi'


"""
Classes:
***Game_Board()
tracks the locations of the 24 tiles and their status (dry, flooded, sunk)
Includes a 'shuffle' method to generate a random layout for each game
Includes a 'flip' method for flooding / shoring_up a tile
includes a 'sink' method for removing a tile from the game
A data structure  (I think it would be a dictionary in Python) for tile information:
--ID (zero thru 23)
--Name
--Associated_Treasure (if any)
--Associated_Adventure (if any)
####
We could build a Tile class and let the Game_Board track 24 Tile objects, but not sure which approach would be more complex


****Flood_Deck()
Contains the 24 flood cards
Each card is either:
-- in the deck (with a position)
-- in the discard pile
--- removed from the
Includes a 'shuffle' method for initial setup
Includes a 'draw' method for flipping a card (reshuffle deck if empty)
Includes a 'sink' method for removing that card if the associated tile is sunk
Includes a 'waters rise' method for shuffling the discard pile and placing it on top of the deck
####
Not exactly sure where to place the code for having players escape to safety (or lose the game) when their tile is sunk.  My initial guess is to have the Board drive the 'sink' action and tell the Flood_Deck to sink the matching card.

***Treasure_Deck()
Contains the 28 treasure cards
Each card is either:
-- in the deck (with a position)
-- in the discard pile
-- in a player's hand
Includes a 'shuffle' method for initial setup
Includes a 'draw' method for assigning the top card to a player (reshuffle if deck is empty)
Includes a 'give' method for moving the card from one player to another
includes a 'play' method for executing cards and placing them to discard.

***Player()
Tracks Adventurer type and location of player on board and any treasures being carried
Has method's for:
--tracking treasure cards in hand
--can_move (lists possible movement destinations, taking special movement abilities into account)
--move
--can_shore_up (lists underwater tiles that player can shore up from current location, or from a passed-in location)
--shore_up
--give_card (probably doesn't need a 'can' method, just some error checking in case the A.I tries something illegal)
--capture_treasure (need 4 of a kind in hand and be on matching tile)
--draw_card (checks for hand limit; may use a special card to free up space)
--play_special_card (complex logic here)
<<surely forgetting something>>
####
I think the easiest approach would be to build 6 one-off Player classes (one for each adventurer type) and hard-code their additional abilities (diver movement, engineer shore_up, messenger card_giving, etc.).  The game instance can randomly create 2 to 4 player instances during initialization.


***Forbidden_Island(num_players, difficulty)
Tracks Water Level
Checks for game won / Game lost
Initializes a game
--build Board instance
--build Flood_Deck instance
--draw 6 Flood_Deck cards and 'flip' matching tiles on the board
--build 2-4 Player instances
--build Treasure_Deck instance
--each Player draws 2 treasure cards
Drives the turns with a while loop
Tracks special circumstances  or "interrupts" such as a player having to escape from a tile that just sunk.
"""