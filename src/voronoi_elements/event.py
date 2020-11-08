from src.voronoi_elements.point import Point


class Event:
  def __init__(self, pt: Point, site=None) -> None:
    self.__pt: Point = pt
    self.__site = site
    self.__deleted: bool = False

    self.__node = None  # Circle events link back to Arc node

  @property
  def pt(self) -> Point:
    return self.__pt

  @property
  def deleted(self) -> bool:
    return self.__deleted

  @deleted.setter
  def deleted(self, d) -> None:
    self.__deleted = d

  @property
  def site(self):
    return self.__site

  @site.setter
  def site(self, site) -> None:
    self.__site = site

  @property
  def node(self):
      return self.__node

  @node.setter
  def node(self, n) -> None:
    self.__node = n

  def __eq__(self, event) -> bool:
    return self.pt.x == event.pt.x and self.pt.y == event.pt.y

  def __ne__(self, event) -> bool:
    return self.pt.x != event.pt.x or self.pt.y != event.pt.y

  def __lt__(self, event) -> bool:
    return self.pt.y < event.pt.y if self.pt.y != event.pt.y else self.pt.x < event.pt.x

  def __gt__(self, event) -> bool:
    return self.pt.y > event.pt.y if self.pt.y != event.pt.y else self.pt.x > event.pt.x

  def __le__(self, event) -> bool:
    return not self > event

  def __ge__(self, event) -> bool:
    return not self < event
