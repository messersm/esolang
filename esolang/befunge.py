"""

For documentation of the language see:
https://esolangs.org/wiki/Befunge

"""

import string
import sys

if sys.version_info.major < 3:
    chr = unichr

from random import choice


class BefungeInterpreter(object):
    """Befunge-93 interpreter"""

    lang = "Befunge"
    ext = ".bf"

    WIDTH = 80
    HEIGHT = 25

    def __init__(self):
        self.dx = 1
        self.dy = 0
        self.x = 0
        self.y = 0

        self.grid = [[" "] * self.WIDTH for _ in range(self.HEIGHT)]
        self.stack = []
        self.string_mode = False

    def load(self, code):
        for row, line in enumerate(code.split("\n")):
            for col, c in enumerate(line):
                self.grid[row][col] = c

    def run(self, code, infile=sys.stdin, outfile=sys.stdout):
        self.load(code)

        while True:
            run = self.step(infile, outfile)
            if not run:
                break

    def step(self, infile=sys.stdin, outfile=sys.stdout):
        op = self.grid[self.y][self.x]

        if self.string_mode:
            if op == '"':
                self.string_mode = False
            else:
                self.stack.append(ord(op))
        else:
            if op == "+":
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a + b)
            elif op == "-":
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b - a)
            elif op == "*":
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a * b)
            elif op == "/":
                a = self.stack.pop()
                b = self.stack.pop()

                if a == 0:
                    msg = "Divsion by zero. What result do you want? "

                    while True:
                        try:
                            result = int(input(msg))
                            self.stack.append(result)
                        except ValueError:
                            msg = "Input must be an integer. Try again: "
                else:
                    self.stack.append(b // a)
            elif op == "%":
                # TODO: Befunge doesn't define behaviour for a == 0
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(b % a)
            elif op == "!":
                a = self.stack.pop()
                self.stack.append(int(not a))
            elif op == "`":
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(int(b > a))
            elif op == ">":
                self.dx, self.dy = 1, 0
            elif op == "<":
                self.dx, self.dy = -1, 0
            elif op == "^":
                self.dx, self.dy = 0, -1
            elif op == "v":
                self.dx, self.dy = 0, 1
            elif op == "?":
                self.dx, self.dy = choice(
                    (1, 0), (-1, 0), (0, -1), (0, 1))
            elif op == "_":
                a = self.stack.pop()
                if a:
                    self.dx, self.dy = -1, 0
                else:
                    self.dx, self.dy = 1, 0
            elif op == "|":
                a = self.stack.pop()
                if a:
                    self.dx, self.dy = -1, 0
                else:
                    self.dx, self.dy = 1, 0
            elif op == '"':
                self.string_mode = True
            elif op == ":":
                self.stack.append(self.stack[-1])
            elif op == "\\":
                a = self.stack.pop()
                b = self.stack.pop()
                self.stack.append(a)
                self.stack.append(b)
            elif op == "$":
                self.stack.pop()
            elif op == ".":
                a = self.stack.pop()
                outfile.write(a)
            elif op == ",":
                a = self.stack.pop()
                outfile.write(chr(a))
            elif op == "#":
                self.x += self.dx
                self.y += self.dy
            elif op == "g":
                y = self.stack.pop()
                x = self.stack.pop()
                try:
                    self.stack.append(ord(self.grid[y][x]))
                except IndexError:
                    self.stack.append(0)
            elif op == "p":
                # TODO: out of bounds undefined?
                y = self.stack.pop()
                x = self.stack.pop()
                v = self.stack.pop()
                self.grid[y][x] = chr(v)
            elif op == "&":
                # TODO
                raise NotImplementedError()
            elif op == "~":
                # TODO
                raise NotImplementedError()
            elif op == "@":
                return False
            elif op in string.digits:
                self.stack.append(int(op))

        # move pc
        self.x += self.dx
        self.y += self.dy
        self.x %= self.WIDTH
        self.y %= self.HEIGHT

        return True
