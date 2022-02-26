import re
from copy import copy, deepcopy
import numpy as np


class Term:  # Maybe add EXPR for verifying (also add to Polynomial too)

  def __init__(self, string='0'):
    string = string.replace(' ', '')
    self.coefficient = int([*re.findall(r'[\-\d]+(?:(?=[A-Za-z])|(?=$))', string), '1'][0]) if not re.match(r'-([A-Za-z])', string) else -1
    self.variable = [*re.findall(r'[A-Za-z]+', string), None][0]
    self.degree = int([*re.findall(r'(?<=\^)\d+', string), '1'][0])

  def copy(self):
    return copy(self)

  def __repr__(self):
    return f"{self.coefficient if self.coefficient != 1 else ''}{self.variable if self.variable != None else ''}{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[self.degree//10**i%10] for i in range(len(str(self.degree))-1, -1, -1)) if self.variable != None and self.degree != 1 else ''}"

  def __neg__(self):
    term = self.copy()
    term.coefficient *= -1
    return term

  def __mul__(self, other):  # Scalar
    term = self.copy()
    term.coefficient *= other
    return term

  def __rmul__(self, other):
    term = self.copy()
    term.coefficient *= other
    return term

  def __add__(self, other):
    assert self & other
    term = self.copy()
    term.coefficient += other.coefficient
    return term

  def __iadd__(self, other):
    assert self & other
    self.coefficient += other.coefficient
    return self

  def __sub__(self, other):
    assert self & other
    term = self.copy()
    term.coefficient -= other.coefficient
    return term

  def __isub__(self, other):
    assert self & other
    self.coefficient -= other.coefficient
    return self

  def __and__(self, other):
    return self.variable == other.variable and self.degree == other.degree



class Polynomial:

  def __init__(self, string=''):
    string = string.replace(' ', '')
    str_terms = re.split(r'(?<=[A-Za-z\d])(?:\+|(?=\-))', string)
    self.terms = [Term(str_term) for str_term in str_terms]
    self.degree = max((term.degree for term in self.terms), default=None)

  def copy(self):
    return deepcopy(self)

  def __repr__(self):
    return '+'.join(map(str, self.terms)).replace('+-', '-')

  def __contains__(self, degree):
    return next((True for term in self.terms if degree == term.degree), False)
    
  def __getitem__(self, degree):
    return next((term for term in self.terms if degree == term.degree), Term('0'))

  def __neg__(self):
    polynomial = self.copy()
    for term in polynomial.terms: term *= -1
    return polynomial

  def __mul__(self, other):  # Scalar
    polynomial = self.copy()
    if other == 0: polynomial.terms, polynomial.degree = [], None
    for term in polynomial.terms: term *= other
    return polynomial

  def __rmul__(self, other):
    polynomial = self.copy()
    if other == 0: polynomial.terms, polynomial.degree = [], None
    for term in polynomial.terms: term *= other
    return polynomial

  def __imul__(self, other):
    if other == 0: self.terms, self.degree = [], None
    for term in self.terms: term *= other
    return self

  def __add__(self, other):
    polynomial = self.copy()
    polynomial.terms = self.terms+other.copy().terms
    polynomial.simplify()
    polynomial.degree = max(term.degree for term in polynomial.terms)
    return polynomial

  def __iadd__(self, other):
    self.terms += other.copy().terms
    self.simplify()
    self.degree = max(term.degree for term in self.terms)
    return self

  def __sub__(self, other):
    return self+-other

  def __isub__(self, other):
    return self.__iadd__(-other)

  def sort(self):
    self.terms.sort(key=lambda term: term.degree, reverse=True)

  def simplify(self):  # Combine like terms
    self.sort()
    i = len(self.terms)-1
    while i > 0:
      if self.terms[i] & self.terms[i-1]:
        self.terms[i-1] += self.terms.pop(i)
        if self.terms[i-1].coefficient == 0:
          del self.terms[i-1]
          i -= 1
      print(self)
      i -= 1
    self.degree = max(term.degree for term in self.terms)

  # def normalize(self, degree=None):
  #   self.sort()
  #   new_terms = []
  #   if degree == None:
  #     degree = self.degree
  #   else:
  #     pass
  #   for term in self.terms:

  #     for n in range(degree-term.degree):
  #       new_terms.append(Term(f''))
  #       degree -= 1
  #       pass


class Equation:

  def __init__(self, string):
    string = string.replace(' ', '')
    str_left, str_right = string.split('=', 1)
    self.left = Polynomial(str_left)
    self.right = Polynomial(str_right)

  def copy(self):
    return deepcopy(self)

  def __repr__(self):
    return str(self.left)+' = '+str(self.right)

  def __neg__(self):
    equation = self.copy()
    equation.left *= -1
    equation.right *= -1
    return equation

  def __mul__(self, other):  # Scalar
    equation = self.copy()
    equation.left *= other
    equation.right *= other
    return equation

  def __mul__(self, other):
    equation = self.copy()
    equation.left *= other
    equation.right *= other
    return equation

  def __imul__(self, other):
    self.left *= other
    self.right *= other
    return self

  def __add__(self, other):
    equation = self.copy()
    equation.left += other.left
    equation.right += other.right
    return equation

  def __iadd__(self, other):
    self.left += other.left
    self.right += other.right
    return self

  def __sub__(self, other):
    equation = self.copy()
    equation.left -= other.left
    equation.right -= other.right
    return equation

  def __isub__(self, other):
    self.left -= other.left
    self.right -= other.right
    return self

  def simplify(self):
    self.left -= self.right
    self.right = Polynomial()
    self.left.simplify()


class SimplifiedEquation(Equation):

  def __init__(self, equation):
    equation = equation.copy()
    equation.simplify()
    self.left = equation.left
    self.right = equation.right
    self.terms = {self.left[degree] if degree in self.left else  for degree in range(self.left.degree-1, -1, -1)}

  def get(degree):
    return 



class System:

  def __init__(self, string):
    string = string.replace(' ', '')
    self.equations = [Equation(equation) for equation in string.split('\n')]

  def __repr__(self):
    return '\n'.join(map(str, self.equations))


class LinearSystem(System):

  def __init__(self, string):
    super().__init__(string)
    assert len(self.equations) == 2, "Linear system must have two equations"
    self.equation1, self.equation2 = self.equations

  def simplify(self):
    self.equation1.simplify()
    self.equation2.simplify()

  def solve(self):
    self.simplify()

    pass











