from matplotlib import pyplot as plt
from src.voronoi import Voronoi

if __name__ == "__main__":
  voronoi = Voronoi(20, 20)
  points = [(10, 15), (6, 18), (9, 14), (18, 3), (5, 8)]
  voronoi.generate(points=points)
  edges = voronoi.edges
  fig = plt.figure()
  # fig.show()
  ax = fig.add_subplot(111)
  # for pt in points:
  #   ax.plot(pt[0], pt[1], c='k', marker='o')
  for edge in edges:
    p1 = edge.left.as_tuple()
    p2 = edge.right.as_tuple()
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], c='b')

  plt.draw()
  plt.show()
