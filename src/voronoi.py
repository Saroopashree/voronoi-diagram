from heapq import heappop, heappush

from typing import List, Any

from src.voronoi_elements.point import Point
from src.voronoi_elements.edge import Edge
from src.voronoi_elements.event import Event
from src.voronoi_elements.arc import Arc


class Voronoi:
  def __init__(self, height: int = 400, width: int = 400) -> None:
    self.__height: int = height
    self.__width: int = width

    self.__pq: list = []
    self.__edges: List[Edge] = []
    self.__tree = None
    self.__firstPoint = None
    self.__stillOnFirstRow: bool = True
    self.__points: List[Point] = []  # List to hold the Voronoi Point objects
    self.__sweepPt = None

  @property
  def height(self) -> int:
    return self.__height

  @height.setter
  def height(self, h: int) -> None:
    self.__height = h

  @property
  def width(self) -> int:
    return self.__width

  @width.setter
  def width(self, w: int) -> None:
    self.__width = w

  @property
  def pq(self) -> list:
    return self.__pq

  @pq.setter
  def pq(self, pq) -> None:
    self.__pq = pq

  @property
  def tree(self):
    return self.__tree

  @tree.setter
  def tree(self, t) -> None:
    self.__tree = t

  @property
  def edges(self) -> List[Edge]:
    return self.__edges

  @edges.setter
  def edges(self, e) ->  None:
    self.__edges = e

  @property
  def firstPoint(self):
    return self.__firstPoint

  @firstPoint.setter
  def firstPoint(self, pt) -> None:
    self.__firstPoint = pt

  @property
  def stillOnFirstRow(self) -> bool:
    return self.__stillOnFirstRow

  @stillOnFirstRow.setter
  def stillOnFirstRow(self, is_on_first_row) -> None:
    self.__stillOnFirstRow = is_on_first_row

  @property
  def sweepPt(self):
    return self.__sweepPt

  @sweepPt.setter
  def sweepPt(self, s) -> None:
    self.__sweepPt = s

  def generate(self, points) -> None:
    # points => List of (x, y) tuples
    for idx, pt in enumerate(points):
      point = Point(pt, idx)
      self.__points.append(point)
      event = Event(Point(pt), site=pt)
      heappush(self.pq, event)

    while self.pq:
      event = heappop(self.pq)
      if not event.deleted:
        self.sweepPt = event.pt
        # If multiple points are in the first row
        if self.stillOnFirstRow and self.firstPoint:
          if self.sweepPt.y != self.firstPoint.y:
            self.stillOnFirstRow = False

        if event.site:
          self.processSite(event)
        else:
          self.processCircle(event)

    if self.tree and not self.tree.isLeaf:
      self.finishEdges(self.tree)

      # Complete Voronoi Edges with partners.
      for e in self.__edges:
        if e.partner:
          if e.b is None:
            e.start.y = self.height
          else:
            e.start = e.partner.end

  def findArc(self, x):
    n = self.__tree
    while not n.isLeaf:
      # Compute breakpoint based on sweep line
      line_x = self.computeBreakPoint(n)
      # If tie, can choose either one
      if line_x > x:
        n = n.left
      else:
        n = n.right
    return n

  def computeBreakPoint(self, n):
    left = n.getLargestLeftDescendant()
    right = n.getSmallestRightDescendant()

    # degenerate case: might be same point, so return it.
    if left.site == right.site:
      return left.site.x

    # both on horizontal line? Decide based on relation to sweepPt.x
    p1 = left.site.y - self.sweepPt.y
    p2 = right.site.y - self.sweepPt.y
    if p1 == 0 and p2 == 0:
      if self.sweepPt.x > right.site.x:
        return right.site.x
      elif self.sweepPt.x < left.site.x:
        return left.site.x
      else:
        # between, so can choose either one. Go right
        return right.site.x

    # on same horizontal line as sweep. Break arbitrarily
    if p1 == 0:
      return left.site.x
    if p2 == 0:
      return right.site.x

    h1 = left.site.x
    h2 = right.site.x

    a = 1 / (4 * p1) - 1 / (4 * p2)
    b = -h1 / (2 * p1) + h2 / (2 * p2)
    c = (p1 / 4 + h1 * h1 / (4 * p1)) - (p2 / 4 + h2 * h2 / (4 * p2))

    # not quadratic. only one solution. What if b is zero?
    if a == 0:
      x = -c / b
      return x

    # two solutions, possibly
    sq = b * b - 4 * a * c

    x1 = (-b - (sq ** 0.5)) / (2 * a)
    x2 = (-b + (sq ** 0.5)) / (2 * a)

    # since left.site is to the left of right.site, base decision on respective heights
    if left.site.y < right.site.y:
      return max(x1, x2)
    return min(x1, x2)

  def processSite(self, event: Event) -> None:
    # Process a point site
    if self.tree is None:
      self.tree = Arc(event.pt)
      self.firstPoint = event.pt
      return

    # must handle special case when two points are at top-most y coordinate, in
    # which case the root is a leaf node. Note that when sorting events, ties
    # are broken by x coordinate, so the next point must be to the right
    if self.tree.isLeaf and event.pt.y == self.tree.site.y:
      left = self.tree
      right = Arc(event.pt)

      start = Point(((self.firstPoint.x + event.pt.x) / 2, self.height))
      edge = Edge(start, self.firstPoint, event.pt)

      self.tree = Arc(edge=edge)
      self.tree.left = left
      self.tree.right = right

      self.__edges.append(edge)
      return

    # find point on parabola where event.pt.x bisects with vertical line,
    leaf = self.findArc(event.pt.x)

    # Special case where there are multiple points, all horizontal with first point
    # so keep expanding to the right
    if self.stillOnFirstRow:
      leaf.setLeft(Arc(leaf.site))
      start = Point(((leaf.site.x + event.pt.x) / 2, self.height))

      leaf.edge = Edge(start, leaf.site, event.pt)
      leaf.isLeaf = False
      leaf.setRight(Arc(event.pt))

      self.__edges.append(leaf.edge)
      return

    # If leaf had a circle event, it is no longer valid
    # since it is being split
    if leaf.circle_event:
      leaf.circle_event.deleted = True

    # Voronoi edges discovered between two sites. Leaf.site is higher
    # giving orientation to these edges.
    start = leaf.pointOnBisectionLine(event.pt.x, self.sweepPt.y)
    neg_ray = Edge(start, leaf.site, event.pt)
    pos_ray = Edge(start, event.pt, leaf.site)
    neg_ray.partner = pos_ray
    self.__edges.append(neg_ray)

    # old leaf becomes root of two nodes, and grandparent of two
    leaf.edge = pos_ray
    leaf.isLeaf = False

    left = Arc()
    left.edge = neg_ray
    left.left = Arc(leaf.site)
    left.right = Arc(event.pt)

    leaf.left = left
    leaf.right = Arc(leaf.site)

    self.generateCircleEvent(left.left)
    self.generateCircleEvent(leaf.right)

  def processCircle(self, event: Event) -> None:
    # Process a circle event
    node = event.node

    # Find neighbor on the left and right.
    left_a = node.getLeftAncestor()
    left = left_a.getLargestLeftDescendant()
    right_a = node.getRightAncestor()
    right = right_a.getSmallestRightDescendant()

    # Eliminate old circle events if they exist.
    if left.circleEvent:
      left.circleEvent.deleted = True
    if right.circleEvent:
      right.circleEvent.deleted = True

    # Circle defined by left - node - right. Terminate Voronoi rays
    p = node.pointOnBisectionLine(event.pt.x, self.sweepPt.y)

    # this is a real Voronoi point! Add to appropriate polygons
    if left.site.polygon.last == node.site.polygon.first:
      node.site.polygon.addToRear(p)
    else:
      node.site.polygon.addToFront(p)

    left.site.polygon.addToFront(p)
    right.site.polygon.addToRear(p)

    # Found Voronoi vertex. Update edges appropriately
    left_a.edge.end = p
    right_a.edge.end = p

    # Find where to record new voronoi edge. Place with
    # (left) or (right), depending on which of left_a/right_a is higher
    # in the beachline tree. Without loss of generality, assume left_a is higher.
    # Reason is because node is being deleted and the highest ancestor (left_a) is
    # interior node that represents breakpoint involving node, and this interior
    # node must now represent the breakpoint [left|right]. Since left_a is higher,
    # it will remain while right_a is being removed (effectively replaced by right).
    t = node
    ancestor = None
    while t != self.tree:
      t = t.parent
      if t == left_a:
        ancestor = left_a
      elif t == right_a:
        ancestor = right_a

    ancestor.edge = Edge(p, left.site, right.site)
    self.__edges.append(ancestor.edge)

    # eliminate middle arc (leaf node) from beach line tree
    node.remove()

    # May find new neighbors after deletion so must check
    # for circles as well...
    self.generateCircleEvent(left)
    self.generateCircleEvent(right)

  def finishEdges(self, n):
    """
    Close all Voronoi edges against maximum bounding box, based on how edge extends.
    """
    n.edge.finish(self.width, self.height)
    n.edge.left.polygon.addToFront(n.edge.end)
    n.edge.right.polygon.addToRear(n.edge.end)

    if not n.left.isLeaf:
      self.finishEdges(n.left)
    if not n.right.isLeaf:
      self.finishEdges(n.right)

  def generateCircleEvent(self, node):
    """
    There is possibility of a circle event with this new node being the
    middle of three consecutive nodes. If so, then add new circle
    event to the priority queue for further processing.
    """
    # Find neighbor on the left and right, should they exist.
    left_a = node.getLeftAncestor()
    if left_a is None:
      return
    left = left_a.getLargestLeftDescendant()

    right_a = node.getRightAncestor()
    if right_a is None:
      return
    right = right_a.getSmallestRightDescendant()

    # sanity check. Must be different
    if left.site == right.site:
      return

    # If two edges have no intersection, leave now
    p = left_a.edge.intersect(right_a.edge)
    if p is None:
      return

    radius = ((p.x - left.site.x) ** 2 + (p.y - left.site.y) ** 2) ** 0.5

    # make sure choose point at bottom of circumcircle
    circle_event = Event(Point((p.x, p.y - radius)))
    if circle_event.pt.y >= self.sweepPt.y:
      return

    node.circleEvent = circle_event
    circle_event.node = node
    heappush(self.pq, circle_event)
