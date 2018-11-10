from decode_tree import decode_tree


class BitStream:
    def __init__(self, numbers):
        self.numbers = iter(numbers)
        self.init_bit_range()

    def next_number(self):
        self.number = next(self.numbers)
        self.bit_range = range(self.number.bit_length())
        self.next_bit()

    def next_bit(self):
        try:
            self.bit_n = next(self.bit_range)
        except StopIteration:
            self.next_number()

    def __iter__(self):
        return self

    def __next__(self):
        pass


def bit_stream(numbers):
    for number in numbers:
        for i in range(number.bit_length()):
            yield 1 if number & (1 << i) else 0

def decode(byte_seq):
    for bit in bit_stream(byte_seq):
        pass
