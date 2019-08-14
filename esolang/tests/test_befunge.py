"""Unittests for the Brainfuck interpreter.

Code Examples taken from:
 * https://esolangs.org/wiki/brainfuck
"""

from unittest import TestCase

from io import StringIO

from esolang.lang.befunge import BefungeInterpreter as Interpreter

HELLO_WORLD = """64+"!dlroW ,olleH">:#,_@"""

HELLO_WORLD_OUTPUT = "Hello World!\n"


class BefungeTests(TestCase):
    def run_code(self, code, interpreter=None):
        """Run the brainfuck code and return the standard output as string."""
        if interpreter is None:
            interpreter = Interpreter()
        outfile = StringIO()
        interpreter.run(code, outfile=outfile)
        outfile.seek(0)
        return outfile.read()

    def test_hello_world(self):
        self.assertEqual(HELLO_WORLD_OUTPUT, self.run_code(HELLO_WORLD))
