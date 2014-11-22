
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


