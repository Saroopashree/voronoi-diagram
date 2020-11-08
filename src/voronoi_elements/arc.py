from src.voronoi_elements.point import Point


class Arc:
  """
  Every interior node represents breakpoint between neighboring
  sites. If an interior node has two leaf nodes for children,
  then the breakpoint is between these two nodes. Otherwise
  the breakpoint is between the largest descendant in the left-subtree
  and the smallest descendant in the right-subtree (in other words
  neighboring nodes on the beachline).

  Construct leaf node with point.

  Every interior node contains references to bisection edge which
  is initially an infinite half edge but then becomes a full finite
  edge as the algorithm progresses (or indeed, when finishing edges
  at the end).

  Discovered potential circle events are stored with the associated
  Arc node.
  """

  def __init__(self, point=None, edge=None):
    self.parent = None
    self.left = None
    self.right = None
    self.edge = edge
    self.site = point
    self.isLeaf = False
    if point:
      self.isLeaf = True
    self.circleEvent = None

  def __str__(self):
    left_s = ''
    if self.left:
      left_s = str(self.left)
    right_s = ''
    if self.right:
      right_s = str(self.right)

    return '(pt=' + str(self.site) + ', left=' + left_s + ", right=" + right_s + ')'

  def pointOnBisectionLine(self, x, sweep_y):
    """
    Given y-coordinate of sweep line and desired x intersection,
    return point on the bisection line with given x coordinate
    """
    if self.site.y == sweep_y:
      # vertical line halfway between x and site's x
      return Point(((x + self.site.x) / 2, sweep_y))
    else:
      # slope of bisection line is negative reciprocal
      # of line connecting points (x,sweepY) and self.site
      m = -(x - self.site.x) / (sweep_y - self.site.y)
      halfway = ((x + self.site.x) / 2, (sweep_y + self.site.y) / 2)
      b = halfway[1] - m * halfway[0]
      y = m * x + b

    return Point((x, y))

  def setLeft(self, n):
    self.left = n
    n.parent = self

  def setRight(self, n):
    self.right = n
    n.parent = self

  def getLeftAncestor(self):
    """
    Find first ancestor with right link to a parent of self (if exists).
    """
    parent = self.parent
    n = self
    while parent is not None and parent.left == n:
      n = parent
      parent = parent.parent

    return parent

  def getRightAncestor(self):
    """
    Find first ancestor with right link to a parent of self (if exists).
    """
    parent = self.parent
    n = self
    while parent is not None and parent.right == n:
      n = parent
      parent = parent.parent

    return parent

  def getLargestLeftDescendant(self):
    """Find largest value in left sub-tree."""
    n = self.left
    while not n.isLeaf:
      n = n.right

    return n

  def getSmallestRightDescendant(self):
    """Find smallest value in right sub-tree."""
    n = self.right
    while not n.isLeaf:
      n = n.left

    return n

  def remove(self):
    """Remove leaf node from tree. """
    grand_parent = self.parent.parent
    if self.parent.left == self:
      if grand_parent.left == self.parent:
        grand_parent.setLeft(self.parent.right)
      else:
        grand_parent.setRight(self.parent.right)
    else:
      if grand_parent.left == self.parent:
        grand_parent.setLeft(self.parent.left)
      else:
        grand_parent.setRight(self.parent.left)
