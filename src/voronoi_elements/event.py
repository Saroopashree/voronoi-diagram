class Event:
  """Event in the queue. If an event is deleted, it still remains in the queue, but is not processed."""

  def __init__(self, p, site=None):
    self.p = p
    self.site = site
    self.y = p.y
    self.deleted = False

    # Circle events link back to Arc node
    self.node = None

  # built-in methods to support Event being used in priority queue
  def __lt__(self, other):
    """Higher Y values are "smaller" for events. Tie breaker is on smaller x value."""
    if self.y > other.y:
      return True
    if self.y < other.y:
      return False

    if self.p.x < other.p.x:
      return True

    return False

  def __eq__(self, other):
    return self.p.x == other.p.x and self.p.y == other.p.y

  def __ne__(self, other):
    return not self.p.x == other.p.x or not self.p.y == other.p.y

  # These can all be defined in terms of < above
  def __gt__(self, other):
    return other < self

  def __ge__(self, other):
    return not self < other

  def __le__(self, other):
    return not other < self
