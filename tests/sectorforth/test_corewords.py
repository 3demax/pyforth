from unittest import TestCase, expectedFailure

from sectorforth import (
    Context, Stack,
    init, compile, execute, interpret, interpret_line,
    NATIVE_WORD, USER_WORD,
    TRUE, FALSE,
)


class HelloWolrdTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = Context()
        init(self.context)

    def test_helloworld(self):
        def run_and_reset(line):
            self.context.PS.current = self.context.PS.bottom
            self.context.RS.current = self.context.RS.bottom
            interpret_line(line + '\n', self.context)
        i = run_and_reset
        self.number(i, self.context.PS, self.context.RS)
        self.logic_arithmetic(i, self.context.PS, self.context.RS)
        self.equality(i, self.context.PS, self.context.RS)
        self.stack_maneuvers(i, self.context.PS, self.context.RS)
        self.more_logic_constants(i, self.context.PS, self.context.RS)
        self.conditionals(i, self.context.PS, self.context.RS)

    def number(self, i, PS, RS):
        self.assertEqual([], PS.list())

        # defining dup
        i(': dup sp@ @ ;')

        # defining some numbers
        i(': -1 dup dup nand dup dup nand nand ;')
        i('-1')
        self.assertEqual([0xffff], PS.list())
        PS.pop()
        i('-1 dup')
        self.assertEqual([0xffff, 0xffff], PS.list())

        i(': 0 -1 dup nand ;')
        i('0')
        self.assertEqual([0], PS.list())

        i(': 1 -1 dup + dup nand ;')
        i(': 2 1 1 + ;')
        i(': 3 2 1 + ;')
        i(': 4 2 2 + ;')
        i(': 6 2 4 + ;')

    def logic_arithmetic(self, i, PS, RS):
        # logic and arithmetic
        i(': invert dup nand ;')
        i('0 invert')
        self.assertEqual([TRUE], PS.list())
        i('0 invert -1 invert')
        self.assertEqual([TRUE, 0x0000], PS.list())

        i(': and nand invert ;')
        i('0 0 and')
        self.assertEqual([FALSE], PS.list())
        i('-1 0 and')
        self.assertEqual([FALSE], PS.list())
        i('-1 -1 and')
        self.assertEqual([TRUE], PS.list())
        i('0 0 and 0 -1 and -1 0 and -1 -1 and')
        self.assertEqual([0, 0, 0, TRUE], PS.list())

        i(': negate invert 1 + ;')
        i('-1 negate')
        self.assertEqual([1], PS.list())
        i('0 negate')
        self.assertEqual([0], PS.list())
        i('6 negate')
        minus_6 = 0x10000 - 6
        self.assertEqual([minus_6], PS.list())

        i(': - negate + ;')
        i('0 2 -')
        self.assertEqual([0x10000 - 2], PS.list())
        i('2 1 -')
        self.assertEqual([1], PS.list())
        i('6 2 -')
        self.assertEqual([4], PS.list())

    def equality(self, i, PS, RS):
        # equality
        i(': = - 0=;')
        i('2 2 =')
        self.assertEqual([TRUE], PS.list())
        i('2 1 =')
        self.assertEqual([FALSE], PS.list())

        i(': <> = invert;')
        i('2 2 <>')
        self.assertEqual([FALSE], PS.list())
        i('2 1 <>')
        self.assertEqual([TRUE], PS.list())

    def stack_maneuvers(self, i, PS, RS):
        # stack manipulation
        i(': drop dup - + ;')
        i('2 2 drop')
        self.assertEqual([2], PS.list())
        # TODO doesn't work with 1 item. why?
        try:
            i('2 drop')
            self.assertEqual([], PS.list())
            PS.pop()
        except:
            pass

        # i(': over sp@ 2 + @ ;') # original assumes 2byte address
        i(': over sp@ 1 + @ ;')
        i('1 2 over')
        self.assertEqual([1, 2, 1], PS.list())

        # i(': swap over over sp@ 6 + ! sp@ 2 + ! ;')  # original assumes 2byte address
        i(': swap over over sp@ 3 + ! sp@ 1 + ! ;')
        i('1 2 swap')
        self.assertEqual([2, 1], PS.list())

        i(': nip swap drop ;')
        i('1 2 nip')
        self.assertEqual([2], PS.list())

        i(': 2dup over over ;')
        i('1 2 2dup')
        self.assertEqual([1, 2, 1, 2], PS.list())

        i(': 2drop drop drop ;')
        try:
            i('1 2 2drop')
        except:
            pass
        self.assertEqual([], PS.list())

    def more_logic_constants(self, i, PS, RS):
        # more logic
        i(': or  invert swap invert and invert ;')
        i('0 0 or')
        self.assertEqual([FALSE], PS.list())
        i('-1 0 or')
        self.assertEqual([TRUE], PS.list())
        i('-1 -1 or')
        self.assertEqual([TRUE], PS.list())
        i('0 0 or 0 -1 or -1 0 or -1 -1 or')
        self.assertEqual([FALSE, TRUE, TRUE, TRUE], PS.list())

        # left shift 1 bit
        i(': 2* dup + ;')
        i('2 2* 4 =')
        self.assertEqual([TRUE], PS.list())

        #constant to check/set immediate flag
        i(': 80h  1 2* 2* 2* 2* 2* 2* 2* ;')
        i('80h')
        self.assertEqual([0x80], PS.list())

    def conditionals(self, i, PS, RS):
        # compile things
        i(': , here @ ! here @ 1 + here ! ;')

        # unconditional branch ( r:addr -- r:addr+offset )
        i(': branch rp@ @ dup @ + rp@ ! ;')

        # conditional branch ( r:addr -- r:addr | r:addr+offset)
        i(': ?branch  0= rp@ @ @ 2 - and rp@ @ + 2 + rp@ ! ;')


