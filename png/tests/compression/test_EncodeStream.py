import unittest
from compression.huffman import HuffmanTree, Node, HuffByte, EncodeStream


class TestHuffmanTree(unittest.TestCase):
    """ really high level, doesnt count as unittests """
    def setUp(self):
        self.es = EncodeStream()

    def test_encodedecode_singleByte(self):
        stream = bytearray("a", "ascii")
        self.es.raw_stream = stream
        self.es.encode()
        print("encoded stream:")
        print(self.es.encoded_stream)

        self.es.decode(self.es._huffman_tree.mapping)

        decoded_stream = self.es.raw_stream
        print("output raw_stream : ")
        print(decoded_stream)
        self.assertEqual(stream, decoded_stream)

    def test_encodedecode_doubleByte(self):

        stream = bytearray("abc", "ascii")
        self.es.raw_stream = stream
        self.es.encode()
        print("encoded stream:")
        print(self.es.encoded_stream)

        self.es.decode(self.es._huffman_tree.mapping)

        decoded_stream = self.es.raw_stream
        print("output raw_stream : ")
        print(decoded_stream)
        self.assertEqual(stream, decoded_stream)

    def test_encodedecode_longString(self):
        stream = bytearray("adkjJHJLKdfgmcxmncmxm2398u2JHHFSdfadaps34ooiqwqekmdajnvajdafvkjnsfjv", "ascii")
        #stream = bytearray("abc", "ascii")

        self.es.raw_stream = stream
        self.es.encode()
        print("encoded stream:")
        print(self.es.encoded_stream)

        self.es.decode(self.es._huffman_tree.mapping)

        decoded_stream = self.es.raw_stream
        print("output raw_stream : ")
        print(decoded_stream)
        self.assertEqual(stream, decoded_stream)

if __name__ == '__main__':
    unittest.main()
