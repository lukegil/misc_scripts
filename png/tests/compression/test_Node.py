import unittest
from compression.huffman import Node

class TestNode(unittest.TestCase):
    def setUp(self):
        self.n = Node()

    def test_init__left(self):
        self.assertIsNone(self.n._left)

    def test_init__right(self):
        self.assertIsNone(self.n._right)

    def test_init__value(self):
        self.assertIsNone(self.n._value)

    def test_value(self):
        tv = "test value"
        self.n.value = tv
        self.assertEqual(self.n.value, tv)

    def test_left(self):
        new_left = Node()
        self.n.left = new_left

        self.assertIs(self.n.left, new_left)

    def test_right(self):
        new_right = Node()
        self.n.right = new_right

        self.assertIs(self.n.right, new_right)





if __name__ == '__main__':
    unittest.main()
