import org.fusesource.jansi.Ansi;
import org.fusesource.jansi.AnsiConsole;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.net.URI;
import java.util.*;
import java.util.stream.Collectors;

import static org.fusesource.jansi.Ansi.Color.*;

public class WordleGame {
    private int numLetters = 5;
    private int numGuesses = 6;
    private static final String WORD_LIST_FILE = "words.txt";
    private String word = "";
    private List<String> guesses = new ArrayList<>();
    private boolean hintUsed = false;
    private static final Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        AnsiConsole.systemInstall();
        WordleGame game = new WordleGame();
        game.play();
        AnsiConsole.systemUninstall();
    }

    public void play() {
        while (true) {
            showWelcomeScreen();
            setDifficulty();
            word = getWord();
            if (word == null) continue;

            guesses = new ArrayList<>(Collections.nCopies(numGuesses, "_".repeat(numLetters)));
            hintUsed = false;
            boolean guessedCorrectly = false;

            for (int attempt = 0; attempt < numGuesses; attempt++) {
                refreshPage("Attempt " + (attempt + 1));
                showGuesses();
                String guess = guessWord(guesses.subList(0, attempt));
                guesses.set(attempt, guess);
                showProgressBar(attempt + 1, numGuesses);

                if (guess.equals(word)) {
                    guessedCorrectly = true;
                    break;
                }
            }

            gameOver(guessedCorrectly);
            if (!playAgain()) break;
        }
    }

    private void showWelcomeScreen() {
        clearConsole();
        System.out.println(Ansi.ansi()
                .fgBright(GREEN)
                .bold()
                .a("Welcome to Wordle!\n")
                .reset());
        System.out.println(Ansi.ansi()
                .fgBright(CYAN)
                .a("""
                     __        __   _                            _        
                     \\ \\      / /__| | ___ ___  _ __ ___   ___  | |_ ___  
                      \\ \\ /\\ / / _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\ | __/ _ \\ 
                       \\ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
                        \\_/\\_/ \\___|_|\\___\\___/|_| |_| |_|\\___|  \\__\\___/ 
                    """)
                .reset());
        System.out.println(Ansi.ansi()
                .fgBright(CYAN)
                .a("Wordle is a simple word-guessing game. Try to guess the word in the fewest attempts possible!\n")
                .reset());
        System.out.print("Press Enter to start the game!");
        scanner.nextLine();
    }

    private void setDifficulty() {
        System.out.println(Ansi.ansi().fgBright(BLUE).a("\nSelect difficulty level:").reset());
        System.out.println("1. Easy (6 letters, 7 guesses)");
        System.out.println("2. Medium (5 letters, 6 guesses) [default]");
        System.out.println("3. Hard (4 letters, 5 guesses)");

        String choice = scanner.nextLine().trim();
        switch (choice) {
            case "1":
                numLetters = 6;
                numGuesses = 7;
                break;
            case "3":
                numLetters = 4;
                numGuesses = 5;
                break;
            default:
                numLetters = 5;
                numGuesses = 6;
        }
    }

    private String getWord() {
        List<String> wordList = getWordsFromFile().stream()
                .filter(w -> w.length() == numLetters)
                .collect(Collectors.toList());

        if (wordList.isEmpty()) {
            System.out.println(Ansi.ansi().fgBright(RED).a("No words available for " + numLetters + " letters. Please choose another difficulty.").reset());
            return null;
        }
        return wordList.get(new Random().nextInt(wordList.size())).toUpperCase();
    }

    private String guessWord(List<String> previousGuesses) {
        while (true) {
            System.out.print("\nGuess word (or type 'hint'): ");
            String guess = scanner.nextLine().toUpperCase();
            if ("HINT".equals(guess)) {
                if (hintUsed) {
                    System.out.println(Ansi.ansi().fgBright(YELLOW).a("You have already used your hint for this game.").reset());
                } else {
                    useHint();
                }
                continue;
            }
            if (previousGuesses.contains(guess)) {
                System.out.println(Ansi.ansi().fgBright(YELLOW).a("You've already guessed " + guess + ".").reset());
            } else if (guess.length() != numLetters) {
                System.out.println(Ansi.ansi().fgBright(YELLOW).a("Your guess must be " + numLetters + " letters.").reset());
            } else if (!guess.matches("[A-Z]+")) {
                System.out.println(Ansi.ansi().fgBright(YELLOW).a("Invalid input: Only English letters are allowed.").reset());
            } else {
                return guess;
            }
        }
    }

    private void useHint() {
        for (int i = 0; i < word.length(); i++) {
            if (guesses.get(guesses.size() - 1).charAt(i) == '_') {
                char hintLetter = word.charAt(i);
                System.out.println(Ansi.ansi().fgBright(BLUE).a("Hint: The letter '" + hintLetter + "' is in position " + (i + 1)).reset());
                hintUsed = true;
                return;
            }
        }
        System.out.println(Ansi.ansi().fgBright(RED).a("No hints available; you've already uncovered all positions!").reset());
    }

    private void showGuesses() {
        System.out.println("\nGuesses:");
        for (String guess : guesses) {
            StringBuilder styledGuess = new StringBuilder();
            for (int i = 0; i < guess.length(); i++) {
                char gChar = guess.charAt(i);
                char wChar = word.charAt(i);
                if (gChar == wChar) {
                    styledGuess.append(Ansi.ansi().fgBright(GREEN).bold().a(gChar).reset());
                } else if (word.contains(String.valueOf(gChar))) {
                    styledGuess.append(Ansi.ansi().fgBright(YELLOW).bold().a(gChar).reset());
                } else {
                    styledGuess.append(Ansi.ansi().fg(BLACK).a(gChar).reset());
                }
            }
            System.out.println(styledGuess);
        }
    }

    private void showProgressBar(int current, int total) {
        int barLength = 30;
        int filledLength = (int) ((double) current / total * barLength);
        StringBuilder bar = new StringBuilder();
        for (int i = 0; i < barLength; i++) {
            if (i < filledLength) {
                bar.append("█");
            } else {
                bar.append("-");
            }
        }
        System.out.println(Ansi.ansi()
                .fgBright(GREEN)
                .a(String.format("Guesses Used: |%s| %d/%d (%.0f%%)",
                        bar, current, total, (double) current / total * 100))
                .reset());
    }

    private void gameOver(boolean guessedCorrectly) {
        refreshPage("Game Over");
        showGuesses();
        if (guessedCorrectly) {
            System.out.println(Ansi.ansi().fgBright(GREEN).bold().a("Correct! The word was " + word).reset());
            showCelebration();
        } else {
            System.out.println(Ansi.ansi().fgBright(RED).bold().a("Sorry, the word was " + word).reset());
            showConsolation();
        }
        System.out.println("\nFetching word definition...");
        String definition = fetchWordDefinition(word);
        System.out.println(Ansi.ansi().fgBright(CYAN).a("Definition of " + word + ": " + definition).reset());
    }

    private String fetchWordDefinition(String word) {
        try {
            URL url = new URI("https://api.dictionaryapi.dev/api/v2/entries/en/" + word).toURL();
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String response = reader.lines().collect(Collectors.joining());
            reader.close();

            return response.contains("definition") ? response : "No definition found.";
        } catch (Exception e) {
            return "Error fetching definition: " + e.getMessage();
        }
    }

    private boolean playAgain() {
        System.out.print("\nDo you want to play again? (y/n): ");
        return "y".equalsIgnoreCase(scanner.nextLine());
    }

    private void refreshPage(String headline) {
        clearConsole();
        System.out.println(Ansi.ansi().fgBright(BLUE).bold().a("=== " + headline + " ===").reset());
    }

    private void showCelebration() {
        System.out.println(Ansi.ansi()
                .fgBright(GREEN)
                .a("""
                 ██╗   ██╗ ██████╗ ██╗   ██╗███████╗██████╗ 
                 ██║   ██║██╔═══██╗██║   ██║██╔════╝██╔══██╗
                 ██║   ██║██║   ██║██║   ██║█████╗  ██████╔╝
                 ╚██╗ ██╔╝██║   ██║██║   ██║██╔══╝  ██╔═══╝ 
                  ╚████╔╝ ╚██████╔╝╚██████╔╝███████╗██║     
                   ╚═══╝   ╚═════╝  ╚═════╝ ╚══════╝╚═╝     
                """)
                .reset());
        System.out.println(Ansi.ansi()
                .fgBright(CYAN)
                .a("🎉 Congratulations! You guessed the word! 🎉")
                .reset());
    }

    private void showConsolation() {
        System.out.println(Ansi.ansi()
                .fgBright(RED)
                .a("""
                  __     ______  _    _   _      ____   _____ 
                  \\ \\   / / __ \\| |  | | | |    / __ \\ / ____|
                   \\ \\_/ / |  | | |  | | | |   | |  | | (___  
                    \\   /| |  | | |  | | | |   | |  | |\\___ \\ 
                     | | | |__| | |__| | | |___| |__| |____) |
                     |_|  \\____/ \\____/  |______\\____/|_____/ 
                """)
                .reset());
        System.out.println(Ansi.ansi()
                .fgBright(RED)
                .a("Better luck next time! The word was " + word + ".")
                .reset());
    }

    private void clearConsole() {
        System.out.print("\033[H\033[2J");
        System.out.flush();
    }

    private List<String> getWordsFromFile() {
        List<String> wordList = new ArrayList<>();
        try {
            wordList = Files.readAllLines(Paths.get(WORD_LIST_FILE));
        } catch (IOException e) {
            System.out.println(Ansi.ansi().fgBright(RED).a("Error reading the word list file.").reset());
        }
        return wordList;
    }
}
