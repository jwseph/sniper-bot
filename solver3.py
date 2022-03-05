# import re

# string = input('> ').replace(' ', '')
# string = re.sub(r'(?:(?<=[-+])|(?<=^))(?=[^-\d])', '1', string)
# str_terms = re.split(r'(?<=[A-Za-z\d])(?:\+|(?=\-))', string)
# assert all(re.match(r'-?\d+\*?[xy]?', str_term) for str_term in str_terms), 'bruh'
# terms = {(int(re.search(r'-?\d+(?=\D|$)', str_term).group()), re.search(r'[^-\d*].*|$', str_term).group()) for str_term in str_terms}

# print(terms)


def solve_linear(equation, var='x'):
  expression = equation.replace("=","-(")+")"
  grouped = eval(expression.replace(var, '1j'))
  return -grouped.real/grouped.imag


solve = lambda equation, var='x': (lambda grouped: -grouped.real/grouped.imag)(eval((equation.replace("=","-(")+")").replace(var, '1j')))











