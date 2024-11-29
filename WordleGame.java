import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.util.*;
import java.util.stream.Collectors;

public class WordleGame {
    private int numLetters = 5;
    private int numGuesses = 6;
    private String word = "";
    private List<String> guesses = new ArrayList<>();
    private boolean hintUsed = false;
    private static final Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        WordleGame game = new WordleGame();
        game.play();
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
        System.out.println("Welcome to Wordle!\n");
        System.out.println("Wordle is a simple word-guessing game.");
        System.out.println("Try to guess the word in the fewest attempts possible!\n");
        System.out.print("Press Enter to start the game!");
        scanner.nextLine();
    }

    private void setDifficulty() {
        System.out.println("\nSelect difficulty level:");
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
        List<String> wordList = getEnglishWords().stream()
                .filter(w -> w.length() == numLetters)
                .collect(Collectors.toList());
        if (wordList.isEmpty()) {
            System.out.println("No words available for " + numLetters + " letters. Please choose another difficulty.");
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
                    System.out.println("You have already used your hint for this game.");
                } else {
                    useHint();
                }
                continue;
            }
            if (previousGuesses.contains(guess)) {
                System.out.println("You've already guessed " + guess + ".");
            } else if (guess.length() != numLetters) {
                System.out.println("Your guess must be " + numLetters + " letters.");
            } else if (!guess.matches("[A-Z]+")) {
                System.out.println("Invalid input: Only English letters are allowed.");
            } else {
                return guess;
            }
        }
    }

    private void useHint() {
        for (int i = 0; i < word.length(); i++) {
            if (guesses.get(guesses.size() - 1).charAt(i) == '_') {
                char hintLetter = word.charAt(i);
                System.out.println("Hint: The letter '" + hintLetter + "' is in position " + (i + 1));
                hintUsed = true;
                return;
            }
        }
        System.out.println("No hints available; you've already uncovered all positions!");
    }

    private void showGuesses() {
        System.out.println("\nGuesses:");
        for (String guess : guesses) {
            StringBuilder styledGuess = new StringBuilder();
            for (int i = 0; i < guess.length(); i++) {
                char gChar = guess.charAt(i);
                char wChar = word.charAt(i);
                if (gChar == wChar) {
                    styledGuess.append("[").append(gChar).append("]");
                } else if (word.contains(String.valueOf(gChar))) {
                    styledGuess.append("(").append(gChar).append(")");
                } else {
                    styledGuess.append(gChar);
                }
            }
            System.out.println(styledGuess);
        }
    }

    private void gameOver(boolean guessedCorrectly) {
        refreshPage("Game Over");
        showGuesses();
        if (guessedCorrectly) {
            System.out.println("Correct! The word was " + word);
            showCelebration();
        } else {
            System.out.println("Sorry, the word was " + word);
            showConsolation();
        }
        System.out.println("\nFetching word definition...");
        String definition = fetchWordDefinition(word);
        System.out.println("Definition of " + word + ": " + definition);
    }

    private String fetchWordDefinition(String word) {
        try {
            URI uri = new URI("https", "api.dictionaryapi.dev", "/api/v2/entries/en/" + word, null);
            URL url = uri.toURL();
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
        System.out.println("=== " + headline + " ===");
    }

    private void showCelebration() {
        System.out.println("\n🎉 Congratulations! 🎉");
    }

    private void showConsolation() {
        System.out.println("\nBetter luck next time!");
    }

    private List<String> getEnglishWords() {
        return Arrays.asList("apple", "happy", "beach", "other", "world"); // Replace with an English word list.
    }

    private void clearConsole() {
        System.out.print("\033[H\033[2J");
        System.out.flush();
    }
}