from collections import deque


class Polygon:
  """
  Represents a polygon in the Voronoi Diagram around a point pt=(x,y).
  Points are listed counter clockwise. When horizontal or vertical lines
  in the Voronoi Diagram are computed, the polygons are often incomplete.
  The computed Edges in the Diagram are accurate, however.
  """

  def __init__(self, pt):
    self.points = []
    self.pt = pt
    self.first = None
    self.last = None

  def isEmpty(self):
    return self.first is None

  def addToEnd(self, pt):
    if len(self.points) == 0:
      self.first = self.last = pt
      self.points.append(pt)
    else:
      self.points.append(pt)
      self.last = pt

  def addToFront(self, pt):
    if len(self.points) == 0:
      self.first = self.last = pt
      self.points.append(pt)
    else:
      self.points.insert(0, pt)
      self.first = pt

  def __str__(self):
    rep = '{'
    for pt in self.points:
      rep = rep + str(pt) + ', '
    rep = rep + '}'
    return rep
