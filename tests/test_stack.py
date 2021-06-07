from unittest import TestCase, expectedFailure

from stack import (
    Stack, MappedStack,
    StackOverflow, StackUnderflow
)


class StackTest(TestCase):
    def test_push(self):
        pass

    def test_pop(self):
        pass


class MappedStackTest(TestCase):
    def setUp(self):
        memory = [0] * 0xffff
        self.stack = MappedStack(memory, 0xffff, size=0xffff)

    def test_empty_stack(self):
        self.assertEqual([], self.stack.list())

    def test_stack_underflow(self):
        with self.assertRaises(StackUnderflow):
            self.stack.pop()

    def test_stack_overflow(self):
        for i in range(0, self.stack.size):
            self.stack.push(i)
        with self.assertRaises(StackOverflow):
            self.stack.push('no more')

    def test_put_take(self):
        expected = 1
        self.stack.push(expected)
        self.assertEqual([expected], self.stack.list())
        ret = self.stack.pop()
        self.assertEqual(expected, ret)

    def test_str(self):
        for i in range(1, 4):
            self.stack.push(i)
        self.assertEqual('[1, 2, 3]', str(self.stack))
