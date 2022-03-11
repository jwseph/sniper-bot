solve_linear = lambda equation, var='x': (lambda grouped: -grouped.real/grouped.imag)(eval((equation.replace("=","-(")+")").replace(var, '1j')))


from scipy.optimize import fsolve
import re
import numpy as np
from numpy import pi, e, sqrt, log, abs, sin, cos, tan, arcsin, arccos, arctan


def sanitize(string):
  string = string.replace(' ', '')
  assert '=' in string, 'Only equations are allowed'
  # assert not re.match(r'[A-Za-z][A-Za-z]+', string), 'Only single letters are allowed in string'
  string = re.sub(r'(?:(\d)([A-Za-z]))|(?:([A-Za-z])(\d))|(?:(?<![A-Za-z])([\dA-Za-z])(\())|(?:(\))([\dA-Za-z]))', r'\1\3\5\7*\2\4\6\8', string.replace('^', '**'))
  string = string.replace('=', '-(')+')'
  variables = set(re.findall(r'(?<![A-Za-z])[A-Za-z](?![A-Za-z])', string))
  return string, variables


equations = []
variables = set()
while True:
  inp = input()
  if inp == '' or inp.isspace(): break
  sanitized = sanitize(inp)
  equations.append(sanitized[0])
  variables.update(sanitized[1])
variables = sorted(list(variables))

exec(f"""
def f(p):
  {','.join(variables)} = p
  return ({', '.join(equations)})
print('\\n'.join(variable+' = '+re.sub(r'.0$', '', str(round(value, 8))) for variable, value in zip(variables, fsolve(f, ({'1,'*(len(variables)-1)}1)))))
""")