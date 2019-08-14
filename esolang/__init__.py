# We use this list to let the submodules add interpreters on their own
INTERPRETERS = []

# Import modules and let them register with INTERPRETERS.
import esolang.lang.befunge
import esolang.lang.brainfuck
import esolang.lang.monkeys
