// http://nifty.stanford.edu/2011/schwarz-evil-hangman
#include <iostream>
#include <fstream>
#include <cctype>
#include <set>
#include <map>
#include <algorithm>
using namespace std;

typedef int Match;  // See GetMatch

Match GetMatch(const string &word);  // Returns binary match, i.e. 's' & "business" -> 0b00100011 (which is the same as 0b100011)
bool isMatch(const string &word, Match &match);  // Returns whether or not a word matches a match

ifstream fin("dictionary.txt");
char guess;  // For temporarily saving user input
set<string> words;  // List of words
set<int> lengths;  // All possible lengths of words
set<char> letters;  // List of guessed letters
int length;  // Length that the user chose
int guesses;  // Number of guesses left
bool show_total;  // Show number of words that are left
string display_word;  // Word that is displayed, i.e. b-sin-ss


int main() {

  // Add words to a set for easy removal
  for (string word; fin >> word;) {
    words.insert(word);
    lengths.insert(word.length());
  }

  cout << "Evil Hangman" << endl;

  // Prompt for length of word
  do {
    cout << "Enter length: ";
    cin >> length;
  }
  while (lengths.find(length) == lengths.end());

  // Remove words with incorrect lengths
  words.erase(remove_if(words.begin(), words.end(), [](const string &word){return word.length() == length;}), words.end());

  // Set display word
  display_word = string(length, '-');

  // Prompt for number of guesses
  do {
    cout << "Enter number of guesses: ";
    cin >> guesses;
  }
  while (guesses <= 0);

  // Prompt for running total of words left
  do {
    cout << "Show number of words left? [y/n]: ";
    cin >> guess;
  }
  while (guess != 'y' && guess != 'n');
  show_total = (guess == 'y');

  // While there are still guesses left
  for (;guesses > 0; --guesses) {

    cout << "You have " << guesses+1 << " guesses left.\r\n";
    cout << "Used letters:";

    // Enter guessed letters
    for (const char &letter: letters) {
      cout << ' ' << letter;
    }
    cout << "\nWord: " << display_word << endl;

    // Get unique guess
    do {
      cout << "Enter guess: ";
      cin >> guess;
      if (islower(guess)) guess -= 32;
    }
    while (!isalpha(guess) || letters.find(guess) != letters.end());

    // Fill in map with number of matches
    map<Match, int, greater<Match>> matches;
    for (const string &word: words) {
      Match match = GetMatch(word);
      auto it = matches.find(match);
      if (it == matches.end()) matches.insert({match, 1});
      else it->second += 1;
    }

    // Are there any matches?
    if (matches.empty()) cout << "Sorry, there are no " << guess << "'s\n"; // No matches
    else {

      // Get match with most matches (already sorted greatest to least) and print stuff
      Match best_match = matches.begin()->first;
      if (show_total) cout << "There are now " << matches.begin()->second << " possible words";

      // Filter words based on best match
      words.erase(remove_if(words.begin(), words.end(), [&](const string &word){return !isMatch(word, best_match);}), words.end());

      // Has the player won?
      if (words.size() == 1) {
        cout << "You win! The word was: " << *words.begin() << endl;
        return EXIT_SUCCESS;
      }

      // Update display word
      for (int i = 0; i < length; i++) if (best_match&1<<i) display_word[i] = guess;
    }

    cout << '\n' << endl;
  }

  // Print out random possible word on loss
  auto it = words.begin();
  advance(it, rand()%words.size());
  cout << "You lose! The word was: " << *it;

  return EXIT_SUCCESS;
}


Match GetMatch(const string &word) {
  Match value;
  for (const char& letter: word) {
    value <<= 1;
    value += (letter == guess);
  }
  return value;
}


bool isMatch(const string &word, Match &match) {
  for (int i = 0; i < length; i++) if ((word[i] == guess) != (match&1<<i)) return false;
  return true;
}

