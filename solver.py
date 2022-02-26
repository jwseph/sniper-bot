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

  def __mul__(self, other):
    term = self.copy()
    term.coefficient *= other
    return term

  def __rmul__(self, other):
    term = self.copy()
    term.coefficient *= other
    return term



class Polynomial:

  def __init__(self, string=''):
    string = string.replace(' ', '')
    str_terms = re.split(r'(?<=[A-Za-z\d])(?:\+|(?=\-))', string)
    self.terms = [Term(str_term) for str_term in str_terms]
    self.degree = max(term.degree for term in self.terms)

  def copy(self):
    return deepcopy(self)

  def __repr__(self):
    return '+'.join(map(str, self.terms)).replace('+-', '-')

  def __neg__(self):
    polynomial = copy(self)
    polynomial.terms = [-term for term in self.terms]

  def sort(self):
    self.terms.sort(key=lambda term: term.degree, reverse=True)

  def normalize(self, degree=None):
    self.sort()
    if degree == None:
      degree = self.degree
    else:
    for term in self.terms:
      if
      degree -= 1


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

  def normalize(self):
    self.left += -self.right
    self.right = Polynomial()
    self.left.sort()








