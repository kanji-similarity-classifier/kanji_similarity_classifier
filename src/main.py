from PIL import Image
import imagehash

import json
import os

# Path to file containing all the kanji.
KANJI_FILE = os.path.join('.', 'test.csv')

# Path to directory containing all kanji images.
IMGS_DIR = os.path.join('.', 'output')
# File extension for all kanji images.
IMG_EXT = '.png'

# Path to file to output results in.
# Must be `.json`.
OUTPUT_FILE = os.path.join('.', 'scores.json')


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
    differences -- a dict of the format `differences[k1][k2] == someNum`
    largest -- the largest difference score in `differences`
    smallest -- the smallest difference score in `differences`
    '''
    for kanji in differences:
        kanji_differences = differences[kanji]
        for other_kanji in kanji_differences:
            difference = kanji_differences[other_kanji]
            normalized = (difference - smallest) / (largest - smallest)
            differences[kanji][other_kanji] = normalized


# smallest difference will always be 0 as
# this script is guaranteed to compare a kanji to itself
largest_difference = 0
differences = {}

# guarantees to only use kanji that have corresponding image files
all_kanji = [image_name.rstrip(IMG_EXT) for image_name in os.listdir(IMGS_DIR)]
processing = 1
total = len(all_kanji)

for kanji in all_kanji:
    print(f'{processing} / {total}: {kanji}')
    differences[kanji] = {}
    kanji_image_hash = get_kanji_image_hash(kanji)

    for other_kanji in all_kanji:
        other_kanji_image_hash = get_kanji_image_hash(other_kanji)
        difference = kanji_image_hash - other_kanji_image_hash
        if difference > largest_difference:
            largest_difference = difference
        differences[kanji][other_kanji] = difference
    processing += 1

normalize_differences(differences, largest_difference)
differences['largestDifference'] = largest_difference
json.dump(differences, open(OUTPUT_FILE, 'w', encoding='utf-8'))
