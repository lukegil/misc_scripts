import unittest
from compression.huffman import HuffmanTree, Node, HuffByte


class TestHuffmanTree(unittest.TestCase):

    def setUp(self):
        self.ht = HuffmanTree()

    def test_init__mapping(self):
        calc = self.ht._mapping
        norm = dict
        self.assertIsInstance(calc, norm)

    def test_init__tree(self):
        calc = self.ht._tree
        norm = Node
        self.assertIsInstance(calc, norm)

    def test_mapping(self):
        hb = HuffByte(value=7)
        d = {hb.value : hb}
        self.ht.mapping = d

        calc = self.ht.mapping
        norm = d

        self.assertDictEqual(norm, calc)

    def test_tree(self):
        root = Node()
        self.ht.tree = root

        calc = self.ht.tree
        norm = root
        self.assertIs(norm, calc)

    def test__build_mapping(self):
        hb = HuffByte(value=bytes("a", "ascii"), encoded_value=3, frequency=1.0 )
        n = Node()
        n.value = hb
        self.ht.tree.left = n

        norm = {hb.value : hb}
        calc = self.ht._build_mapping()
        self.assertDictEqual(norm, calc)

    def test__getLeaves_baseCase(self):
        hb = HuffByte(value=bytes("a", "ascii"), encoded_value=3, frequency=1.0 )
        node = Node()
        node.value = hb
        mapping = {}

        norm = {hb.value : hb}
        self.ht._get_leaves(node, 0, mapping)
        calc = mapping

        self.assertDictEqual(norm, calc)

    def test__getLeaves_recurseNode(self):
        hb = HuffByte(value=bytes("a", "ascii"), encoded_value=3, frequency=1.0 )
        node = Node()
        node.value = hb

        root = Node()
        root.left = node
        mapping = {}

        norm = {hb.value : hb}
        self.ht._get_leaves(root, 0, mapping)
        calc = mapping
        self.assertDictEqual(norm, calc)

    def test__getLeaves_recursePath(self):
        hb = HuffByte(value=bytes("a", "ascii"), encoded_value=3, frequency=1.0 )
        node = Node()
        node.value = hb

        root = Node()
        root.left = node
        mapping = {}

        norm = 3
        self.ht._get_leaves(root, 1, mapping)
        calc = mapping[hb.value].encoded_value
        self.assertEqual(norm, calc)

    def test_addLeaves_base(self):
        prev_node = Node()
        hb_val = HuffByte(value=bytes("a", "ascii"), encoded_value=3, frequency=1.0)
        cur_shift = 0

        self.ht._add_leaves(prev_node, cur_shift, hb_val)
        self.assertIs(prev_node.left.value, hb_val)

    def test_addLeaves_recurse(self):
        root = Node()
        prev_node = Node()
        root.right = prev_node

        hb_val = HuffByte(value=bytes("a", "ascii"), encoded_value=5, frequency=1.0)
        cur_shift = hb_val.encoded_value.bit_length() - 2

        self.ht._add_leaves(root, cur_shift, hb_val)
        norm = root.right.left.value
        calc = hb_val
        self.assertIs(norm, calc)


if __name__ == '__main__':
    unittest.main()
