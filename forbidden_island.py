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
import fi_randomai

import os
import sys
import argparse
import json


parser = argparse.ArgumentParser(description='The Forbidden Island game')
parser.add_argument("gameType", type=str, help="For ai game enter 'a', for human game enter 'h'",
                    choices=['a', 'ar', 'h'])
parser.add_argument("numPlayers", type=int, help="Number of players between 2 and 4 inclusive",
                    choices=[2, 3, 4])
parser.add_argument("difficulty",  type=int, help="Difficulty number between 0 and 3 inclusive"\
                    " from easiest to hardest", choices=[0, 1, 2, 3])
parser.add_argument("--baseValues",  type=str, help="The base values for the ai to determine the"\
                    " action weights")
parser.add_argument("--save",  type=str, nargs=2,  help="Save game state to <file> <Num Runs>")
parser.add_argument("--load",  type=str, nargs='+', help="Load game state from: <file> <line number>")
parser.add_argument("--rerun", type=str, nargs=1, help="Rerun this many times")
ARGS = parser.parse_args()


STATE_FILE_LOAD = None


class Forbidden_Island():
  """Contains the game state"""
  def __init__(self, num_players, difficulty, save=False):
    """
    inputs:
      num_players: must be 2, 3 or 4
      difficulty: must be 0, 1, 2, or 3
    """
    if num_players < 2 or num_players > 4:
      raise Exception('num_player error')
    if difficulty < 0 or difficulty > 3:
      raise Exception('difficulty error')

    if STATE_FILE_LOAD != None:
      loadedState = STATE_FILE_LOAD[0][STATE_FILE_LOAD[1]]
      self.BOARD = fi_game.Game_Board(len(loadedState['players']), loadedState['board'])
      self.floodDeck = fi_game.Flood_Deck(self.BOARD, loadedState['floodDeck'])
      self.treasureDeck = fi_game.Treasure_Deck(loadedState['treasureDeck'])
      self.waterLevel = loadedState['waterLevel']
      self.players = []
      self.adventurers = []
      for num, player in enumerate(loadedState['players']):
        self.players.append(fi_game.Player(num, self.adventurers, self, player))
        self.adventurers.append(self.players[-1].adventurer)
    else:
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

    # Set Current Player
    self.currentPlayer = self.players[0]
    self.dontDiscard = [-1, -1, -1, -1]
    self.actionsRemaining = 3
    self.gameOver = False  # Continue playing until this is true
    self.gameWon = False   # Set to True if adventurers escape with all treasures

    if save:
      self.savedState = self.saveGameState()


  def saveGameState(self):
    save = {}
    save['numPlayers'] = self.BOARD.numPlayers
    save['board'] = list(self.BOARD.board)
    save['waterLevel'] = self.waterLevel
    save['floodDeck'] = {}
    save['floodDeck']['deck'] = self.floodDeck.deck
    save['floodDeck']['discard'] = self.floodDeck.discard
    save['treasureDeck'] = self.treasureDeck.deck
    save['players'] = []
    for player in self.players:
      save['players'].append({'hand': player.hand, 'adventurer': player.adventurer})
    return save


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
          agents[rtn[1]].playSpecial(rtn[1], rtn[2])
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
          if type(swimTo) is str and swimTo.startswith('fly'):
            p = int(swimTo.split('_')[-1])
            c = None
            for card in game.players[int(p)].hand:
              if 'action' in card and card['action'] == 'Helicoptor Lift':
                c = card
                break
            agents[p].playSpecial(pawn.playerId, c)
          elif swimTo < 0:
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


def play_game_ai(num_players=4, difficulty=0, baseValues=None, AIType="MultiAgent"):
  numTurns = 0
  game = Forbidden_Island(num_players, difficulty)
  reasonGameEnded = "Game still in progress"  #if game has ended, explain here
  agents = []
  playerInput = []
  if AIType == "RandomAI":
    for plyr in xrange(num_players):
      agents.append(fi_randomai.Random_AI_Agent(game, plyr))
  else:
    for plyr in xrange(num_players):
      agents.append(fi_play_ai.AI_Agent(game, plyr, fi_ai.AI(game, baseValues)))  

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
          agents[rtn[1]].playSpecial(rtn[1], rtn[2])
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
        game.gameOver = True
        reasonGameEnded = card
        break
      else:
        fi_display.print_card(card)
    if game.gameOver != False:
      break
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
          if type(swimTo) is str and swimTo.startswith('fly'):
            p = int(swimTo.split('_')[-1])
            c = None
            for card in game.players[int(p)].hand:
              if 'action' in card and card['action'] == 'Helicoptor Lift':
                c = card
                break
            agents[p].playSpecial(pawn.playerId, c)
          elif swimTo < 0:
            game.gameOver = True
            reasonGameEnded = "Player was unable to escape a sinking tile"        
          else:
            pawn.move(swimTo)
    fi_display.print_bold("Flood Cards Drawn: {}".format(str(tilesFlooded)), 6)
    game.nextPlayer()

  string = ''
  rtn = 0
  if game.gameOver == 'win':
    rtn = 1
    string += "WIN, "
    fi_display.print_bold(reasonGameEnded, 2)
  else:
    fi_display.print_bold(reasonGameEnded, 1)
    string += "LOSS, "

  string += "{}, {}, {}, ".format(numTurns, game.waterLevel+1,
      len([t for t in game.BOARD.board if t['status'] != 'sunk']))
  for a in range(6):
    if a in [p.adventurer for p in game.players]:
       string += "P, "
    else:
       string += ", "
  for tr in range(4):
    if game.BOARD.captured[tr]:
      string += "C, "
    else:
       string += ", "
  string += reasonGameEnded
  outFile = 'run_results_' + str(AIType) + '.csv'
  if not os.path.isfile(outFile):
    string = "Result, Turns, Water Level, Tiles Left, Diver, Engineer, Explorer, Messenger, "\
        "Navigator, Pilot, Tr1, Tr2, Tr3, Tr4, Reason\n" + string
  with open(outFile, 'a') as ofh:
    print >> ofh, string

  return rtn
  print "Number of Turns made:", numTurns


if __name__ == '__main__':
  runs = 1
  if ARGS.rerun != None:
    runs = ARGS.rerun[0]
  for run in range(int(runs)):
    if ARGS.save != None:
      save = {}
      for num in range(int(ARGS.save[1])):
        game = Forbidden_Island(ARGS.numPlayers, ARGS.difficulty, True)
        save[num] = dict(game.savedState)
      with open(ARGS.save[0], 'w') as fh:
        json.dump(save, fh, sort_keys=True, indent=2)
      print "Success!"
      sys.exit(0)

    elif ARGS.load != None:
      loadedStates = json.load(open(ARGS.load[0]))
      start = 0
      end = len(loadedStates)
      if len(ARGS.load) == 2:
        start = int(ARGS.load[1])
        end = int(start) + 1
      for state in range(start, end):
        STATE_FILE_LOAD = [loadedStates, str(state)]
        if ARGS.gameType == 'a':
          rtn = play_game_ai(ARGS.numPlayers, ARGS.difficulty, ARGS.baseValues)
          print "STATE", state
          if runs == 1 and len(ARGS.load) == 2:
            sys.exit(rtn)
        elif ARGS.gameType == 'h':
          play_game_human(ARGS.numPlayers, ARGS.difficulty)
      sys.exit(0)

    if ARGS.gameType == 'a':
      rtn = play_game_ai(ARGS.numPlayers, ARGS.difficulty, ARGS.baseValues, "MultiAgent")
      if runs == 1:
        sys.exit(rtn)
    elif ARGS.gameType == 'ar':
      rtn = play_game_ai(ARGS.numPlayers, ARGS.difficulty, ARGS.baseValues, "RandomAI")
      if runs == 1:
        sys.exit(rtn)
    elif ARGS.gameType == 'h':
      play_game_human(ARGS.numPlayers, ARGS.difficulty)
