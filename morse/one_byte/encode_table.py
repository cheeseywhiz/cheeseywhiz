import collections
from decode_tree import decode_tree


class MutableMapping(collections.abc.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__dict = dict(*args, **kwargs)

    def __getitem__(self, key):
        return self.__dict[key]

    def __setitem__(self, key, value):
        self.__dict[key] = value

    def __delitem__(self, key):
        self.__dict.__delitem__(key)

    def __iter__(self):
        return iter(self.__dict)

    def __len__(self):
        return len(self.__dict)

    def __repr__(self):
        return repr(self.__dict)


def pack_bit_seq(bit_seq):
    byte = 0

    for i, bit in enumerate(bit_seq):
        byte |= bit << i

    return byte


class EncodeTable(MutableMapping):
    def __getitem__(self, key):
        return super().__getitem__(key.upper())

    def __setitem__(self, key, value):
        super().__setitem__(key.upper(), value)

    def __delitem__(self, key):
        super().__delitem__(key.upper())

    def set_char(self, char, bit_seq):
        byte = pack_bit_seq(bit_seq)
        byte |= len(bit_seq) << 5
        self[char] = byte

    def encode_leaf(self, node, *bit_seq):
        if node is not None:
            if node.char is not None:
                self.set_char(node.char, bit_seq)

            self.encode_node(node, *bit_seq)

        return self

    def encode_node(self, node, *bit_seq):
        return self \
            .encode_leaf(node.dot, *bit_seq, 0) \
            .encode_leaf(node.dash, *bit_seq, 1)


encode_table = EncodeTable({' ': 0}).encode_node(decode_tree)
