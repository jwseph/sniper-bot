


string = input('> ')
numbers = list(map(int, string.replace(' ', '').replace('(', '').replace(')', '').split(',')))
points = list(zip(*[iter(numbers)]*2))
n = len(points)

area = abs(1/2*sum(points[i-1][0]*points[i][1]-points[i][0]*points[i-1][1] for i in range(n)))
perimeter = sum(((points[i-1][0]-points[i-1][1])**2+(points[i][0]-points[i][1])**2)**0.5 for i in range(n))
angle_sum = 180*(n-2)
print('Area:', area, 'sq units')
print('Perimeter:', perimeter, 'units')
print('Interior Angle Sum:', angle_sum, 'degrees')
print('Exterior Angle Sum: 360 degrees')

