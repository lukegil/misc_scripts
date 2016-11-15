

class HuffByte(object):
    def __init__(self, value="", encoded_value=int(), frequency=int()):
        self.value = value,
        self.encoded_value = encoded_value
        self.frequency = frequency


class Node(object):
    def __init__(self):
        self._left = None
        self._right = None
        self._value = HuffByte(None, 0, 0)

    @property
    def left(self):
        """ the left branch of Node """
        return self._left

    @left.setter
    def left(self, node):
        """ set the left branch of Node

            @type - Node
            @param - the node the left edge should reference
        """
        self._left = node

    @property
    def right(self):
        """ the right branch of Node """
        return self._right

    @right.setter
    def right(self, node):
        """ set the right branch of Node

            @type - Node
            @param - the node the right edge should reference
        """
        self._right = node

    @property
    def value(self):
        """ the value of a Node, defaults to None """
        return self._value

    @value.setter
    def value(self, val):
        """ set the value of Node

            @type - any
            @param - value of the Node
        """
        self._value = val


class HuffmanTree(object):
    """ A Huffman Tree, comprised of a mapping of byte-values to encodings
        and a tree, a root Node. Left turns are 1, right turns are 0

        The two attributes either return themselves, or try to build themselves
        out of the other attribute
    """
    def __init__(self):
        self._mapping = {}
        self._tree = Node()

    @property
    def mapping(self):
        if (self._mapping):
            return self._mapping
        elif (self._tree):
            self.mapping = self._build_mapping()
            return self.mapping
        else:
            return None

    @mapping.setter
    def mapping(self, map_dict):
        self._mapping = map_dict

    @property
    def tree(self):
        if (self._tree):
            return self._tree
        elif (self._mapping):
            self.tree = self._build_tree()
            return self.tree
        else:
            return None

    @tree.setter
    def tree(self, node):
        self._tree = node

    def _build_mapping(self):
        root_node = self.tree

        mapping = {}
        self._get_leaves(root_node, 1, mapping)
        return mapping

    def _get_leaves(self, cur_node, path, mapping):
        # we found a leaf
        if (cur_node and cur_node.value):
            mapping[cur_node.value] = path

        # no leaf found, try to take the left and right branches
        elif (cur_node):
            l_np = (path << 1) ^ 1 #append 1
            r_np = (path << 1) #append 0

            self._get_leaves(cur_node.left, l_np, mapping)
            self._get_leaves(cur_node.right, r_np, mapping)

    def _add_leaves(self, prev_node, value, cur_shift):
        pass

    def _build_tree(self):
        root = Node()
        mapping = self.mapping



class HuffmanBlock(object):
    def __init__(self):
        self._raw_stream = bytearray()
        self._encoded_stream = ""
        self._tbl_root = Node()
        self._freq_tbl = {}
        self._huffman_tbl = {}
        self.next_data = int()

    @property
    def raw_stream(self):
        """ the input to be encoded """
        return self._raw_stream

    @raw_stream.setter
    def raw_stream(self, stream):
        """ set the input stream

            @type - list or string
            @param - a string or list of bytes to be encoded
        """
        self._raw_stream = bytearray(stream, "ascii")

    @property
    def freq_tbl(self):
        """ dict of probabilities for byte values """
        return self._freq_tbl

    @freq_tbl.setter
    def freq_tbl(self, dic):
        """ set the probabilities for byte values

            @type - dictionary
            @param - a dictionary {byte : float}, where float is a
                     probability <= 1
        """
        self._freq_tbl = dic

    @property
    def huffman_table(self):
        """ returns Dict

            {encoding : encoded-value}
            e.g. {"1001" : "A"}

        """
        return self._huffman_tbl

    @huffman_table.setter
    def huffman_table(self, dic):
        """ Set huffman table

            @type - dict
            @param - a dictionary of {encoding : encoded-value}
        """
        self._huffman_tbl = dic

    def encode(self, sample_size):
        if (not self.freq_tbl):
            self.build_frequencies(sample_size)

        if (not self.huffman_table):
            self._tbl_root = self.create_huffman_tree()
            self.huffman_table = self.get_leaves()

        cur_stream = self.raw_stream
        encoded_stream = self.pack_string(cur_stream)

    def pack_string(self, cur_stream):


        encoded_stream = bytearray()
        free_in_hex = 7
        cur_byte = 1
        cache = 0
        while (cur_stream or self.next_data):

            if (not self.next_data and not self.huffman_table.get(cur_stream[0])):
                encoded_stream.append(ord(cur_stream[0]))
                cur_stream = cur_stream[1:]
                continue

            elif (not self.next_data):
                self.next_data = self.huffman_table[cur_stream[0]]



            # If the entire number excluding the first
            # bit  will fit in byte, add it
            l = self.next_data.bit_length() - 1
            if (l <= free_in_hex):
                cur_byte = self.append_to_int(cur_byte, self.next_data)

                free_in_hex -= l

                self.next_data = 0


            # otherwise, grab as many bits (assuming big endiness)
            # as possible and append it. Then prepend the remaining
            # bits with a 1 and add it back to stream, to be processed
            # next time
            else:
                # Get left n bits, add to cur_byte, and push
                # to output
                shift_right = self.next_data.bit_length() - free_in_hex
                b = self.next_data >> shift_right
                cur_byte = self.append_to_int(cur_byte, b)
                encoded_stream.append(cur_byte)

                # Take the untouched bits, and prepend a 1
                mask = (1 << shift_right) - 1
                self.next_data &= mask
                self.next_data |= (1 << shift_right)

                # Next loop will start a new byte
                cur_byte = 1
                free_in_hex = 7

            cur_stream = cur_stream[1:]
        return encoded_stream

    def append_to_int(self, main_int, new_int):
        """ bitwise-append new to main. new_int has leading 1 """
        l = new_int.bit_length() - 1
        main_int <<= l

        new_int = new_int ^ (1 << l)
        main_int |= new_int

        return main_int

    def get_leaves(self):
        """ Return a dict of paths (encodings) and their unencoded values """
        root = self._tbl_root
        leaves = {}
        self.get_leaf(root, 1, leaves)
        return leaves

    def get_leaf(self, cur_node, path, leaves):

        # we found a leaf
        if (cur_node and cur_node.value):
            leaves[cur_node.value] = path

        # no leaf found, try to take the left and right branches
        elif (cur_node):
            l_np = (path << 1) ^ 1 #append 1
            r_np = (path << 1) #append 0

            self.get_leaf(cur_node.left, l_np, leaves)
            self.get_leaf(cur_node.right, r_np, leaves)

        return

    def build_frequencies(self, sample_perc=1.00):
        """ calculate probabilities for a byte to appear
            in raw input stream

            @type - float
            @param - decimal percent of input stream to use as sample
        """
        up_to = len(self.raw_stream) * sample_perc
        stream = self.raw_stream[:int(up_to)]
        freq_tbl = {}

        for byte in stream:
            try:
                freq_tbl[byte] += 1
            except KeyError:
                freq_tbl[byte] = 1

        for key in freq_tbl:
            freq_tbl[key] /= up_to

        self.freq_tbl = freq_tbl

    def create_huffman_tree(self):
        """ Returns root Node. builds a huffman table """

        huff_tbl = []
        ht_len = 0
        for key in self.freq_tbl:
            n_node = Node()
            n_node.value = key
            ins_node = (n_node, self.freq_tbl[key])
            huff_tbl = self.add_to_table(ins_node, huff_tbl)

        while (len(huff_tbl) > 1):
            n_node = Node()
            l = huff_tbl.pop()
            r = huff_tbl.pop()
            p = l[1] + r[1]
            n_node.left = l[0]
            n_node.right = r[0]
            huff_tbl = self.add_to_table((n_node, p), huff_tbl)

        return huff_tbl[0][0]

    def add_to_table(self, ins_tupe, huff_tbl):
        """ Insert a new Node into huff_tbl sorted by probability DESC

            tupe - @type - tuple
                 - @param - (Node, probability)

            huff_tbl - @type - list
                     - @param - list of `tupe`s

            Insert into huff_tbl using binary-search insert, since
            insertion is being done asyncronously. Ordered desc to
            optimize for pop()s
        """
        found = False
        lwr = 0
        upr = len(huff_tbl) - 1
        while not found:
            mid = (upr + lwr) // 2
            prob = ins_tupe[1]

            # empty table
            if (not huff_tbl):
                found = True
                i_at = 0

            # Found midpoint
            elif ((upr - lwr) <= 1 and huff_tbl[lwr][1] > prob > huff_tbl[upr][1]):
                found = True
                i_at = upr

            # `prob` smaller than any in tbl
            elif (huff_tbl[upr][1] >= prob):
                found = True
                i_at = upr + 1

            # `prob` larger than any in tbl
            elif (prob >= huff_tbl[lwr][1]):
                found = True
                i_at = lwr

            # `prob` is midpoint
            elif (prob == huff_tbl[mid][1]):
                found = True
                i_at = mid

            # prob is between lower and mid
            elif (huff_tbl[lwr][1] > prob > huff_tbl[mid][1]):
                upr = mid

            #prob is between mid and upper
            elif (huff_tbl[mid][1] > prob > huff_tbl[upr][1]):
                lwr = mid

        huff_tbl.insert(i_at, ins_tupe)
        return huff_tbl
