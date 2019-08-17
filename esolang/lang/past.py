"""An interpreter for My Unreliable Past programs

https://esolangs.org/wiki/My_Unreliable_Past
"""
import logging
import string
import sys
import threading

from random import choice, random, randrange

from esolang import INTERPRETERS

logger = logging.getLogger(__name__)

if sys.version_info.major < 3:
    chr = unichr
    from Queue import Queue
else:
    from queue import Queue


def align(source):
    """Return a string containing the same program but aligned
    to the start of a transaction or command (in that order).

    This function does not run a complete syntax check, but raises
    an ValueError, if the source is commented incorrectly.

    Examples:
        >>> align("+67; O=0, O+66; O=0, O")
        ' O=0, O+66; O=0, O+67;'
        >>> align("0, O+66, O=")
        ' O+66, O=0,'
        >>> align("=0O")
        'O=0'
        >>> align("some (comments) in here.)(Only ")
        '(Only some (comments) in here.)'

    Raises:
        ValueError: If the source is commented incorrectly.
    """
    # It's important to align at comments first, because
    # and of ";,=+-" could be part of a comment.

    # make sure, we have a correct count of '(' and ')'
    if not source.count('(') == source.count(')'):
        raise ValueError(
            "Incorrectly commented source: count fo '(':" +
            "%d, count for ')': %d." % (source.count('('), source.count(')')))

    indices = [idx for idx in range(len(source)) if source[idx] == '(']
    for start in indices:
        idx = start
        count = 0

        # Run through the source and keep track of the
        # count of opening and closing parentheses.
        # If we reach the starting index again and count is 0
        # we have found a valid starting index for the program,
        # if the count is < 0 at any point, the starting point is invalid.
        while True:
            if source[idx] == '(':
                count += 1
            elif source[idx] == ')':
                count -= 1

            if count < 0:
                break

            idx += 1
            idx %= len(source)
            if idx == start:
                break

        # found a valid start
        if count == 0:
            return source[start:] + source[:start]

    # If we reached this point, there wasn't a valid starting '('.
    if indices:
        raise ValueError(
            "Incorrectly commented source. No valid rotation exists.")

    for char in ";,":
        try:
            idx = source.index(char)
            source = source[idx + 1:] + source[:idx + 1]
            return source
        except ValueError:
            pass

    # no ";" or "," present align at "+-="
    for char in "+-=":
        try:
            idx = source.index(char)
            source = source[idx - 1:] + source[:idx - 1]
            return source
        except ValueError:
            pass

    # Source empty? There could still be syntactically invalid programs,
    # but this is checked later...
    return source


def strip_comments(source):
    """Remove all comments from the source.

    This must be run after align().
    """
    s = ""
    count = 0
    for char in source:
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
        elif count == 0:
            s += char

    return s


class Interpreter(object):
    lang = "My Unreliable Past"
    ext = ".past"

    def __init__(
            self, infile=sys.stdin, outfile=sys.stdout, errfile=sys.stderr):
        self.infile = infile
        self.outfile = outfile
        self.errfile = errfile

        self.registers = dict([(n, 0) for n in "ABCDEFGHIKLMNOPQRSTUWXYZ"])
        self.transactions = []
        self.tc = 0

        self.input_q = Queue()
        self.input = []
        self.input_idx = 0
        self.input_lock = threading.Lock()
        self.input_chance = 0.125

        self.output_q = Queue()
        self.output = []
        self.output_lock = threading.Lock()
        self.output_chance = 0.125

        self.running = True

    def input_thread(self):
        """Keeps reading the infile until it closes."""
        while self.running:
            if self.input_q.empty():
                char = self.infile.read(1)
                if char:
                    self.input_q.put(char)

    def output_thread(self):
        """Write everything from the output_q to outfile."""
        while self.running:
            if not self.output_q.empty():
                char = self.output_q.get()
                self.outfile.write(char)
                self.outfile.flush()

    def setup_registers(self):
        logger.info("Setting up registers. This may take a while...")
        for name in self.registers:

            # Randomize register value
            # 0 with chance 1/2 = 1/2 ** 1
            # 1 with chance 1/4 = 1/2 ** 2
            # [2, 3] with chance 1/8 = 1/2 ** 3
            # [4, 5, 6, 7] with chance 1/16 = 1/2 ** 4
            exp = 0
            while True:
                vmin = int(2**(exp-1))
                vmax = 2**exp
                exp += 1

                # On each iteration, we accept half of the random() result.
                # E.g. This gives us 1/2 ** 3 = 1/8 chance
                # for the 3rd iteration.
                if random() < 0.5:
                    self.registers[name] = randrange(vmin, vmax)
                    break

    def load(self, source):
        # align the source, strip comments and whitespace,
        # split by transaction and command and parse the resulting
        # lists.
        source = align(source)
        source = strip_comments(source)
        for char in string.whitespace:
            source = source.replace(char, "")

        self.transactions = []
        for t in source.split(";"):
            # skip empty transactions
            if not t:
                continue

            commands = []
            for c in t.split(","):
                # skip empty commands
                if not c:
                    continue

                if len(c) < 3:
                    raise ValueError(
                        "Command '%s' too short in transaction '%s'." % (c, t))

                if c[0] not in self.registers:
                    raise ValueError(
                        ("Unsupported register '%s' in " +
                         "transaction '%s'.") % (c[0], t))

                if c[1] not in "+-=":
                    raise ValueError(
                        ("Unsupported operation '%s' in " +
                         "transaction '%s'.") % (c[1], t))

                try:
                    value = int(c[2:])
                except ValueError:
                    raise ValueError(
                        ("Invalid integer '%s' in " +
                         "transaction '%s'.") % (c[2:], t))

                commands.append((c[0], c[1], value))
            self.transactions.append(commands)

    def step(self):
        """Execute a single transaction"""

        # Create a backup, in case we have to rollback.
        backup = dict(self.registers)

        for name, op, value in self.transactions[self.tc]:
            if op == "+":
                self.registers[name] += value
            elif op == "-":
                self.registers[name] -= value
            elif op == "=":
                # Rollback and cancel the transaction,
                # if reg doesn't have the correct value.
                if self.registers[name] != value:
                    self.registers = backup
                    break

        # handle I/O
        if self.registers["O"] != 0:
            if random() < self.output_chance and self.output_q.empty():
                self.output_q.put(chr(self.registers["O"] - 1))
                self.registers["O"] = 0

        if self.registers["I"] == 0:
            if random() < self.input_chance:
                char = None
                if self.infile.closed:
                    # replay already seen input, unless we have none.
                    if len(self.input) > 0:
                        self.input_idx %= len(self.input)
                        char = self.input[self.input_idx]
                        self.input_idx += 1

                elif not self.input_q.empty():
                    # get char from input_q and add it to input
                    char = self.input_q.get()
                    self.input.append(char)

                if char is not None:
                    self.registers["I"] = ord(char) + 1

        self.tc += 1
        self.tc %= len(self.transactions)

    def run(self, source):
        self.load(source)
        self.setup_registers()

        # Set transaction counter to a random transaction.
        self.tc = randrange(len(self.transactions))

        logger.info("Starting I/O threads...")
        t1 = threading.Thread(target=self.input_thread)
        t2 = threading.Thread(target=self.output_thread)
        t1.daemon = t2.daemon = True
        t1.start()
        t2.start()

        while True:
            try:
                self.step()
            except StopIteration:
                break


INTERPRETERS.append(Interpreter)
