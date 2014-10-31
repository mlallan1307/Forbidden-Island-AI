"""
Forbidden Island Project
CS440
Created by: Mike Allan and James Doles
"""

import random

UNIX_ESCAPE = '\033['
COLOR_BASE_FG = UNIX_ESCAPE + '3'
COLOR_BASE_BG = UNIX_ESCAPE + '4'
COLORS    = [COLOR_BASE_FG+str(code)+'m' for code in range(8)]
COLORS_BG = [COLOR_BASE_BG+str(code)+'m' for code in range(8)]
COLORS_BOLD = UNIX_ESCAPE + '1m'
COLOR_RESET = UNIX_ESCAPE + '0m'
PREV_ROW_CARDS= [0, 2, 6, 12, 18, 22]
TREASURE_COLORS = [COLORS[5], COLORS[3], COLORS[1], COLORS[6]]

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
    self.board[tile]['status'] = 'sunk'
    
  def move_player(self, player, tileFrom, tileTo):
    self.board[tileFrom]['players'].remove(player)
    self.board[tileTo]['players'].append(player)

    
#BOARD = Game_Board()
    
class Card_Deck():
  def check_reshuffle(self):
    if len(self.deck) == 0:
      random.shuffle(self.discard)
      self.deck = self.discard
      self.discard = []


class Flood_Deck(Card_Deck):
  
  def __init__(self, board):
    self.BOARD = board
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
    if self.BOARD.board[self.lastDraw]['status'] == 'dry':
      self.BOARD.flip(self.lastDraw)
    else:
      self.BOARD.sink(self.lastDraw)
    return self.lastDraw
    
    
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

"""  def discard(self, cards):  # 30 OCT commended out because name conflice with discard list
   # Notice that this takes a list (or other iterable) of cards)
    for card in cards:
      self.discard.append(card)"""


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
  def __init__(self, player_num, adventurers, treasure_deck, board):
    self.playerId = player_num
    self.treasure_deck = treasure_deck
    self.BOARD = board
    # Hand out Treasure Deck Cards
    self.hand = treasure_deck.new_player_draw()
    # Assign adventurer based on available types
    availAdventurers = [aType for aType in range(len(ADVENTURER_TYPES)) if not aType in adventurers]
    self.adventurer = random.choice(availAdventurers)
    # Assign start tile based on adventurer type
    for idx, tile in enumerate(self.BOARD.board):
      if 'start' in tile and tile['start'] == self.adventurer:
        self.onTile = idx
        self.BOARD.board[idx]['players'].append(self.playerId)

  def __repr__(self):
    return "Player " + str(self.playerId)

  def draw_treasure(self):
    card = self.treasure_deck.draw()
    if card['type'] == 'Waters Rise!':
      #TODO impliment waters rise
      return self.draw_treasure()
    else:
      self.hand.append(card)
      return card
    #TODO enforce hand limit


  def local_tiles(self, onTile=-1):
    if onTile == -1:
      onTile=self.onTile
    r = self.BOARD.board[onTile]['row']
    c = self.BOARD.board[onTile]['column']
    tiles = []
    if r > 0 and self.BOARD.boardMap[r-1][c] != 'E':
      tiles.append(self.BOARD.boardMap[r-1][c])
    if r < 5 and self.BOARD.boardMap[r+1][c] != 'E':
      tiles.append(self.BOARD.boardMap[r+1][c])
    if c > 0 and self.BOARD.boardMap[r][c-1] != 'E':
      tiles.append(self.BOARD.boardMap[r][c-1])
    if c < 5 and self.BOARD.boardMap[r][c+1] != 'E':
      tiles.append(self.BOARD.boardMap[r][c+1])
    return tiles

  def can_move(self):
    """
    returns tree of possible moves
    """
    tiles1 = self.local_tiles()
    moves = []
    for tileNum1 in tiles1:
      tile1 = self.BOARD.board[tileNum1]
      if tile1['status'] != 'sunk':
        moves.append(tileNum1)  # This line added 30 OCT in lieu of append line below that places each tile in its own list   
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
    self.BOARD.flip(tile)
    
    
  def can_give_card(self, onTile=-1):
    """
    returns list of cards that can be given and to what players
    """
    if onTile == -1:
      onTile=self.onTile
    moves = [[], []]
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
    for card in self.hand:
      if card['type'] != 'Special':
          moves[1].append(card)
    return moves  # Note this returns index values


  def give_card(self, player, card):  # Note this expects player & card objects
    if not card in self.hand:
      raise Exception('Error, player cannot give card that is not in their hand')
    self.hand.remove(card)  #  30 OCT, check self.hand, remove card from self, append card to player
    player.hand.append(card)
    

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
    numCards = 4
    print "Before Capture executes"
    print "Hand is " + str(self.hand)
    print "Discard is " + str(self.treasure_deck.discard)
    print "---- Beginning capture!!!!!!! -----"
    for card in self.hand:
      if numCards > 0 and 'treasure' in card and card['treasure'] == treasure:
        self.treasure_deck.discard.append(card)
        self.hand.remove(card)
        numCards -= 1


class Forbidden_Island():
  """Contains the game state"""
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

    # Create  Board
    self.BOARD = Game_Board()
    # Create Flood Deck
    self.floodDeck = Flood_Deck(self.BOARD)
    # Create Treasure Deck
    self.treasureDeck = Treasure_Deck()
    # Set Water Level
    self.waterLevel = difficulty
    # The island starts to sink! Draw top 6 flood cards
    for num in range(6):
      self.BOARD.flip(self.floodDeck.draw())
    # Adventurers Appear!
    self.players = []
    self.adventurers = []
    for num in range(num_players):
      self.players.append(Player(num, self.adventurers, self.treasureDeck, self.BOARD))
      self.adventurers.append(self.players[-1].adventurer)
    # Set Currently Player
    self.currentPlayer = self.players[0]
    self.actionsRemaining = 3
    self.gameOver = False
    
  def nextPlayer(self):
    """Increment currentPlayer to next player; loop to 0 if currentPlayer is last player"""
    if self.players.index(self.currentPlayer) == len(self.players) - 1:
      self.currentPlayer = self.players[0]
    else:
      self.currentPlayer = self.players[self.players.index(self.currentPlayer) + 1]
    self.actionsRemaining = 3



class AI():
  def get_actions(self, player):
    """Get Available Actions
    Takes player class instance and returns possible action sequences
    """
    actions = []

    # Actions on current tile
    gives = player.can_give_card()
    ## GIVE CARDS ##
    # Give 1 card
    for pl in gives[0]:
      for card in gives[1]:
        actions.append([['give', [player.hand[card], pl]]])
    # Give 2 cards to 1 person
    for pNum, pl in enumerate(gives[0]):
      if len(gives[1]) > 1:
        for num, card in enumerate(gives[1]):
          for num2, card2 in enumerate(gives[1][num+1:]):
            actions.append([['give', [player.hand[card], pl]],
              ['give', [player.hand[card2], pl]]])
            # Give 2 cards to 2 people
            if len(gives[0]) > 1:
              for pNum2, pl2 in enumerate(gives[0][pNum+1:]):
                actions.append([['give', [player.hand[card], pl]],
                  ['give', [player.hand[card2], pl2]]])
                actions.append([['give', [player.hand[card], pl2]],
                  ['give', [player.hand[card2], pl]]])
    # Give 3 cards to 1 person
    for pNum, pl in enumerate(gives[0]):
      if len(gives[1]) > 2:
        for num, card in enumerate(gives[1]):
          for num2, card2 in enumerate(gives[1][num+1:]):
            for num3, card3 in enumerate(gives[1][num+num2+2:]):
              actions.append([['give', [player.hand[card], pl]],
                ['give', [player.hand[card2], pl]],
                ['give', [player.hand[card3], pl]]])
              # Give 3 cards to 2 people
              if len(gives[0][pNum+1:]) >= 1:
                for pNum2, pl2 in enumerate(gives[0][pNum+1:]):
                  actions.append([['give', [player.hand[card], pl]],
                    ['give', [player.hand[card2], pl2]],
                    ['give', [player.hand[card3], pl2]]])
                  actions.append([['give', [player.hand[card], pl2]],
                    ['give', [player.hand[card2], pl2]],
                    ['give', [player.hand[card3], pl]]])
                  actions.append([['give', [player.hand[card], pl2]],
                    ['give', [player.hand[card2], pl]],
                    ['give', [player.hand[card3], pl2]]])
                  # Give 3 cards to 3 people
                  if len(gives[0][pNum+pNum2+2:]) >= 1:
                    for pNum3, pl3 in enumerate(gives[0][pNum+pNum2+2:]):
                      actions.append([['give', [player.hand[card], pl]],
                        ['give', [player.hand[card2], pl2]],
                        ['give', [player.hand[card3], pl3]]])
                      actions.append([['give', [player.hand[card], pl]],
                        ['give', [player.hand[card2], pl3]],
                        ['give', [player.hand[card3], pl2]]])
                      actions.append([['give', [player.hand[card], pl2]],
                        ['give', [player.hand[card2], pl]],
                        ['give', [player.hand[card3], pl3]]])
                      actions.append([['give', [player.hand[card], pl2]],
                        ['give', [player.hand[card2], pl3]],
                        ['give', [player.hand[card3], pl]]])
                      actions.append([['give', [player.hand[card], pl3]],
                        ['give', [player.hand[card2], pl]],
                        ['give', [player.hand[card3], pl2]]])
                      actions.append([['give', [player.hand[card], pl3]],
                        ['give', [player.hand[card2], pl2]],
                        ['give', [player.hand[card3], pl]]])
    # Actions involving moving
    """ 30 OCT Commented out because player.can_move() now returns the next possible move
    allMoves  = player.can_move()
    for moves in allMoves:
      moveList = []
      for tile in moves:
        moveList.append(['move', tile])
      actions.append(moveList)
      """
    actions.append(player.can_move())
    return actions
    #gives  = player.can_give_card()
    #shores = player.can_shore_up()
    #caps   = player.can_capture_treasure()


def print_game(game):
  floodMeter = [
    {'level': -1, 'meter':'______'}, 
    {'level':  9, 'meter':'|~  X|'},
    {'level': -1, 'meter':'|____|'},
    {'level':  8, 'meter':'|~  5|'},
    {'level':  7, 'meter':'|~   |'},
    {'level': -1, 'meter':'|____|'},
    {'level':  6, 'meter':'|~  4|'},
    {'level':  5, 'meter':'|~   |'},
    {'level': -1, 'meter':'|____|'},
    {'level':  4, 'meter':'|~  3|'},
    {'level':  3, 'meter':'|~   |'},
    {'level':  2, 'meter':'|~   |'},
    {'level': -1, 'meter':'|____|'},
    {'level':  1, 'meter':'|~  2|'},
    {'level':  0, 'meter':'|~   |'},
    {'level': -1, 'meter':'|____|'}
  ]
  cardSize = 4
  cardSpacing = 4
  cards = 0
  floodMeterLine = len(floodMeter)
  # Print 6 rows
  for row in range(6):
    # Determine number of cards in this row
    numCards = 0
    if row == 0 or row == 5:   # 2 cards
      numCards = 2
    elif row == 1 or row == 4: # 4 cards
      numCards = 4
    elif row == 2 or row == 3: # 6 cards
      numCards = 6
    # Each card is 4 lines, print each one
    for cardLine in range(4):
      line = ''
      # Print beginning spacing if there is any
      for n in range((6-numCards)/2):
        line += ' '*(cardSize+cardSpacing)
      # Print the card line
      for card in range(numCards):
        curCard = PREV_ROW_CARDS[row]+card
        status = game.BOARD.board[curCard]['status']
        border = COLORS[7] # white text
        if 'treasure' in game.BOARD.board[curCard]:
          border = TREASURE_COLORS[game.BOARD.board[curCard]['treasure']]
          border += COLORS_BOLD

        if status == 'flooded':
          border += COLORS_BG[4] # white text, blue background
        elif status == 'sunk':
          line += ' '*(cardSize+cardSpacing)
          continue
        line += border
        if cardLine == 0:
          if game.BOARD.board[curCard]['name'] == 'Fools\' Landing':
            line += COLORS[1] + COLORS_BOLD
            line += str(cards)
            line += COLOR_RESET
            line += border
          else:
            line += str(cards)
          if cards < 10:
            line += '-'*(cardSize-1)
          else:
            line += '-'*(cardSize-2)
          cards += 1
        elif cardLine == 3:
          line += '-'*cardSize
        # Show player location if they are on this card
        elif cardLine == 1:
          line += '|'
          if 0 in game.BOARD.board[curCard]['players']:
            line += '0'
          else:
            line += ' '
          if 1 in game.BOARD.board[curCard]['players']:
            line += '1'
          else:
            line += ' '

          line += border + '|'
        elif cardLine == 2:
          line += '|'
          if 2 in game.BOARD.board[curCard]['players']:
            line += '2'
          else:
            line += ' '
          if 3 in game.BOARD.board[curCard]['players']:
            line += '3'
          else:
            line += ' '

          line += border + '|'
        
        line += COLOR_RESET
        line += ' '*cardSpacing
      # Print Water Level Indicator
      if numCards == 4:
        line += ' '*cardSpacing
        line += ' '*cardSize
      if numCards == 4 or numCards == 6:
        border = COLORS[7] + COLORS_BOLD # white text
        pLine = floodMeterLine - len(floodMeter)
        if pLine < len(floodMeter):
          line += border
          if floodMeter[pLine]['level'] == game.waterLevel:
            line += floodMeter[pLine]['meter'][0]
            line += COLORS[1] + COLORS_BOLD
            line += '>'
            line += COLOR_RESET
            line += border
            line += floodMeter[pLine]['meter'][2:]
          else:
            line += floodMeter[pLine]['meter']
          line += COLOR_RESET
          floodMeterLine += 1

      print line

  # Print Treasure state
  print COLORS[7] + COLORS_BOLD + 'Treasures:'
  line = ''
  line += '  Need: '
  caped = []
  for trNum, captured in game.BOARD.captured.iteritems():
    if captured:
      caped.append(trNum)
  empty = True
  for num in range(4):
    if not num in caped:
      line += TREASURE_COLORS[num]
      line += str(num)
      line += COLORS[7]
      line += ', '
      empty = False
  if not empty:
    line = line[:-2]
  print line

  line = ''
  line += '  Have: '
  empty = True
  for num in range(4):
    if num in caped:
      line += TREASURE_COLORS[num]
      line += str(num)
      line += COLORS[7]
      line += ', '
      empty = False
  if not empty:
    line = line[:-2]
  print line,
  print COLOR_RESET

  # Print players
  print COLORS[7] + COLORS_BOLD + 'Players:'
  for num, player in enumerate(game.players):
    line = '  ' + str(num) + ': '
    trCards = []
    spCards = []
    for card in player.hand:
      if card['type'] == 'Treasure':
        trCards.append(card['treasure'])
      elif card['action'] == 'Helicopter Lift':
        spStr = COLORS[2] + 'Lift' + COLOR_RESET
        spCards.append(spStr)
      elif card['action'] == 'Sandbags':
        spStr = COLORS[2] + 'Sandbags' + COLOR_RESET
        spCards.append(spStr)
    for card in spCards:
      line += card + COLORS_BOLD + COLORS[7] + ', '
    for tr in sorted(trCards):
      line += TREASURE_COLORS[tr]
      line += str(tr)
      line += COLOR_RESET
      line += COLORS_BOLD + COLORS[7] + ', '
    if len(spCards) != 0 or len(trCards) != 0:
      line = line[:-2]   # strip trailing comma
    if game.currentPlayer == player:
        line += '    Actions Remaining: ' + str(game.actionsRemaining)
    print line

def getHumanInput(game):
  actions = getActions(game)
  choice = 0
  if len(actions) == 0:
    print "No Actions available"
    choice = None
  else:
    print "\nAvailable Actions"
    i = 0
    for act in actions:
      print COLORS[2] + str(i) + ": " + COLOR_RESET + str(act)
      i += 1
    choice = int(raw_input("Choose an Action: "))
    while choice < 0 or choice > i-1:
      print "Bad entry!"
      choice = int(raw_input("Enter the number of an action in the list above: "))  
  return actions[choice]


def getActions(game):
  """Returns a list of actions available to Current Player in game"""
  actions = []
  actions.append(('Pass', 'Do Nothing'))
  for move in game.currentPlayer.can_move():
    actions.append(('Move', move)) # Add Moves as Tuples
  for shup in game.currentPlayer.can_shore_up():
    actions.append(('Shore Up', shup)) # Add Shore_Ups as tuples
  if len(game.currentPlayer.can_give_card()[0]) != 0:
    player_card_combinations = []
    for player in game.currentPlayer.can_give_card()[0]:
      for card in game.currentPlayer.can_give_card()[1]:
        actions.append(('Give Card', player, card)) # Add target players & cards
  if game.currentPlayer.can_capture_treasure():
    if game.currentPlayer.onTile in game.currentPlayer.can_capture_treasure()[1]:
      actions.append(('Capture Treasure', game.currentPlayer.can_capture_treasure()[0]))
  return actions

def performAction(action, game):
  """Performs passed action (on the passed game state"""
  if action[0] == 'Pass':
    print "Passing, doing nogthing"
  elif action[0] == 'Move':
    game.currentPlayer.move(action[1])
  elif action[0] == 'Shore Up':
    game.currentPlayer.shore_up(action[1])
  elif action[0] == 'Give Card':
    game.currentPlayer.give_card(game.players[action[1]], action[2])
  elif action[0] == 'Capture Treasure':
    game.currentPlayer.capture_treasure(action[1])
  else:
    raise Exception('Bad Action Passed')
  return True

def play_game(num_players = 4, difficulty = 0):
  game = Forbidden_Island(num_players, difficulty)
  playerInput = []
  for source in xrange(num_players):
    playerInput.append(getHumanInput)
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
  #for t in BOARD.board:
  #  print t
  '''
  # debugging
  game.players[1].move(game.players[0].onTile)
  game.players[2].move(game.players[0].onTile)
  game.players[0].draw_treasure()
  print game.players[0].hand
  '''
  ai = AI()
  actions = ai.get_actions(game.players[0])
  #for a in actions:
  #  print a

  while(game.gameOver == False):
    while game.actionsRemaining > 0:
      print_game(game)
      chosenAction = playerInput[game.players.index(game.currentPlayer)](game)
      performAction(chosenAction, game)
      game.actionsRemaining -= 1
    print "Out of Actions.  Draw two Treasure Cards"
    print game.currentPlayer.draw_treasure()  # TO DO: Add logic to hand "Water's Rise" cards"
    print game.currentPlayer.draw_treasure()
    print "Drawing from the Flood Deck"
    for depth in xrange(game.BOARD.waterLevel[game.waterLevel]['draw']):
      print str(game.floodDeck.flood())   # TO DO: gameOver if Fool's Landing Sinks / Player escapes!
    game.nextPlayer()
    
    
    

  


if __name__ == '__main__':
    play_game()

