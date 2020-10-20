from PIL import Image
import imagehash

import threading
import json
import os

from datetime import datetime as dt  # benchmarking

from kanji_thread import KanjiComparisonThread

# Path to file containing all the kanji.
KANJI_FILE = os.path.join('.', 'test.csv')

# Path to directory containing all kanji images.
IMGS_DIR = os.path.join('.', 'output-test')
# File extension for all kanji images.
IMG_EXT = '.png'

# Path to file to output results in.
# Must be `.json`.
OUTPUT_FILE = os.path.join('.', 'scores', 'test.json')
if not os.path.isdir(os.path.dirname(OUTPUT_FILE)):
    os.mkdir(os.path.dirname(OUTPUT_FILE))

# Store benchmark results.
BENCHMARK_DIR = os.path.join('.', 'benchmarks')
if not os.path.isdir(BENCHMARK_DIR):
    os.mkdir(BENCHMARK_DIR)


def get_kanji_image_hash(kanji_character):
    '''
    Returns the result of calling
    `imagehash.average_hash(PIL.Image.open(...))`.

    Raises `FileNotFoundError` if the image could not be found.
    '''
    kanji_character = kanji_character.strip()
    image = Image.open(os.path.join(IMGS_DIR, kanji_character + IMG_EXT))
    return imagehash.average_hash(image)


def normalize_differences(differences, largest, smallest=0):
    '''
    Normalizes the differences to a scale of [0, 1] with `1`
    indicating the most different and `0` indicating no difference.

    Parameters:
    differences -- a `dict` of the format `differences[k1][k2] == someNum`
    largest -- the largest difference score in `differences`
    smallest -- the smallest difference score in `differences`
    '''
    for kanji in differences:
        kanji_differences = differences[kanji]
        for other_kanji in kanji_differences:
            difference = kanji_differences[other_kanji]
            normalized = (difference - smallest) / (largest - smallest)
            differences[kanji][other_kanji] = round(normalized, 2)


# smallest difference will always be 0 as
# this script is guaranteed to compare a kanji to itself
largest_difference = 0


def compare_kanji(kanji_character, kanji_list, differences):
    global largest_difference
    '''
    Compare `kanji_character` to those in `kanji_list`
    noting difference scores in `differences`.

    `differences` should be a reference to the main `dict` used
    '''
    differences[kanji_character] = {}
    kanji_image_hash = get_kanji_image_hash(kanji_character)

    for other_kanji in kanji_list:
        if kanji == other_kanji:
            differences[kanji_character][other_kanji] = 0
            continue

        try:
            existing_score = differences[other_kanji][kanji_character]  # KeyError
            differences[kanji_character][other_kanji] = existing_score
        except KeyError:
            other_kanji_image_hash = get_kanji_image_hash(other_kanji)
            difference = kanji_image_hash - other_kanji_image_hash
            if difference > largest_difference:
                largest_difference = difference
            differences[kanji_character][other_kanji] = difference


# guarantees to only use kanji that have corresponding image files
all_kanji = [image_name.rstrip(IMG_EXT) for image_name in os.listdir(IMGS_DIR)]
total = len(all_kanji)

differences = {}
KanjiComparisonThread.differences = differences

comparison_start = dt.now()
for kanji in all_kanji:
    # Yes, one can just convert `all_kanji` and `differences` to global
    # variables, but this way feels more portable and customizable.
    thread = KanjiComparisonThread(kanji, all_kanji, compare_kanji)
    thread.start()

# ensure all comparison threads have finished
for thread in threading.enumerate():
    if isinstance(thread, KanjiComparisonThread):
        thread.join()
comparison_end = dt.now()

normalizing_start = dt.now()
normalize_differences(differences, largest_difference)
normalizing_end = dt.now()

differences['largestDifference'] = largest_difference

writing_start = dt.now()
json.dump(differences, open(OUTPUT_FILE, 'w', encoding='utf-8'))
writing_end = dt.now()

with open(os.path.join(BENCHMARK_DIR, str(dt.now()).replace(':', '-')), 'w') as benchmark:
    benchmark.writelines([
        f'{total} kanji\n',
        f'Comparing: {comparison_end - comparison_start}\n',
        f'Normalizing: {normalizing_end - normalizing_start}\n',
        f'Writing: {writing_end - writing_start}'
    ])
