
import sys

class AI():
  """
  This class contains the AI logic that makes decisions about what actions to take
  """

  def makeChoice(self, choiceType, choices, playerId):
    if choiceType == 'action':
      return self.chooseAction(choices)
    elif choiceType == 'discard':
      return self.chooseDiscard(choices)
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


  def chooseAction(self, actions):
    print "Actions:"
    choice = 0
    for num, a in enumerate(actions):
      print a,
      if a[0] == 'Play special':
        choice = num
    print
    return choice


  def chooseDiscard(self, cards):
    print "Discard cards:"
    for c in cards:
      print c,
    print
    return 0


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
    print "Sandbag tiles:"
    for t in tiles:
      print t,
    print
    return tiles[0]


  def choosePilotFly(self, playerId, tiles):
    print "Heli Fly player '{}':".format(playerId)
    for t in tiles:
      print t,
    print
    return tiles[0]

  def choosePassengerFly(self, tile, passengers):
    print "Heli Fly Passengers to tile {}:".format(tile)
    for p in passengers:
      print p,
    print
    return ''

    
