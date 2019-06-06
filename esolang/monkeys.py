"""An interpreter for the Monkeys programming language

https://esolangs.org/wiki/Monkeys
"""

import logging
import string
import sys

from random import randrange

from esolang import INTERPRETERS

# logger = logging.getLogger(__name__)


SETUP = """
..!1.!....
.......2!.
.........!
.3.!......
.......!..
.!....!...
..5.!4....
....6...!.
......!...
.7......!.
""".strip().split("\n")


class Monkey(object):
    def __init__(self, x, y, number):
        self.x = x
        self.y = y
        self.number = number

        self.__value = 0
        self.sleeping = False
        self.mark = None
        self.banana = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value % 256
        # logger.debug("Setting monkey %d to value %d" % (
        #    self.number, self.value))


class Banana(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


ACTIONS = "UP DOWN LEFT RIGHT"
ACTIONS += " LEARN YELL PLAY SLEEP WAKE"
ACTIONS += " GRAB DROP EAT"
ACTIONS += " MARK BACK"
ACTIONS += " TEACH FIGHT BOND EGO"
ACTIONS = ACTIONS.split()


class MonkeysInterpreter(object):
    lang = "Monkeys"
    ext = ".mky"

    def __init__(self, infile=sys.stdin, outfile=sys.stdout, strict=False):
        """

        When in strict mode the interpreter will only accept
        lines of source code, which have exactly 2 items: the monkey
        number and the action the monkey should take. Otherwise it
        will ignore any additional items, which can be used to
        place comments at the end of the line.
        """
        self.infile = infile
        self.outfile = outfile
        self.strict = strict

        self.bananas = []
        self.monkeys = []

        for y in range(10):
            for x in range(10):
                if SETUP[y][x] in string.digits:
                    number = int(SETUP[y][x])
                    monkey = Monkey(x, y, number)
                    self.monkeys.append(monkey)

                if SETUP[y][x] in "!67":
                    self.bananas.append(Banana(x, y))

        self.code = []
        self.pc = 0

    def run(self, source):
        self.load(source)

        while True:
            run = self.step()
            if not run:
                break

    def load(self, source):
        self.code = []
        for line in source.split("\n"):
            try:
                items = line.split(" ")
                if len(items) > 2 and self.strict:
                    continue

                number, action = items[0], items[1]
                number = int(number)
                assert 1 <= number <= 7
                assert action in ACTIONS
                self.code.append((number, action))
            except (IndexError, ValueError, AssertionError):
                # Invalid line
                pass

        self.pc = 0

    def step(self):
        # exit on program end
        if self.pc >= len(self.code):
            return False
        # exit, if all bananas are eaten
        elif not self.bananas:
            return False

        number, action = self.code[self.pc]
        monkey = self.monkeys[number - 1]

        # solo actions
        if monkey.sleeping:
            if action == "WAKE":
                monkey.sleeping = False
        elif action == "SLEEP":
            if not monkey.banana:
                monkey.sleeping = True
        elif action == "LEARN":
            monkey.value = ord(self.infile.read(1))
        elif action == "YELL":
            self.outfile.write(chr(monkey.value))
        elif action == "PLAY":
            monkey.value = randrange(0, 256)

        # movement actions
        elif action == "UP":
            self._move(monkey, 0, -1)
        elif action == "DOWN":
            self._move(monkey, 0, 1)
        elif action == "LEFT":
            self._move(monkey, -1, 0)
        elif action == "RIGHT":
            self._move(monkey, 1, 0)

        # banana actions
        elif action == "GRAB":
            if not monkey.banana:
                monkey.banana = self._banana_at(monkey.x, monkey.y)
        elif action == "DROP":
            monkey.banana = None
        elif action == "EAT":
            if monkey.banana:
                self.bananas.remove(monkey.banana)
                monkey.banana = None

        # marker actions
        elif action == "MARK":
            monkey.mark = self.pc
        elif action == "BACK":
            if monkey.mark is not None:
                # -1 because of the pc increment below
                self.pc = monkey.mark - 1

        # group actions
        elif action == "TEACH":
            for m in self._adjacent(monkey):
                if not m.sleeping:
                    m.value += monkey.value
        elif action == "FIGHT":
            for m in self._adjacent(monkey):
                if not m.sleeping:
                    m.value -= monkey.value
        elif action == "BOND":
            for m in self._adjacent(monkey):
                if not m.sleeping:
                    m.value *= monkey.value
        elif action == "EGO":
            for m in self._adjacent(monkey):
                if not m.sleeping:
                    try:
                        m.value //= monkey.value
                    except ZeroDivisionError:
                        pass

        self.pc += 1
        return True

    def _adjacent(self, monkey):
        return [m for m in self.monkeys if m != monkey
                and abs(monkey.x - m.x) < 2 and abs(monkey.y - m.y) < 2]

    def _move(self, monkey, dx, dy):
        new_x, new_y = monkey.x + dx, monkey.y + dy

        # illegal move
        if (not 0 <= new_x <= 9) or (not 0 <= new_y <= 9):
            monkey.value = (monkey.value - 1) % 256
        # collide
        elif self._monkey_at(new_x, new_y):
            other = self._monkey_at(new_x, new_y)
            if other.sleeping:
                other.sleeping = False
            else:
                if bool(monkey.banana) == bool(other.banana):
                    monkey.value = (monkey.value + 1) % 256
                    other.value = (other.value + 1) % 256
                else:
                    monkey.banana, other.banana = (
                        other.banana, monkey.banana)
        # move and check for adjacent
        else:
            monkey.x, monkey.y = new_x, new_y
            if not self._adjacent(monkey):
                monkey.value = (monkey.value + 1) % 256

            # move the banana as well
            if monkey.banana:
                monkey.banana.x = monkey.x
                monkey.banana.y = monkey.y

    def _monkey_at(self, x, y):
        for m in self.monkeys:
            if m.x == x and m.y == y:
                return m

    def _banana_at(self, x, y):
        for b in self.bananas:
            if b.x == x and b.y == y:
                return b

    @property
    def grid(self):
        """Return a string representing the current grid state.

        Note::
            The given representation may not hold every
            information, when multiple bananas are in one
            place or a monkey is standing in the same position
            as a banana.
        """

        lines = []
        for row in range(10):
            s = ""

            for col in range(10):
                monkey = self._monkey_at(col, row)
                banana = self._banana_at(col, row)

                if monkey:
                    s += str(monkey.number)
                elif banana:
                    s += "!"
                else:
                    s += "."

            lines.append(s)

        return "\n".join(lines)


INTERPRETERS.append(MonkeysInterpreter)
