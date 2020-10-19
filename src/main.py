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


def getKanjiImageHash(kanjiCharacter):
    '''
    Returns the result of calling
    `imagehash.average_hash(PIL.Image.open(...))`.

    Raises `FileNotFoundError` if the image could not be found.
    '''
    kanjiCharacter = kanjiCharacter.strip()
    image = Image.open(os.path.join(IMGS_DIR, kanjiCharacter + IMG_EXT))
    return imagehash.average_hash(image)


def normalizeDifferences(differences, largest, smallest=0):
    '''
    Normalizes the differences to a scale of [0, 1] with `1`
    indicating the most different and `0` indicating no difference.

    Parameters:
    differences -- a dict of the format `differences[k1][k2] == someNum`
    largest -- the largest difference score in `differences`
    smallest -- the smallest difference score in `differences`
    '''
    for kanji in differences:
        kanjiDifferences = differences[kanji]
        for otherKanji in kanjiDifferences:
            difference = kanjiDifferences[otherKanji]
            normalized = (difference - smallest) / (largest - smallest)
            differences[kanji][otherKanji] = normalized


# smallest difference will always be 0 as
# this script is guaranteed to compare a kanji to itself
largest_difference = 0
differences = {}

# guarantees to only use kanji that have corresponding image files
all_kanji = [image_name.rstrip(IMG_EXT) for image_name in os.listdir(IMGS_DIR)]
for kanji in all_kanji:
    differences[kanji] = {}
    kanjiImageHash = getKanjiImageHash(kanji)

    for otherKanji in all_kanji:
        otherKanjiImageHash = getKanjiImageHash(otherKanji)
        difference = kanjiImageHash - otherKanjiImageHash
        if difference > largest_difference:
            largest_difference = difference
        differences[kanji][otherKanji] = difference

normalizeDifferences(differences, largest_difference)
differences['largestDifference'] = largest_difference
json.dump(differences, open(OUTPUT_FILE, 'w', encoding='utf-8'))
