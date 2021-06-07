import sys

from stack import (
    Stack, MappedStack,
    StackOverflow, StackUnderflow
)


from loguru import logger
logger.disable(__name__)


NATIVE_WORD = 0
USER_WORD = 1

BITMASK_8 = 0xFF
BITMASK_16 = 0xFFFF

FALSE = 0
TRUE = 0xffff  # -1,  by convention. but also can ba a non-zero value


class Context:
    # PS = Stack()
    # RS = Stack()
    # PSADDR = 0
    DICT = {}

    TIB = 0x0000
    STATE = 0x1000  # current state (0=interpret, 1=compile)
    TOIN = 0x1002  # current read offset into TIB (>IN)
    RP0 = 0x76fe  # bottom of the return stack
    SP0 = 0xfffe  # bottom of data stack

    def __init__(self):
        self.MEMORY = [0] * BITMASK_16  # 65535
        self.PS = MappedStack(self.MEMORY, self.RP0, size=128)
        self.RS = MappedStack(self.MEMORY, self.SP0, size=128)

def init(context):
    def plus():
        b = context.PS.pop()
        a = context.PS.pop()
        context.PS.push((a + b) & BITMASK_16)

    def is_zero():
        x = context.PS.pop()
        if x == 0:
            context.PS.push(TRUE)  # true value
        else:
            context.PS.push(FALSE)  # false value

    def nand():
        b = context.PS.pop()
        a = context.PS.pop()
        context.PS.push(~(a & b) & BITMASK_16)

    def emit():
        tos = context.PS.pop()
        sys.stdout.write(f'{str(tos)} ')

    def dots():
        sys.stdout.write(f'{str(context.PS)} <- top of stack')

    def dotdict():
        sys.stdout.write(str(context.DICT) + ' ')

    def set():
        addr = context.PS.pop()
        x = context.PS.pop()
        context.MEMORY[addr] = x

    def sp_get():
        context.PS.push(context.PS.current)

    def rp_get():
        context.PS.push(context.RS.current)

    def get():
        addr = context.PS.pop()
        context.PS.push(context.MEMORY[addr])

    context.DICT = {
        '@': (NATIVE_WORD, get),
        '!': (NATIVE_WORD, set),
        'sp@': (NATIVE_WORD, sp_get),
        'rp@': (NATIVE_WORD, rp_get),
        '+': (NATIVE_WORD, plus),
        'nand': (NATIVE_WORD, nand),
        '0=': (NATIVE_WORD, is_zero),
        'emit': (NATIVE_WORD, emit),
        '.s': (NATIVE_WORD, dots),
        '.dict': (NATIVE_WORD, dotdict),
    }


def execute(word, context):
    logger.debug(f'executing: "{word}"')
    ret = True

    if word not in context.DICT.keys():
        logger.debug(f'"{word}" not in dict')
        return False

    mode, body = context.DICT[word]
    if mode == NATIVE_WORD:
        res = body()
        logger.debug(f'native, res={res}')
        ret = ret and (True if res is None else False)
    elif mode == USER_WORD:
        for w in body:
            res = execute(w, context)
            logger.debug(f'user, res={res}')
            ret = ret and res
    else:
        raise Exception(f'Mode {mode} is not supported')

    return ret


def compile(line: str, context):
    logger.debug(f'compiling "{line}"')
    i = 0
    word = ''
    body = []

    next_word = ''
    parsing_word = True
    was_whitespace = True
    for i, c in enumerate(line[2:]):
        if c == ':' and was_whitespace:
            continue
        elif ord(c) < 33 or ord(c) >= 127:
            # whitespace
            if parsing_word:
                word = next_word
                parsing_word = False
            else:
                if next_word:
                    body.append(next_word)
            next_word = ''
            was_whitespace = True
        elif c == ';':
            if was_whitespace:
                break
        else:
            next_word += c
            was_whitespace = False

    context.DICT[word] = (USER_WORD, body)

    return i+3, True


def interpret_line(line, context):
    logger.debug(f'interpreting "{line}"')
    word = ''
    results = True
    last_char_i = 0
    i = 0
    while i < len(line):
        c = line[i]
        if ord(c) < 33 or ord(c) >= 127:
            # whitespace
            if len(word) > 0:
                if word == ':':
                    pos, result = compile(line[last_char_i:], context)
                    results = results and result
                    i = min(pos, len(line))
                elif line.startswith('\\'):
                    # comment, start with \
                    i = len(line)
                    break
                else:
                    res = execute(word, context)
                    results = results and res
                word = ''
            else:
                i += 1
                continue
        else:
            # char found
            word = word + c
            last_char_i = i
        i += 1
    logger.debug(f'interpret results: {results}')
    return results


def interpret(line, context):
    try:
        ret = interpret_line(line + '\n', context)
    except StackUnderflow:
        sys.stdout.write(f'stack underflow')
        ret = False
    except StackOverflow:
        sys.stdout.write(f'stack overflow')
        ret = False

    if ret:
        print(' ok')
    else:
        print(' !!')


def main(argv):
    context = Context()
    init(context)

    # execute files
    filenames = argv[1:]
    for filename in filenames:
        with open(filename) as f:
            for line in f.readlines():
                sys.stdout.write(line)
                interpret(line, context)

    while 1:
        logger.debug('reading')
        line = input().lstrip()
        logger.debug(f'read "{line}"')
        interpret(line, context)


if __name__ == '__main__':
    main(sys.argv)
