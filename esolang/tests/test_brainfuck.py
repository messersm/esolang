"""Unittests for the Brainfuck interpreter.

Code Examples taken from:
 * https://esolangs.org/wiki/brainfuck
"""

from unittest import TestCase

from io import StringIO

from esolang.lang.brainfuck import BrainfuckInterpreter

HELLO_WORLD = """
>++++++++[-<+++++++++>]<.>>+>-[+]++>++>+++[>[->+++<<+++>]<<]>-----.>->
        +++..+++.>-.<<+[>[+>+]>>]<--------------.>>.+++.------.--------.>+.>+.
"""

HELLO_WORLD_OUTPUT = "Hello World!\n"

HELLO_WORLD_2 = """
++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.
+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.
"""

HELLO_WORLD_2_OUTPUT = "Hello World!\n"

CELLSIZE_TEST = """
Calculate the value 256 and test if it's zero
If the interpreter errors on overflow this is where it'll happen
++++++++[>++++++++<-]>[<++++>-]
+<[>-<
    Not zero so multiply by 256 again to get 65536
    [>++++<-]>[<++++++++>-]<[>++++++++<-]
    +>[>
        # Print "32"
        ++++++++++[>+++++<-]>+.-.[-]<
    <[-]<->] <[>>
        # Print "16"
        +++++++[>+++++++<-]>.+++++.[-]<
<<-]] >[>
    # Print "8"
    ++++++++[>+++++++<-]>.[-]<
<-]<
# Print " bit cells\n"
+++++++++++[>+++>+++++++++>+++++++++>+<<<<-]>-.>-.+++++++.+++++++++++.<.
>>.++.+++++++..<-.>>-
Clean up used cells.
[[-]<]
"""


class BrainfuckTests(TestCase):
    def run_code(self, code, interpreter=None):
        """Run the brainfuck code and return the standard output as string."""
        if interpreter is None:
            interpreter = BrainfuckInterpreter()
        outfile = StringIO()
        interpreter.run(code, outfile=outfile)
        outfile.seek(0)
        return outfile.read()

    def test_hello_world(self):
        self.assertEqual(HELLO_WORLD_OUTPUT, self.run_code(HELLO_WORLD))

    def test_hello_world_2(self):
        self.assertEqual(HELLO_WORLD_2_OUTPUT, self.run_code(HELLO_WORLD_2))

    def test_cellsize(self):
        for cellsize in 8, 16, 32:
            interpreter = BrainfuckInterpreter(cellsize=cellsize)
            result = "%d bit cells\n" % cellsize
            self.assertEqual(result, self.run_code(CELLSIZE_TEST, interpreter))

        interpreter = BrainfuckInterpreter(cellsize=None)
        result = "32 bit cells\n"
        self.assertEqual(result, self.run_code(CELLSIZE_TEST, interpreter))
