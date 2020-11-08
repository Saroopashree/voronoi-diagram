from src.voronoi_elements.point import Point


class Arc:
  def __init__(self, point=None, edge=None):
    self.parent = None
    self.left = None
    self.right = None
    self.site = point
    self.edge = edge
    if point:
      self.isLeaf = True
    else:
      self.isLeaf = False
    self.circle_event = None

  # @property
  # def left(self):
  #   return self.left
  #
  # @left.setter
  # def left(self, l):
  #   self.left = l
  #
  # @property
  # def right(self):
  #   return self.right
  #
  # @right.setter
  # def right(self, r):
  #   self.right = r

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

  def getLeftAncestor(self):
    parent = self.parent
    n = self
    while parent is not None and parent.left == n:
      n = parent
      parent = parent.parent

    return parent

  def getRightAncestor(self):
    parent = self.parent
    n = self
    while parent is not None and parent.right == n:
      n = parent
      parent = parent.parent

    return parent

  def getLargestLeftDescendant(self):
    n = self.left
    while not n.isLeaf:
      n = n.right
    return n

  def getSmallestRightDescendant(self):
    n = self.right
    while not n.isLeaf:
      n = n.left
    return n

  def remove(self):
    grand_parent = self.parent.parent
    if self.parent.left == self:
      # If self is a left child of the parent
      if grand_parent.left == self.parent:
        # If parent is a left child of the grand parent
        grand_parent.left = self.parent.right
      else:
        grand_parent.right = self.parent.right
    else:
      if grand_parent.left == self.parent:
        # If parent is a left child of the grand parent
        grand_parent.left = self.parent.left
      else:
        grand_parent.right = self.parent.left

  def __str__(self):
    left_s = ''
    if self.left:
      left_s = str(self.left)
    right_s = ''
    if self.right:
      right_s = str(self.right)

    return '(pt=' + str(self.site) + ', left=' + left_s + ", right=" + right_s + ')'
