from io import StringIO
from unittest import TestCase
from random import randrange

from esolang.lang.abcr import ABCRInterpreter


class ABCRTests(TestCase):
    def test_start(self):
        """On start all fifos are empty and R is 0."""
        intp = ABCRInterpreter()
        self.assertEqual(list(intp.a), [])
        self.assertEqual(list(intp.b), [])
        self.assertEqual(list(intp.c), [])
        self.assertEqual(intp.r.get(), 0)

    def test_dequeue(self):
        """'a', 'b' and 'c' dequeue a single value from a FIFO into R."""
        for name in ('a', 'b', 'c'):
            intp = ABCRInterpreter()
            cmd = name
            q = getattr(intp, name)
            q.append(10)
            q.append(14)
            intp.run(cmd)
            self.assertEqual(list(q), [14])
            self.assertEqual(intp.r.get(), 10)

    def test_enqueue(self):
        """'A', 'B' and 'C' enqueue a single value from R to a FIFO."""
        for name in ('a', 'b', 'c'):
            intp = ABCRInterpreter()
            cmd = name.upper()
            q = getattr(intp, name)
            q.append(10)
            intp.r.put(5)
            intp.run(cmd)
            self.assertEqual(list(q), [10, 5])

    def test_peek(self):
        """'1', '2' and '3' set R to the top value of a FIFO."""
        for name, cmd in (('a', '1'), ('b', '2'), ('c', '3')):
            intp = ABCRInterpreter()
            q = getattr(intp, name)
            q.append(10)
            q.append(14)
            intp.run(cmd)
            self.assertEqual(list(q), [10, 14])
            self.assertEqual(intp.r.get(), 10)

    def test_length(self):
        """'!', '@' and '#' set R to the length of a FIFO."""
        for name, cmd in (('a', '!'), ('b', '@'), ('c', '#')):
            intp = ABCRInterpreter()
            q = getattr(intp, name)
            length = randrange(5, 11)
            for _ in range(length):
                q.append(4)
            backup = list(q)

            intp.run(cmd)
            self.assertEqual(list(q), backup)
            self.assertEqual(intp.r.get(), length)

    def test_add(self):
        """'*', '+' and ',' add the top value of a FIFO to R."""
        for name, cmd in (('a', '*'), ('b', '+'), ('c', ',')):
            intp = ABCRInterpreter()
            intp.r.put(3)
            q = getattr(intp, name)
            q.append(10)
            q.append(14)
            intp.run(cmd)
            self.assertEqual(list(q), [14])
            self.assertEqual(intp.r.get(), 13)

    def test_sub(self):
        """'-', '.' and '/' subtract the top value of a FIFO from R."""
        for name, cmd in (('a', '-'), ('b', '.'), ('c', '/')):
            intp = ABCRInterpreter()
            intp.r.put(3)
            q = getattr(intp, name)
            q.append(10)
            q.append(14)
            intp.run(cmd)
            self.assertEqual(list(q), [14])
            self.assertEqual(intp.r.get(), -7)

    def test_print_number(self):
        """'o', 'p' and 'q' print the top of a FIFO as number."""
        for name, cmd in (('a', 'o'), ('b', 'p'), ('c', 'q')):
            output = StringIO()
            intp = ABCRInterpreter(outfile=output)
            q = getattr(intp, name)
            q.append(10)
            q.append(14)
            intp.run(cmd)
            self.assertEqual(list(q), [10, 14])
            self.assertEqual(output.getvalue(), "10")
