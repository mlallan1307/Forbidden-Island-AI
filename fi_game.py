
import random

TREASURES = ['The Earth Stone', 'The Statue of the Wind', 'The Crystal of Fire', 'The Ocean\'s Chalice']
ADVENTURER_TYPES = ['Diver', 'Engineer', 'Explorer', 'Messenger', 'Navigator', 'Pilot']

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
  def __init__(self, players, loaded=None):
      
    self.numPlayers = players
    if loaded != None:
      self.board = loaded
    else:
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
    #self.captured = {0: True, 1: True, 2: True, 3: True}
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
    self.waterMeter = [
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
    self.board[tile]['status'] = 'sunk'
    if self.board[tile]['name'] == 'Fools\' Landing':
      return "Fools\' Landing has sunk"
    elif 'treasure' in self.board[tile]:
      treasureTiles = [0, 0, 0, 0]
      for tile in self.board:
        if 'treasure' in tile and tile['status'] != 'sunk':
          treasureTiles[tile['treasure']] += 1
      #print treasureTiles
      for num, tile in enumerate(treasureTiles):
        if tile == 0 and self.captured[num] == False:
          return "Treasure {} can\'t be captured".format(num)
    return True


  def move_player(self, player, tileFrom, tileTo):
    self.board[tileFrom]['players'].remove(player)
    self.board[tileTo]['players'].append(player)


  def can_win(self, players):
    for tile in self.board:
      if tile['name'] == 'Fools\' Landing' and len(tile['players']) != len(players):
        return False
    for treasure, captured in self.captured.iteritems():
      if not captured:
        return False
    hasLift = False
    for p in players:
      for card in p.hand:
        if card['type'] == 'Special' and card['action'] == 'Helicoptor Lift':
          hasLift = True
          break
      if hasLift:
        break
    if hasLift:
      return True
    else:
      return False
        


    
#BOARD = Game_Board()
    
class Card_Deck():
  def check_reshuffle(self):
    if len(self.deck) == 0:
      random.shuffle(self.discard)
      self.deck = self.discard
      self.discard = []


class Flood_Deck(Card_Deck):
  
  def __init__(self, board, loaded=None):
    self.BOARD = board
    if loaded != None:
      self.discard = loaded['discard']
      self.deck = loaded['deck']
    else:
      self.discard = []
      self.deck = [n for n in range(24)]
      random.shuffle(self.deck)
  
  def draw(self): #11 NOV folded 'flood' functionality into draw
    self.check_reshuffle()
    lastDraw = self.deck.pop()
    if self.BOARD.board[lastDraw]['status'] == 'dry':
      self.BOARD.flip(lastDraw)
      self.discard.append(lastDraw)
    else:
      rtn = self.BOARD.sink(lastDraw)  #lastDraw is lost when tile is sunk.
      if rtn != True:
        return ["Game Over! {}".format(rtn), lastDraw]
    return [True, lastDraw]
    
    
  def waters_rise(self):
    random.shuffle(self.discard)
    self.deck.extend(self.discard)
    self.discard = []
  

class Treasure_Deck(Card_Deck):
  def __init__(self, loaded=None):
    self.discard = []
    self.deck = []
    if loaded != None:
      self.deck = loaded
    else:
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
        self.deck.append({'type': 'Special', 'action': 'Helicoptor Lift'})
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


  def discard_card(self, card):
    self.discard.append(card)
    return


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
  def __init__(self, player_num, adventurers, fi_game, loaded=None):
    self.playerId = player_num
    self.treasure_deck = fi_game.treasureDeck
    self.flood_deck = fi_game.floodDeck
    self.game = fi_game
    self.BOARD = fi_game.BOARD
    if loaded != None:
      self.hand = loaded['hand']
      self.adventurer = loaded['adventurer']
    else:
      # Hand out Treasure Deck Cards
      self.hand = self.treasure_deck.new_player_draw()
      # Assign adventurer based on available types
      availAdventurers = [aType for aType in range(len(ADVENTURER_TYPES)) if not aType in adventurers]
      self.adventurer = random.choice(availAdventurers)
    # Assign start tile based on adventurer type
    for idx, tile in enumerate(self.BOARD.board):
      if 'start' in tile and tile['start'] == self.adventurer:
        self.onTile = idx
        if loaded == None:
          self.BOARD.board[idx]['players'].append(self.playerId)

  def __repr__(self):
    return "Player " + str(self.playerId)


  def check_treasure_hand(self, hand = ''):
    if hand == '':
      hand = self.hand
    if len(hand) > 5:
      # Hand limit exceeded
      return "hand limit exceeded"
    return hand[-1]


  def draw_treasure(self):
    card = self.treasure_deck.draw()
    if card['type'] == 'Waters Rise!':
      self.flood_deck.waters_rise()
      self.game.waterLevel += 1 # Incrememnt Water level
      if self.game.waterLevel >= 9:
        return "Game Over! The Island has flooded"
      self.treasure_deck.discard_card(card)
      return "Waters Rise"
    else:
      self.hand.append(card)
      return self.check_treasure_hand()


  def discard_treasure(self, card):
    self.hand.remove(card)
    self.treasure_deck.discard_card(card)
    return


  def local_tiles(self, onTile=-1, localOnly=False):
    if onTile == -1:
      onTile=self.onTile
    r = self.BOARD.board[onTile]['row']
    c = self.BOARD.board[onTile]['column']
    tiles = []
    if r > 0 and self.BOARD.boardMap[r-1][c] != 'E': # UP
      tiles.append(self.BOARD.boardMap[r-1][c])
    if r < 5 and self.BOARD.boardMap[r+1][c] != 'E': # Down
      tiles.append(self.BOARD.boardMap[r+1][c])
    if c > 0 and self.BOARD.boardMap[r][c-1] != 'E': # Left
      tiles.append(self.BOARD.boardMap[r][c-1])
    if c < 5 and self.BOARD.boardMap[r][c+1] != 'E': # Right
      tiles.append(self.BOARD.boardMap[r][c+1])
    if self.adventurer == 2 and not localOnly: # Explorer can move and shore up diagonally
      if r > 0 and c > 0 and self.BOARD.boardMap[r-1][c-1] != 'E': # Up left
        tiles.append(self.BOARD.boardMap[r-1][c-1])
      if r > 0 and c < 5 and self.BOARD.boardMap[r-1][c+1] != 'E': # Up Right
        tiles.append(self.BOARD.boardMap[r-1][c+1])
      if r < 5 and c > 0 and self.BOARD.boardMap[r+1][c-1] != 'E': # Down left
        tiles.append(self.BOARD.boardMap[r+1][c-1])
      if r < 5 and c < 5 and self.BOARD.boardMap[r+1][c+1] != 'E': # Down Right
        tiles.append(self.BOARD.boardMap[r+1][c+1])
    return sorted(tiles)


  def navigator_tiles(self):
    """
    Returns a list of tiles that a navigator could move this player to
    NOTE: Navigator can't use this to move themself
    """
    tiles1 = self.can_move(localOnly=True)
    tiles2 = []
    for t1 in tiles1:
      move2 = self.can_move(t1, localOnly=True)
      for t2 in move2:
        if t2 != self.onTile and not t2 in tiles1 and not t2 in tiles2:
          tiles2.append(t2)
    tiles1.extend(tiles2)
    return sorted(tiles1)


  def diver_moves(self, onTile=-1, exitPoints=[], explored=[], depth=0):
    """ get diver moves
    Diver can move through 1 or more adjacent flooded/sunk tiles for 1 action
    """
    if onTile == -1:
      onTile=self.onTile
    # For some reason exitPoints and explored are not empty of this isnt this players first action
    if depth == 0:
      exitPoints=[]
      explored=[]
    # Get local tiles
    localTiles = self.local_tiles(onTile)
    # Investigate each local tile
    # Add current tile to explored list
    if not onTile in explored:
      explored.append(onTile)
    for t in localTiles:
      # Ignore tiles that are already a known exit point & Don't repeat explored tiles
      if not t in exitPoints and not t in explored:
        # If this local tile is not sunk then it is an exit point!
        if self.BOARD.board[t]['status'] != 'sunk':
          exitPoints.append(t)
          exitPoints = list(set(exitPoints))
        # If this local tile is not dry then diver may be able to go further...
        if self.BOARD.board[t]['status'] != 'dry':
          # Recursive call to get any exit points from this tile
          rtn = self.diver_moves(t, list(exitPoints), list(explored), depth+1)
          exitPoints.extend(rtn[0])
          exitPoints = list(set(exitPoints))
          explored.extend(rtn[1])
          explored = list(set(explored))
    return [sorted(list(set(exitPoints))), explored]


  def can_move(self, onTile=-1, localOnly=False):
    """
    returns tree of possible moves
    """
    if onTile == -1:
      onTile=self.onTile
    localTiles = self.local_tiles(onTile, localOnly)
    moves = []
    for tileNum in localTiles:
      tile = self.BOARD.board[tileNum]
      if tile['status'] != 'sunk':
        moves.append(tileNum) 

    """ Commented out on 30 OCT; this method now returns immediate moves only
    moves.append([tileNum1])
    tiles2 = self.local_tiles(tileNum1)
    for tileNum2 in tiles2:
      tile2 = self.BOARD.board[tileNum2]
      if tile2['status'] != 'sunk' and tileNum2 != self.onTile:
        moves.append([tileNum1, tileNum2])
        tiles3 = self.local_tiles(tileNum2)
        for tileNum3 in tiles3:
          tile3 = self.BOARD.board[tileNum3]
          if tile3['status'] != 'sunk' and tileNum3 != tileNum1 and tileNum3 != self.onTile:
            moves.append([tileNum1, tileNum2, tileNum3])
    """
    return moves
    
    
  def move(self, tileTo):
    self.BOARD.move_player(self.playerId, self.onTile, tileTo)
    self.onTile = tileTo
  
  
  def can_shore_up(self, onTile=-1):
    """
    returns list of tiles that can be shored-up
    """
    if onTile == -1:
      onTile=self.onTile
    tiles = self.local_tiles(onTile)
    moves = []
    for tileNum in tiles:
      tile = self.BOARD.board[tileNum]
      if tile['status'] == 'flooded':
        moves.append(tileNum)
    # Check current tiles
    if self.BOARD.board[onTile]['status'] == 'flooded':
      moves.append(onTile)
    return moves
    
    
  def shore_up(self, tile):
    if type(tile) is list:
      for t in tile:
        self.BOARD.flip(t)
    else:
      self.BOARD.flip(tile)
    
    
  def can_give_card(self, onTile=-1):
    """
    returns list of cards that can be given and to what players
    """
    if onTile == -1:
      onTile=self.onTile
    moves = [[], []]
    if self.adventurer == 3: # Messenger can give card to a player anywhere
      for player in range(self.BOARD.numPlayers):
        if player != self.playerId:
          moves[0].append(player)
    else:
      for player in self.BOARD.board[onTile]['players']:
        # Ignore moves to self
        if player != self.playerId:
          moves[0].append(player)
    """30 OCT commented out; now returns the Card object
    for num, card in enumerate(self.hand):
      # Can't give special cards
      if card['type'] != 'Special':
        moves[1].append(num)
    """
    # Make a list of unique treasure cards
    myTreasures = []
    for card in self.hand:
      if card['type'] != 'Special':
        inHand = False
        for tr in myTreasures:
          if card == tr:
            inHand = True
        if not inHand:
          myTreasures.append(card)

    for card in myTreasures:
      if card['type'] != 'Special':
          moves[1].append(card)
    return moves  # Note this returns index values


  def give_card(self, player, card):  # Note this expects player & card objects
    if not card in self.hand:
      raise Exception('Error, player cannot give card that is not in their hand')
    self.hand.remove(card)
    player.hand.append(card)
    return self.check_treasure_hand(player.hand)


  def can_capture_treasure(self):
    """
    Determine if capture Treasure Action is possible
    returns list containing [treasure to capture, tiles that can be captured on]
    """
    treasureCards = []
    for card in self.hand:
      if 'treasure' in card:
        treasureCards.append(card['treasure'])
    # Atleast 4 cards are needed to capture
    if len(treasureCards) < 4:
      return False
    canCapture = -1
    for treasure, captured in self.BOARD.captured.iteritems():
      if not captured and treasureCards.count(treasure) >= 4:
        canCapture = treasure
        break
    if canCapture == -1:
      return False
    treasureTiles = []
    # Get treasure tiles
    for num, tile in enumerate(self.BOARD.board):
      if 'treasure' in tile and tile['treasure'] == canCapture and tile['status'] != 'sunk':
        treasureTiles.append(num)
    return [canCapture, treasureTiles]


  def capture_treasure(self, treasure):
    if self.BOARD.board[self.onTile]['status'] == 'sunk':
      raise Exception('Error cannot capture treasure on sunk tile')
    if not 'treasure' in self.BOARD.board[self.onTile]:
      raise Exception('Error cannot capture treasure on a non-treasure tile')
    if not self.BOARD.board[self.onTile]['treasure'] == treasure:
      raise Exception('Error cannot capture {} on this tile'.format(TREASURES[treasure]))
    numCards = 0
    for card in self.hand:
      if 'treasure' in card:
        if card['treasure'] == treasure:
          numCards += 1
    if numCards < 4:
      raise Exception('Error not enough treasure cards')
    self.BOARD.captured[treasure] = True
    print "Before Capture executes"
    print "Hand is " + str(self.hand)
    print "Discard is " + str(self.treasure_deck.discard)
    print "---- Beginning capture!!!!!!! -----"
    for num in range(4):
      for card in self.hand:
        if card['type'] == 'Treasure' and card['treasure'] == treasure:
          self.discard_treasure(card)
          break


