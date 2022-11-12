import random
import re
from urllib.parse import urlparse


def is_url(word):
  try:
    result = urlparse(word)
    return all([result.scheme, result.netloc])
  except:
    return False

DEFAULTS = {
  'SPACES': {'faces': 0.05, 'actions': 0.075, 'stutters': 0.1},
  'WORDS': 1,
  'EXCLAMATIONS': 1
}

_spaces_modifier_faces = 0.075 #0.05
_spaces_modifier_actions = 0.15 #0.075
_spaces_modifier_stutters = 0.2 #0.1
_words_modifier = 1
_exclamations_modifier = 1

faces = [
  "(・`ω´・)",
  ";;w;;",
  "OwO",
  "UwU",
  ">w<",
  "^w^",
  "uwu",
  "^-^",
  ":3",
  "x3"
]
exclamations = [
  "!?",
  "?!!",
  "?!?1",
  "!!11",
  "?!?!"
]
actions = [
  # "\*blushes\*",
  # "\*whispers to self\*",
  # "\*cries\*",
  # "\*screams\*",
  # "\*sweats\*",
  # "\*twerks\*",
  # "\*runs away\*",
  # "\*screeches\*",
  # "\*walks away\*",
  # "\*sees bulge\*",
  # "\*looks at you\*",
  # "\*notices bulge\*",
  # "\*starts twerking\*",
  # "\*huggles tightly\*",
  # "\*boops your nose\*",
  "\*bwushes\*",
  "\*whispews to sewf\*",
  "\*cwies\*",
  "\*scweams\*",
  "\*sweats\*",
  "\*twewks\*",
  "\*wuns away\*",
  "\*wawks away\*",
  "\*sees bulge\*",
  "\*wooks at you\*",
  "\*notices buldge\*",
  "\*stawts twewking\*",
  "\*huggles tightwy\*",
  "\*boops youw nose\*",
]
uwu_map = [
  [r"[rl]", r"w"],
  [r"[RL]", r"W"],
  [r"([nN])([aeiouAEIOU])", r"\1y\2"]
  [r"ove", r"uv"],
]

def uwuify_words(words:list) -> str:
  def f(word):
    if is_url(word): return word
    random.seed(word)
    for old_word, new_word in uwu_map:
      # Generate a random value for every map so words will be partly uwuified instead of not at all
      if random.random() > _words_modifier: continue
      word = re.sub(old_word, new_word, word)
    return word
  uwuified_sentence = map(f, words)
  return uwuified_sentence


def uwuify_spaces(words:list) -> str:
  def check_capital(word, first_character, words, index:int) -> str:
    # If the first character is upper, the word is less than or equal to 50% upper, and the previous word doesn't exist or has punctuation after it
    if (first_character.isupper()) and (sum(letter.isupper() for letter in word)/len(word) <= 0.5) and (index == 0 or words[index-1][-1] in '.!?\-'):
      # Remove the first capital letter
      return first_character.lower()+word[1:]
    else:
      return word
  def f(word:str, index:int) -> str:
    random.seed(word)
    r = random.random()
    if len(word) == 0: return word
    first_character = word[0]
    if r <= _spaces_modifier_faces:
      # Add random face before the word
      word += ' '+faces[random.randint(0, len(faces)-1)]
      word = check_capital(word, first_character, words, index)
    elif r <= _spaces_modifier_actions:
      # Add random action before the word
      word += ' '+actions[random.randint(0, len(actions)-1)]
      word = check_capital(word, first_character, words, index)
    elif r <= _spaces_modifier_stutters:
      # Add stutter with a length between 0 and 2
      stutter = random.randint(0, 2)
      word = (first_character+'-')*stutter+word
    return word
  uwuified_sentence = (f(word, index) for index, word in enumerate(words))
  return uwuified_sentence


def uwuify_exclamations(words:list) -> str:
  pattern = re.compile(r'[?!]+$')
  def f(word):
    random.seed(word)
    # If there are no exclamations return
    if not re.match(pattern, word) or random.random() > _exclamations_modifier: return word
    word = re.sub(pattern, '', word)+exclamations[random.randint(0, len(exclamations)-1)]
    return word
  uwuified_sentence = list(map(f, words))
  return uwuified_sentence


def uwuify_sentence(sentence:str) -> str:
  words = sentence.strip().split(' ')
  words = uwuify_spaces(uwuify_exclamations(uwuify_words(words)))
  uwuified_string = ' '.join(words)
  return uwuified_string

uwuify = uwuify_sentence
