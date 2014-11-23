
import fi_display

class Human_Agent():
  """This class contains logic for deciding normal turn actions, escaping
  a sinking tile, and discarding or playing a 6th card.   A.I. Agents can be
  a subclass of this class"""     
  
  def __init__(self, fi_game, playerId):
    self.game = fi_game
    self.playerId = playerId
  
  
  def getChoice(self, maxChoice):
    choice = self.fix_input(raw_input(fi_display.get_formated_string("Choice: ")))
    while choice < 0 or choice > maxChoice-1:
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


  def getActions(self):
    """Returns a list of actions available to Current Player in game"""
    actions = []
    actions.append(('Pass', 'Do Nothing'))
    for move in self.game.currentPlayer.can_move():
      actions.append(('Move', move)) # Add Moves as Tuples
    for shup in self.game.currentPlayer.can_shore_up():
      actions.append(('Shore Up', shup)) # Add Shore_Ups as tuples
    for ID, player in enumerate(self.game.players):
      for card in player.hand:
        if card['type'] == 'Special':
          actions.append(('Play special', ID, card))
    if len(self.game.currentPlayer.can_give_card()[0]) != 0:
      player_card_combinations = []
      for player in self.game.currentPlayer.can_give_card()[0]:
        for card in self.game.currentPlayer.can_give_card()[1]:
          actions.append(('Give Card', player, card)) # Add target players & cards
    if self.game.currentPlayer.can_capture_treasure():
      if self.game.currentPlayer.onTile in self.game.currentPlayer.can_capture_treasure()[1]:
        actions.append(('Capture Treasure', self.game.currentPlayer.can_capture_treasure()[0]))
    return actions


  def getAgentAction(self):
    """Called on Player's turn to get normal turn actions"""
    actions = self.getActions()
    choice = 0
    if len(actions) == 0:
      fi_display.print_bold("No Actions available", 1)
      choice = None
    else:
      fi_display.print_bold("\nAvailable Actions")
      i = 0
      for act in actions:
        if len(act) == 3 and type(act[-1]) is dict:
          act = list(act)
          act[-1] = act[-1]['action']
          act = tuple(act)
        fi_display.print_bold('  {}: '.format(i), 7, act, 2)
        i += 1
      choice =self.getChoice(i)
    return actions[choice]
      

  def getDiscardCard(self):
    """Gets the card that the player wants to discard"""
    cardTxt, cardsRaw = fi_display.print_player_hand(self.game.players[self.playerId])
    fi_display.print_bold("Player #{} hand limit reached".format(self.playerId), 1)
    fi_display.print_bold("Please select a card to discard:")
    for num, card in enumerate(cardTxt.split(', ')):
      fi_display.print_bold('  {}: '.format(num), 7, card, 2)
    choice = self.getChoice(len(cardsRaw))
    self.game.players[self.playerId].discard_treasure(cardsRaw[choice])
    return 


  def getSwim(self):
    """Called when a player must escape a sinking tile.
    Returns the number of a tile to escape to, or -1 to end game"""
    #onTile = self.game.players[self.playerId].onTile
    safeTiles = self.game.players[self.playerId].can_move()
    fi_display.print_bold('Oh no!  Player {}\'s tile has sunk'.format(self.playerId), 1)
    choice = -1
    if safeTiles == []:
      fi_display.print_bold("DISASTER!  This player cannot leave the sinking tile.  GAME OVER!!", 1)
      return -1
    fi_display.print_bold('Available Safe Tiles: ', 7, safeTiles, 2)
    while choice not in safeTiles:
      choice = int(raw_input(fi_display.get_formated_string("Enter a tile to swim to: ")))
    return choice 
      


  def playSpecial(self, player, card):
    if card['action'] == "Sandbags":
      string = fi_display.get_formated_string("Sandbag: ", 2, "Enter tile number to shore up: ")
      choice = self.fix_input(raw_input(string))
      while choice < 0 or choice > 23:
        fi_display.print_bold("Bad entry!", 1)
        choice = self.fix_input(raw_input(string))
        if self.game.BOARD.board[choice]['status'] != 'flooded':
          choice = -1
          fi_display.print_bold("Tile not flooded", 1)
      self.game.players[self.playerId].shore_up(choice)
      self.game.players[player].discard_treasure(card)

    elif card['action'] == "Helicoptor Lift":
      # unfinished
      pass


