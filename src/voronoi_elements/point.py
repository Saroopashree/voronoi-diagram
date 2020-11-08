
class Point:
  # Describes any point in a Voronoi Diagram
  # Can be a site or a point joined by a Voronoi Edge
  def __init__(self, coord: tuple = (0, 0), idx=None) -> None:
    self.__x: float = coord[0]
    self.__y: float = coord[1]

    self.__idx: int = idx if (idx is not None) else -1
    from src.voronoi_elements.polygon import Polygon
    self.__polygon: Polygon = Polygon(self)

  @property
  def x(self) -> float:
    return self.__x

  @x.setter
  def x(self, x: float) -> None:
    self.__x = x

  @property
  def y(self) -> float:
    return self.__y

  @y.setter
  def y(self, y: float) -> None:
    self.__y = y

  @property
  def polygon(self):
    return self.__polygon

  @polygon.setter
  def polygon(self, p):
    self.__polygon = p

  def __eq__(self, pt) -> bool:
    return self.__x == pt.x and self.__y == pt.y

  def __ne__(self, pt) -> bool:
    return self.__x != pt.x or self.__y != pt.y

  def __str__(self) -> str:
    return "(" + str(self.__x) + "," + str(self.__y) + ")"

  def as_tuple(self):
    return tuple([self.x, self.y])
