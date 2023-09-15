import csv
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

import numpy as np
import numpy.typing as tnp

COLUMNS_HEADER = "word", "start_row", "start_col", "end_row", "end_col"


class Cell(NamedTuple):
    """
    Cointainer for the row and column position of a single cell in a 2-dimensional array.
    """

    row: int
    column: int


class Letter(NamedTuple):
    """
    Container for a single letter with a cell matching its position in
    a 2-dimencional array.
    """

    char: str
    cell: Cell


class Word(NamedTuple):
    """
    A container for a word string and the cells matching the first and last
    characters of a word.
    """

    word: str
    start: Cell
    end: Cell


def get_word_search(file_path: Path) -> tnp.NDArray[np.str_]:
    """Returns a matrix generated from a csv file."""
    word_search = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        for row in csv_reader:
            word_search.append(row)
    return np.array(word_search)


def get_words_to_find(file_path: Path) -> list[str]:
    """Returns a list of words loaded from a text file."""
    with open(file_path, "r", encoding="utf-8") as words_file:
        return [word.replace("\n", "") for word in words_file.readlines()]


def save_words_to_csv(
    file_path: Path,
    words: list[Word],
    header: Sequence[str] = COLUMNS_HEADER,
) -> None:
    """Saves the list of words and its metadata to a csv file."""
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",")
        if header and len(header) == 5:
            csv_writer.writerow(header)
        for word, start, end in words:
            csv_writer.writerow((word, *start, *end))


def create_words_dictionary(words: list[str]) -> dict[str, list[str]]:
    """
    Returns a dictionary where the keys are the initials of all the words
    and the values are a list of words that correspond to that initial.
    """
    word_dict = {}
    for word in words:
        initial = word[0]
        if word_dict.get(initial) is None:
            word_dict[initial] = [word]
        else:
            word_dict[initial].append(word)
    return word_dict


def get_adjacent_cells(matrix: tnp.NDArray, position: Cell) -> list[Letter]:
    """
    Returns the adjacent (verticall, horizontal and diagonal) cells of a given cell.

    Parameters
    ----------
    matrix : ndarray
        A 2-dimensional array.
    position : Cell
        The row and column of the cell to get the adjacent cells from.

    Returns
    -------
    list of Letter
        A list contining all the adjacent cells with their respective value,
        row and column.
    """

    max_row, max_column = matrix.shape
    position_row, position_column = position

    adjancent_cells: list[Letter] = []

    start_row = -1 if position_row > 0 else 0
    end_row = 2 if position_row < max_row - 1 else 1
    start_column = -1 if position_column > 0 else 0
    end_column = 2 if position_column < max_column - 1 else 1

    for row_deviation in range(start_row, end_row):
        for column_deviation in range(start_column, end_column):
            if row_deviation == 0 and column_deviation == 0:
                continue

            current_row = position_row + row_deviation
            current_column = position_column + column_deviation
            cell_value = matrix[current_row, current_column]

            adjancent_cells.append(
                Letter(cell_value, Cell(current_row, current_column))
            )

    return adjancent_cells


def cells_match_to_word(
    matrix: tnp.NDArray[np.str_],
    word: str,
    start: Cell,
    direction: tnp.NDArray[np.int32],
) -> bool:
    """
    Takes the amount of cells from the given start cell following the given
    direction until the amount of cells is equal to the lenght of the word and
    compares it to the joint values.

    Parameters
    ----------
    matrix : ndarray
        2-dimensional array
    word : str
        A literal string to which the taken cells are compare against.
    start : Cell
        The cell from which to start taking the rest of the cells.
    direction : ndarray of int32
        A 2D vector that represents the 'steps' to take from the start cell.

    Returns
    -------
    bool
        True if the joint values of the taken cells match the given word.
        False if the values don't match or there's no enough cells to match
        the word's lenght.
    """
    current_position = np.array(start)
    letters = []

    try:
        for _ in range(len(word)):
            letter = matrix[*current_position]
            letters.append(letter)
            current_position += direction
    except IndexError:
        return False

    return word == "".join(letters)


def get_matched_words(
    word_search: tnp.NDArray[np.str_],
    start_point: Cell,
    letters: list[Letter],
    words: list[str],
) -> list[Word]:
    """
    Returns the words found (if any) from the given start point cell.

    Parameters
    ----------
    word_search : ndarray
        2-dimensional array.
    start_point : Cell
        A cell from which start matching words.
    letters : list of Letter
        The list of adjacent cells to the start cell.
    words : list of str
        List of all the words to match.

    Returns
    -------
    list of Word
        A list of all the matched words, with the position of the cells matching the first
        and last letter of the word.
    """

    start_row, start_column = start_point
    char_to_match = 1  # First letter has already been matched, match next letter

    words_matched: list[Word] = []

    for letter, letter_cell in letters:
        for word in words:
            if letter != word[char_to_match]:
                continue

            row_step = letter_cell.row - start_row
            column_step = letter_cell.column - start_column

            cells_match = cells_match_to_word(
                word_search,
                word,
                Cell(start_row, start_column),
                np.array([row_step, column_step]),
            )
            if not cells_match:
                continue

            words_matched.append(
                Word(
                    word,
                    Cell(start_row, start_column),
                    Cell(
                        start_row + row_step * (len(word) - 1),
                        start_column + column_step * (len(word) - 1),
                    ),
                )
            )
    return words_matched


def filter_words(filter_from: list[str], words_to_filter: list[str]) -> None:
    for word in words_to_filter:
        filter_from.remove(word)


def find_words(word_search: tnp.NDArray, words: list[str]) -> list[Word]:
    """
    Returns a list of words found in the word search matrix. Each word contains the
    actual string representation of the word, the position (row an column) of the
    characters matching the first and last characte of the wordr.

    Parameters
    ----------
    word_search : ndarray
        A 2-dimensional array of string characters representing a word search.
    words : list of str
        The complete set of words to search for in the word search.
    """
    words_initial = create_words_dictionary(words)
    words_found: list[Word] = []

    for row_index, row in enumerate(word_search):
        for column_index, letter in enumerate(row):
            if not words_initial:
                return words_found

            if letter not in words_initial:
                continue

            words_to_match = words_initial[letter]
            adjacent_letters = get_adjacent_cells(
                word_search, Cell(row_index, column_index)
            )
            start_point = Cell(row_index, column_index)
            words_matched = get_matched_words(
                word_search, start_point, adjacent_letters, words_to_match
            )

            if not words_matched:
                continue

            words_found.extend(words_matched)
            words_to_filter = [word.word for word in words_matched]
            filter_words(words_to_match, words_to_filter)

            if not words_to_match:
                del words_initial[letter]

    return words_found
