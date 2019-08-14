from collections import defaultdict

import sys

from esolang import INTERPRETERS

if sys.version_info.major < 3:
    chr = unichr


class BrainfuckInterpreter(object):
    lang = "Brainfuck"
    ext = ".b"

    def __init__(self, cellsize=8):
        """Create a new Brainfuck Interpreter.

        Args:
            cellsize: The size of a single memory cell in Bit.
                      (can be set to None, which means infinite memory per cell.
        """

        if cellsize is None:
            self.cellsize = cellsize
            self.MAXNUM = float("inf")
        else:
            try:
                self.cellsize = int(cellsize)
                if cellsize < 1:
                    raise ValueError()
            except ValueError:
                raise ValueError("cellsize must be int >= 1")

            self.MAXNUM = 2 ** self.cellsize

        self.memory = defaultdict(lambda: 0)
        self.pointer = 0

    def __build_jump_targets(self, code):
        """Return a dict of jump targets."""
        targets = {}
        opening = []

        for index, char in enumerate(code):
            if char == "[":
                opening.append(index)
            elif char == "]":
                try:
                    open_idx = opening.pop()
                    targets[open_idx] = index
                    targets[index] = open_idx
                except IndexError:
                    raise ValueError("Bracket at char %d doesn't open." % index)

        if opening:
            raise ValueError("Bracket at char %d doesn't close." % opening.pop())

        return targets

    def run(self, code, infile=sys.stdin, outfile=sys.stdout):
        jump_targets = self.__build_jump_targets(code)
        index = 0

        while True:
            # Reached EOF.
            if index >= len(code):
                break

            char = code[index]

            if char == ">":
                self.pointer += 1
            elif char == "<":
                self.pointer -= 1
            elif char == "+":
                self.memory[self.pointer] += 1
                if self.cellsize:
                    self.memory[self.pointer] %= self.MAXNUM
            elif char == "-":
                self.memory[self.pointer] -= 1
                if self.cellsize:
                    self.memory[self.pointer] %= self.MAXNUM
            elif char == ".":
                outfile.write(str(chr(self.memory[self.pointer])))
            elif char == ",":
                self.memory[self.pointer] = ord(infile.read())
            elif char == "[":
                if not self.memory[self.pointer]:
                    index = jump_targets[index]
            elif char == "]":
                if self.memory[self.pointer]:
                    index = jump_targets[index]

            index += 1

        return self.memory[self.pointer]

    def memory_as_list(self):
        """Return the internal memory as list."""
        min_ptr = min(self.memory.keys())
        max_ptr = max(self.memory.keys())
        return [self.memory[ptr] for ptr in range(min_ptr, max_ptr+1)]


INTERPRETERS.append(BrainfuckInterpreter)