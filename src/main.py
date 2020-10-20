from PIL import Image
import imagehash

import threading
import json
import os

from datetime import datetime as dt  # benchmarking

from kanji_thread import KanjiComparisonThread

# Path to directory containing all kanji images.
IMGS_DIR = os.path.join('.', 'output')
# File extension for all kanji images.
IMG_EXT = '.png'

# Path to file to output results in.
# Must be `.json`.
OUTPUT_FILE = os.path.join('.', 'scores', 'scores.json')
if not os.path.isdir(os.path.dirname(OUTPUT_FILE)):
    os.mkdir(os.path.dirname(OUTPUT_FILE))

# Store benchmark results.
BENCHMARK_DIR = os.path.join('.', 'benchmarks')
if not os.path.isdir(BENCHMARK_DIR):
    os.mkdir(BENCHMARK_DIR)

KANJI_PER_SUBLIST = 30  # optimal(?) for 13108


def wait_for_threads(thread_type=KanjiComparisonThread):
    '''
    A simple method that calls `join()`
    on all current threads of type `thread_type`.
    '''
    for thread in threading.enumerate():
        if isinstance(thread, thread_type):
            thread.join()


def generate_kanji_image_hash(kanji_character):
    '''
    Returns the result of calling
    `imagehash.average_hash(PIL.Image.open(...))`.

    Raises `FileNotFoundError` if the image could not be found.
    '''
    kanji_character = kanji_character.strip()
    image = Image.open(os.path.join(IMGS_DIR, kanji_character + IMG_EXT))
    return imagehash.average_hash(image)


def generate_hashes(all_kanji):
    hashes = {}
    i = 1
    for kanji in all_kanji:
        t0 = dt.now()
        hashes[kanji] = generate_kanji_image_hash(kanji)
        print(f'HASHING: {dt.now() - t0} for {kanji} [{i} / 13108]')
        i += 1
    return hashes


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


# guarantees to only use kanji that have corresponding image files
all_kanji = [image_name.rstrip(IMG_EXT) for image_name in os.listdir(IMGS_DIR)]
total_kanji = len(all_kanji)
kanji_sublists = [all_kanji[i:i + KANJI_PER_SUBLIST] for i in range(0, total_kanji, KANJI_PER_SUBLIST)]
processing = 1  # benchmarking

differences = {}
# smallest difference will always be 0 as
# this script is guaranteed to compare a kanji to itself
largest_difference = 0
KanjiComparisonThread.differences = differences

hashing_start = dt.now()
HASHES = generate_hashes(all_kanji)
hashing_end = dt.now()


def compare_kanji(kanji_character, kanji_list, differences):
    global largest_difference
    '''
    Compare `kanji_character` to those in `kanji_list`
    noting difference scores in `differences`.

    `differences` should be a reference to the main `dict` used
    '''
    kanji_image_hash = HASHES[kanji_character]

    for other_kanji in kanji_list:
        if kanji == other_kanji:
            try:
                differences[kanji_character][other_kanji] = 0
            except KeyError:
                differences[kanji_character] = {}
                differences[kanji_character][other_kanji] = 0
            continue

        other_kanji_image_hash = HASHES[other_kanji]
        difference = kanji_image_hash - other_kanji_image_hash
        if difference > largest_difference:
            largest_difference = difference

        try:
            differences[kanji_character][other_kanji] = difference
        except KeyError:
            differences[kanji_character] = {}
            differences[kanji_character][other_kanji] = difference

        try:
            differences[other_kanji][kanji_character] = difference
        except KeyError:
            differences[other_kanji] = {}
            differences[other_kanji][kanji_character] = difference


comparison_start = dt.now()
for kanji in all_kanji:
    # Start multiple threads with `kanji` as the main kanji with each
    # thread being responsible for comparing to a subset of all kanji.
    t0 = dt.now()
    for sublist in kanji_sublists:
        thread = KanjiComparisonThread(kanji, sublist, compare_kanji)
        thread.start()
    wait_for_threads()
    print(f'COMPARISON: {dt.now() - t0} for {kanji} [{processing} / {total_kanji}]')
    processing += 1

    # Since all the scores for `kanji` were generated,
    # remove `kanji` from the sublists so it isn't compared again.
    # Prevents duplicate comparisons and reduces number of iterations needed.
    sublist = kanji_sublists[0]
    sublist.remove(kanji)  # `kanji` will always be first in the list
    try:
        sublist[0]  # avoid `len(sublist)``
    except IndexError:
        kanji_sublists.remove(sublist)  # remove empty sublists
comparison_end = dt.now()

# verification
verifying_start = dt.now()
if len(differences) != total_kanji:
    print('Some comparisons were not found')
for kanji in differences:
    if len(differences[kanji]) != total_kanji:
        print('Some comparisons were not found')
verifying_end = dt.now()

normalizing_start = dt.now()
normalize_differences(differences, largest_difference)
normalizing_end = dt.now()

differences['largestDifference'] = largest_difference

writing_start = dt.now()
json.dump(differences, open(OUTPUT_FILE, 'w', encoding='utf-8'))
writing_end = dt.now()

# benchmarking
with open(os.path.join(BENCHMARK_DIR, str(dt.now()).replace(':', '-')), 'w') as benchmark:
    benchmark.writelines([
        f'{total_kanji} kanji\n',
        f'{KANJI_PER_SUBLIST} kanji per sublist\n',
        f'Hashing: {hashing_end - hashing_start}\n',
        f'Comparing: {comparison_end - comparison_start}\n',
        f'Verifying: {verifying_end - verifying_start}\n',
        f'Normalizing: {normalizing_end - normalizing_start}\n',
        f'Writing: {writing_end - writing_start}\n',
        'Sublists (pausing per kanji)',
    ])
