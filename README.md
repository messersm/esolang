# esolang
> A collection of interpreters for "esoteric" programming languages
written in Python.

## About
``esolang`` provides a collections of interpreters of
[esoteric programming languages](https://esolangs.org)
together with a framework for writing new interpreters and
a collection of some examples.

Supported languages are:
 * [Brainfuck](https://esolangs.org/wiki/Brainfuck)
 * [Befunge](https://esolangs.org/wiki/Befunge) (incomplete)
 * [Monkeys](https://esolangs.org/wiki/Monkeys)

## Development status
``esolang`` is in early development and it's a just-for-fun project
anyway. For now you can simply run programs, if a suitable interpreter
is implemented, but I would like add functionality for setting
interpreter parameters, step-by-step-execution and interpreter state
inspection. If you would like to [contribute](#contributing), send a pull request or
an email. 

Please do note, that I don't strive to implement support for
as many languages as possible, but simply for a few well known
esoteric languages as well as those, which I think are being fun
in some way. (But I will gladly add a new language to this
project, if you have some running interpreter for it and
are willing to license it under the MIT License.) 

## Installation
For now you have to clone this repository and go from there:
```sh
git clone https://github.com/messersm/esolang.git
```

## Running programs
From the repository root you can execute a program like this: 
```sh
$ python -m esolang <source.ext>
```

``.ext`` must be a file extension associated with a supported language.
To get a list of supported languages together with their associated
file extension use the ``--list`` flag:
```sh
$ python -m esolang --list
```

If your file does not have the associated file extension, you
can still run it by specifying the language:  
```sh
$ python -m esolang --lang <language> <source.ext> 
```

## Contributing
As mentioned above, send me a pull request or an email, if you
want to contribute.

Right now, there are no conventions in place, which would
enable features like single-stepping, debugging, interpreter
state introspection, etc. but I'm working on that. (You
can take a look at the ``Interpreter`` class in ``interpreter.py``
to get an idea, but this is really just a draft.) 

The idea is to have a minimum set of conventions about
attribute and method names and behavior a class should have,
in order to enable esolang to derive the information necessary
to implement these features, without having the author of the
interpreter to write any additional code in order to fit into the
framework. (Using Python introspection this should be no problem,
once some conventions have been developed.) 

For now, an interpreter class should provide the following:
 * A ``lang`` attribute (a string), which specifies the
   name of the language.
 * An ``ext`` attribute (a string), which specifies the file
   extension used by the language.
 * An ``__init__()`` method with no non-optional arguments.
 * A ``run()`` method which takes one argument that contains
   the source code of a file written in this language (as string). 

Let's say, we want to write an interpreter for an esoteric
programming language named "FYI" which prints the contents of each line
that starts with ``"FYI: "`` (and does nothing more).

Here is, how an interpreter could look like:
```python
# fyi.py
class FYIInterpreter(object):
    lang = "FYI"    
    ext = ".fyi"
    
    def run(self, source):
        for line in source.split("\n"):
            if line.startswith("FYI: "):
                print(line)

# This will make the interpreter available to the command
# line interface of esolang. Additionally esolang.__init__.py
# must have a line 'import esolang.lang.fyi'.
from esolang import INTERPRETERS 
INTERPRETERS.append(FYIInterpreter)
```

A hello world program would look like this:
```
# hello.fyi
# Run with 'python -m esolang hello.fyi'
FYI: Hello world!
```
The file could be executed like this:
```sh
$ python -m esolang hello.fyi
```
