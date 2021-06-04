class StackOverflow(Exception):
    pass


class StackUnderflow(Exception):
    pass


class Stack:
    def __init__(self):
        # preallocated
        self.items = [0] * 128
        self.current = -1

    def pop(self):
        if self.current <= -1:
            raise StackOverflow('stack underflow')
        elif self.current > len(self.items) - 1:
            raise StackOverflow('stack overflow')
        else:
            ret = self.items[self.current]
            self.current -= 1
            return ret

    def push(self, i):
        self.items[self.current + 1] = i
        self.current += 1

    def append(self, *args):
        return self.push(*args)

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return str(self.items[:max(0, self.current + 1)])

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.items[:max(0, self.current + 1)] == other.items[:max(0, self.current + 1)]
