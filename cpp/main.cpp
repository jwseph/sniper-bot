// http://nifty.stanford.edu/2011/schwarz-evil-hangman
#include <iostream>
#include <fstream>
#include <cctype>
#include <set>
#include <map>
#include <algorithm>
#include <vector>
#include "dictionary.cpp"
using namespace std;

typedef int Match;  // See GetMatch

Match GetMatch(const string &word);  // Returns binary match, i.e. 's' & "business" -> 0b00100011 (which is the same as 0b100011)
bool isMatch(const string &word, Match match);  // Returns whether or not a word matches a match

// ifstream fin("dictionary.txt");
char guess;  // For temporarily saving user input
vector<string> words;  // List of words
set<int> lengths;  // All possible lengths of words
set<char> letters;  // List of guessed letters
int length;  // Length that the user chose
int guesses;  // Number of guesses left
bool show_total;  // Show number of words that are left
string display_word;  // Word that is displayed, i.e. b-sin-ss


int main() {

  // Add words to a set for easy removal
  for (string word; fin >> word;) {
    words.push_back(word);
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
  words.erase(
    remove_if(
      words.begin(),
      words.end(),
      [](const string word)->bool {return word.size() != length;}
    ),
    words.end()
  );

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

    cout << "\n\nYou have " << guesses << " guesses left.\nUsed letters:";

    // Enter guessed letters
    for (const char &letter: letters) {
      cout << ' ' << letter;
    }
    cout << "\nWord: " << display_word << endl;

    // Get unique guess
    do {
      cout << "Enter guess: ";
      cin >> guess;
      if (isupper(guess)) guess += 32;
    }
    while (!isalpha(guess) || letters.find(guess) != letters.end());
    letters.insert(guess);

    // Fill in map with number of matches
    map<Match, int> matches;
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
      auto it = max_element(matches.begin(), matches.end(), [](const auto &word1, const auto &word2) {return word2.second > word1.second;});
      Match best_match = it->first;
      if (show_total && matches.size() > 1) cout << "There are now " << it->second << " possible words\n";

      // Filter words based on best match
      words.erase(remove_if(words.begin(), words.end(), [&](const string &word){return !isMatch(word, best_match);}), words.end());

      // Update display word
      for (int i = 0; i < length; i++) if (best_match>>(length-1-i)&1) display_word[i] = guess;

      // Has the player won?
      if (words.size() == 1 && all_of(display_word.begin(), display_word.end(), [](const char &letter) {return letter != '-';})) {
        cout << "You win! The word was: " << *words.begin() << endl;
        return 0;
      }
    }
  }

  // Print out random possible word on loss (below code is compatible with any container)
  auto it = words.begin();
  advance(it, rand()%words.size());
  cout << "You lose! The word was: " << *it;

  return 0;
}


Match GetMatch(const string &word) {
  Match value;
  for (const char& letter: word) {
    value <<= 1;
    value += (letter == guess);
  }
  return value;
}


bool isMatch(const string &word, Match match) {
  for (int i = 0; i < length; i++) if ((word[i] == guess) != (match>>(length-1-i)&1)) return false;
  return true;
}
