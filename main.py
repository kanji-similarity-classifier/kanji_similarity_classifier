from PIL import Image
import imagehash
import os

# Path to file containing all the kanji.
KANJI_FILE = os.path.join('.', 'test.csv')

# Path to directory containing all kanji images.
IMGS_DIR = os.path.join('.', 'output')
# File extension for all kanji images.
IMG_EXT = '.png'

# Path to file to output results in.
# Must be `.csv`.
OUTPUT_FILE = os.path.join('.', 'kanji_similarity.csv')


def getKanjiImageHash(kanjiCharacter):
    '''
    Returns the result of calling
    `imagehash.average_hash(PIL.Image.open(...))`.

    Raises `FileNotFoundError` if the image could not be found.
    '''
    kanjiCharacter = kanjiCharacter.strip()
    image = Image.open(os.path.join(IMGS_DIR, kanjiCharacter + IMG_EXT))
    return imagehash.average_hash(image)


with open(KANJI_FILE, 'r', encoding='utf-8') as kanjiFile:
    with open('.txt', 'w', encoding='utf-8') as outputFile:
        kanjiCharacters = kanjiFile.readlines()

        for kanji in kanjiCharacters:
            try: kanjiImageHash = getKanjiImageHash(kanji)
            except:
                kanji_skipped += 1
                continue

            for otherKanji in kanjiCharacters:
                try: otherKanjiImageHash = getKanjiImageHash(otherKanji)
                except:
                    kanji_skipped += 1
                    continue
                difference = kanjiImageHash - otherKanjiImageHash


                outputFile.write(f'{kanji.strip()}: {kanjiImageHash}\n')
                outputFile.write(f'{otherKanji.strip()}: {otherKanjiImageHash}\n')
                outputFile.write(str(difference) + '\n\n')
