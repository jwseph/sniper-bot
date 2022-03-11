class Point:
  """Immutable point type"""
  __slots__ = 'x', 'y'
  def __init__(self, iterable):
    self.x, self.y = iterable
  def __repr__(self):
    return f"({self.x}, {self.y})"
  def __pow__(self, point):  # Cross product
    return self.x*point.y-point.x*self.y
  def __or__(self, point):  # Pythagorean
    return ((point.x-self.x)**2+(point.y-self.y)**2)**0.5


def is_convex(vertices):
  # https://math.stackexchange.com/questions/1743995
  if len(vertices) < 3: return False
  w_sign = x_sign = x_first_sign = x_flips = y_sign = y_first_sign = y_flips = 0
  for prev, curr, next in zip([vertices[-1]]+vertices[:-1], vertices, vertices[1:]+[vertices[0]]):  # Previous, current, and next indices, in order
    # Previous edge vector (before)
    bx = curr.x-prev.x
    by = curr.y-prev.y
    # Next edge vector (after)
    ax = next.x-curr.x
    ay = next.y-curr.y
    # Calculate sign flips using the next edge vector (after), recording the first sign
    if ax > 0:
      if x_sign == 0: x_first_sign = 1
      elif x_sign < 0: x_flips += 1
      x_sign = 1
    elif ax < 0:
      if x_sign == 0: x_first_sign = -1
      elif x_sign > 0: x_flips += 1
      x_sign = -1
    if x_flips > 2: return False
    if ay > 0:
      if y_sign == 0: y_first_sign = 1
      elif y_sign < 0: y_flips += 1
      y_sign = 1
    elif ay < 0:
      if y_sign == 0: y_first_sign = -1
      elif y_sign > 0: y_flips += 1
      y_sign = -1
    if y_flips > 2: return False
    # Find out the orientation of this pair of edges, and ensure it does not differ from previous ones.
    w = bx*ay-ax*by
    if w_sign == 0 and w != 0: w_sign = w
    elif (w_sign > 0) != (w > 0): return False
  # Final/wraparound sign flips:
  if x_sign != 0 and x_first_sign != 0 and x_sign != x_first_sign: x_flips += 1
  if y_sign != 0 and y_first_sign != 0 and y_sign != y_first_sign: y_flips += 1
  # Concave polygons have two sign flips along each axis.
  if not x_flips == y_flips == 2: return False
  # This is a convex polygon
  return True


string = input('> ')
numbers = list(map(float, string.replace(' ', '').replace('(', '').replace(')', '').split(',')))
vertices = [Point(vertex) for vertex in zip(*[iter(numbers)]*2)]
n = len(vertices)

convex = is_convex(vertices)
area = abs(1/2*sum(prev**curr for prev, curr in zip([vertices[-1]]+vertices[:-1], vertices)))
perimeter = sum(prev|curr for prev, curr in zip([vertices[-1]]+vertices[:-1], vertices))
angle_sum = 180*(n-2)
print('Convex' if convex else 'Concave')
print('Area:', area, 'sq units')
print('Perimeter:', perimeter, 'units')
print('Interior Angle Sum:', angle_sum, 'degrees')
print('Exterior Angle Sum: 360 degrees')




