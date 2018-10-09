from decode_tree import decode_tree
from encode_table import encode_table


def decode(byte_seq):
    return decode_tree.decode(byte_seq)


def encode(string):
    return [
        encode_table[char]
        for char in string
    ]


def main():
    import pprint
    string = 'dont get bogged down'
    byte_seq = encode(string)
    encoding = bytes(byte_seq)
    inverse = decode(encoding)
    print(f'string = {string !r}')
    print('byte_seq = ', end='')
    pprint.pprint(list(map(bin, byte_seq)))
    print(f'encoding = {encoding !r}')
    print(f'inverse = {inverse !r}')


if __name__ == '__main__':
    main()
