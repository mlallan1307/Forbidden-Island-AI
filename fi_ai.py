
import sys

class AI():
  """
  This class contains the AI logic that makes decisions about what actions to take
  """

  def __init__(self, game):
    self.game = game
    self.foolsLanding = []
    for num, tile in enumerate(game.BOARD.board):
      if tile['name'] == 'Fools\' Landing':
        self.foolsLanding = [num, tile]

  def makeChoice(self, choiceType, choices, playerId):
    if choiceType == 'action':
      return self.chooseAction(choices, playerId)
    elif choiceType == 'discard':
      return self.chooseDiscard(choices, playerId)
    elif choiceType == 'swim':
      return self.chooseSwim(choices, playerId)
    elif choiceType == 'navigator move':
      return self.chooseNavigatorMove(choices, playerId)
    elif choiceType == 'sandbag':
      return self.chooseSandbag(choices)
    elif choiceType == 'heli fly pilot':
      return self.choosePilotFly(choices[0], choices[1])
    elif choiceType == 'heli fly passenger':
      return self.choosePassengerFly(choices[0], choices[1])
    raise Exception("Unknown choice type '{}'".format(choiceType))
    return -1


  def chooseAction(self, actions, playerId):
    treasureAssignments = self.playerCardDesignations()
    self.updateFloodPriorityList()
    print "Actions:"
    choice = 0
    priority = 999
    for num, a in enumerate(actions):
      print num, a,
      lastChoice = choice
      if a[0] == 'Shore Up':
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
          floodPriority = 1
          if t in self.floodPriorityList:
            floodPriority = float(self.floodPriorityList[t])/10
          if len(tiles) > 1:
            choice, priority = self.updateChoice(num, priority, choice, 1+floodPriority)
          else:
            choice, priority = self.updateChoice(num, priority, choice, 2+floodPriority)
      elif a[0] == 'Play special':
        choice, priority = self.updateChoice(num, priority, choice, 10)
      elif a[0] == 'Give Card':
        player = a[1]
        tr = a[2]['treasure']
        if treasureAssignments[tr]['player'] == player and treasureAssignments[tr]['numCards'] < 4:
          # Give card to card leader for this treasure
          choice, priority = self.updateChoice(num, priority, choice, 3)
          if choice == num:
            print "-----------------------------------------------------"
            print "-----------------------------------------------------"
            print "--------------GIVE CARD-------------------"
            print "-----------------------------------------------------"
            print "-----------------------------------------------------"
      elif a[0] == 'Move':
        if self.moveToTreasure(playerId, treasureAssignments, a[1]):
          choice, priority = self.updateChoice(num, priority, choice, 2)
        else:
          takeMove = self.moveToProtect(playerId, a[1])
          if takeMove != 0:
            print "-----------------------------------------------------"
            print "-----------------------------------------------------"
            print "TAKE MOVE", takeMove
            print "-----------------------------------------------------"
            print "-----------------------------------------------------"
            choice, priority = self.updateChoice(num, priority, choice, 4+takeMove)
      elif a[0] == 'Capture Treasure':
        choice, priority = self.updateChoice(num, priority, choice, 1)
      if lastChoice != choice:
        print priority
      else:
        print
    print
    return choice

  
  def chooseDiscard(self, cards, playerId):
    treasureAssignments = self.playerCardDesignations()
    choice = 0
    priority = 999
    print "Discard cards:"
    for num, card in enumerate(cards):
      print card,
      if card['type'] == 'Treasure':
        ta = treasureAssignments[card['treasure']]
        if ta['player'] == -1:
          # discard treasure card for treasure that has been captured
          choice, priority = self.updateChoice(num, priority, choice, 0)
        elif ta['numCards'] > 4:
          choice, priority = self.updateChoice(num, priority, choice, 1)
        elif ta['numCards'] == 4 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 2)
        elif ta['numCards'] == 3 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 4)
        elif ta['numCards'] == 2 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 5)
        elif ta['numCards'] == 1 and ta['player'] != playerId:
          choice, priority = self.updateChoice(num, priority, choice, 6)
      else:
        choice, priority = self.updateChoice(num+6, priority, choice, 3)
    print
    return choice


  def chooseSwim(self, tiles, playerId):
    print "Swim Tiles for player '{}':".format(playerId)
    for t in tiles:
      print t,
    print
    return tiles[0]


  def chooseNavigatorMove(self, tiles, playerId):
    print "Navigator move player '{}':".format(playerId)
    for t in tiles:
      print t,
    print
    return tiles[0]


  def chooseSandbag(self, tiles):
    self.updateFloodPriorityList()
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
    print "Heli Fly player '{}':".format(playerId)
    choice = self.foolsLanding[0]
    for t in tiles:
      print t,
    print
    return choice


  def choosePassengerFly(self, tile, passengers):
    print "Heli Fly Passengers to tile {}:".format(tile)
    for p in passengers:
      print p,
    print
    return ''


  def updateChoice(self, choice, curPriority, curChoice, priority):
    if priority < curPriority:
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
    return cardLeaders
      
       
  def moveToTreasure(self, playerId, trAssign, tile):
    canCapture = False
    treasureNum = -1
    for trNum, trA in enumerate(trAssign):
      if trA['player'] == playerId and trA['numCards'] >= 4:
        canCapture = True
        treasureNum = trNum
    if not canCapture:
      return False
    # Find nearest treasure tile
    if 'treasure' in self.game.BOARD.board[tile] and \
        self.game.BOARD.board[tile]['treasure'] == treasureNum:
      return True
    destinations = []
    for tileNum, gameTile in enumerate(self.game.BOARD.board):
      if 'treasure' in gameTile and gameTile['treasure'] == treasureNum and \
          gameTile['status'] != 'sunk':
        destinations.append(tileNum)
    shortestRoute = []
    for dest in destinations:
      route = self.pathFinding(dest, playerId)
      print route
      if len(shortestRoute) == 0 or len(shortestRoute) > len(route):
        shortestRoute = route
    if len(shortestRoute) > 1 and tile == shortestRoute[1]:
      return True
    else:
      return False


  def pathFinding(self, goalTile, playerId, onTile=-1, localOnly=False):
    # TODO utilize diver move ability
    playerObj = self.game.players[playerId]
    if onTile == -1:
      onTile = playerObj.onTile
    moves = self.pathFindingRecursive(onTile, goalTile, playerObj, [onTile], 0, localOnly)
    return moves


  def pathFindingRecursive(self, onTile, goalTile, playerObj, path, depth, localOnly):
    #print goalTile, depth, onTile, path
    if depth >= 10:
      return []
    elif onTile == goalTile:
      return list(path)
    moves = playerObj.can_move(onTile, localOnly)
    for tile in moves:
      if tile == goalTile:
        myPath = list(path)
        myPath.append(tile)
        return myPath
    # none of the moves are to the goal tile, go deeper...
    shortestRoute = []
    for tile in moves:
      if not tile in path:
        myPath = list(path)
        myPath.append(tile)
        result = self.pathFindingRecursive(tile, goalTile, playerObj, list(myPath), depth+1,
                                           localOnly)
        if len(shortestRoute) == 0 or (len(shortestRoute) > len(result) and len(result) > 0):
          shortestRoute = list(result)
    return shortestRoute

    
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
    for trNum in [tr for tr, cap in self.game.BOARD.captured.iteritems() if cap == False]:
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
        path = self.pathFinding(tileNum, 0, self.foolsLanding[0], True)
        criticalPath.extend(path)
    self.criticalPath = list(set(criticalPath))
    

  def moveToProtect(self, playerId, moveTile):
    """
    0, 1    - -8+-4 = -12
    0       - -8
    1, 2, 3 - -4-3-2 = -9
    1, 2    - -4-3 = -7
    3, 4    - -3
    """
    shoreUpList = self.game.players[playerId].can_shore_up(moveTile)
    value = 0
    for tile in shoreUpList:
      if tile in self.floodPriorityList:
        if self.floodPriorityList[tile] == 0:
          value -= 8
        else:
          value -= 5 - self.floodPriorityList[tile]
    return float(value)/10

