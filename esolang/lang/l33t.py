"""Interpreter for the l33t programming language.

https://esolangs.org/wiki/L33t
http://web.archive.org/web/20060708073949/http://electrod.ifreepages.com/l33tspec.htm
"""

import logging
import socket
import string
import sys

from collections import defaultdict

from esolang import INTERPRETERS

# logging
logger = logging.getLogger(__name__)

STANDARD_ERROR = "j00 4r3 teh 5ux0r\n"
CONNECTION_ERROR = "h0s7 5uXz0r5! c4N'7 c0Nn3<7 l0l0l0l0l l4m3R !!!\n"
IF_EIF_ERROR = "l34rn t0 cL0s3 y0uR 1Fs!!!\n"


# opcodes
NOP = 0
WRT = 1
RD = 2
IF = 3
EIF = 4
FWD = 5
BAK = 6
INC = 7
DEC = 8
CON = 9
END = 10


class StandardConnection(object):
    """Socket emulation for files."""

    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile

    def send(self, msg):
        self.outfile.write(msg)
        return len(msg)

    def recv(self, length):
        return self.infile.read(length)

    def close(self):
        pass


class L33tInterpreter(object):
    lang = "l33t"
    ext = ".l33t"

    def __init__(self, infile=sys.stdin, outfile=sys.stdout, errfile=sys.stderr,
                 memsize=64 * 1024):
        self.infile = infile
        self.outfile = outfile
        self.errfile = errfile

        self.connection = StandardConnection(self.infile, self.outfile)

        self.memsize = int(memsize)
        assert memsize > 0

        self.memory = defaultdict(lambda: 0)

        # memory pointer
        self.ptr = 0

        # instruction pointer
        self.pc = 0

    @property
    def mem(self):
        """Returns a copy of the current memory."""
        try:
            return [self.memory[i] for i in range(0, max(self.memory.keys())+1)]
        except ValueError:
            return []

    def parse(self, source):
        for i, word in enumerate(source.split()):
            self.memory[i] = sum([int(c) for c in word if c in string.digits])
            self.ptr += 1

        logger.debug("Source loaded. pc = %d, ptr = %d" % (self.pc, self.ptr))
        logger.debug("Code: %s" % str(self.mem))

    def step(self):
        op = self.memory[self.pc]

        if op == NOP:
            pass
        elif op == WRT:
            self.connection.send(bytes(chr(self.memory[self.ptr])))
        elif op == RD:
            self.memory[self.ptr] = ord(self.connection.recv(1))
        elif op == IF:
            if self.memory[self.ptr] == 0:
                addrs = [k for (k, v) in self.memory.items()
                         if v == IF or v == EIF]

                lower = [addr for addr in addrs if addr <= self.pc]
                upper = [addr for addr in addrs if addr > self.pc]

                indices = sorted(upper)
                indices.append(sorted(lower))

                closing_pc = None
                opening_count = 0
                for i in indices:
                    instr = self.memory[i]
                    if instr == IF:
                        opening_count += 1
                    elif instr == EIF:
                        if opening_count == 0:
                            closing_pc = i
                            break
                        else:
                            opening_count -= 1
                else:
                    self.errfile.write(IF_EIF_ERROR)
                    raise StopIteration(IF_EIF_ERROR)

                self.pc = closing_pc
        elif op == EIF:
            if self.memory[self.ptr] == 0:
                addrs = [k for (k, v) in self.memory.items()
                         if v == IF or v == EIF]

                lower = [addr for addr in addrs if addr <= self.pc]
                upper = [addr for addr in addrs if addr > self.pc]

                indices = list(reversed(lower))
                indices.append(reversed(upper))

                opening_pc = None
                closing_count = 0
                for i in indices:
                    instr = self.memory[i]
                    if instr == IF:
                        if closing_count == 0:
                            opening_pc = i
                            break
                        else:
                            closing_count -= 1
                    elif instr == EIF:
                        closing_count += 1
                else:
                    self.errfile.write(IF_EIF_ERROR)
                    raise StopIteration(IF_EIF_ERROR)

                self.pc = opening_pc
        elif op == FWD:
            self.pc += 1
            self.pc %= self.memsize
            self.ptr += self.memory[self.pc] + 1
            self.ptr %= self.memsize
        elif op == BAK:
            self.pc += 1
            self.pc %= self.memsize
            self.ptr -= self.memory[self.pc] + 1
            self.ptr %= self.memsize
        elif op == INC:
            self.pc += 1
            self.pc %= self.memsize
            self.memory[self.ptr] += self.memory[self.pc] + 1
            self.memory[self.ptr] %= 256
        elif op == DEC:
            self.pc += 1
            self.pc %= self.memsize
            self.memory[self.ptr] -= self.memory[self.pc] + 1
            self.memory[self.ptr] %= 256
        elif op == CON:
            try:
                sock = socket.socket()
                addrs = [(self.ptr + i) % self.memsize for i in range(6)]
                values = [self.memory[addr] for addr in addrs]
                if values == [0, 0, 0, 0, 0, 0]:
                    self.connection.close()
                    self.connection = StandardConnection(
                        self.infile, self.outfile)
                else:
                    host = ".".join(str(values[i]) for i in range(4))
                    port = values[4] * 256 + values[5]
                    sock.connect((host, port))
                    self.connection.close()
                    self.connection = sock
            except socket.error:
                self.errfile.write(CONNECTION_ERROR)
        elif op == END:
            raise StopIteration()
        else:
            self.errfile.write(STANDARD_ERROR)

        self.pc += 1
        self.pc %= self.memsize

    def run(self, source=None):
        if source is not None:
            self.parse(source)

        while True:
            try:
                self.step()
            except StopIteration:
                return


INTERPRETERS.append(L33tInterpreter)
