
import fi_ai

class Node:
  """A node in a search tree. Contains a pointer to the parent (the node
  that this is a successor of) and to the actual state for this node. Note
  that if a state is arrived at by two paths, then there are two nodes with
  the same state.  Also includes the action that got us to this state, and
  the total path_cost (also known as g) to reach the node.  Other functions
  may add an f and h value; see best_first_graph_search and astar_search for
  an explanation of how the f and h values are handled. You will not need to
  subclass this class."""

  def __init__(self, state, parent=None):
      "Create a search tree Node, derived from a parent by an action."
      update(self, state=state, parent=parent, depth=0)
      if parent:
          self.depth = parent.depth + 1

  def __repr__(self):
      return "<Node %s>" % (self.state,)

  def expand(self, tiles):
      "List the nodes reachable in one step from this node."
      return [Node(tile, self) for tile in tiles]

  def path(self):
      "Return a list of nodes forming the path from the root to this node."
      node, path_back = self, []
      while node:
          path_back.append(node.state)
          node = node.parent
      return list(reversed(path_back))


class FIFOQueue():
  """A First-In-First-Out Queue."""
  def __init__(self):
    self.A = []; self.start = 0
  def append(self, item):
    self.A.append(item)
  def __len__(self):
    return len(self.A) - self.start
  def extend(self, items):
    self.A.extend(items)
  def pop(self):
    e = self.A[self.start]
    self.start += 1
    if self.start > 5 and self.start > len(self.A)/2:
      self.A = self.A[self.start:]
      self.start = 0
    return e
  def __contains__(self, item):
    return item in self.A[self.start:]


def tree_search(startTile, goalTile, ai, playerId, localOnly, frontier=FIFOQueue()):
  """Search through the successors of a problem to find a goal.
  The argument frontier should be an empty queue.
  Don't worry about repeated paths to a state. [Fig. 3.7]"""
  frontier.append(Node(startTile))
  while frontier:
    node = frontier.pop()
    #print startTile, goalTile, node.depth, "->", node.state
    if node.state == goalTile:
      return node
    frontier.extend(node.expand(ai.getMoves(playerId, node.state, localOnly)))
  return None

def breadth_first_search(startTile, goalTile, ai, playerId, localOnly):
  "[Fig. 3.11]"
  node = Node(startTile)
  if node.state == goalTile:
    return node
  frontier = FIFOQueue()
  frontier.append(node)
  explored = set()
  while frontier:
    node = frontier.pop()
    #print startTile, goalTile, node.depth, "->", node.state
    explored.add(node.state)
    for child in node.expand(ai.getMoves(playerId, node.state, localOnly)):
      #print " child:", child.state
      if child.state not in explored and child not in frontier:
        if child.state == goalTile:
          return child
        frontier.append(child)
  return None

def update(x, **entries):
  """Update a dict; or an object with slots; according to entries.
  >>> update({'a': 1}, a=10, b=20)
  {'a': 10, 'b': 20}
  >>> update(Struct(a=1), a=10, b=20)
  Struct(a=10, b=20)
  """
  if isinstance(x, dict):
      x.update(entries)
  else:
      x.__dict__.update(entries)
  return x
