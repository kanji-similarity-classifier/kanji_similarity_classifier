const fs = require('fs');
const path = require('path');
const { createCanvas } = require('canvas');

/** Directory in which to output the images. */
const OUTPUT_DIR = path.join('.', 'output');
/** Number of characters to process. */
const NUM_OF_CHARS = 13108;
/** The file containing the kanji characters. */
const KANJI_FILE = path.join('.', 'kanji.csv');

// ensure `OUTPUT_DIR` exists
const doesDirExist = fs.existsSync(OUTPUT_DIR) && fs.lstatSync(OUTPUT_DIR).isDirectory();
if (!doesDirExist) {
    fs.mkdirSync(OUTPUT_DIR);
} // if

/// get kanji characters
const kanjiFile = fs.readFileSync(KANJI_FILE, 'utf-8');
const kanjiCharacters = kanjiFile.split(/\r?\n/);
kanjiCharacters.length = NUM_OF_CHARS;

// prepare canvas for text-to-image conversion
const fontSize = 1000;
const fontPadding = 5;
const canvasLength = fontSize + fontPadding;
const canvas = createCanvas(canvasLength, canvasLength);
const canvasCenter = canvas.width / 2;

// setup context
const context = canvas.getContext('2d');
context.fillStyle = '#ffffff';
context.font = `${fontSize}px sans-serif`;
context.textAlign = 'center';
context.textBaseline = 'middle';

kanjiCharacters.forEach((character) => {
    context.fillText(character, canvasCenter, canvasCenter);

    // See: https://stackoverflow.com/questions/6926016
    const imageString = canvas.toDataURL().replace(/^data:image\/png;base64,/, '');
    fs.writeFile(path.join(OUTPUT_DIR, `${character}.png`),imageString, 'base64', () => {})

    context.clearRect(0, 0, canvasLength, canvasLength);
});
