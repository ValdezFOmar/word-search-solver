import csv
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import numpy.typing as tnp
import pytesseract as tess
from PIL import Image


def extract_text(image_path: Path) -> str:
    image = Image.open(image_path)
    config = r"--psm 6"
    return tess.image_to_string(image, config=config)


def process_text_to_matrix(text: str):
    for line in text.splitlines():
        yield (char for char in line if char != ' ')


def save_chars_to_csv(path: Path, data: Iterable):
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    with open(path.with_suffix(".csv"), "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",")
        for row in data:
            csv_writer.writerow(row)


def process_images():
    ...


def main():
    if len(sys.argv) < 2:
        print(f"{sys.argv[0]}: Not enough arguments.")
        return

    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"{sys.argv[0]}: '{image_path}' File doesn't exists.")
        return

    text = extract_text(image_path)
    chars = process_text_to_matrix(text)
    path_to_save = Path("ocr_output", image_path.stem)
    save_chars_to_csv(path_to_save, chars)


if __name__ == "__main__":
    main()
