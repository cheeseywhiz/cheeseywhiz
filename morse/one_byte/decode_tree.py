import dataclasses


@dataclasses.dataclass
class Node:
    char: str
    dot: 'Node' = None
    dash: 'Node' = None


@dataclasses.dataclass
class DecodeTree:
    dot: Node
    dash: Node

    def decode_byte(self, byte):
        if not byte:
            return ' '

        n_bits = (byte & 0b111_00000) >> 5
        ptr = self

        for bit_n in range(n_bits):
            ptr = ptr.dash if byte & (1 << bit_n) else ptr.dot

        return ptr.char

    def decode(self, byte_seq):
        return ''.join(map(self.decode_byte, byte_seq))


decode_tree = DecodeTree(
    Node(
        'E',
        Node(
            'I',
            Node(
                'S',
                Node(
                    'H',
                    Node('5'),
                    Node('4'),
                ),
                Node(
                    'V',
                    None,
                    Node('3'),
                ),
            ),
            Node(
                'U',
                Node('F'),
                Node(
                    None,
                    None,
                    Node('2'),
                ),
            ),
        ),
        Node(
            'A',
            Node(
                'R',
                Node('L'),
                Node(
                    None,
                    Node('+'),
                    None,
                ),
            ),
            Node(
                'W',
                Node('P'),
                Node(
                    'J',
                    None,
                    Node('1'),
                ),
            ),
        ),
    ),
    Node(
        'T',
        Node(
            'N',
            Node(
                'D',
                Node(
                    'B',
                    Node('6'),
                    Node('='),
                ),
                Node(
                    'X',
                    Node('/'),
                ),
            ),
            Node(
                'K',
                Node('C'),
                Node('Y'),
            ),
        ),
        Node(
            'M',
            Node(
                'G',
                Node(
                    'Z',
                    Node('7'),
                    None,
                ),
                Node('Q'),
            ),
            Node(
                'O',
                Node(
                    None,
                    Node('8'),
                    None,
                ),
                Node(
                    None,
                    Node('9'),
                    Node('0'),
                ),
            ),
        ),
    ),
)
