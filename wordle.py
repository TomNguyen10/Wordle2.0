import random
import contextlib
import nltk
from nltk.corpus import words
from rich.console import Console
from rich.theme import Theme
from string import ascii_letters, ascii_uppercase
import time

nltk.download("words")

console = Console(width=60, theme=Theme({"warning": "red on yellow"}))

NUM_LETTERS = 5
NUM_GUESSES = 6
HINT_LIMIT = 2
SCORES = {
    "correct_guess": 10,
    "wrong_guess": -2,
    "hint_penalty_position": -3,
    "hint_penalty_anagram": -2,
}
WORD_CATEGORIES = {
    "Animals": ["tiger", "eagle", "horse", "zebra", "whale"],
    "Foods": ["apple", "pizza", "bread", "pasta", "grape"],
    "Countries": ["italy", "spain", "japan", "india", "china"],
}

difficulty_levels = {
    "easy": 10,
    "medium": 6,
    "hard": 4
}

leaderboard = []


def get_word_by_difficulty(level):
    word_list = words.words()
    if level == "easy":
        return random.choice([word for word in word_list if len(word) == 5 and word.islower()]).upper()
    elif level == "medium":
        return random.choice([word for word in word_list if len(word) == 6 and word.islower()]).upper()
    elif level == "hard":
        return random.choice([word for word in word_list if len(word) == 7 and word.islower()]).upper()
    else:
        return random.choice(word_list).upper()


def get_word_from_category(category):
    if category in WORD_CATEGORIES:
        return random.choice(WORD_CATEGORIES[category]).upper()
    else:
        return get_word_by_difficulty("medium")


def show_anagram_hint(word):
    scrambled = ''.join(random.sample(word, len(word)))
    console.print(
        f"Anagram hint: [bold blue]{scrambled}[/] (penalty applied)", style="warning")


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


def reveal_letter_hint(word, guesses):
    hidden_letters = [i for i, letter in enumerate(
        word) if all(g[i] != letter for g in guesses)]
    if hidden_letters:
        random_position = random.choice(hidden_letters)
        hint_letter = word[random_position]
        console.print(
            f"Hint: The letter '{hint_letter}' is at position {random_position + 1}", style="bold blue")
        return hint_letter
    return ""


def encouragement_message():
    console.print("[bold cyan]Keep going! You're doing great![/]")
    console.print("""
    ──────▄▌▐▀▀▀▀▀▀▀▀▀▀▀▌
    ───▄▄██▌█▄▄▄▄▄▄▄▄▄▄▐
    ▄▄▄▌▐██▌█─▌▌─▌▌─▌▌─▐
    ███████▌█──────────▐
    ▀❍▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
    """, justify="center")


def celebration_animation():
    console.print("[bold green]Congratulations! You guessed it![/]")
    console.print("""
    ────█─▄▀█──█▀▄─█────
    ───▐▌──────────▐▌──
    ───█▌▀▄──▄▄──▄▀▐█──
    ────▀▄▄██▄▀▄▀▄██▀───
    """, justify="center")


def game_over(guesses, word, guessed_correctly):
    if guessed_correctly:
        celebration_animation()
    else:
        console.print(f"\n[bold white on red]Sorry, the word was {word}[/]")
        encouragement_message()


def refresh_page(headline):
    console.clear()
    console.rule(f"[bold blue]:leafy_green: {headline} :leafy_green:[/]\n")


def show_leaderboard():
    console.print("\n[bold magenta]Leaderboard[/]")
    for idx, score in enumerate(sorted(leaderboard, reverse=True)[:5], 1):
        console.print(f"{idx}. {score} points")
    console.print("\n")


def main():
    score = 0
    games_played = 0
    games_won = 0

    while True:
        refresh_page("Wordle")

        show_leaderboard()

        difficulty = console.input(
            "Choose difficulty (easy, medium, hard): ").lower()
        category = console.input(
            "Choose a category or type 'any': ").strip().capitalize()

        if category != "Any" and category in WORD_CATEGORIES:
            word = get_word_from_category(category)
        else:
            word = get_word_by_difficulty(difficulty)

        hints_used = 0
        multiplier = 2 if random.random() < 0.2 else 1
        guesses = ["_" * NUM_LETTERS] * NUM_GUESSES
        with contextlib.suppress(KeyboardInterrupt):
            for idx in range(NUM_GUESSES):
                refresh_page(
                    f"Guess {idx + 1}/{NUM_GUESSES} (Score Multiplier: x{multiplier})")
                show_guesses(guesses, word)

                user_action = console.input(
                    "\nType 'guess' to guess, 'hint' for a letter hint, or 'anagram' for an anagram hint: ").strip().lower()

                if user_action == "hint":
                    if hints_used >= HINT_LIMIT:
                        console.print(
                            "No more hints allowed this game.", style="warning")
                    else:
                        reveal_letter_hint(word, guesses)
                        hints_used += 1
                        score += SCORES["hint_penalty_position"]
                elif user_action == "anagram":
                    if hints_used >= HINT_LIMIT:
                        console.print(
                            "No more hints allowed this game.", style="warning")
                    else:
                        show_anagram_hint(word)
                        hints_used += 1
                        score += SCORES["hint_penalty_anagram"]
                elif user_action == "guess":
                    guess = console.input("Guess word: ").upper()
                    if guess in guesses[:idx]:
                        console.print(
                            f"You've already guessed {guess}.", style="warning")
                        continue
                    if len(guess) != NUM_LETTERS:
                        console.print(
                            "Your guess must be 5 letters.", style="warning")
                        continue
                    guesses[idx] = guess
                    if guess == word:
                        games_won += 1
                        game_over(guesses, word, True)
                        score += SCORES["correct_guess"] * multiplier
                        break
                    else:
                        score += SCORES["wrong_guess"]
                else:
                    console.print("Invalid action.", style="warning")
                    continue

            if guesses[idx] != word:
                game_over(guesses, word, False)

            games_played += 1
            console.print(
                f"\nGames Played: {games_played} | Wins: {games_won} | Losses: {games_played - games_won}")
            console.print(f"Total Score: {score}")

            leaderboard.append(score)
            play_again = console.input(
                "\nDo you want to play again? (y/n): ").lower()
            if play_again != "y":
                break


main()
