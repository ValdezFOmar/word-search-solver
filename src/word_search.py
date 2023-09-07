import csv


WORD_SEARCH_EXAMPLE = "example/word-search.csv"
WORDS_TO_FIND_EXAMPLE = "example/words-to-find.txt"
WORDS_FOUND_OUTPUT = 'example/words-found.csv'


def get_word_search(file: str) -> list[list]:
    word_search = []
    with open(file, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        for row in csv_reader:
            word_search.append(row)
    return word_search


def get_words_to_find(file: str) -> list[str]:
    with open(file, 'r', encoding='utf-8') as words_file:
        return [word.replace('\n', '') for word in words_file.readlines()]


def save_words_to_csv(path_to_file: str, words: list[tuple]) -> None:
    COLUMNS_HEADER = ('word', 'start_row', 'start_col', 'end_row', 'end_col')
    with open(path_to_file, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(COLUMNS_HEADER)
        for word, start, end in words:
            csv_writer.writerow([word, start[0], start[1], end[0], end[1]])


def create_words_dictionary(words: list[str]) -> dict[str, list[str]]:
    dictionary = {}
    for word in words:
        initial = word[0]
        if dictionary.get(initial) is None:
            dictionary[initial] = [word]
        else:
            dictionary[initial].append(word)
    return dictionary


def get_adjancent_cells(
        matrix: list[list],
        row_index: int,
        column_index: int) -> list[tuple[str, int, int]]:

    maximum_row_index = len(matrix) - 1
    maximum_columns_index = len(matrix[0]) - 1

    adjancent_cells = []

    start_row = -1 if row_index > 0 else 0
    end_row = 2 if row_index < maximum_row_index else 1
    start_column = -1 if column_index > 0 else 0
    end_column = 2 if column_index < maximum_columns_index else 1

    for row_deviation in range(start_row, end_row):
        for column_deviation in range(start_column, end_column):
            if row_deviation == 0 and column_deviation == 0:
                continue
            cell_row_index = row_index + row_deviation
            cell_column_index = column_index + column_deviation
            cell = matrix[cell_row_index][cell_column_index]
            adjancent_cells.append((cell, cell_row_index, cell_column_index))

    return adjancent_cells


def cells_match_to_word(
        matrix: list[list],
        word: str,
        start: tuple[int, int],
        direction: tuple[int, int]) -> bool:

    number_cells_to_match = len(word)
    row_step, column_step = direction
    row_start, column_start = start
    next_row = row_start
    next_column = column_start

    letters = []

    try:
        for _ in range(number_cells_to_match):
            letter = matrix[next_row][next_column]
            letters.append(letter)
            next_row += row_step
            next_column += column_step
    except IndexError:
        return False

    word_found = ''.join(letters)

    return True if word == word_found else False


def get_matched_words(
        word_search: list[list], 
        start_point: tuple[int, int], 
        letters: list[tuple], 
        words: list[str]) -> list[tuple[str, int, int]]:

    start_row, start_column = start_point
    char_to_match = 1  # First letter has already been matched, match next char

    words_matched = []

    for letter, letter_row, letter_column in letters:
        for word in words:
            if letter != word[char_to_match]:
                continue

            row_step = letter_row - start_row
            column_step = letter_column - start_column

            match = cells_match_to_word(word_search, word, (start_row, start_column), (row_step, column_step))
            if not match:
                continue

            words_matched.append(
                (word, (start_row, start_column),
                (start_row + row_step * (len(word) - 1),
                 start_column + column_step * (len(word) - 1)))
            )
    return words_matched


def filter_words(filter_from: list[str], words_to_filter) -> None:
    for word in words_to_filter:
        filter_from.remove(word)


def find_words(word_search: list[list], words: list[str]):
    words_initial = create_words_dictionary(words)
    words_found = []

    for row_index, row in enumerate(word_search):
        for column_index, letter in enumerate(row):
            if letter not in words_initial:
                continue

            words_to_match = words_initial[letter]
            adjacent_letters = get_adjancent_cells(word_search, row_index, column_index)
            start_point = (row_index, column_index)
            words_matched = get_matched_words(word_search, start_point, adjacent_letters, words_to_match)

            if not words_matched:
                continue

            words_found.extend(words_matched)
            words_to_filter = [word[0] for word in words_matched]
            filter_words(words_to_match, words_to_filter)

            if not words_to_match:
                del words_initial[letter]
    return words_found


def main():
    word_search_matrix = get_word_search(WORD_SEARCH_EXAMPLE)
    words_to_find = get_words_to_find(WORDS_TO_FIND_EXAMPLE)

    words_found = find_words(word_search_matrix, words_to_find)
    save_words_to_csv(WORDS_FOUND_OUTPUT, words_found)


if __name__ == '__main__':
    main()
