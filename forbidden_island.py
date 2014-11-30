"""
Forbidden Island Project
CS440
Created by: Mike Allan and James Doles
"""

import fi_display
import fi_play_ai
import fi_play_human
import fi_game
import fi_ai

import sys
import argparse

parser = argparse.ArgumentParser(description='The Forbidden Island game')
parser.add_argument("gameType", type=str, help="For ai game enter 'a', for human game enter 'h'",
                    choices=['a', 'h'])
parser.add_argument("numPlayers", type=int, help="Number of players between 2 and 4 inclusive",
                    choices=[2, 3, 4])
parser.add_argument("difficulty",  type=int, help="Difficulty number between 0 and 3 inclusive"\
                    " from easiest to hardest", choices=[0, 1, 2, 3])
ARGS = parser.parse_args()


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
    self.BOARD = fi_game.Game_Board(num_players)
    # Create Flood Deck
    self.floodDeck = fi_game.Flood_Deck(self.BOARD)
    # Create Treasure Deck
    self.treasureDeck = fi_game.Treasure_Deck()
    # Set Water Level
    self.waterLevel = difficulty
    # The island starts to sink! Draw top 6 flood cards
    for num in range(6):
      self.floodDeck.draw()
    # Adventurers Appear!
    self.players = []
    self.adventurers = []
    for num in range(num_players):
      self.players.append(fi_game.Player(num, self.adventurers, self))
      self.adventurers.append(self.players[-1].adventurer)
    # Set Currently Player
    self.currentPlayer = self.players[0]
    self.actionsRemaining = 3
    self.gameOver = False  # Continue playing until this is true
    self.gameWon = False   # Set to True if adventurers escape with all treasures
    
  def nextPlayer(self):
    """Increment currentPlayer to next player; loop to 0 if currentPlayer is last player"""
    if self.players.index(self.currentPlayer) == len(self.players) - 1:
      self.currentPlayer = self.players[0]
    else:
      self.currentPlayer = self.players[self.players.index(self.currentPlayer) + 1]
    self.actionsRemaining = 3


def performAction(action, game):
  """Performs passed action to modify the passed game state"""
  if action[0] == 'Pass':
    fi_display.print_bold(" Passing, doing nothing", 3)
  elif action[0] == 'Move':
    game.currentPlayer.move(action[1])
  elif action[0] == 'Move Player':
    return action
  elif action[0] == 'Shore Up':
    game.currentPlayer.shore_up(action[1])
  elif action[0] == 'Play special':
    return action
  elif action[0] == 'Give Card':
    rtn = game.currentPlayer.give_card(game.players[action[1]], action[2])
    if rtn == "hand limit exceeded":
      return [rtn, int(action[1])]
  elif action[0] == 'Capture Treasure':
    game.currentPlayer.capture_treasure(action[1])
  elif action == 'Fly to any tile':
    return action
  elif action == 'WIN GAME!':
    return 'win'
  else:
    raise Exception('Bad Action Passed')
  return True

def play_game_human(num_players = 4, difficulty = 0):
  game = Forbidden_Island(num_players, difficulty)
  reasonGameEnded = "Game still in progress"  #if game has ended, explain here
  agents = []
  playerInput = []
  for plyr in xrange(num_players):
    #playerInput.append(getHumanInput)
    agents.append(fi_play_human.Human_Agent(game, plyr))  
  #ai = AI()
  #actions = ai.get_actions(game.players[0])
  #for a in actions:
  #  print a

  while(game.gameOver == False):
    player = game.players.index(game.currentPlayer)
    pilotAction = False
    if game.currentPlayer.adventurer == 5:
      pilotAction = True
    while game.actionsRemaining > 0:
      fi_display.print_game(game)
      chosenAction = agents[player].getAgentAction(pilotAction)
      #playerInput[game.players.index(game.currentPlayer)](game)
      rtn = performAction(chosenAction, game)
      if rtn != True:
        if rtn[0] == "hand limit exceeded":
          agents[rtn[1]].getDiscardCard()
        elif rtn[0] == "Move Player":
          agents[rtn[1]].navigatorMove(rtn[2])
        elif rtn[0] == "Play special":
          agents[player].playSpecial(rtn[1], rtn[2])
          game.actionsRemaining += 1
        elif rtn == 'Fly to any tile':
          pilotAction = False
          agents[player].flyToTile()
        elif rtn == 'win':
          game.gameOver = rtn
          reasonGameEnded = "You have WON! Congratulations!"
          break
      game.actionsRemaining -= 1
    if game.gameOver != False:
      break
    fi_display.print_bold("Out of Actions.  Draw two Treasure Cards", 6)
    for i in range(2):
      card = game.currentPlayer.draw_treasure()
      if card == "hand limit exceeded":
        agents[player].getDiscardCard()
      elif type(card) is str and card.startswith('Game Over'):
        fi_display.print_bold("Drew \'Water\'s Rise\' card", 1)
        fi_display.print_card(card)
        return False
      else:
        fi_display.print_card(card)
    fi_display.print_bold("Drawing from the Flood Deck", 6)
    tilesFlooded = []
    for depth in xrange(game.BOARD.waterMeter[game.waterLevel]['draw']):
      floodDeckDraw = game.floodDeck.draw()
      if floodDeckDraw[0] != True:
        game.gameOver = True
        reasonGameEnded = floodDeckDraw[0]
        tilesFlooded.append(floodDeckDraw[1])
        break
      else:
        tilesFlooded.append(floodDeckDraw[1])
      for pawn in game.players:
        if (game.BOARD.board[floodDeckDraw[1]]['status'] == 'sunk') and \
           (pawn.onTile == floodDeckDraw[1]):
          fi_display.print_bold("****PLAYER ON SUNK TILE*******", 1)
          swimTo = agents[pawn.playerId].getSwim()
          if swimTo < 0:
            game.gameOver = True
            reasonGameEnded = "Player was unable to escape a sinking tile"        
          else:
            pawn.move(swimTo)
    fi_display.print_bold("Flood Cards Drawn: {}".format(str(tilesFlooded)), 6)
    game.nextPlayer()
  if game.gameOver == 'win':
    print
    fi_display.print_bold(reasonGameEnded, 2)
  else:
    fi_display.print_bold(reasonGameEnded, 1)


def play_game_ai(num_players=4, difficulty=0):
  numTurns = 0
  game = Forbidden_Island(num_players, difficulty)
  reasonGameEnded = "Game still in progress"  #if game has ended, explain here
  agents = []
  playerInput = []
  for plyr in xrange(num_players):
    agents.append(fi_play_ai.AI_Agent(game, plyr, fi_ai.AI(game)))  

  while(game.gameOver == False):
    numTurns += 1
    player = game.players.index(game.currentPlayer)
    pilotAction = False
    if game.currentPlayer.adventurer == 5:
      pilotAction = True
    while game.actionsRemaining > 0:
      fi_display.print_game(game)
      chosenAction = agents[player].getAgentAction(pilotAction)
      #playerInput[game.players.index(game.currentPlayer)](game)
      rtn = performAction(chosenAction, game)
      if rtn != True:
        if rtn[0] == "hand limit exceeded":
          agents[rtn[1]].getDiscardCard()
        elif rtn[0] == "Move Player":
          agents[rtn[1]].navigatorMove(rtn[2])
        elif rtn[0] == "Play special":
          agents[player].playSpecial(rtn[1], rtn[2])
          game.actionsRemaining += 1
        elif rtn == 'Fly to any tile':
          pilotAction = False
          agents[player].flyToTile()
        elif rtn == 'win':
          game.gameOver = rtn
          reasonGameEnded = "You have WON! Congratulations!"
          break
      game.actionsRemaining -= 1
    if game.gameOver != False:
      break
    fi_display.print_bold("Out of Actions.  Draw two Treasure Cards", 6)
    for i in range(2):
      card = game.currentPlayer.draw_treasure()
      if card == "hand limit exceeded":
        agents[player].getDiscardCard()
      elif type(card) is str and card.startswith('Game Over'):
        fi_display.print_bold("Drew \'Water\'s Rise\' card", 1)
        fi_display.print_card(card)
        return False
      else:
        fi_display.print_card(card)
    fi_display.print_bold("Drawing from the Flood Deck", 6)
    tilesFlooded = []
    for depth in xrange(game.BOARD.waterMeter[game.waterLevel]['draw']):
      floodDeckDraw = game.floodDeck.draw()
      if floodDeckDraw[0] != True:
        game.gameOver = True
        reasonGameEnded = floodDeckDraw[0]
        tilesFlooded.append(floodDeckDraw[1])
        break
      else:
        tilesFlooded.append(floodDeckDraw[1])
      for pawn in game.players:
        if (game.BOARD.board[floodDeckDraw[1]]['status'] == 'sunk') and \
           (pawn.onTile == floodDeckDraw[1]):
          fi_display.print_bold("****PLAYER ON SUNK TILE*******", 1)
          swimTo = agents[pawn.playerId].getSwim()
          if swimTo < 0:
            game.gameOver = True
            reasonGameEnded = "Player was unable to escape a sinking tile"        
          else:
            pawn.move(swimTo)
    fi_display.print_bold("Flood Cards Drawn: {}".format(str(tilesFlooded)), 6)
    game.nextPlayer()
  if game.gameOver == 'win':
    print
    fi_display.print_bold(reasonGameEnded, 2)
  else:
    fi_display.print_bold(reasonGameEnded, 1)
  print "Number of Turns made:", numTurns


if __name__ == '__main__':
  if ARGS.gameType == 'a':
    play_game_ai(ARGS.numPlayers, ARGS.difficulty)
  elif ARGS.gameType == 'h':
    play_game_human(ARGS.numPlayers, ARGS.difficulty)

