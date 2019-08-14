import sys


class Interpreter(object):
    def __init__(self, infile=sys.stdin, outfile=sys.stdout):
        self.infile = infile
        self.outfile = outfile
        self.code = []
        self.pc = 0

    def load(self, source):
        raise NotImplementedError("Implement in subclass")

    def exec(self, line):
        raise NotImplementedError()

    def step(self):
        try:
            line = self.code[self.pc]
        except IndexError:
            raise StopIteration("EOF reached.")

        self.exec(line)
        self.pc += 1

    def run(self, source=None):
        if source:
            self.load(source)

        while True:
            try:
                self.step()
            except StopIteration:
                pass
