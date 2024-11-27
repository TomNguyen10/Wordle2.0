import random
import contextlib
import nltk
from nltk.corpus import words
from rich.console import Console
from rich.theme import Theme
from string import ascii_letters, ascii_uppercase

nltk.download("words")

console = Console(width=40, theme=Theme({"warning": "red on yellow"}))

# Global variables to be adjusted based on difficulty
NUM_LETTERS = 5
NUM_GUESSES = 6


def set_difficulty():
    console.print("\nSelect difficulty level:")
    console.print("1. Easy (6 letters, 7 guesses)")
    console.print("2. Medium (5 letters, 6 guesses) [default]")
    console.print("3. Hard (4 letters, 5 guesses)")
    choice = console.input("\nEnter choice (1/2/3): ").strip()

    global NUM_LETTERS, NUM_GUESSES

    if choice == "1":
        NUM_LETTERS = 6
        NUM_GUESSES = 7
    elif choice == "3":
        NUM_LETTERS = 4
        NUM_GUESSES = 5
    else:
        NUM_LETTERS = 5
        NUM_GUESSES = 6


def get_word():
    word_list = words.words()
    word_list_length_n = [
        word for word in word_list if len(word) == NUM_LETTERS]
    random_word = random.choice(word_list_length_n).upper()
    return random_word


def guess_word(previous_guesses):
    guess = console.input("\nGuess word: ").upper()
    if guess in previous_guesses:
        console.print(f"You've already guessed {guess}.", style="warning")
        return guess_word(previous_guesses)
    if len(guess) != NUM_LETTERS:
        console.print(
            f"Your guess must be {NUM_LETTERS} letters.", style="warning")
        return guess_word(previous_guesses)
    if any((invalid := letter) not in ascii_letters for letter in guess):
        console.print(
            f"Invalid letter: '{invalid}'. Please use English letters.", style="warning")
        return guess_word(previous_guesses)
    return guess


def show_guesses(guesses, word):
    letter_status = {letter: letter for letter in ascii_uppercase}
    for guess in guesses:
        styled_guess = []
        for letter, correct in zip(guess, word):
            if letter == correct:
                style = "bold white on green"
            elif letter in word:
                style = "bold white on yellow"
            elif letter in ascii_letters:
                style = "white on #666666"
            else:
                style = "dim"
            styled_guess.append(f"[{style}]{letter}[/]")
            if letter != "_":
                letter_status[letter] = f"[{style}]{letter}[/]"
        console.print("".join(styled_guess), justify="center")
    console.print("\n" + "".join(letter_status.values()), justify="center")


def game_over(guesses, word, guessed_correctly):
    refresh_page(headline="Game Over")
    show_guesses(guesses, word)
    if guessed_correctly:
        console.print(f"\n[bold white on green]Correct, the word is {word}[/]")
    else:
        console.print(f"\n[bold white on red]Sorry, the word was {word}[/]")


def refresh_page(headline):
    console.clear()
    console.rule(f"[bold blue]:leafy_green: {headline} :leafy_green:[/]\n")


def main():
    while True:
        refresh_page("Wordle")
        set_difficulty()
        word = get_word()
        guesses = ["_" * NUM_LETTERS] * NUM_GUESSES
        with contextlib.suppress(KeyboardInterrupt):
            for idx in range(NUM_GUESSES):
                refresh_page(headline=f"Guess {idx + 1}")
                show_guesses(guesses, word)
                guesses[idx] = guess_word(previous_guesses=guesses[:idx])
                if guesses[idx] == word:
                    break
        game_over(guesses, word, guessed_correctly=guesses[idx] == word)
        play_again = console.input(
            "\nDo you want to play again? (y/n): ").lower()
        if play_again != "y":
            break


main()
