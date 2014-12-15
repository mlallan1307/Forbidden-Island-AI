'''
Created on Dec 12, 2014

@author: james
This module contains a random AI agent that always randomly picks an assigned value.
'''

import fi_display
import fi_play_human
import random

class Random_AI_Agent(fi_play_human.Human_Agent):
  """This agent always randomly chooses when presented with an action or other choice
  """
  
  def getChoice(self, choiceList, choiceType, choices, fixInput=False):
    choice = random.choice(xrange(len(choiceList)))
    while not choice in choiceList:
      fi_display.print_bold("Bad entry!", 1)
      choice = self.fix_input(raw_input(fi_display.get_formated_string("Enter the number "\
                              "of an action in the list above: ")))
    return choice

  def navigatorMove(self, tiles):
    fi_display.print_bold("Navigator can move player {} to one of these tiles: {}".format(
                          self.playerId, ', '.join(str(x) for x in tiles)), 2)
    tile = random.choice(tiles)
    self.game.players[self.playerId].move(tile)
    return


  def getSwim(self):
    """Called when a player must escape a sinking tile.
    Returns the number of a tile to escape to, or -1 to end game"""
    #onTile = self.game.players[self.playerId].onTile
    fi_display.print_bold('Oh no!  Player {}\'s tile has sunk'.format(self.playerId), 1)
    if self.game.players[self.playerId].adventurer == 0:
      safeTiles = self.game.players[self.playerId].diver_moves()[0]
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
    choice = random.choice(safeTiles)
    return choice 

  def flyToTile(self, player=-1):
    if player == -1:
      player = self.playerId
    # Get the tile to fly to
    fi_display.print_bold("Heli Fly: ", 2, "Enter tile number to fly to: ")
    available_tiles = []
    for tile in self.game.BOARD.board:
      if tile['status'] != 'sunk':
        available_tiles.append(self.game.BOARD.board.index(tile))
    tile = random.choice(available_tiles)
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
      tile = random.choice(floodedTiles)
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
      randomPassengers = ""
      for otherPlayer in otherPlayers:
        if random.choice(xrange(2)) == 0:
          randomPassengers = randomPassengers +str(otherPlayer) + " "
      playerList = randomPassengers
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