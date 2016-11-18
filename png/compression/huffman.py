import random, sys

class HuffByte(object):
    """ a data object representing a byte, its encoding, and its frequency
        in a given document
    """
    def __init__(self, value=bytes(), encoded_value=int(), frequency=float()):
        """
            value
                @type - bytes
                @param - the byte found in a source document

            encoded_value
                @type - int
                @param - the integer given as the byte value by the huffman
                         tree.

            frequency
                @type - float
                @param - (# times this byte appears) / (total bytes in doc)
        """
        self.value = value
        self.encoded_value = encoded_value
        self.frequency = frequency

class Node(object):
    def __init__(self):
        self._left = None
        self._right = None
        self._value = HuffByte(bytes(), 0, 0)

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
    """ A Huffman Tree, comprised of (i) a mapping of byte-values to encodings
        and (ii) a pointer to a tree's root Node. Left turns are 1, right turns are 0

        The two attributes either return themselves, try to build themselves
        out of the other attribute, or return None
    """
    def __init__(self):
        """
        _mapping
            @type - dic
            @param - Keys are a byte value (aka Huffbyte.value).
                     Values are HuffBytes

        _tree
            @type - Node
            @param - the root node to a Huffman tree.
        """
        self._mapping = {}
        self._tree = Node()

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, map_dict):
        """ sets value of `mapping` attribute

            @type - dic
            @param - {HuffByte.value : HuffByte}
        """
        self._mapping = map_dict

    @property
    def tree(self):
        # If we have a tree, return it
        return self._tree


    @tree.setter
    def tree(self, node):
        self._tree = node

    def tree_to_mapping(self):
        self.mapping = self._build_mapping()

    def mapping_to_tree(self):
        self.tree = self._build_tree()

    def _build_mapping(self):
        """ From a Huffman tree, recursively build a mapping of byte values to HuffBytes """
        root_node = self.tree
        mapping = {}
        self._get_leaves(root_node, 1, mapping)

        return mapping

    def _get_leaf(self, cur_node, path, shifts):
        """" walk down a tree, following path, upon finding
             a leaf, return (leaf, path, shifts)
        """

        # we found a leaf
        if ((cur_node and cur_node.value and cur_node.value.value) or shifts <= 0 ):
            return (cur_node, path, shifts)

        # the path doesn't exist on the tree
        if (cur_node is None):
            return None

        # no leaf found, take the left or right branches
        shifts -= 1
        direction = (1 & path >> shifts)

        next_node = cur_node.left if direction == 1 else cur_node.right

        return self._get_leaf(next_node, path, shifts)


    def _get_leaves(self, cur_node, path, mapping):
        """ recursively walk down a tree and map paths to
            leaf values. Returns None, works on mapping object

            cur_node
                @type - Node
                @param - a Node. If value is None, then is not a leaf

            path
                @type - int
                @param - the current integer representation of the value based on
                         the huffman tree. All begin with 1

            mapping
                @type - dic
                @param - the output dict of {HuffByte.value : HuffByte}
        """

        # we found a leaf
        if (cur_node and cur_node.value and cur_node.value.value):
            cur_node.value.encoded_value = path
            mapping[cur_node.value.value] = cur_node.value

        # no leaf found, try to take the left and right branches
        elif (cur_node):
            l_np = (path << 1) ^ 1 #append 1
            r_np = (path << 1) #append 0

            self._get_leaves(cur_node.left, l_np, mapping)
            self._get_leaves(cur_node.right, r_np, mapping)

    def _build_tree(self):
        """ From _mapping, build a Huffman Tree of Nodes() """
        root = Node()
        mapping = self.mapping

        for key in mapping:
            v = mapping[key]
            ev = v.encoded_value.bit_length()
            shift = ev - 2
            self._add_leaves(root, shift, v)

        return root

    def _add_leaves(self, prev_node, cur_shift, leaf_val):
        """ Recursively build a tree, based on encoded values of a HuffByte

            prev_node
                @type - Node
                @param - the node that references the one we walked to

            cur_shift
                @type - int
                @param - the nth bit of leaf_val.encoded_value

            leaf_val
                @type - HuffByte
                @param - the value we're trying to add to a leaf
        """

        # BASE CASE - we've reached the bottom of the tree, add leaf_val and return
        if (cur_shift < 0):
            prev_node.value = leaf_val
            return

        # Ensure that either the right or left node exists (depending on value
        # of direction). If not, build it
        direction = (leaf_val.encoded_value >> cur_shift) & 1
        cur_shift -= 1

        if (direction == 1 and prev_node.left is None):
            new_node = Node()
            prev_node.left = new_node

        elif (direction == 1):
            new_node = prev_node.left

        elif (direction == 0 and prev_node.right is None):
            new_node = Node()
            prev_node.right = new_node

        elif (direction == 0):
            new_node = prev_node.right


        # Otherwise, take the given branch and recall the function
        n = prev_node.left if direction == 1 else prev_node.right
        self._add_leaves(n, cur_shift, leaf_val)

class EncodeStream(object):
    def __init__(self):
        self._raw_stream = bytearray()
        self._encoded_stream = bytearray()
        self._huffman_tree = HuffmanTree()

    @property
    def raw_stream(self):
        """ the input to be encoded """
        return self._raw_stream

    @raw_stream.setter
    def raw_stream(self, stream):
        """ set the input stream

            @type - bytearray
            @param - the bytearray to be encoded
        """
        self._raw_stream = stream

    @property
    def encoded_stream(self):
        """ the encoded output """
        return self._encoded_stream

    @encoded_stream.setter
    def encoded_stream(self, stream):
        """ set the input stream

            @type - bytearray
            @param - the bytearray that was encoded
        """

        self._encoded_stream = stream

    def encode(self, sample_size=1.00):
        huffbytes = build_huffByte_freqs(self.raw_stream, sample_size)
        node_list = huffBytes_to_Nodes(huffbytes)

        saved = set_recursion_limit(node_list)
        node_list = sort_NodeList(node_list)
        set_recursion_limit(node_list, saved)

        self._huffman_tree = build_huffman_tree(node_list)
        self._huffman_tree.tree_to_mapping()
        self.encoded_stream = self._pack_input(self.raw_stream, self._huffman_tree.mapping)

    def decode(self, mapping):
        self._huffman_tree.mapping = mapping
        self._huffman_tree.mapping_to_tree()
        self.raw_stream = self._unpack_encoded(self.encoded_stream, self._huffman_tree.tree)

    def _pack_input(self, stream, mapping):
        output = bytearray()
        bspace = 7
        in_byte = 0
        out_byte = 1

        while stream or in_byte:

            if (not in_byte and mapping.get(stream[0], None) is None):
                output.append(stream[0])
                stream = stream[1:]

            elif (not in_byte):
                in_byte = mapping.get(stream[0], None).encoded_value

            # If the entire number excluding the first
            # bit  will fit in byte, add it
            l = in_byte.bit_length() - 1
            if (l <= bspace):
                out_byte = append_to_int(out_byte, in_byte)
                bspace -= l
                in_byte = 0
                stream = stream[1:]

            else:
                # Get left n bits, add to out_byte, and push
                # to output
                shift = in_byte.bit_length() - bspace - 1
                b = in_byte >> shift
                out_byte = append_to_int(out_byte, b)
                output.append(out_byte)

                # Take the untouched bits, and prepend a 1
                mask = (1 << shift) - 1
                in_byte &= mask
                in_byte |= (1 << shift)

                # Next loop will start a new byte
                out_byte = 1
                bspace = 7

        output.append(out_byte)

        return output


    def _unpack_encoded(self, stream, tree):
        output = bytearray()
        bspace = 7
        in_byte = 0
        root = self._huffman_tree.tree
        cur_node = root
        i = 0
        while (stream or in_byte):
            if (not in_byte):
                in_byte = stream[0]
                stream = stream[1:]

            shifts = in_byte.bit_length() - 1

            leaf = self._huffman_tree._get_leaf(cur_node, in_byte, shifts)

            # it's not in the table
            if (leaf is None):
                output.append(in_byte)
                in_byte = 0
                continue

            cur_node, path, shifts = leaf
            if (cur_node.value and cur_node.value.value):
                # found it
                output.append(cur_node.value.value)

                # part of path that was used. "2" is there due to leading 1
                rs = shifts
                # invert the path
                m = path >> rs
                mask = ~m & ((2 ** m.bit_length()) - 1) # dealing with two's comp.
                mask <<= rs
                # add a mask of all 1s to keep unused part of path
                m2 = 2**rs - 1
                mask |= m2

                # kill the used part of the number
                path &= mask

                # add a leading 1 to the path if we haven't reachedthe end of the number
                path |= (1 << rs) if rs > 0 else 0
                in_byte = path if shifts >= 0 else 0
                cur_node = root

            else:
                # we haven't reached a leaf yet, so on the next loop
                # will grab the next byte and begin reading that path from
                # cur_node, the node we left off on
                in_byte = 0

        return output

def build_huffByte_freqs(byte_stream, sample_size=1.00):
    """ Returns list of HuffBytes with frequencies set

        byte_stream
            @type - bytearray
            @param - the raw data

        sample_size
            @type - float
            @param - what percent of the data to review for frequencies
    """
    up_to = len(byte_stream) * sample_size
    byte_stream = byte_stream[:int(up_to)]
    freq_tbl = {}
    max_freq = 0
    for byte in byte_stream:
        try:
            freq_tbl[byte].frequency += 1/up_to

        except KeyError:
            b = HuffByte(value = byte, frequency = 1/up_to)
            freq_tbl[byte] = b

    return list(freq_tbl.values())

def huffBytes_to_Nodes(hb_list):
    return [hb_to_node(hb) for hb in hb_list]

def hb_to_node(hb):
    new_node = Node()
    new_node.value = hb
    return new_node

def set_recursion_limit(node_list, limit=0):
    if (not limit):
        limit = len(node_list)**2

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(limit)
    return old


def sort_NodeList(node_list, pv=None):
    """ Sort a set of Nodes with HuffByte values into desc by frequency using quicksort """

    # Base case
    if (len(node_list) <= 1):
        return node_list

    # calculate the pivot as mean of three
    if (pv is None):
        pv = 0
        for i in range(3):
            pv += random.choice(node_list).value.frequency / 3



    smaller = []
    middle = []
    larger = []
    for i in range(len(node_list)):
        n = node_list[i]
        # partition the values
        if (n.value.frequency < pv):
            smaller.append(n)
        elif (n.value.frequency > pv):
            larger.append(n)
        else:
            middle.append(n) # to handle equal frequencies

    return sort_NodeList(larger) + middle + sort_NodeList(smaller)

def insert_to_NodeList(node, node_list):
    """ Insert a new Node into huff_tbl sorted by probability DESC

        node - @type - tuple
             - @param - (Node, probability)

        node_list - @type - list
                 - @param - list of `tupe`s

        Insert into huff_tbl using binary-search insert, since
        insertion is being done asyncronously. Ordered desc to
        optimize for pop()s
    """
    found = False
    lwr = 0
    upr = len(node_list) - 1
    while not found:

        # up here to allow for ln_freq setting
        if (not node_list):
            found = True
            i_at = 0
            continue

        mid = (upr + lwr) // 2
        freq = node.value.frequency

        ln_freq = node_list[lwr].value.frequency
        md_freq = node_list[mid].value.frequency
        un_freq = node_list[upr].value.frequency



        # Found midpoint
        if ((upr - lwr) <= 1 and ln_freq > freq > un_freq):
            found = True
            i_at = upr

        # `prob` smaller than any in tbl
        elif (un_freq >= freq):
            found = True
            i_at = upr + 1

        # `prob` larger than any in tbl
        elif (freq >= ln_freq):
            found = True
            i_at = lwr

        # `prob` is midpoint
        elif (freq == md_freq):
            found = True
            i_at = mid

        # prob is between lower and mid
        elif (ln_freq > freq > md_freq):
            upr = mid

        #prob is between mid and upper
        elif (md_freq > freq > un_freq):
            lwr = mid

    node_list.insert(i_at, node)
    return node_list

def build_huffman_tree(node_list):
    """ Returns a HuffmanTree object

        @type - {}
        @param - the bytestream to
        """
    while (len(node_list) > 1):
        n1 = node_list.pop()
        n2 = node_list.pop()

        new_node = Node()
        new_node.value.frequency = n1.value.frequency + n2.value.frequency
        new_node.left = n1
        new_node.right = n2
        node_list = insert_to_NodeList(new_node, node_list)

    HT = HuffmanTree()
    HT.tree = node_list[0]
    return HT

def append_to_int(int1, int2):
    """ bitwise append int2 to int1 and return
        NB: int2 has preceding 1 that should be stripped
    """
    l = int2.bit_length() - 1
    int1 <<= l

    int2 = int2 ^ (1 << l)
    int1 |= int2

    return int1
