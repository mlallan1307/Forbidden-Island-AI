
ADVENTURER_TYPES_SHORT = ['DIV', 'ENG', 'EXP', 'MSG', 'NAV', 'PLT']

UNIX_ESCAPE = '\033['
COLOR_BASE_FG = UNIX_ESCAPE + '3'
COLOR_BASE_BG = UNIX_ESCAPE + '4'
COLORS    = [COLOR_BASE_FG+str(code)+'m' for code in range(8)]
COLORS_BG = [COLOR_BASE_BG+str(code)+'m' for code in range(8)]
COLORS_BOLD = UNIX_ESCAPE + '1m'
COLOR_RESET = UNIX_ESCAPE + '0m'
PREV_ROW_CARDS= [0, 2, 6, 12, 18, 22]
TREASURE_COLORS = [COLORS[5], COLORS[3], COLORS[1], COLORS[6]]


def print_bold(string1, color_num1=7, string2='', color_num2=7):
  string1 = str(string1)
  string2 = str(string2)
  if string2 != '':
    print get_formated_string(string1, color_num1, string2, color_num2)
  else:
    print get_formated_string(string1, color_num1)


def get_formated_string(string1, color_num1=7, string2='', color_num2=7):
  if string2 != '':
    return '{0}{1}{2}{3}{4}{5}'.format(COLORS[color_num1], COLORS_BOLD, str(string1),
                                       COLORS[color_num2], str(string2), COLOR_RESET)
  else:
    return '{0}{1}{2}{3}'.format(COLORS[color_num1], COLORS_BOLD, str(string1), COLOR_RESET)


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
            line += str(curCard)  ##NOV11 was cards
            line += COLOR_RESET
            line += border
          else:
            line += str(curCard)  #NOV11 was cards
          if curCard < 10:  ##NOV11 was cards
            line += '-'*(cardSize-1)
          else:
            line += '-'*(cardSize-2)
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
  print '{}{}Players:{}'.format(COLORS[7], COLORS_BOLD, COLOR_RESET)
  for num, player in enumerate(game.players):
    print '  {}{} {}{}:'.format(COLORS[7], ADVENTURER_TYPES_SHORT[player.adventurer],
      COLORS_BOLD, str(num)),
    print print_player_hand(player)[0],
    if game.currentPlayer == player:
      print '   {}Actions Remaining: {}{}'.format(COLORS_BOLD, str(game.actionsRemaining),
                                                  COLOR_RESET)
    else:
      print COLOR_RESET


def color_card_types(special, treasure):
  cards = []
  for card in special:
    cards.append(COLORS_BOLD + card +  COLORS[7] + ', ')
  for tr in sorted(treasure):
    cards.append(COLORS_BOLD + TREASURE_COLORS[tr] + str(tr) + COLOR_RESET + COLORS_BOLD +
                 COLORS[7] + ', ')
  return cards


def print_player_hand(player):
  trCards = []
  trCardsNumOnly = []
  trCardsRaw = []
  Cards = []
  CardsRaw = []
  for card in player.hand:
    if card['type'] == 'Treasure':
      trCards.append(card['treasure'])
      trCardsNumOnly.append(card['treasure'])
      trCardsRaw.append(card)
    elif card['action'] == 'Helicoptor Lift':
      spStr = COLORS[2] + 'Lift' + COLOR_RESET
      Cards.append(spStr)
      CardsRaw.append(card)
    elif card['action'] == 'Sandbags':
      spStr = COLORS[2] + 'Sandbags' + COLOR_RESET
      Cards.append(spStr)
      CardsRaw.append(card)
  if len(trCardsRaw) != 0:
    trCardsNumOnly, trCardsRaw = (list(t) for t in zip(*sorted(zip(trCardsNumOnly, trCardsRaw))))
  CardsRaw.extend(trCardsRaw)
  cardTxt = color_card_types(Cards, trCards)
  line = ""
  for card in cardTxt:
    line += card
  if len(cardTxt) != 0:
    line = line[:-2]   # strip trailing comma
  return [line, CardsRaw]


def print_card(card):
  if card == 'Waters Rise':
    print ' {0}{1}{2}{3}'.format(COLORS_BOLD, COLORS[1], card, COLOR_RESET)
    return
  elif card['type'] == 'Treasure':
    print ' {0}{1}Treasure: {2}{3}{4}'.format(COLORS_BOLD, COLORS[7],
        TREASURE_COLORS[int(card['treasure'])], card['treasure'], COLOR_RESET)
    return
  elif card['action'] == 'Helicoptor Lift':
    print ' {0}{1}Special: {2}{3}{4}'.format(COLORS_BOLD, COLORS[7], COLORS[2], card['action'],
        COLOR_RESET)
    return
  elif card['action'] == 'Sandbags':
    print ' {0}{1}Special: {2}{3}{4}'.format(COLORS_BOLD, COLORS[7], COLORS[2], card['action'],
        COLOR_RESET)
    return
  else:
    print ' {0}{1}??Unkown Card??{2}'.format(COLORS_BOLD, COLORS[7], COLOR_RESET)
    return


