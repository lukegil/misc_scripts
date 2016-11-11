import unittest
from compression.huffman import HuffmanBlock, Node


class TestHuffmanBlock(unittest.TestCase):
    def setUp(self):
        self.s = HuffmanBlock()

    def test_init__raw_stream(self):
        self.assertEqual(self.s._raw_stream, bytearray())

    def test_init__encoded_stream(self):
        self.assertEqual(self.s._encoded_stream, "")

    def test_init__tbl_root(self):
        self.assertIsInstance(self.s._tbl_root, Node)

    def test_init__freq_tbl(self):
        self.assertEqual(self.s._freq_tbl, {})

    def test_raw_stream(self):
        ts = "abc"
        self.s.raw_stream = ts
        self.assertEqual(self.s.raw_stream, bytearray(ts, "ascii"))
        self.assertIsInstance(self.s.raw_stream, bytearray)

    def test_freq_tbl(self):
        tbl = {
            1 : 2,
            3 : 4
        }

        self.s.freq_tbl = tbl
        self.assertDictEqual(tbl, self.s.freq_tbl)

    def test_build_frequencies__basic(self):
        ts = "aabbcdeee"
        new_tbl = {
            ord("a") : 2/9.0,
            ord("b") : 2/9.0,
            ord("c") : 1/9.0,
            ord("d") : 1/9.0,
            ord("e") : 3/9.0,
        }

        self.s.raw_stream = ts
        self.s.build_frequencies()
        self.assertDictEqual(new_tbl, self.s.freq_tbl)

    def test_build_frequencies__sample(self):
        ts = "aabbcdee"
        new_tbl = {
            ord("a") : 2/2
        }

        self.s.raw_stream = ts
        self.s.build_frequencies(0.25)
        self.assertDictEqual(new_tbl, self.s.freq_tbl)

    def test_addToTable_empty(self):
        huff_tbl = []
        ins_tupe = (Node(), 0.3)
        huff_tbl_res = self.s.add_to_table(ins_tupe, huff_tbl)

        self.assertEqual(huff_tbl_res, [ins_tupe])


    def test_addToTable_larger(self):
        huff_tbl = [(Node(), 0.25), (Node(), 0.2), (Node(), 0.01)]
        ins_tupe = (Node(), 0.3)

        huff_tbl_res = self.s.add_to_table(ins_tupe, huff_tbl)
        huff_tbl.insert(0, ins_tupe)

        self.assertEqual(huff_tbl_res, huff_tbl)

    def test_addToTable_middle(self):
        huff_tbl = [(Node(), 0.25), (Node(), 0.2), (Node(), 0.01),]
        ins_tupe = (Node(), 0.2)

        huff_tbl_res = self.s.add_to_table(ins_tupe, huff_tbl)
        huff_tbl.insert(1, ins_tupe)

        self.assertEqual(huff_tbl_res, huff_tbl)

    def test_addToTable_smaller(self):
        huff_tbl = [(Node(), 0.25), (Node(), 0.2), (Node(), 0.01)]
        ins_tupe = (Node(), 0.005)

        huff_tbl_res = self.s.add_to_table(ins_tupe, huff_tbl)
        huff_tbl.append(ins_tupe)

        self.assertEqual(huff_tbl_res, huff_tbl)

    def test_addToTable_normal(self):
        huff_tbl = [(Node(), 0.26), (Node(), 0.25), (Node(), 0.24), (Node(), 0.2), (Node(), 0.01)]
        ins_tupe = (Node(), 0.24)

        huff_tbl_res = self.s.add_to_table(ins_tupe, huff_tbl)
        huff_tbl.insert(1, ins_tupe)

        self.assertEqual(huff_tbl_res, huff_tbl)

    def test_createHuffmanTbl(self):
        pass

    def test_getLeaf_base(self):
        n = Node()
        val = "A"
        n.value = val
        path = 5
        leaves = {}

        norm_dict = {val : path}
        self.s.get_leaf(n, path, leaves)
        self.assertDictEqual(leaves, norm_dict)

    def test_getLeaf_left(self):
        root = Node()
        val = "A"
        left_node = Node()
        left_node.value = val
        root.left = left_node
        leaves = {}

        norm_dict = {val : 3}
        self.s.get_leaf(root, 1, leaves)
        self.assertDictContainsSubset(norm_dict, leaves)

    def test_getLeaf_right(self):
        root = Node()
        val = "B"
        right_node = Node()
        right_node.value = val
        root.right = right_node
        leaves = {}

        norm_dict = {val : 2}
        self.s.get_leaf(root, 1, leaves)
        self.assertDictContainsSubset(norm_dict, leaves)

    def test_getLeaf_both(self):
        root = Node()

        val1 = "A"
        left_node = Node()
        left_node.value = val1
        root.left = left_node

        val2 = "B"
        right_node = Node()
        right_node.value = val2
        root.right = right_node
        leaves = {}

        norm_dict = {val1 : 3, val2 : 2}
        self.s.get_leaf(root, 1, leaves)
        self.assertDictEqual(norm_dict, leaves)

    def test_getLeaves_empty(self):
        self.s._tbl_root = Node()

        leaves = self.s.get_leaves()
        self.assertDictEqual(leaves, {})

    def test_getLeaves_single(self):
        self.s._tbl_root = Node()
        val = "A"
        left_node = Node()
        left_node.value = val
        self.s._tbl_root.left = left_node

        norm_dict = {val : 3}
        leaves = self.s.get_leaves()
        self.assertDictEqual(norm_dict, leaves)

    def test_getLeaves_nested(self):
        self.s._tbl_root = Node()
        val = "A"
        left_node1 = Node()
        left_node2 = Node()
        left_node2.value = val
        left_node1.left = left_node2
        self.s._tbl_root.left = left_node1

        norm_dict = {val : 7}
        leaves = self.s.get_leaves()
        self.assertDictEqual(norm_dict, leaves)

    def test_getLeavesDecode_both(self):
        self.s._tbl_root = Node()

        val1 = "A"
        left_node = Node()
        left_node.value = val1
        self.s._tbl_root.left = left_node

        val2 = "B"
        right_node = Node()
        right_node.value = val2
        self.s._tbl_root.right = right_node
        leaves = {}

        norm_dict = {val1 : 3, val2 : 2}
        leaves = self.s.get_leaves()
        self.assertDictEqual(norm_dict, leaves)

    def test_appendToInt(self):
        main_int = 7 # 111
        new_int = 6 # 110
        norm_int = 30 # 11110

        calc_int = self.s.append_to_int(main_int, new_int)
        self.assertEqual(norm_int, calc_int)


    def test_packString_KeyError(self):
        val = "C"
        raw_stream = val
        self.s.huffman_table = {"A" : 1, "B" : 2}

        norm_val = bytearray([ord(val)])
        calc_val = self.s.pack_string(raw_stream)
        self.assertEqual(norm_val, calc_val)

    def test_packString_fitsSingle(self):
        val = "A"
        raw_stream = val
        self.s.huffman_table = {
                                "A" : 7, # 111
                                "B" : 2
                                }

        norm_val = bytearray([7]) # 1111
        calc_val = self.s.pack_string(raw_stream)
        self.assertEqual(norm_val, calc_val)

    def test_packString_fitsDouble(self):
        val = "AB"
        raw_stream = val
        self.s.huffman_table = {
                                "A" : 7, # 111
                                "B" : 2 # 10
                                }

        norm_val = bytearray([14]) # 1110
        calc_val = self.s.pack_string(raw_stream)
        self.assertEqual(norm_val, calc_val)

    def test_packString_overflow(self):
        val = "AB"
        raw_stream = val
        self.s.huffman_table = {
                                "A" : 272, # 100010000
                                "B" : 5 # 101
                                }

        norm_val = bytearray([136, 21]) # 10001000 10101
        calc_val = self.s.pack_string(raw_stream)
        self.assertEqual(norm_val, calc_val)


if __name__ == '__main__':
    unittest.main()
