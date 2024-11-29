import random
import contextlib
import nltk
import requests
from nltk.corpus import words
from rich.console import Console
from rich.theme import Theme
from string import ascii_uppercase

try:
    words.words()
except LookupError:
    nltk.download("words")

console = Console(width=40, theme=Theme({"warning": "red on yellow"}))


def show_welcome_screen():
    """Display a welcome screen with ASCII art."""
    console.clear()
    console.rule("[bold green]Welcome to Wordle![/bold green]")
    console.print("""
[bold cyan]
  __        __   _                            _        
  \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___  
   \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \ 
    \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
     \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/ 
[/bold cyan]
""", justify="center")
    console.print(
        "Wordle is a simple word-guessing game. Try to guess the word in the fewest attempts possible!\n", justify="center")
    console.input("[bold green]Press Enter to start the game![/bold green]")


def show_progress_bar(current, total):
    """Display a progress bar for the number of guesses."""
    percentage = (current / total) * 100
    bar_length = 30  # Length of the progress bar
    filled_length = int(bar_length * current // total)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    console.print(
        f"[bold green]Guesses Used:[/] |{bar}| {current}/{total} ({percentage:.0f}%)", justify="center")


def show_celebration():
    """Display celebratory ASCII art for winning."""
    console.print("""
[bold green]
██╗   ██╗ ██████╗ ██╗   ██╗███████╗██████╗ 
██║   ██║██╔═══██╗██║   ██║██╔════╝██╔══██╗
██║   ██║██║   ██║██║   ██║█████╗  ██████╔╝
╚██╗ ██╔╝██║   ██║██║   ██║██╔══╝  ██╔═══╝ 
 ╚████╔╝ ╚██████╔╝╚██████╔╝███████╗██║     
  ╚═══╝   ╚═════╝  ╚═════╝ ╚══════╝╚═╝     
[/bold green]
""", justify="center")
    console.print(
        "[bold cyan]Congratulations! You guessed the word![/bold cyan]\n", justify="center")


def show_consolation(word):
    """Display a consolation message with ASCII art."""
    console.print("""
[bold red]
   __     ______  _    _   _      ____   _____ 
   \ \   / / __ \| |  | | | |    / __ \ / ____|
    \ \_/ / |  | | |  | | | |   | |  | | (___  
     \   /| |  | | |  | | | |   | |  | |\___ \ 
      | | | |__| | |__| | | |___| |__| |____) |
      |_|  \____/ \____/  |______\____/|_____/ 
[/bold red]
""", justify="center")
    console.print(
        f"[bold red]Better luck next time! The word was {word}.[/bold red]\n", justify="center")


class WordleGame:
    def __init__(self):
        self.NUM_LETTERS = 5
        self.NUM_GUESSES = 6
        self.word = ""
        self.guesses = []
        self.hint_used = False

    def set_difficulty(self):
        """Set the difficulty level and adjust game parameters."""
        console.print("\nSelect difficulty level:")
        console.print("1. Easy (6 letters, 7 guesses)")
        console.print("2. Medium (5 letters, 6 guesses) [default]")
        console.print("3. Hard (4 letters, 5 guesses)")

        choice = console.input("\nEnter choice (1/2/3): ").strip()
        if choice == "1":
            self.NUM_LETTERS = 6
            self.NUM_GUESSES = 7
        elif choice == "3":
            self.NUM_LETTERS = 4
            self.NUM_GUESSES = 5
        else:
            self.NUM_LETTERS = 5
            self.NUM_GUESSES = 6

    def get_word(self):
        """Fetch a random word of the correct length."""
        word_list = [word.upper() for word in words.words() if len(
            word) == self.NUM_LETTERS and word.isalpha()]
        if not word_list:
            console.print(f"No words available for {self.NUM_LETTERS} letters. Please choose another difficulty.",
                          style="warning")
            return None
        return random.choice(word_list)

    def guess_word(self, previous_guesses):
        """Prompt the user to guess a word or use a hint."""
        while True:
            guess = console.input("\nGuess word (or type 'hint'): ").upper()
            if guess == "HINT":
                if self.hint_used:
                    console.print(
                        "You have already used your hint for this game.", style="warning")
                else:
                    self.use_hint()
                continue
            if guess in previous_guesses:
                console.print(
                    f"You've already guessed {guess}.", style="warning")
            elif len(guess) != self.NUM_LETTERS:
                console.print(
                    f"Your guess must be {self.NUM_LETTERS} letters.", style="warning")
            elif not guess.isalpha():
                console.print(
                    f"Invalid input: Only English letters are allowed.", style="warning")
            else:
                return guess

    def use_hint(self):
        """Reveal one correct letter in its correct position."""
        for i, letter in enumerate(self.word):
            if self.guesses[-1][i] == "_":
                self.guesses[-1] = self.guesses[-1][:i] + \
                    letter + self.guesses[-1][i + 1:]
                console.print(
                    f"[bold white on blue]Hint: The letter '{letter}' is in position {i + 1}[/]")
                self.hint_used = True
                return
        console.print(
            "No hints available; you've already uncovered all positions!", style="warning")

    def show_guesses(self):
        """Display all guesses with color-coded feedback."""
        letter_status = {letter: letter for letter in ascii_uppercase}
        for guess in self.guesses:
            styled_guess = []
            for g_letter, w_letter in zip(guess, self.word):
                if g_letter == w_letter:
                    style = "bold white on green"
                elif g_letter in self.word:
                    style = "bold white on yellow"
                else:
                    style = "white on dim"
                styled_guess.append(f"[{style}]{g_letter}[/]")
                if g_letter in ascii_uppercase:
                    letter_status[g_letter] = f"[{style}]{g_letter}[/]"
            console.print("".join(styled_guess), justify="center")
        console.print("\n" + "".join(letter_status.values()), justify="center")

    def refresh_page(self, headline):
        """Clear the console and display a headline."""
        console.clear()
        console.rule(f"[bold blue]:leafy_green: {headline} :leafy_green:[/]\n")

    def fetch_word_definition(self, word):
        """
        Fetch the definition of a word from DictionaryAPI.
        """
        try:
            response = requests.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            if response.status_code == 200:
                data = response.json()
                meanings = data[0].get("meanings", [])
                if not meanings:
                    return "No definitions found."
                definition = meanings[0]["definitions"][0]["definition"]
                return definition
            elif response.status_code == 404:
                return "Word not found in the dictionary."
            else:
                return "Error fetching definition. Try again later."
        except Exception as e:
            return f"An error occurred: {e}"

    def game_over(self, guessed_correctly, word):
        """Handle game-over logic."""
        self.refresh_page(headline="Game Over")
        self.show_guesses()
        if guessed_correctly:
            console.print(
                f"\n[bold white on green]Correct! The word was {self.word}[/]")
        else:
            console.print(
                f"\n[bold white on red]Sorry, the word was {self.word}[/]")
        console.print("\nFetching word definition...")
        definition = self.fetch_word_definition(word)
        console.print(f"\n[bold blue]Definition of {word}:[/] {definition}")

    def play(self):
        """Run the main game loop."""
        while True:
            show_welcome_screen()
            self.refresh_page("Wordle")
            self.set_difficulty()
            self.word = self.get_word()
            if not self.word:
                continue

            self.guesses = ["_" * self.NUM_LETTERS] * self.NUM_GUESSES
            self.hint_used = False
            guessed_correctly = False

            with contextlib.suppress(KeyboardInterrupt):
                for attempt in range(self.NUM_GUESSES):
                    self.refresh_page(headline=f"Attempt {attempt + 1}")
                    self.show_guesses()
                    self.guesses[attempt] = self.guess_word(
                        previous_guesses=self.guesses[:attempt])
                    if self.guesses[attempt] == self.word:
                        guessed_correctly = True
                        break

            self.game_over(guessed_correctly, word=self.word)
            if guessed_correctly:
                show_celebration()
            else:
                show_consolation(word=self.word)
            play_again = console.input(
                "\nDo you want to play again? (y/n): ").lower()
            if play_again != "y":
                console.print("\n[bold cyan]Thanks for playing! Goodbye![/]")
                break


if __name__ == "__main__":
    game = WordleGame()
    game.play()
