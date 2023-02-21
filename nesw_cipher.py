#!/usr/bin/env python

"""NorthEast SouthWest Cipher

This is a tool to encipher plaintext messages with a hand cipher created by the
author of this tool. The cipher has similarities with the Vigenère and Playfair
ciphers.

The cipher consists of finding each letter of the plaintext in a 5x5 square
containing the alphabet and writing in the ciphertext the letter that is
adjacent to it in one of the eight cardinal and ordinal directions, starting
from the chosen direction (north by default) and rotating around the compass
rose once after each letter by a chosen rotation, wrapping around the edges of
the square as necessary. The default is to rotate by 2 steps after each letter,
skipping the ordinal directions if a cardinal direction was chosen and
vice-versa. While using all 8 directions results in a stronger cipher, 2 steps
was chosen as the default because the cipher originally only used the cardinal
directions.

A keyword may also be used to reorder the letters of the alphabet for building
the square, as is usually done in the Playfair cipher. Since the modern version
of the Latin alphabet contains 26 letters, one letter is omitted from the
square and replaced in the plaintext and keyword with a different letter,
preferably one that looks like the omitted letter. For instance, if "J" is
omitted it may be replaced with "I" (this is the default), or "V" may be
replaced with "U".

Deciphering a message is done by the same process as enciphering, with all
choices being the same, except the starting direction, which must be opposite
to the one used for enciphering.
"""
import argparse
from os.path import exists, isfile
from string import ascii_lowercase
from sys import stdin

ALPHABET_ROWS = 5
ALPHABET_COLS = 5
ROTATION = 2
REPLACEMENT = "ji"
DIRECTIONS = ["n", "ne", "e", "se",
              "s", "sw", "w", "nw"]
LETTERS = ascii_lowercase


def validate_keyword(keyword):
    """Takes a keyword and checks whether it contains only letters.

    Returns:
        keyword if valid

    Raises:
        ValueError: if keyword has characters which are not letters.
    """

    for char in keyword:
        if char.lower() not in LETTERS:
            raise ValueError("argument passed to 'keyword' must contain only "
                             "letters")
    return keyword


def validate_replacement(replacement):
    """Takes a replacement pair and checks whether it is composed of exactly
    two unique letters.

    Returns:
        replacement if valid

    Raises:
        ValueError: if replacement pair is anything other than two unique
        letters.
    """
    replacement = replacement.lower()
    valid = (len(replacement) == 2 and
             replacement[0] != replacement[1] and
             replacement[0] in LETTERS and
             replacement[1] in LETTERS)

    if not valid:
        raise ValueError("Parameter 'replacement' expects argument to be "
                         "a string of exactly two unique letters "
                         f"(received: '{replacement}')")
    return replacement


def validate_direction(direction):
    """Takes a direction and checks whether it is in the directions list.

    Returns:
        direction if valid

    Raises:
        ValueError: if direction is not in the directions list.
    """
    if direction not in DIRECTIONS:
        raise ValueError("Parameter 'direction' expects argument to be a "
                         f"value from the directions list: {DIRECTIONS} "
                         f"(received: '{direction}')")
    return direction


def validate_rotation(rotation):
    """Takes a number of rotation steps and checks whether it is a non-zero
    integer within a range between a negative value equivalent to half the size
    of DIRECTIONS up to the corresponding positive value.

    Returns:
        rotation if valid

    Raises:
        ValueError: if rotation is zero or outside the specified range.
    """
    # Enciphering a message with no rotation is equivalent to using
    # a substitution cipher, so let's avoid that, while also ensuring
    # it rotation can't be greater than a half turn
    limit = len(DIRECTIONS)//2
    valid = (isinstance(rotation, int) and rotation != 0 and
             abs(rotation) <= limit)
    if not valid:
        raise ValueError("Parameter 'rotation' expects argument to be a "
                         f"non-zero integer from {-limit} to {limit} "
                         f"(received: '{type(rotation).__name__}': "
                         f"{rotation} )")
    return rotation


def build_alphabet(keyword, replacement=REPLACEMENT):
    """Builds a square with the letters of the alphabet, replacing one letter
    with another so that it fits the square.

    Parameters:
        keyword: a keyword used to reorder the letters of the alphabet before
                 building the square. replacement: a pair of unique letters.

    Returns:
        The resulting alphabet square as a 2d list.

    Raises:
        ValueError: If there's a mismatch between the number of available
                    letters and the size of the alphabet square.
    """
    keyword = validate_keyword(keyword)
    remove, replace = validate_replacement(replacement)

    keyword = (keyword.lower() + LETTERS).replace(remove, replace)
    keyword = list(dict.fromkeys(keyword))

    # This error should never happen with normal usage, I'm only checking for
    # this in case anyone decides to modify this program for a language with an
    # alphabet of a different size, or otherwise change the dimensions of the
    # alphabet in order to use a different set of characters.
    if (len(keyword)) != ALPHABET_ROWS * ALPHABET_COLS:
        raise RuntimeError("the number of available letters to build "
                           "the alphabet square does not match its size")

    alphabet = [["" for _ in range(ALPHABET_ROWS)]
                for _ in range(ALPHABET_COLS)]

    letter_index = 0
    for row in range(ALPHABET_ROWS):
        for col in range(ALPHABET_COLS):
            alphabet[row][col] = keyword[letter_index]
            letter_index += 1
    return alphabet


def find_letter(alphabet, letter):
    """Finds the coordinates of a letter in the alphabet.

    Parameters:
        alphabet: a 2d list containing the alphabet in which to find
                  the letter. Should be generated with build_alphabet()
        letter: the letter to be found.

    Returns:
        A tuple with the coordinates of the found letter or None if the letter
        is not in the alphabet square.
    """
    found = None

    for row in range(ALPHABET_ROWS):
        for col in range(ALPHABET_COLS):
            if alphabet[row][col] == letter.lower():
                found = row, col
    return found


def encipher(plaintext, keyword="", replacement=REPLACEMENT,
             direction=DIRECTIONS[0], rotation=ROTATION):
    """Enciphers a plaintext message using the NorthEast SouthWest Cipher.

    Parameters:
        plaintext: the plaintext message to be enciphered.
        keyword: a keyword used to reorder the letters of the alphabet.
        replacement: a pair of letters, where the second one replaces the first
                     in the plaintext. A valid replacement consists of exactly
                     two unique letters.
        direction: the direction from which to start applying the cipher. Valid
                   choices are any of the values in the 'DIRECTIONS' list.
        rotation: the number of rotation steps used to change direction after
                  each letter. Should be a non-zero integer with absolute value
                  equal to or lower than half the size of the 'DIRECTIONS'
                  list. Positive values are clockwise steps, negative values
                  are widdershins steps.

    Returns:
        The resulting ciphertext.
    """
    alphabet = build_alphabet(keyword, replacement)
    direction = validate_direction(direction)
    rotation = validate_rotation(rotation)
    remove, replace = replacement

    cardinals = ["n", "e", "s", "w"]

    def update_direction(direction):
        return DIRECTIONS[(DIRECTIONS.index(direction) + rotation)
                          % len(DIRECTIONS)]

    output = ""
    for character in plaintext:
        is_upper = character.isupper()

        if character.lower() == remove:
            character = replace

        coordinates = find_letter(alphabet, character)

        if not coordinates:
            output += character
            continue

        # By counting the appearances of each letter that represents a cardinal
        # direction, we may use directions that point to cells other than the
        # ones neighboring the current letter in the alphabet square; e.g.:
        # "nn", "ssww" etc. for letters 2 cells away, or the half winds ("nne",
        # "sse", "ene" etc.) for letters a knight's move away.
        north, east, south, west = [direction.count(i) for i in cardinals]

        row, col = ((coordinates[0] - north + south) % ALPHABET_ROWS,
                    (coordinates[1] - west + east) % ALPHABET_COLS)

        character = alphabet[row][col]
        direction = update_direction(direction)

        output += character.upper() if is_upper else character
    return output.strip()


def main():
    """Parses command line parameters and passes them as arguments to
    encipher(). By default, plaintext is read from standard input and the
    resulting ciphertext is written to standard output.
    """
    def parse_keyword(keyword):
        try:
            value = validate_keyword(keyword)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "keyword must contain only letters") from exc
        return value

    def parse_replacement(replacement):
        try:
            value = validate_replacement(replacement)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "replacement must be two unique letters") from exc
        return value

    def output_file(filename):
        if exists(filename):
            raise argparse.ArgumentTypeError(
                f"can't open '{filename}': file already exists")
        return filename

    def input_file(filename):
        if isfile(filename) or filename == "-":
            return filename
        raise argparse.ArgumentTypeError(
            f"can't open '{filename}': no such file")

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", dest="input", metavar="INPUT_FILE", default="-",
                       type=input_file,
                       help=("text file containing a message to be enciphered "
                             "(read from standard input if not specified)"))
    parser.add_argument("-o", dest="output", metavar="OUTPUT_FILE", default="",
                        type=output_file,
                        help="text file to output the enciphered message to "
                             "(write to standard output if not specified)")
    group.add_argument("-m", dest="message", default="",
                       help="a message to be enciphered (cannot be used if an "
                            "input file was specified)")
    parser.add_argument("-k", dest="keyword", default="", type=parse_keyword,
                        help="keyword used to generate an alphabet key "
                             "(default: no keyword)")
    parser.add_argument("-r", dest="replacement", default=REPLACEMENT,
                        type=parse_replacement,
                        help="a pair of letters, where the first one replaces "
                             "the second one in the generated "
                             "alphabet key (default: %(default)s)")
    parser.add_argument("-d", dest="direction", metavar="DIRECTION",
                        default=DIRECTIONS[0], choices=DIRECTIONS,
                        help="direction from which to start enciphering; "
                             "choose one of %(choices)s "
                             "(default: %(default)s)")
    parser.add_argument("-s", dest="step_size", metavar="STEP_SIZE",
                        type=int, default=ROTATION,
                        choices=range(1, len(DIRECTIONS)//2+1),
                        help="change the size of the steps used for rotation;"
                             " choose one of %(choices)s"
                             " (default: %(default)s)")
    parser.add_argument("-w", dest="widdershins", action="store_true",
                        help="use widdershins rotation to encipher message "
                             "(default: clockwise rotation)")

    args = parser.parse_args()

    rotation = -args.step_size if args.widdershins else args.step_size

    if args.message:
        plaintext = args.message
        args.input = ""
    else:
        plaintext = ""

    if args.input == "-":
        for line in stdin:
            plaintext += line
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as file:
            for line in file:
                plaintext += line

    ciphertext = encipher(plaintext, args.keyword,
                          args.replacement, args.direction, rotation)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(ciphertext)
    else:
        print(ciphertext)


if __name__ == "__main__":
    main()
