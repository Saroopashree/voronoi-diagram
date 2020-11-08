from heapq import heappop, heappush

from src.voronoi_elements.point import Point
from src.voronoi_elements.edge import Edge
from src.voronoi_elements.event import Event
from src.voronoi_elements.arc import Arc


class Voronoi:
  def __init__(self, width=800, height=400):
    self.width = width
    self.height = height

  def process(self, points):
    """Process given points, represented as tuple (x,y) to return edge collection."""
    self.pq = []
    self.edges = []
    self.tree = None
    self.firstPoint = None  # handle tie breakers with first
    self.stillOnFirstRow = True
    self.points = []

    # Each point has unique identifier
    for idx in range(len(points)):
      pt = Point(points[idx], idx)
      self.points.append(pt)
      event = Event(pt, site=pt)
      heappush(self.pq, event)

    while self.pq:
      event = heappop(self.pq)
      if event.deleted:
        continue

      self.sweepPt = event.p

      # Special case if multiple points are all on first row.
      if self.stillOnFirstRow and self.firstPoint:
        if self.sweepPt.y != self.firstPoint.y:
          self.stillOnFirstRow = False

      if event.site:
        self.processSite(event)
      else:
        self.processCircle(event)

        # complete edges that remain and stretch to infinity
    if self.tree and not self.tree.isLeaf:
      self.finishEdges(self.tree)

      # Complete Voronoi Edges with partners.
      for e in self.edges:
        if e.partner:
          if e.b is None:
            e.start.y = self.height
          else:
            e.start = e.partner.end

  def findArc(self, x):
    """
    Find correct arc leaf node in BeachLine for this x coordinate. Don't have to
    check each parabola, only 2*log(n) of them.
    """
    n = self.tree
    while not n.isLeaf:
      line_x = self.computeBreakPoint(n)  # compute breakpoint based on sweep line

      # if tie, can choose either one.
      if line_x > x:
        n = n.left
      else:
        n = n.right

    return n

  def computeBreakPoint(self, n):
    """
    With sweep line Y coordinate and left/right children of interior node. You want
    to find the x-coordinate of the breakpoint, which changes based upon the y-value
    of the sweep line. Must compute intersection of two parabolas.

    Parabola can be computed as 4p(y-k)=(x-h)^2 where (h,k) is the site point, which
    becomes the focal point for the parabola. p is the distance to the directrix
    (aka, the sweep line) from the site's point (site.y - sweepPt.y)

    y1 = (1/4p1)x^2 + (-h1/2p1)x + (h1^2/4p1+k1) and compute for (h2,k2,p2)

    Only subtlety is that to simplify equation, normalize y-coordinates so
    k1 = p1/4 and k2 = p2/4; seems to eliminate most errors.

    Now set to each other and subtract to get:

    0 = (1/4p1 - 1/4p2)x^2 + (-h1/2p1 + h2/2p2) + (h1^2/4p1+k1) - (h2^2/4p2+k2)

    Compute for x using quadratic formula: (-b +/- sqrt(b^2-4ac))/2a
    """
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

  def processSite(self, event):
    """Process a site event from the queue."""

    if self.tree is None:
      self.tree = Arc(event.p)
      self.firstPoint = event.p
      return

    # must handle special case when two points are at top-most y coordinate, in
    # which case the root is a leaf node. Note that when sorting events, ties
    # are broken by x coordinate, so the next point must be to the right
    if self.tree.isLeaf and event.y == self.tree.site.y:
      left = self.tree
      right = Arc(event.p)

      start = Point(((self.firstPoint.x + event.p.x) / 2, self.height))
      edge = Edge(start, self.firstPoint, event.p)

      self.tree = Arc(edge=edge)
      self.tree.setLeft(left)
      self.tree.setRight(right)

      self.edges.append(edge)
      return

    # find point on parabola where event.pt.x bisects with vertical line,
    leaf = self.findArc(event.p.x)

    # Special case where there are multiple points, all horizontal with first point
    # so keep expanding to the right
    if self.stillOnFirstRow:
      leaf.setLeft(Arc(leaf.site))
      start = Point(((leaf.site.x + event.p.x) / 2, self.height))

      leaf.edge = Edge(start, leaf.site, event.p)
      leaf.isLeaf = False
      leaf.setRight(Arc(event.p))

      self.edges.append(leaf.edge)
      return

    # If leaf had a circle event, it is no longer valid
    # since it is being split
    if leaf.circleEvent:
      leaf.circleEvent.deleted = True

    # Voronoi edges discovered between two sites. Leaf.site is higher
    # giving orientation to these edges.
    start = leaf.pointOnBisectionLine(event.p.x, self.sweepPt.y)
    neg_ray = Edge(start, leaf.site, event.p)
    pos_ray = Edge(start, event.p, leaf.site)
    neg_ray.partner = pos_ray
    self.edges.append(neg_ray)

    # old leaf becomes root of two nodes, and grandparent of two
    leaf.edge = pos_ray
    leaf.isLeaf = False

    left = Arc()
    left.edge = neg_ray
    left.setLeft(Arc(leaf.site))
    left.setRight(Arc(event.p))

    leaf.setLeft(left)
    leaf.setRight(Arc(leaf.site))

    self.generateCircleEvent(left.left)
    self.generateCircleEvent(leaf.right)

  def finishEdges(self, n):
    """
    Close all Voronoi edges against maximum bounding box, based on how edge extends.
    """
    n.edge.finish(self.width, self.height)
    n.edge.left.polygon.addToFront(n.edge.end)
    n.edge.right.polygon.addToEnd(n.edge.end)

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
    if circle_event.p.y >= self.sweepPt.y:
      return

    node.circleEvent = circle_event
    circle_event.node = node
    heappush(self.pq, circle_event)

  def processCircle(self, event):
    """Process circle event."""
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
    p = node.pointOnBisectionLine(event.p.x, self.sweepPt.y)

    # this is a real Voronoi point! Add to appropriate polygons
    if left.site.polygon.last == node.site.polygon.first:
      node.site.polygon.addToEnd(p)
    else:
      node.site.polygon.addToFront(p)

    left.site.polygon.addToFront(p)
    right.site.polygon.addToEnd(p)

    # Found Voronoi vertex. Update edges appropriately
    left_a.edge.end = p
    right_a.edge.end = p

    # Find where to record new voronoi edge. Place with
    # (left) or (right), depending on which of left_a/right_a is higher
    # in the beach-line tree. Without loss of generality, assume left_a is higher.
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
    self.edges.append(ancestor.edge)

    # eliminate middle arc (leaf node) from beach line tree
    node.remove()

    # May find new neighbors after deletion so must check
    # for circles as well...
    self.generateCircleEvent(left)
    self.generateCircleEvent(right)