from math import atan2
from matplotlib import pyplot as plt
from src.voronoi import Voronoi

if __name__ == "__main__":
  voronoi = Voronoi(20, 20)
  points = [(10, 15), (5, 17), (17, 14), (15, 4.5), (5, 8)]
  voronoi.process(points=points)
  edges = voronoi.edges

  fig = plt.figure()
  ax = fig.add_subplot(111)
  for pt in points:
    ax.plot(pt[0], pt[1], c='k', marker='o')

  for pt in voronoi.points:
    print(str(pt.polygon))
    polygon_vertices = pt.polygon.points
    n = len(polygon_vertices)

    # Sort the vertices in counter-clockwise direction
    centroid = tuple(map(lambda a: sum(a) / n, zip(*map(lambda a: a.as_tuple(), polygon_vertices))))
    polygon_vertices = sorted(polygon_vertices, key=lambda a: atan2(centroid[1] - a.y, centroid[0] - a.x))

    for i in range(n):
      x = [polygon_vertices[i].x, polygon_vertices[(i + 1) % n].x]
      y = [polygon_vertices[i].y, polygon_vertices[(i + 1) % n].y]
      ax.plot(x, y, c='b')

  ax.set_xlim([0, 20])
  ax.set_ylim([0, 20])

  plt.draw()
  plt.show()
