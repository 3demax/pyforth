import sys

from stack import Stack, StackOverflow, StackUnderflow


from loguru import logger
logger.disable(__name__)


NATIVE_WORD = 0
USER_WORD = 1


class Context:
    PS = Stack()
    RS = Stack()
    PSADDR = 0
    DICT = {}


def init(context):
    def plus():
        b = context.PS.pop()
        a = context.PS.pop()
        context.PS.append(a + b)

    def is_zero():
        x = context.PS.pop()
        if x == 0:
            context.PS.append(-1)  # true value
        else:
            context.PS.append(0)  # false value

    def emit():
        tos = context.PS.pop()
        sys.stdout.write(f'{str(tos)} ')

    def dots():
        sys.stdout.write(f'{context.PS} <- top of stack')

    def dotdict():
        sys.stdout.write(str(context.DICT) + ' ')

    context.DICT = {
        '+': (NATIVE_WORD, plus),
        '0=': (NATIVE_WORD, is_zero),
        '1': (NATIVE_WORD, lambda: context.PS.append(1)),
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
        raise Exception(f'Mode {mode} is not suppoorted')

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


def interpret(line, context):
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
    return results


def main():
    context = Context()
    init(context)

    CORE_WORDS = [
        ': 2 1 1 + ;',
        ': . emit ;',
    ]
    for line in CORE_WORDS:
        interpret(line, context)

    while 1:
        line = input().lstrip()
        try:
            ret = interpret(line + '\n', context)
        except StackUnderflow:
            sys.stdout.write(f'stack underflow')
            ret = False
        except StackOverflow:
            sys.stdout.write(f'stack underflow')
            ret = False

        if ret:
            print(' ok')
        else:
            print(' !!')


if __name__ == '__main__':
    main()
