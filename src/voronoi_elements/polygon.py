from collections import deque

from src.voronoi_elements.point import Point


class Polygon:
  def __init__(self, pt: Point):
    self.__points = deque([])
    self.__pt = pt
  
  @property
  def len(self) -> int:
    return len(self.__points)
  
  @property
  def first(self) -> Point:
    return self.__points[0]
  
  @property
  def last(self) -> Point:
    return self.__points[-1]
  
  def addToFront(self, pt: Point) -> None:
    self.__points.appendleft(pt)
    
  def addToRear(self, pt: Point) -> None:
    self.__points.append(pt)
    
  def __str__(self) -> str:
    return "{" + ", ".join([str(pt) for pt in self.__points]) + "}"
