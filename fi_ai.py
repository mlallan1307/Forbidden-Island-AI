
import fi_utils

import sys
import random

class AI():
  """
  This class contains the AI logic that makes decisions about what actions to take
  """

  def __init__(self, game, baseValues=None):
    self.kill = False
    self.groupFly = False
    self.game = game
    self.foolsLanding = []
    self.shortestRouteDict = {}
    self.playerMoves = {}
    self.moveTT = {}
    self.tilePriorityDict = {}
    self.floodPriorityList = {}
    self.baseValues = []
    for num, tile in enumerate(game.BOARD.board):
      if tile['name'] == 'Fools\' Landing':
        self.foolsLanding = [num, tile]
    if baseValues != None:
      self.baseValues = [float(i) for i in baseValues.split(', ')]
    else:
      self.baseValues = [1.25, 8.33, 1.42, 10.10, -5.00, -2.00, 1.18, 0.67, 6.22, 7.00, 1.88, 1]


  def resetData(self):
    self.playerCardDesignations()
    # Clear moves and shortest route
    self.playerMoves = {}
    self.shortestRouteDict = {}
    # Calls critical paths which sets moves and routes with local only flag
    self.floodPriorityList = {}
    self.updateFloodPriorityList()
    # Clear moves and shortest route again so it's not local only
    self.playerMoves = {}
    self.shortestRouteDict = {}
    self.moveTT = {}
    self.tilePriorityDict = {}


  def makeChoice(self, choiceType, choices, playerId):
    self.resetData()
    if choiceType == 'action':
      return self.chooseAction(choices, playerId)
    elif choiceType == 'discard':
      return self.chooseDiscard(choices, playerId)
    elif choiceType == 'swim':
      self.playerMoves.clear()
      if self.game.actionsRemaining == 0:
        self.resetData()
      return self.chooseSwim(choices, playerId)
    elif choiceType == 'navigator move':
      return self.chooseNavigatorMove(choices, playerId)
    elif choiceType == 'sandbag':
      if self.game.actionsRemaining == 0:
        self.resetData()
      return self.chooseSandbag(choices)
    elif choiceType == 'heli fly pilot':
      if self.game.actionsRemaining == 0:
        self.resetData()
      return self.choosePilotFly(choices[0], choices[1])
    elif choiceType == 'heli fly passenger':
      if self.game.actionsRemaining == 0:
        self.resetData()
      return self.choosePassengerFly(choices[0], choices[1])
    raise Exception("Unknown choice type '{}'".format(choiceType))
    return -1


  def chooseAction(self, actions, playerId):
    tilePriority = self.tilePriority(playerId)
    baseShoreUp      = self.baseValues[0]
    baseMovePlayer   = self.baseValues[1]
    baseFlyToAnyTile = self.baseValues[2]
    baseHeliLift     = self.baseValues[3]
    baseFlyPriority1 = self.baseValues[4]
    baseFlyPriority2 = self.baseValues[5]
    baseSandbag      = self.baseValues[6]
    baseGiveCard     = self.baseValues[7]
    baseMove         = self.baseValues[8]
    baseSecondMove   = self.baseValues[9]
    baseCapture      = self.baseValues[10]
    baseTileInRangeInc = self.baseValues[11]
    print self.baseValues

    winSequence = self.checkWinSequence(playerId, actions)
    if winSequence != False:
      print 
      print winSequence
      if actions[winSequence][0] != 'Capture Treasure':
        self.kill = True
      return winSequence

    print "Actions:"
    choice = 0
    priority = 999
    for num, a in enumerate(actions):
      print num, a,
      lastChoice = choice
      if a[0] == 'Shore Up':
        floodPriority = baseShoreUp
        if type(a[1]) is list:
          tileList = []
          tiles = []
          for t in a[1]:
            tileList.append(self.game.BOARD.board[t])
            tiles.append(t)
        else:
          tileList = [self.game.BOARD.board[a[1]]]
          tiles = [a[1]]
        for tNum, t in enumerate(tiles):
          if t in self.floodPriorityList:
            floodPriority -= float(5 - self.floodPriorityList[t])/10
        if len(tiles) > 1:
          choice, priority = self.updateChoice(num, priority, choice, floodPriority)
        else:
          choice, priority = self.updateChoice(num, priority, choice, 1+floodPriority)
      elif a[0] == 'Move Player':
        tilePriorityTemp = self.tilePriority(a[1])
        weights = [tilePriorityTemp[t] for t in a[2]]
        if len(weights) != 0:
          minWeight = min(weights)
          if minWeight <= -5 and minWeight < tilePriorityTemp[self.game.players[a[1]].onTile]:
            choice, priority = self.updateChoice(num, priority, choice,
                baseMovePlayer+float(minWeight)/10)
        
      elif a == 'Fly to any tile' or a[0] == 'Play special':
        if a == 'Fly to any tile' or a[2]['action'] == 'Helicoptor Lift':
          base = baseHeliLift
          player = playerId
          if not a == 'Fly to any tile':
            base = baseFlyToAnyTile
            player = a[1]
          if not a == 'Fly to any tile' and a[1] != playerId:
            tilePriorityTemp = self.tilePriority(a[1])
          elif a == 'Fly to any tile':
            tilePriorityTemp = dict(tilePriority)
          else:
            tilePriorityTemp = dict(tilePriority)
          if min(tilePriorityTemp.values()) < tilePriorityTemp[self.game.players[player].onTile]:
            if min(tilePriorityTemp.values()) <= baseFlyPriority1:
              choice, priority = self.updateChoice(num, priority, choice, base)
            elif min(tilePriorityTemp.values()) <= baseFlyPriority2:
              choice, priority = self.updateChoice(num, priority, choice,
                  base+(float(min(tilePriorityTemp.values()))/10))
        elif a[2]['action'] == 'Sandbags':
          base = baseSandbag
          for n in range(3):
            if n in self.floodPriorityList.values():
              if self.tileInRange(baseSandbag, n, playerId) != False:
                base += baseTileInRangeInc
              choice, priority = self.updateChoice(num, priority, choice, base+n)

      elif a[0] == 'Give Card':
        player = a[1]
        tr = a[2]['treasure']
        if self.treasureAssignments[tr]['player'] == player and \
            self.treasureAssignments[tr]['numCards'] < 4:
          # Give card to card leader for this treasure
          choice, priority = self.updateChoice(num, priority, choice, baseGiveCard)
      elif a[0] == 'Move':
        if self.game.BOARD.board[self.foolsLanding[0]] != self.foolsLanding[1]:
          print self.game.BOARD.board[self.foolsLanding[0]]
          print self.foolsLanding[1]
          sys.exit()
        # check for potential win
        if self.game.actionsRemaining > 1:
          if a[1] == self.foolsLanding[0] and not False in self.game.BOARD.captured.values() and \
              3 == len(self.game.BOARD.board[self.foolsLanding[0]]['players']) and \
              not playerId in self.game.BOARD.board[self.foolsLanding[0]]['players']:
            numLifts = self.numHeliLifts()
            if numLifts >= 1:
              return num
          else:
            groups = self.numGroups()
            numLeft = len([c for c in self.game.BOARD.captured.values() if c == False])
            treasure = -1
            player = -1
            for trNum, tr in enumerate(self.treasureAssignments):
              if tr['numCards'] >= 4:
                treasure = trNum
                player = tr['player']
                break
            if len(groups) > 1 and len(self.numGroups(playerId)) == 1 and (numLeft == 0 or \
                (numLeft == 1 and treasure != -1 and player != playerId)) and \
                len(self.game.BOARD.board[a[1]]['players']) > 1:
              print "Move!", a[1]
              return num

        if tilePriority[a[1]] < tilePriority[self.game.players[playerId].onTile]:
          choice, priority = self.updateChoice(num, priority, choice,
              baseMove+(float(tilePriority[a[1]])/10))
        elif self.game.actionsRemaining > 1:
          # See if player can move to a better tile this turn (instead of passing)
          for move1 in self.getMoves(playerId, a[1]):
            if tilePriority[move1] < tilePriority[self.game.players[playerId].onTile]:
              choice, priority = self.updateChoice(num, priority, choice,
                  baseSecondMove+(float(tilePriority[move1])/10))
      elif a[0] == 'Capture Treasure':
        choice, priority = self.updateChoice(num, priority, choice, baseCapture)
      elif a[0] == 'WIN GAME!':
        return num
      if lastChoice != choice:
        print priority
      else:
        print
    print
    return choice


  def checkWinSequence(self, playerId, actions):
    # Get number of heli lift cards
    numLifts = self.numHeliLifts()
    if numLifts < 1:
      return False

    # Determine player locations and how split up they are
    playerMap = {}
    groups = self.numGroups()
    for tNum, tile in enumerate(self.game.BOARD.board):
      for p in tile['players']:
        playerMap[p] = tNum

    # check that there is only one treasure left to capture
    numLeft = len([c for c in self.game.BOARD.captured.values() if c == False])
    if numLeft != 1:
      return False
    # make sure the player can capture the remaining treasure
    treasure = -1
    player = -1
    for num, tr in enumerate(self.treasureAssignments):
      if tr['numCards'] >= 4:
        treasure = num
        player = tr['player']
        break
    if treasure == -1 or player != playerId:
      return False

    playerTileNum = self.game.players[playerId].onTile
    playerTile = self.game.BOARD.board[playerTileNum]
    if 'treasure' in playerTile and playerTile['treasure'] == treasure:
      for num, a in enumerate(actions):
        if a[0] == 'Capture Treasure':
          return num

    if len(groups) == 1 and numLifts >= 3:
      if len([c for c in self.game.players[playerId].hand if 'action' in c and \
          c['action'] == 'Helicoptor Lift']) >= 2:
        # Fly on your own
        for num, a in enumerate(actions):
          if a[0] == 'Play special' and a[1] == playerId and a[2]['action'] == 'Helicoptor Lift':
            self.groupFly = True
            return num
      else:
        for num, a in enumerate(actions):
          if a[0] == 'Play special' and a[2]['action'] == 'Helicoptor Lift':
            self.groupFly = True
            return num
    return False


  def numHeliLifts(self):
    numLifts = 0
    for p in self.game.players:
      for card in p.hand:
        if 'action' in card and card['action'] == 'Helicoptor Lift':
          numLifts += 1
    return numLifts


  def numGroups(self, playerId=-1):
    groups = []
    for tNum, tile in enumerate(self.game.BOARD.board):
      if len(tile['players']) > 0:
        if playerId == -1:
          groups.append(tile['players'])
        elif playerId in tile['players']:
          return tile['players'] # return player's group
    return groups


  def tileInRange(self, base, priority, playerId):
    tiles = [t for t, p in self.floodPriorityList.iteritems() if p == priority]
    b = base
    for p in [self.pathFinding(t, playerId) for t in tiles]:
      if len(p)-2 < self.game.actionsRemaining:
        return self.game.actionsRemaining - len(p) - 2
    return False

  
  def chooseDiscard(self, cards, playerId):
    # Get the special card play choice numbers
    hasSpecial = {'Helicoptor Lift': False, 'Sandbags': False}
    for num, card in enumerate(cards):
      if card['type'] == 'Special' and card['action'] in hasSpecial:
        hasSpecial[card['action']] = True
    if not False in hasSpecial.values():
      hasSpecial['Helicoptor Lift'] = 6
      hasSpecial['Sandbags'] = 7
    elif hasSpecial['Helicoptor Lift'] == False:
      hasSpecial['Sandbags'] = 6
    elif hasSpecial['Sandbags'] == False:
      hasSpecial['Helicoptor Lift'] = 6

    choice = 0
    priority = 999
    print "Discard cards:"
    for num, card in enumerate(cards):
      print card,
      if card['type'] == 'Treasure':
        ta = self.treasureAssignments[card['treasure']]
        if ta['player'] == -1:
          # discard treasure card for treasure that has been captured
          choice, priority = self.updateChoice(num, priority, choice, 1)
        elif ta['numCards'] > 4:
          choice, priority = self.updateChoice(num, priority, choice, 2)
        elif ta['numCards'] == 4 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 3)
        elif ta['numCards'] == 3 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 5)
        elif ta['numCards'] == 2 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 6)
        elif ta['numCards'] == 1 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 7)
      elif card['action'] == 'Sandbags' and 0 in self.floodPriorityList.values():
        # shore up citical tile
        choice, priority = self.updateChoice(hasSpecial['Sandbags'], priority, choice, 0)
      else:
        choice, priority = self.updateChoice(hasSpecial[card['action']], priority, choice, 4)
    print
    return choice


  def chooseSwim(self, tiles, playerId):
    tilePriority = self.tilePriority(playerId)
    print "Swim Tiles for player '{}':".format(playerId)
    choice = 0
    priority = 999
    player = self.game.players[playerId]
    for t in tiles:
      print t,
      print "chooseSwim"
      moves = self.getMoves(playerId, t)
      if len(moves) == 0 and not t == self.foolsLanding[0]:
        print " @@@@@@Tile {} is a TRAP!".format(t)
        choice, priority = self.updateChoice(t, priority, choice, 0)
      elif len(moves) == 0:
        choice, priority = self.updateChoice(t, priority, choice, 0+tilePriority[t])
      else:
        choice, priority = self.updateChoice(t, priority, choice,
            min([tilePriority[tile] for tile in moves]))
      print choice, priority,
    print
    return choice


  def chooseNavigatorMove(self, tiles, playerId):
    tilePriority = self.tilePriority(playerId)
    print "Navigator move player '{}':".format(playerId)
    choice = tiles[0]
    priority = 999
    for t in tiles:
      print t,
      choice, priority = self.updateChoice(t, priority, choice, tilePriority[t])
    print
    return choice


  def chooseSandbag(self, tiles):
    print "Sandbag tiles:"
    choice = tiles[0]
    priority = 999
    for t in tiles:
      print t,
      if t in self.floodPriorityList:
        choice, priority = self.updateChoice(t, priority, choice, self.floodPriorityList[t])
    print
    return choice


  def choosePilotFly(self, playerId, tiles):
    """
    Choosing heli fly tile:
      fly to high priority flood tile
      fly to player to give card
      fly to tile to capture
      fly to fools landing to leave
    """
    print "Heli Fly player '{}':".format(playerId)
    choice = 0
    priority = 999
    tilePriority = self.tilePriority(playerId, True)
    for t in tiles:
      print t,
      choice, priority = self.updateChoice(t, priority, choice, tilePriority[t])
    print
    return choice


  def choosePassengerFly(self, tile, passengers):
    """
    Choosing passenger fly:
      same priorities as pilot fly for each potential passenger
    """
    print "Heli Fly Passengers to tile {}:".format(tile)
    choices = []
    for p in passengers:
      print p,
      tilePriority = self.tilePriority(p, True)
      if tilePriority[tile] <= -5 or self.groupFly == True:
        choices.append(p)
    print
    if len(choices) == 0:
      return ''
    else:
      return ' '.join(map(str, choices))


  def tilePriority(self, playerId, fly=False):
    if playerId in self.tilePriorityDict:
      return dict(self.tilePriorityDict[playerId])
    if not playerId in self.moveTT:
      self.moveTT[playerId] = self.moveToTreasure(playerId, self.treasureAssignments)
    tiles = {}
    for tileNum, gameTile in enumerate(self.game.BOARD.board):
      if gameTile['status'] != 'sunk':
        tiles[tileNum] = 0
    for tile, priority in tiles.iteritems():
      gameTile = self.game.BOARD.board[tile]
      if tile == self.foolsLanding[0]:
        tiles[tile] -= 0.1
      # Leave Island if all treasures captured
      if not False in self.game.BOARD.captured.values():
        if tile == self.foolsLanding[0]:
          tiles[tile] = -10
        else:
          print "Tile Priority"
          self.pathFinding(self.foolsLanding[0], playerId, tile)
          value = 10 - len(self.shortestRoute) + 1 # +1 since fools landing is included in list
          tiles[tile] -= value
          print "priority away from fools landing", tile,  tiles[tile]
      # Move to capture treasure if player can
      if 'treasure' in gameTile and fly:
        trAssign = self.treasureAssignments[gameTile['treasure']]
        if trAssign['player'] == playerId and trAssign['numCards'] >= 4:
          # Fly to tile to capture treasure
          tiles[tile] -= 5
      elif 'treasure' in gameTile and self.moveTT[playerId] != False:
        value = float(self.moveTT[playerId][tile])/2
        print "treasure:", tile, self.moveTT[playerId][tile], value
        tiles[tile] += value
      # Move to give player a card
      for player in gameTile['players']:
        # Determine if player needs card and we arnt on same tile
        if player != playerId and not playerId in gameTile['players']:
          for trNum, tr in enumerate(self.treasureAssignments):
            # Other player is card leader
            for card in self.game.players[playerId].hand:
              if 'treasure' in card and card['treasure'] == trNum:
                # I have a card that this player needs
                localTiles = self.getMoves(playerId, tile)
                localBase = 0
                if tr['player'] == player and tr['numCards'] == 3:
                  tiles[tile] -= 2
                  localBase = 1
                elif tr['player'] == player and tr['numCards'] == 2:
                  tiles[tile] -= 1
                  localBase = 0.5
                elif tr['player'] == player and tr['numCards'] == 1:
                  tiles[tile] -= 0.5
                  localBase = 0.25
                for t in localTiles:
                    tiles[t] -= localBase
      # Move to shore up tiles
      shoreUps = self.game.players[playerId].can_shore_up(tile)
      #print "player {} can shore up {} from {}".format(playerId, shoreUps, tile)
      for t in shoreUps:
        if self.floodPriorityList[t] == 0:
          tiles[tile] -= 6
        elif self.floodPriorityList[t] == 1:
          tiles[tile] -= 2
        elif self.floodPriorityList[t] == 2:
          tiles[tile] -= 1
        elif self.floodPriorityList[t] == 3:
          tiles[tile] -= 0.5
        else:
          tiles[tile] -= 0.25
      if self.game.players[playerId].adventurer == 1 and len(shoreUps) > 1:
        tiles[tile] -= 3

    print tiles
    self.tilePriorityDict[playerId] = dict(tiles)
    return tiles


  def updateChoice(self, choice, curPriority, curChoice, priority):
    if priority < curPriority:
      curChoice = choice
      curPriority = priority
    elif priority == curPriority and bool(random.getrandbits(1)):
      # Randomly overide equivalent choices
      curChoice = choice
      curPriority = priority
    return curChoice, curPriority


  def playerCardDesignations(self):
    treasureCards= {0: 0, 1: 0, 2: 0, 3: 0}
    players = []
    for pNum, player in enumerate(self.game.players):
      players.append(dict(treasureCards))
      for card in player.hand:
        if card['type'] == 'Treasure':
          players[pNum][card['treasure']] += 1
    leaderDict = {'player': 0, 'numCards': 0}
    cardLeaders = [dict(leaderDict), dict(leaderDict), dict(leaderDict), dict(leaderDict)]
    for treasure in range(4):
      if self.game.BOARD.captured[treasure]:
        # mark as -1 if treasure captured
        cardLeaders[treasure]['numCards'] = -1
        cardLeaders[treasure]['player'] = -1
        continue
      for pNum, p in enumerate(players):
        if p[treasure] > cardLeaders[treasure]['numCards']:
          cardLeaders[treasure]['numCards'] = p[treasure]
          cardLeaders[treasure]['player'] = pNum
        elif p[treasure] == cardLeaders[treasure]['numCards']:
          unassigned = True
          for cl in cardLeaders:
            if cl['player'] == pNum:
              unassigned = False
          if unassigned:
            cardLeaders[treasure]['numCards'] = p[treasure]
            cardLeaders[treasure]['player'] = pNum
    print cardLeaders
    self.treasureAssignments = list(cardLeaders)


  def moveToTreasure(self, playerId, trAssign):
    canCapture = False
    treasureNum = -1
    for trNum, trA in enumerate(trAssign):
      if trA['player'] == playerId and trA['numCards'] >= 4:
        canCapture = True
        treasureNum = trNum
    if not canCapture:
      return False
    # Find nearest treasure tile
    destinations = []
    tiles = {}
    for tileNum, gameTile in enumerate(self.game.BOARD.board):
      if 'treasure' in gameTile and gameTile['treasure'] == treasureNum and \
          gameTile['status'] != 'sunk':
        destinations.append(tileNum)
        tiles[tileNum] = -10
      else:
        tiles[tileNum] = 0
    onTile = self.game.players[playerId].onTile
    # If current tile is a destination, no point in looking at every tile
    if onTile in destinations:
      return dict(tiles)
    for dest in destinations:
      self.pathFinding(dest, playerId)
      if len(self.shortestRoute) != 0:
        # Remove tile player is on and treasure tile
        route = self.shortestRoute[1:-1]
        for i, tile in enumerate(route):
          value = 9 - len(route)-i-1
          if tiles[tile] != 0:
            tiles[tile] -= float(value)/2
          else:
            tiles[tile] -= value
          if tiles[tile] <= -10 and not tile in destinations:
            tiles[tile] = -9
      localTiles = self.getMoves(playerId, dest)
      for tile in localTiles:
        tiles[tile] = -9
    print tiles
    return dict(tiles)

  def pathFinding(self, goalTile, playerId, onTile=-1, localOnly=False):
    playerObj = self.game.players[playerId]
    if onTile == -1:
      onTile = playerObj.onTile
    if goalTile in self.shortestRouteDict and onTile in self.shortestRouteDict[goalTile]:
      print "GOT THAT"
      self.shortestRoute = list(self.shortestRouteDict[goalTile][onTile])
      return self.shortestRoute
    elif not goalTile in self.shortestRouteDict:
      self.shortestRouteDict[goalTile] = {}
    node = fi_utils.breadth_first_search(onTile, goalTile, self, playerId, localOnly)
    #moves = pathFindingRecursive(onTile, goalTile, playerObj, [onTile], 0, localOnly)
    if node == None:
      moves = []
    else:
      moves = node.path()
    print onTile, goalTile, moves
    self.shortestRoute = list(moves)
    self.shortestRouteDict[goalTile][onTile] = list(moves)
    return self.shortestRoute


  def getMoves(self, playerId, tile=-1, localOnly=False):
    playerObj = self.game.players[playerId]
    if tile == -1:
      tile = playerObj.onTile
    if playerId in self.playerMoves and tile in self.playerMoves[playerId]:
      return list(self.playerMoves[playerId][tile])
    if playerObj.adventurer == 0 and not localOnly: # diver
      moves = playerObj.diver_moves(tile)[0]
    else:
      moves = playerObj.can_move(tile, localOnly)
    if not playerId in self.playerMoves:
      self.playerMoves[playerId] = {}
    self.playerMoves[playerId][tile] = list(moves)
    return list(moves)

    
  def updateFloodPriorityList(self):
    """
    Priority levels:
    0: fools landing, only treasure tile left for uncaptured treasure
    1: both treasure tiles flooded for uncaptured treasure
    2: one treasure tile flooded for uncaptured treasure
    3: tile part of critical path (captured treasure tile or non treasure tile)
    4: tile not part of critical path
    """
    self.updateCriticalPath()
    # priorityList is in the format {'Tile number': 'Priority Level (lower = more important)'}
    priorityList = {}
    if self.foolsLanding[1]['status'] == 'flooded':
      priorityList[self.foolsLanding[0]] = 0
    # loop through uncaptured treasures
    treasuresLeft = [0, 0, 0, 0]
    uncappedTr = [tr for tr, cap in self.game.BOARD.captured.iteritems() if cap == False]
    # add dummy treasure so loop happens even if all treasure is captured
    uncappedTr.append(99)
    for trNum in uncappedTr:
      for tileNum, boardTile in enumerate(self.game.BOARD.board):
        if 'treasure' in boardTile and boardTile['treasure'] == trNum:
          if boardTile['status'] == 'flooded':
            priorityList[tileNum] = 2
            treasuresLeft[trNum] += 1
          elif boardTile['status'] == 'dry':
            treasuresLeft[trNum] += 1
        elif boardTile['status'] == 'flooded':
          if 'treasure' in boardTile and self.game.BOARD.captured[boardTile['treasure']]:
            # Include flooded tiles even if they have already been captured
            priorityList[tileNum] = 4
          elif not 'treasure' in boardTile and not tileNum == self.foolsLanding[0]:
            # include non treasure tiles as less important
            priorityList[tileNum] = 4
    for tile, priority in priorityList.iteritems():
      boardTile = self.game.BOARD.board[tile]
      if 'treasure' in boardTile and treasuresLeft[boardTile['treasure']] == 1:
        # Only one left on this treasure, move to top of priority
        priorityList[tile] = 0
      elif 'treasure' in boardTile and treasuresLeft[boardTile['treasure']] == 2:
        # Check to see if both tiles are flooded
        for tile2, priority2 in priorityList.iteritems():
          boardTile2 = self.game.BOARD.board[tile2]
          if tile != tile2 and 'treasure' in boardTile2 and \
              boardTile2['treasure'] == boardTile['treasure']:
            # Both tiles for this treasure are flooded
            priorityList[tile] = 1
            priorityList[tile2] = 1
      elif priority == 4 and tile in self.criticalPath:
         priorityList[tile] = 3
    print "  ****PRIORITY LIST: ", priorityList
    self.floodPriorityList = dict(priorityList)


  def updateCriticalPath(self):
    # get all the tiles on the path between fools landing and all treasure tiles
    criticalPath = []
    for tileNum, boardTile in enumerate(self.game.BOARD.board):
      if 'treasure' in boardTile and boardTile['status'] != 'sunk':
        self.pathFinding(tileNum, 0, self.foolsLanding[0], True)
        criticalPath.extend(self.shortestRoute)
    self.criticalPath = list(set(criticalPath))
    

