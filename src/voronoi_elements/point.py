class Point:
  """
  Every point defines center of a Voronoi Polygon. Maintains index for post-processing.
  Voronoi Polygon is defined here rather than Arc because those objects come and
  go as the BeachLine is processed.

  To deal with floating point issues, all values are rounded to four digits of precision.
  This allows test cases to be accurately defined and helps eliminate special cases.
  """

  def __init__(self, p, idx=None):
    """ p is a tuple (x,y)."""
    self.x = round(p[0], 4)
    self.y = round(p[1], 4)

    from src.voronoi_elements.polygon import Polygon
    self.polygon = Polygon((self.x, self.y))
    self.idx = idx

  def __eq__(self, other):
    if other is None:
      return False
    return self.x == other.x and self.y == other.y

  def __ne__(self, other):
    if other is None: return False
    return self.x != other.x or self.y != other.y

  def __str__(self):
    return '(' + str(self.x) + ',' + str(self.y) + ')'

  def as_tuple(self):
    return tuple([self.x, self.y])
