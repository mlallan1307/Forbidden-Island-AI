
import fi_display

class Human_Agent():
  """This class contains logic for deciding normal turn actions, escaping
  a sinking tile, and discarding or playing a 6th card.   A.I. Agents can be
  a subclass of this class"""     
  
  def __init__(self, fi_game, playerId):
    self.game = fi_game
    self.playerId = playerId
  
  
  def getChoice(self, choiceList, choiceType, choices, fixInput=True):
    if fixInput:
      choice = self.fix_input(raw_input(fi_display.get_formated_string("Choice: ")))
    else:
      choice = raw_input(fi_display.get_formated_string("Choice: "))
      return choice
    while not choice in choiceList:
      fi_display.print_bold("Bad entry!", 1)
      choice = self.fix_input(raw_input(fi_display.get_formated_string("Enter the number "\
                              "of an action in the list above: ")))
    return choice


  def fix_input(self, choice):
    try:
      choice = int(choice)
    except ValueError:
      choice = -1
    return choice


  def getActions(self, pilotAction=False):
    """Returns a list of actions available to Current Player in game"""
    actions = []
    # Win Game
    if self.game.BOARD.can_win(self.game.players):
      actions.append('WIN GAME!')
      return actions
    # PASS
    actions.append(('Pass', 'Do Nothing'))
    # Move
    if self.game.currentPlayer.adventurer == 0:
      for move in self.game.currentPlayer.diver_moves():
        actions.append(('Move', move)) # Add Moves as Tuples
    else:
      if pilotAction:
        actions.append('Fly to any tile')
      for move in self.game.currentPlayer.can_move():
        actions.append(('Move', move)) # Add Moves as Tuples
    # Navigator can move another player up to 2 adjacent tiles
    if self.game.currentPlayer.adventurer == 4:
      for pNum, player in enumerate(self.game.players):
        if pNum != self.playerId:
          actions.append(('Move Player', pNum, player.navigator_tiles()))
    # Shore Up
    shoreUps = self.game.currentPlayer.can_shore_up()
    for shup in shoreUps:
      actions.append(('Shore Up', shup)) # Add shoreUps as tuples
    # Engineer can shore of 2 tiles for 1 action
    if self.game.currentPlayer.adventurer == 1 and len(shoreUps) > 1:
      for i, tile1 in enumerate(shoreUps[:-1]):
        for j, tile2 in enumerate(shoreUps[i+1:]):
          actions.append(('Shore Up', sorted([tile1, tile2])))
    # Play special cards
    for ID, player in enumerate(self.game.players):
      for card in player.hand:
        if card['type'] == 'Special':
          actions.append(('Play special', ID, card))
    # Give cards
    if len(self.game.currentPlayer.can_give_card()[0]) != 0:
      player_card_combinations = []
      for player in self.game.currentPlayer.can_give_card()[0]:
        for card in self.game.currentPlayer.can_give_card()[1]:
          actions.append(('Give Card', player, card)) # Add target players & cards
    # Capture Treasure
    if self.game.currentPlayer.can_capture_treasure():
      if self.game.currentPlayer.onTile in self.game.currentPlayer.can_capture_treasure()[1]:
        actions.append(('Capture Treasure', self.game.currentPlayer.can_capture_treasure()[0]))
    return actions


  def getAgentAction(self, pilotAction=False):
    """Called on Player's turn to get normal turn actions"""
    actions = self.getActions(pilotAction)
    choice = 0
    if len(actions) == 0:
      fi_display.print_bold("No Actions available", 1)
      choice = None
    else:
      fi_display.print_bold("\nAvailable Actions")
      i = -1
      for act in actions:
        i += 1
        if len(act) == 3 and type(act[-1]) is dict and act[-1]['type'] == 'Special':
          act = list(act)
          act[-1] = act[-1]['action']
          act = tuple(act)
        fi_display.print_bold('  {}: '.format(i), 7, act, 2)
      choice = self.getChoice(range(i+1), 'action', actions)
    return actions[choice]
      

  def getDiscardCard(self):
    """Gets the card that the player wants to discard"""
    cardTxt, cardsRaw = fi_display.print_player_hand(self.game.players[self.playerId])
    fi_display.print_bold("Player #{} hand limit reached".format(self.playerId), 1)
    fi_display.print_bold("Please select a card to discard:")
    choiceCount = -1
    specialDict = {'Helicoptor Lift': -1, 'Sandbags': -1}
    for card in cardTxt.split(', '):
      choiceCount += 1
      fi_display.print_bold('  {}: '.format(choiceCount), 7, card, 2)
      if cardsRaw[choiceCount]['type'] == 'Special' and \
         cardsRaw[choiceCount]['action'] in specialDict:
        specialDict[cardsRaw[choiceCount]['action']] = choiceCount
    specialCount = choiceCount
    specialChoiceDict = {}
    if any(v != -1 for v in specialDict.itervalues()):
      fi_display.print_bold("Or Play one of your spcial cards:")
      for card, hasCard in specialDict.iteritems():
        if hasCard != -1:
          specialCount += 1
          fi_display.print_bold('  {}: '.format(specialCount), 7,
                                "Play '{}' card".format(cardsRaw[hasCard]['action']), 2)
          specialChoiceDict[specialCount] = cardsRaw[hasCard]
    choice = self.getChoice(range(specialCount+1), 'discard', cardsRaw)
    if choice <= choiceCount:
      self.game.players[self.playerId].discard_treasure(cardsRaw[choice])
    else:
      self.playSpecial(self.playerId, specialChoiceDict[choice])
    return 


  def getSwim(self):
    """Called when a player must escape a sinking tile.
    Returns the number of a tile to escape to, or -1 to end game"""
    #onTile = self.game.players[self.playerId].onTile
    fi_display.print_bold('Oh no!  Player {}\'s tile has sunk'.format(self.playerId), 1)
    if self.game.players[self.playerId].adventurer == 0:
      safeTiles = self.game.players[self.playerId].diver_moves()
    elif self.game.players[self.playerId].adventurer == 5:
      safeTiles = []
      for num, tile in enumerate(self.game.BOARD.board):
        if tile['status'] != 'sunk':
          safeTiles.append(num)
    else:
      safeTiles = self.game.players[self.playerId].can_move()
    choice = -1
    if safeTiles == []:
      fi_display.print_bold("DISASTER!  This player cannot leave the sinking tile.  GAME OVER!!", 1)
      return -1
    fi_display.print_bold('Available Safe Tiles: ', 7, safeTiles, 2)
    choice = self.getChoice(safeTiles, 'swim', safeTiles)
    return choice 
      

  def navigatorMove(self, tiles):
    fi_display.print_bold("Navigator can move player {} to one of these tiles: {}".format(
                          self.playerId, ', '.join(str(x) for x in tiles)), 2)
    tile = self.getChoice(tiles, 'navigator move', tiles)
    self.game.players[self.playerId].move(tile)
    return


  def flyToTile(self, player=-1):
    if player == -1:
      player = self.playerId
    # Get the tile to fly to
    fi_display.print_bold("Heli Fly: ", 2, "Enter tile number to fly to: ")
    tile = self.getChoice(range(24), 'heli fly pilot', [player, [t for t in range(24) \
                          if self.game.BOARD.board[t]['status'] != 'sunk']])
    while tile < 0 or tile > 23 or self.game.BOARD.board[tile]['status'] == 'sunk':
      if tile != -1 and self.game.BOARD.board[tile]['status'] == 'sunk':
        fi_display.print_bold("Can't fly to sunk tile", 1)
      else:
        fi_display.print_bold("Bad entry!", 1)
      tile = self.fix_input(raw_input('Choice: '))
    self.game.players[player].move(tile)
    return tile


  def playSpecial(self, player, card):
    if card['action'] == "Sandbags":
      floodedTiles = [t for t in range(24) if self.game.BOARD.board[t]['status'] == 'flooded']
      if len(floodedTiles) == 0:
        # no flooded tiles
        self.game.players[player].discard_treasure(card)
        return
      fi_display.print_bold("Sandbag: ", 2, "Enter tile number to shore up: ")
      tile = self.getChoice(range(24), 'sandbag', floodedTiles)
      while not tile in floodedTiles:
        fi_display.print_bold("Bad entry!", 1)
        tile = self.fix_input(raw_input('Choice: '))
        if self.game.BOARD.board[tile]['status'] != 'flooded':
          tile = -1
          fi_display.print_bold("Tile not flooded", 1)
      self.game.players[self.playerId].shore_up(tile)
      self.game.players[player].discard_treasure(card)
      return

    elif card['action'] == "Helicoptor Lift":
      # Get the tile to fly to
      fromTile = self.game.players[player].onTile
      tile = self.flyToTile(player)
      self.game.players[player].discard_treasure(card)
      # Determine if any other players can be moved too
      otherPlayers = list(self.game.BOARD.board[fromTile]['players'])
      if player in otherPlayers:
        otherPlayers.remove(player)
      if len(otherPlayers) == 0:
        # No other players can move, finished
        return
      # Show the other players that can be moved
      fi_display.print_bold("Available players to move also: ", 7, otherPlayers)
      fi_display.print_bold("Enter the players you want to move also (space seperated): ", 2)
      playerList = self.getChoice(otherPlayers, 'heli fly passenger', [tile, otherPlayers],
                                  fixInput=False)
      if playerList == '':
        # Player hit enter with no players so no other players will move, finished
        fi_display.print_bold('No players selected', 6)
        return
      while True:
        try:
          playerListSplit = playerList.split()
          for p in playerListSplit:
            if not int(p) in otherPlayers:
              raise Exception("Player '{}' not on tile".format(str(p)))
          # Given list is valid, move all players listed and finish
          for p in playerListSplit:
            self.game.players[int(p)].move(tile)
          return
        except Exception, e:
          fi_display.print_bold("Bad entry! {}".format(e), 1)
        playerList = raw_input('Choice: ')


