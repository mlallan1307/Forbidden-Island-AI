
import random

TREASURES = ['The Earth Stone', 'The Statue of the Wind', 'The Crystal of Fire', 'The Ocean\'s Chalice']
ADVENTURER_TYPES = ['Diver', 'Engineer', 'Explorer', 'Messenger', 'Navigator', 'Pilot']

"""
TODO:
 enforce hand limit
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
      {'name': 'Temple of the Moon', 'status': 'dry', 'players':[], 'treasure': 0},
      {'name': 'Temple of the Sun',  'status': 'dry', 'players':[], 'treasure': 0},
      {'name': 'Whipering Garden',   'status': 'dry', 'players':[], 'treasure': 1},
      {'name': 'Howling Garden',     'status': 'dry', 'players':[], 'treasure': 1},
      {'name': 'Cave of Embers',     'status': 'dry', 'players':[], 'treasure': 2},
      {'name': 'Cave of Shadows',    'status': 'dry', 'players':[], 'treasure': 2},
      {'name': 'Coral Palace',       'status': 'dry', 'players':[], 'treasure': 3},
      {'name': 'Tidal Palace',       'status': 'dry', 'players':[], 'treasure': 3},
      {'name': 'Fools\' Landing',    'status': 'dry', 'players':[], 'start': 5},
      {'name': 'Iron Gate',          'status': 'dry', 'players':[], 'start': 0},
      {'name': 'Bronze Gate',        'status': 'dry', 'players':[], 'start': 1},
      {'name': 'Copper Gate',        'status': 'dry', 'players':[], 'start': 2},
      {'name': 'Silver Gate',        'status': 'dry', 'players':[], 'start': 3},
      {'name': 'Gold Gate',          'status': 'dry', 'players':[], 'start': 4},
      {'name': 'Twilight Hollow',    'status': 'dry', 'players':[]},
      {'name': 'Watchtower',         'status': 'dry', 'players':[]},
      {'name': 'Clifs of Abandon',   'status': 'dry', 'players':[]},
      {'name': 'Lost Lagoon',        'status': 'dry', 'players':[]},
      {'name': 'Dunes of Deception', 'status': 'dry', 'players':[]},
      {'name': 'Observatory',        'status': 'dry', 'players':[]},
      {'name': 'Phantom Rock',       'status': 'dry', 'players':[]},
      {'name': 'Crimson Forest',     'status': 'dry', 'players':[]},
      {'name': 'Breakers Bridge',    'status': 'dry', 'players':[]},
      {'name': 'Misty Marsh',        'status': 'dry', 'players':[]}
    ]
    random.shuffle(self.board)
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
          self.board[tileCount]['row'] = i
          self.board[tileCount]['column'] = j
          tileCount += 1
    self.waterLevel = [
      {'draw': 2, 'skill': 'Novice'},
      {'draw': 2, 'skill': 'Normal'},
      {'draw': 3, 'skill': 'Elite'},
      {'draw': 3, 'skill': 'Legendary'},
      {'draw': 3},
      {'draw': 4},
      {'draw': 4},
      {'draw': 5},
      {'draw': 5},
      {'draw': 'Dead'}
    ]
  
  
  def flip(self, tile):
    if self.board[tile]['status'] == 'dry':
      self.board[tile]['status'] = 'flooded'
    elif self.board[tile]['status'] == 'flooded':
      self.board[tile]['status'] = 'dry'
    else:
      raise Exception('Tile status not "dry" or "flooded"')
      
      
  def sink(self, tile):
    self.board[tile]['status'] == 'sunk'
    
  def move_player(self, player, tileFrom, tileTo):
    self.board[tileFrom]['players'].remove(player)
    self.board[tileTo]['players'].append(player)

    
BOARD = Game_Board()
    
class Card_Deck():
  def check_reshuffle(self):
    if len(self.deck) == 0:
      random.shuffle(self.discard)
      self.deck = self.discard
      self.discard = []


class Flood_Deck(Card_Deck):
  
  def __init__(self):
    self.discard = []
    self.deck = [n for n in range(23)]
    random.shuffle(self.deck)
  
  
  def draw(self):
    self.check_reshuffle()
    self.lastDraw = self.deck.pop()
    self.discard.append(self.lastDraw)
    return self.lastDraw
  
  
  def flood(self):
    self.draw()
    if BOARD.board[self.lastDraw]['status'] == 'dry':
      BOARD.flip(self.lastDraw)
    else:
      BOARD.sink(self.lastDraw)
    
    
  def waters_rise(self):
    random.shuffle(self.discard)
    self.deck.extend(self.discard)
    self.discard = []
  

class Treasure_Deck(Card_Deck):
  def __init__(self):
    self.discard = []
    self.deck = []
    for n in range(5):
      self.deck.append({'type': 'Treasure', 'treasure': 0})
    for n in range(5):
      self.deck.append({'type': 'Treasure', 'treasure': 1})
    for n in range(5):
      self.deck.append({'type': 'Treasure', 'treasure': 2})
    for n in range(5):
      self.deck.append({'type': 'Treasure', 'treasure': 3})
    for n in range(3):
      self.deck.append({'type': 'Waters Rise!'})
    for n in range(3):
      self.deck.append({'type': 'Special', 'action': 'Helicopter Lift'})
    for n in range(2):
      self.deck.append({'type': 'Special', 'action': 'Sandbags'})
    random.shuffle(self.deck)
  

  def new_player_draw(self):
    hand = []
    while len(hand) < 2:
      tmp = self.deck.pop()
      # Waters Rise! card is ignored on intial drawing
      if tmp['type'] == 'Waters Rise!':
        self.deck.append(tmp)
        random.shuffle(self.deck)
      else:
        hand.append(tmp)
    return hand
  
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
  def __init__(self, player_num, adventurers, treasure_deck):
    global BOARD
    self.playerId = player_num
    # Hand out Treasure Deck Cards
    self.hand = treasure_deck.new_player_draw()
    # Assign adventurer based on available types
    availAdventurers = [aType for aType in range(len(ADVENTURER_TYPES)) if not aType in adventurers]
    self.adventurer = random.choice(availAdventurers)
    # Assign start tile based on adventurer type
    for idx, tile in enumerate(BOARD.board):
      if 'start' in tile and tile['start'] == self.adventurer:
        self.onTile = idx
        BOARD.board[idx]['players'].append(self.playerId)
    
  
  def local_tiles(self):
    r = BOARD.board[self.onTile]['row']
    c = BOARD.board[self.onTile]['column']
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
      if tile['status'] == 'flooded':
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
    if BOARD.board[self.onTile]['status'] == 'sunk':
      raise Exception('Error cannot capture treasure on sunk tile')
    if not 'treasure' in BOARD.board[self.onTile]:
      raise Exception('Error cannot capture treasure on a non-treasure tile')
    if not BOARD.board[self.onTile]['treasure'] == treasure:
      raise Exception('Error cannot capture {} on this tile'.format(TREASURES[treasure]))
    numCards = 0
    for card in self.hand:
      if 'treasure' in card:
        if card['treasure'] == treasure:
          numCards += 1
    if numCards < 4:
      raise Exception('Error not enough treasure cards')
      
    BOARD.captured[treasure] = True
    numCards = 4
    for card in self.hand:
      if numCards > 0 and 'treasure' in card and card['treasure'] == treasure:
        self.hand.remove(card)
        numCards -= 1
    
    
class Forbidden_Island():
  def __init__(self, num_players, difficulty):
    """
    inputs:
      num_players: must be 2, 3 or 4
      difficulty: must be 0, 1, 2, or 3
    """
    if num_players < 2 or num_players > 4:
      raise Exception('num_player error')
    if difficulty < 0 or difficulty > 3:
      raise Exception('difficulty error')

    # Create Flood Deck
    self.floodDeck = Flood_Deck()
    # Create Treasure Deck
    self.treasureDeck = Treasure_Deck()
    # The island starts to sink! Draw top 6 flood cards
    for num in range(6):
      BOARD.flip(self.floodDeck.draw())
    # Adventurers Appear!
    self.players = []
    self.adventurers = []
    for num in range(num_players):
      self.players.append(Player(num, self.adventurers, self.treasureDeck))
      self.adventurers.append(self.players[-1].adventurer)
    # Set Water Level
    self.waterLevel = difficulty

'''
Then when we play the game:
game = Forbidden_Island(4, 1)
game.player[0].player_special_card()
'''

def print_game(game):
  cardSize = 4
  cardSpacing = 4
  cards = 1
  for row in range(6):
    numCards = 0
    if row == 0 or row == 5:   # 2 cards
      numCards = 2
    elif row == 1 or row == 4: # 4 cards
      numCards = 4
    elif row == 2 or row == 3: # 6 cards
      numCards = 6
    for cardLine in range(4):
      line = ''
      for n in range((6-numCards)/2):
        line += ' '*(cardSize+cardSpacing)
      for card in range(numCards):
        if cardLine == 0:
          line += str(cards)
          if cards < 10:
            line += '-'*(cardSize-1)
          else:
            line += '-'*(cardSize-2)
          cards += 1
        elif cardLine == 3:
          line += '-'*cardSize
        
        line += ' '*cardSpacing
      print line

  """
  print '                {0}1---{1}    {2}2---{3}                '.format()
  print '                {0}|{1}{2}|{3}    {4}|{5}{6}|{7}                '.format()
  print '                {0}|{1}{2}|{3}    {4}|{5}{6}|{7}                '.format()
  print '                {0}----{1}    {2}----{3}                '.format()
  print
  print '        {0}3---{1}    {2}4---{3}    {4}5---{5}    {6}6---{7}        '.format()
  print '        {0}|{1}{2}|{3}    {4}|{5}{6}|{7}    {8}|{9}{10}|{11}    {12}|{13}{14}|{15}        '.format()
  print '        {0}|{1}{2}|{3}    {4}|{5}{6}|{7}    {8}|{9}{10}|{11}    {12}|{13}{14}|{15}        '.format()
  print '        {0}----{1}    {2}----{3}    {4}----{5}    {6}----{7}        '.format()
  print
  print '7---    8---    9---    10--    11--    12--'.format()
  print '|  |    |  |    |  |    |  |    |  |    |  |'.format()
  print '|  |    |  |    |  |    |  |    |  |    |  |'.format()
  print '----    ----    ----    ----    ----    ----'.format()
  print
  print '13--    14--    15--    16--    17--    18--'.format()
  print '|  |    |  |    |  |    |  |    |  |    |  |'.format()
  print '|  |    |  |    |  |    |  |    |  |    |  |'.format()
  print '----    ----    ----    ----    ----    ----'.format()
  print
  print '        {0}19--{1}    {2}20--{3}    {4}21--{5}    {6}22--{7}        '.format()
  print '        {0}|{1}{2}|{3}    {4}|{5}{6}|{7}    {8}|{9}{10}|{11}    {12}|{13}{14}|{15}        '.format()
  print '        {0}|{1}{2}|{3}    {4}|{5}{6}|{7}    {8}|{9}{10}|{11}    {12}|{13}{14}|{15}        '.format()
  print '        {0}----{1}    {2}----{3}    {4}----{5}    {6}----{7}        '.format()
  print
  print '                {0}23--{1}    {2}24--{3}                '.format()
  print '                {0}|{1}{2}|{3}    {4}|{5}{6}|{7}                '.format()
  print '                {0}|{1}{2}|{3}    {4}|{5}{6}|{7}                '.format()
  print '                {0}----{1}    {2}----{3}                '.format()
  """

def play_game():
  game = Forbidden_Island(4, 0)
  """
  print BOARD.boardMap
  print 
  for p in game.players:
    print p.playerId, p.onTile, p.hand
  for t in BOARD.board:
    print t
  print game.floodDeck.deck
  for c in game.treasureDeck.deck:
    print c
  """
  print_game(game)

if __name__ == '__main__':
    play_game()

