from pathlib import Path

import word_search as ws

WORD_SEARCH_EXAMPLE = Path("examples", "word-search.csv")
WORDS_TO_FIND_EXAMPLE = Path("examples", "words-to-find.txt")
WORDS_FOUND_OUTPUT = Path("examples", "words-found.csv")


def main():
    word_search_matrix = ws.get_word_search(WORD_SEARCH_EXAMPLE)
    words_to_find = ws.get_words_to_find(WORDS_TO_FIND_EXAMPLE)

    words_found = ws.find_words(word_search_matrix, words_to_find)
    ws.save_words_to_csv(WORDS_FOUND_OUTPUT, words_found)


if __name__ == "__main__":
    main()
