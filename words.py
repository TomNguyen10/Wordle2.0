import nltk
from nltk.corpus import words

nltk.download("words")

word_list = words.words()

file_path = "words.txt"

with open(file_path, "w", encoding="utf-8") as file:
    for word in word_list:
        file.write(word + "\n")

print(f"Words have been saved to {file_path}")
