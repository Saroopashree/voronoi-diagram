from src.voronoi_elements.point import Point
from src.voronoi_elements.constants import maxValue


class Edge:
  # Edge of a Voronoi Polygon
  def __init__(self, p: Point, left: Point, right: Point):
    self.left: Point = left
    self.right: Point = right
    self.partner = None
    self.end = None

    self.right_y_first = right.y > left.y
    self.right_x_first = right.x > left.x

    if left.y == right.y:
      self.m = maxValue
      self.b = None
      self.x = (right.x + left.x) / 2
      self.start = Point((p.x, p.y))
    else:
      self.m = (right.x - left.x) / (right.y - left.y)
      self.b = p.y - self.m * p.x
      self.x = None
      self.start = Point((p.x, p.y))

  def finish(self, width, height):
    # Close half edge, if self.end does not exist, assuming bounding box.
    # Might extend point in both directions. Crop to bounding box as needed.
    if self.right_y_first:
      y = width * self.m + self.b
      if y < 0:
        p = (-self.b / self.m, 0)
      elif y > height:
        p = ((height - self.b) / self.m, height)
      else:
        p = (width, y)
    elif self.b is None:
      p = (self.x, 0)
    else:
      p = (0, self.b)

    self.end = Point(p)

  def intersect(self, other):
    # Return point of intersection between two (half-)edges
    if self.b is None:
      if other.b is None:
        if self.x == other.x:
          return self.x
        return None

      p = Point((self.x, self.x * other.m + other.b))
    elif other.b is None:
      p = Point((other.x, other.x * self.m + self.b))
    else:
      # parallel lines have no intersection
      if self.m == other.m:
        return None
      else:
        x = (other.b - self.b) / (self.m - other.m)
        y = self.m * x + self.b
        p = Point((x, y))

    # self and other share a point. Ensure intersection is viable
    # based on orientation. Bisecting lines have -1/m slopes, which
    # is why X is paired with Y in the cX variables below.
    self_x_first = self.start.x < p.x
    self_y_first = self.start.y < p.y

    other_x_first = other.start.x < p.x
    other_y_first = other.start.y < p.y

    c1 = not (self_x_first == self.right_y_first)
    c2 = not (self_y_first == self.right_x_first)
    c3 = not (other_x_first == other.right_y_first)
    c4 = not (other_y_first == other.right_x_first)
    if c1 or c2 or c3 or c4:
      return None
    return p

  def __str__(self):
    end_s = str(self.end) if self.end else ''
    return '[' + str(self.start) + ',' + end_s + ']'
