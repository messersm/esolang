"""Interpreter for ABCR

https://esolangs.org/wiki/ABCR
https://github.com/Steven-Hewitt/ABCR
"""

from __future__ import print_function

import string
import sys

from collections import deque
from operator import add, sub

from esolang.helpers import flow, Register, Fifo, FileBuffer
from esolang import INTERPRETERS

if sys.version_info.major < 3:
    chr = unichr


class ABCRInterpreter(object):
    lang = "ABCR"
    ext = ".abcr"

    def __init__(self,
                 infile=sys.stdin, outfile=sys.stdout, errfile=sys.stderr):
        self.r = Register(0)
        self.a = Fifo(lambda: 0, lambda: 0)
        self.b = Fifo(lambda: 1, lambda: 1)
        self.c = Fifo(
            pop_default=self._read_all_chars_into_c,
            peek_default=self.r.get)

        self.source = None
        self.pc = 0  # program counter

        self.infile = infile
        self.outfile = outfile
        self.errfile = errfile

        self.inbuffer = FileBuffer(self.infile)

        self.commands = {
            "a": flow(self.r.put, self.a.get),
            "b": flow(self.r.put, self.b.get),
            "c": flow(self.r.put, self.c.get),

            "A": flow(self.a.put, self.r.get),
            "B": flow(self.b.put, self.r.get),
            "C": flow(self.c.put, self.r.get),

            # r = f.peek()
            "1": flow(self.r.put, self.a.peek),
            "2": flow(self.r.put, self.b.peek),
            "3": flow(self.r.put, self.c.peek),

            "!": flow(self.r.put, len, self.a),
            "@": flow(self.r.put, len, self.b),
            "#": flow(self.r.put, len, self.c),

            # r = r + f.get()
            "*": flow(self.r.put, add, self.r.get, self.a.get),
            "+": flow(self.r.put, add, self.r.get, self.b.get),
            ",": flow(self.r.put, add, self.r.get, self.c.get),

            # r = r - f.get()
            "-": flow(self.r.put, sub, self.r.get, self.a.get),
            ".": flow(self.r.put, sub, self.r.get, self.b.get),
            "/": flow(self.r.put, sub, self.r.get, self.c.get),

            # output values as numbers
            "o": flow(self.outfile.write, self.a.peek),
            "p": flow(self.outfile.write, self.b.peek),
            "q": flow(self.outfile.write, self.c.peek),

            # output values as characters
            "O": flow(self.outfile.write, chr, self.a.peek),
            "P": flow(self.outfile.write, chr, self.b.peek),
            "Q": flow(self.outfile.write, chr, self.c.peek),

            # loops
            "4": flow(self._skip_loop_if_zero, self.a.peek),
            "5": flow(self._skip_loop_if_zero, self.b.peek),
            "6": flow(self._skip_loop_if_zero, self.c.peek),
            "7": flow(self._skip_loop_if_zero, self.r.get),

            # marks
            "x": self._jump_back_to_loop_start,

            # inc, dec R
            "(": flow(self.r.put, sub, self.r.get, 1),
            ")": flow(self.r.put, add, self.r.get, 1),

            "i": self._read_signed_into_r,
        }

    def _skip_loop_if_zero(self, value):
        if value == 0:
            while self.pc < len(self.source) and self.source[self.pc] != "x":
                self.pc += 1

    def _jump_back_to_loop_start(self):
        while self.source[self.pc] not in "4567" and self.pc > 0:
            self.pc -= 1

        # The run() loop automatically increments pc after calling
        # us, so have have to decrement pc one more time.
        self.pc -= 1

    def _read_signed_into_r(self):
        s = ""

        while True:
            char = self.inbuffer.get()

            if char in "-+0123456789":
                s += char
            else:
                self.inbuffer.put(char)
                break

        try:
            self.r.put(int(s))
        except ValueError:
            self.r.put(0)

    def _read_all_chars_into_c(self):
        char = self.inbuffer.get()
        if not char:
            raise EOFError(
                "Tried to read from C-queue without available input.")

        while char:
            self.c.put(ord(char))
            char = self.inbuffer.get()

    def run(self, source):
        self.source = source

        while True:
            if self.pc >= len(self.source):
                break

            char = self.source[self.pc]
            func = self.commands.get(char, None)
            if func is None:
                pass
            else:
                func()

            self.pc += 1


INTERPRETERS.append(ABCRInterpreter)
