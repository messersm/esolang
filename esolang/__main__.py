from __future__ import print_function

import os.path
import sys

from argparse import ArgumentParser
from esolang import INTERPRETERS


def list_languages():
    print("Available languages:")
    for cls in INTERPRETERS:
        print("  - %s (%s)" % (cls.lang, cls.ext))


def select_interpreter(filename, lang=None):
    if lang is None:
        ext = os.path.splitext(filename)[-1]
        classes = [cls for cls in INTERPRETERS if cls.ext == ext]
        if not classes:
            raise ValueError(
                ("No interpreter available for extension '%s'.\n" +
                 "Please specify a language using --lang.") % ext)
        elif len(classes) > 1:
            langs = ["'%s'" % cls.lang for cls in classes]
            raise ValueError(
                ("Multiple interpreters available for extension '%s'.\n" +
                 "Please specify a language using --lang.\n" +
                 "Candidates are: %s") % (ext, ", ".join(langs)))
        else:
            return classes[0]
    else:
        classes = [cls for cls in INTERPRETERS if cls.lang == lang]
        if not classes:
            raise ValueError("No interpreter available for lang '%s'" % lang)
        else:
            return classes[0]


def main():
    # build parser and parse command line arguments
    parser = ArgumentParser(
        description="Run esoteric programming language source files.")
    parser.add_argument(
        "filenames", metavar="filename", nargs="*",
        help="an esolang filename to run")
    parser.add_argument(
        "-L", "--list", action="store_const", const=True, default=False,
        help="list all available esoteric programming languages")
    parser.add_argument(
        "-l", "--lang",
        help="interpret the given filename(s) in the given esolang")

    args = parser.parse_args()

    if args.list:
        list_languages()
    elif not args.filenames:
        parser.print_usage()
    else:
        jobs = []

        for filename in args.filenames:
            try:
                cls = select_interpreter(filename, args.lang)
                jobs.append((cls, filename))
            except ValueError as e:
                print(e, file=sys.stderr)
                sys.exit(1)

        for cls, filename in jobs:
            try:
                with open(filename, "r") as f:
                    source = f.read()
            except IOError as e:
                print(e, file=sys.stderr)
                sys.exit(2)

            try:
                intp = cls()
                intp.run(source)
            except ValueError as e:
                print(e, file=sys.stderr)
                sys.exit(3)
            except RuntimeError as e:
                print(e, file=sys.stderr)
                sys.exit(4)


if __name__ == '__main__':
    main()
