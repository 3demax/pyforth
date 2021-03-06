from unittest import TestCase, expectedFailure

from sectorforth import (
    Context, Stack,
    init, compile, execute, interpret, interpret_line,
    NATIVE_WORD, USER_WORD
)


class ContextCase(TestCase):
    def setUp(self) -> None:
        self.context = Context()
        init(self.context)


class ContextCaseTest(ContextCase):
    def test_stacks_empty(self):
        ctx = self.context
        self.assertEqual([], ctx.PS.list())
        self.assertEqual([], ctx.RS.list())


class ExecutorTest(ContextCase):
    def test_execute(self):
        self.context.PS.append(1)
        self.context.PS.append(2)
        ret = execute('+', self.context)
        self.assertTrue(ret)
        stack = Stack()
        stack.push(3)
        self.assertEqual(3, stack.pop())


class InterpreterTest(ContextCase):
    def test_unknown_word(self):
        line = 'asdasd'
        interpret(line, self.context)

    def test_compile(self):
        line = ': 2+ 2 + ;'
        res = interpret_line(line, self.context)
        self.assertTrue('2+' in self.context.DICT.keys())
        self.assertEqual(self.context.DICT['2+'], (USER_WORD, ['2', '+']))


class CompilerTest(ContextCase):
    def test_compile(self):
        line = ': 2+ 2 + ;'
        pos, res = compile(line, self.context)
        self.assertTrue('2+' in self.context.DICT.keys())
        self.assertEqual(self.context.DICT['2+'], (USER_WORD, ['2', '+']))
        self.assertEqual(
            (10, True), (pos, res)
        )

    def test_plus(self):
        line = ': plus + ;'
        pos, res = compile(line, self.context)
        self.assertTrue('plus' in self.context.DICT.keys())
        self.assertEqual(self.context.DICT['plus'], (USER_WORD, ['+']))
        self.assertEqual(
            (10, True), (pos, res),
        )

        line = ': 2 1 1 + ;'
        pos, res = compile(line, self.context)
        self.assertTrue('plus' in self.context.DICT.keys())
        self.assertEqual(self.context.DICT['plus'], (USER_WORD, ['+']))
        self.assertEqual(
            (11, True), (pos, res)
        )


class IntegrationTest(ContextCase):
    def test_exec_compiled(self):
        line = ': . emit ;'
        pos, res = compile(line, self.context)

        self.context.PS.push(1)
        res = execute('emit', self.context)
        self.assertTrue(res)

        self.context.PS.push(1)
        res = execute('.', self.context)
        self.assertTrue(res)
