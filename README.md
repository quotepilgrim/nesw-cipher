# NorthEast SouthWest Cipher
This is a command line tool implementing a hand cipher which I have invented.
The cipher bears some similarities to both the Playfair and Vigenère Cipher

Enciphering a message with this cipher consists of finding each letter of the
plaintext in a 5x5 square containing the alphabet and writing in the ciphertext
one of the letters that is adjacent to it in a given direction, starting from an
initial chosen direction and rotating around the compass rose once after each
letter, wrapping around the edges of the square as necessary.

By default we start from North and rotate clockwise 2 steps after each letter,
meaning ordinal directions are skipped and we only use the four cardinal
directions. Rotation by 1 or 3 steps includes all eight directions, while 4
steps results in alternating between the starting direction and its opposite
direction (i.e. North and South). No more than 4 steps of rotation are ever
necessary, as using counterclockwise rotation accounts for all possibilities.

A keyword may be used to reorder the letters of the alphabet for building the
square, as is usually done in the Playfair cipher. Since the modern version of
the Latin alphabet contains 26 letters, "J" is omitted from the alphabet in
order to fit the square, and all of its instances in the plaintext replaced with
"I". Any letter can be omitted instead of "J" and replaced by a different
letter. For instance, we can omit "V" and replace it with "U".

Deciphering a message is done through the same process as enciphering, with all
choices being the same, except the starting direction, which must be opposite to
the one used for enciphering.

### Note

This is a tool made only for my own personal use for a one-time thing, which
was to create an online puzzle several years ago that is so far unsolved. Not
only that, this is a rewrite from scratch of the script I made back then,
meaning not even I have ever used this tool apart from testing it. Make of that
what you will.

That said, I made a point of documenting the code the best I could, as well as
giving detailed information on how to use this tool on the command line, in case
anyone (including myself) wants to use this at some point in the future... for
whatever reason.

## Usage

To run the program you must have Python 3.x installed, then you should be able
to open a terminal/command prompt in the same folder as the script and type
```python nesw_cipher.py -h``` or ```./nesw_cipher.py``` (on Linux, you should
make the script executable first with ```chmod +x nesw_cipher.py```), press
Enter, and get the following message explaining all of the available command
line parameters:

```
usage: nesw_cipher.py [-h] [-f INPUT_FILE] [-o OUTPUT_FILE] [-m MESSAGE]
                      [-k KEYWORD] [-r REPLACEMENT] [-d DIRECTION]
                      [-s STEP_SIZE] [-w]

options:
  -h, --help      show this help message and exit
  -f INPUT_FILE   text file containing a message to be enciphered (read from
                  standard input if not specified)
  -o OUTPUT_FILE  text file to output the enciphered message to (write to
                  standard output if not specified)
  -m MESSAGE      a message to be enciphered (cannot be used if an input file
                  was specified)
  -k KEYWORD      keyword used to generate an alphabet key (default: no
                  keyword)
  -r REPLACEMENT  a pair of letters, where the first one replaces the second
                  one in the generated alphabet key (default: ji)
  -d DIRECTION    direction from which to start enciphering; choose one of n,
                  ne, e, se, s, sw, w, nw (default: n)
  -s STEP_SIZE    change the size of the steps used for rotation; choose one
                  of 1, 2, 3, 4 (default: 2)
  -w              use widdershins rotation to encipher message(default:
                  clockwise rotation)
```

## Examples

Encipher a message with default options, then decipher by running the script on
the resulting ciphertext but starting from South, which is opposite the default
direction of North:

```bash
$ ./nesw_cipher.py -m "lorem ipsum dolor sit amet"
fpwdg kurpn infpw rdu flzu

$ ./nesw_cipher.py -m "fpwdg kurpn infpw rdu flzu" -d s
lorem ipsum dolor sit amet
```

Same as above, now using a keyword to reorder the alphabet square:

```bash
$ ./nesw_cipher.py -m "lorem ipsum dolor sit amet" -k northeast
drscf kxakp lndrs abh flnh

$ ./nesw_cipher.py -m "drscf kxakp lndrs abh flnh" -ds -knortheast
lorem ipsum dolor sit amet
```

Start from East and use widdershins (couterclockwise) rotation, then decipher
by starting from West using the same rotation used to encipher:

(notice the effect of "J" being omitted from the alphabet)
```bash
$ ./nesw_cipher.py -m "the quick brown fox jumps over the lazy dog" -w -de
ucd vqdbp cmnbo anc kplut izks ogk mvyd eif

$ ./nesw_cipher.py -m "ucd vqdbp cmnbo anc kplut izks ogk mvyd eif" -w -dw
the quick brown fox iumps over the lazy dog
```

Same as above, using a step size of 1 instead of the default 2:

```bash
$ ./nesw_cipher.py -m "the quick brown fox jumps over the lazy dog" -wde -s1
udz ptnhl cniqm ptd klgir safs pcy pkee ekb

$ ./nesw_cipher.py -m "udz ptnhl cniqm ptd klgir safs pcy pkee ekb" -wdw -s1
the quick brown fox iumps over the lazy dog
```

And now replacing "V" with "U":

```bash
$./nesw_cipher.py -m "the quick brown fox jumps over the lazy dog" -wde -rvu -s1
pdz kzmhq cnjpm otd fqhor safs kcy kjee efb

$ ./nesw_cipher.py -m "pdz kzmhq cnjpm otd fqhor safs kcy kjee efb" -wdw -rvu -s1
the quick brown fox jumps ouer the lazy dog
```

Read message from file and output result to a separate file, then decipher the
output file:

```
$ ./nesw_cipher.py -f plaintext.txt -dne -o ciphertext.txt

$ ./nesw_cipher.py -f ciphertext.txt -dsw
You thought I was going to say something about a fox and a dog, didn't you?
```

Encipher and decipher a message in one line:

```
$ ./nesw_cipher.py -f pipe.txt | ./nesw_cipher.py -ds
All this appears to do is output the contents of "pipe.txt", but it shows that
you can pipe the output of other programs into this tool and vice versa.
```

Notice how case, whitespace, and punctuation are preserved. As these are things
that may reveal information about the content of a message, it is a good idea to
only use lowercase letters, and only use spaces to sparate the message in groups
of a fixed length instead of separating words (i.e. "thequ ickbr ownfo xjump
sover thela zydog), which is common practice with hand ciphers. Numbers are also
not enciphered, so avoid them as well.

These examples should be enough to demonstrate how all of the available command
line flags can be used.
