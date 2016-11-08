import os, sys
import binascii


def open_file(filepath):
    if (os.path.isfile(filepath) is False): raise ValueError()

    return open(filepath, "r+").read()

def is_png(data):
    first_eight = data[:8]
    PNG_id = "89 50 4e 47 0d 0a 1a 0a"
    if (binascii.hexlify(first_eight) == PNG_id):
        return True
    return False

def type_to_eng(type_hex):
    try:
        int(type_hex, 16)
    except ValueError:
        raise TypeError("type_to_eng requires hex, you pass : {}".format(type_hex))

    type_hex = type_hex.replace("0x", "").lower()

    mapping = {
        "49484452" : "IHDR",
        "504c5445" : "PLTE",
        "49444154" : "IDAT",
        "49454e44" : "IEND",
        "74524e53" : "tRNS",
        "8348524d" : "cHRM",
        "67414d41" : "gAMA",
        "69434350" : "iCCP",
        "73424954" : "sBIT",
        "73524742" : "sRGB",
        "74455874" : "tEXt",
        "7a545874" : "zTXt",
        "69545874" : "iTXt",
        "624b4744" : "bKGD",
        "68495354" : "hIST",
        "70485973" : "pHYs",
        "73504c54" : "sPLT",
        "74494d45" : "tIME",

    }

    return mapping.get(type_hex, None)

def byte_to_hex(bytes):
    d = binascii.hexlify(bytes)
    return []
def break_into_chunks(data):

    # PNG's begin with an identifier. If this has not yet been stripped,
    # we should remove it
    PNG_id = "89 50 4e 47 0d 0a 1a 0a".replace(" " , "")
    if (binascii.hexlify(data[:8]) == PNG_id):
        data = data[8:]

    png = {}

    while data:

        # CHUNK LENGTH
        # First four bytes of a chunk are the length of its data (so excludes
        # name and CRC)
        chunk_len = data[:4]
        chunk_len = int(binascii.hexlify(chunk_len), 16)
        data = data[4:]

        # CHUNK TYPE
        # Second four bytes specify the type of chunk_len
        chunk_type = data[:4]
        chunk_type = binascii.hexlify(chunk_type)
        data = data[4:]

        # CHUNK DATA
        # the next n bytes (where n = chunk_len) are the actual data of the
        # chunk. If chunk_len = 0, this doesn't exist
        raw_chunk_data = data[:chunk_len]
        hex_chunk_data = binascii.hexlify(raw_chunk_data)
        data = data[chunk_len:]

        # CHUNK CRC
        # the next 4 bytes are the cyclic redundancy code (CRC)
        chunk_CRC = data[:4]
        chunk_CRC = binascii.hexlify(chunk_CRC)
        data = data[4:]

        png[chunk_type] = {
            "length" : chunk_len,
            "data" : hex_chunk_data,
            "raw_data" : raw_chunk_data,
            "crc" : chunk_CRC,
            "type" : type_to_eng(chunk_type)
        }

    return png

if __name__ == "__main__":
    fp = "/Users/LukeGilson/misc_scripts/png/test_png_1px.png"
    data = open_file(fp)
    k = break_into_chunks(data)
    for i in k:
        print "=== {} ===".format(i)
        for j in k[i]:
            print "{} : {}".format(j, k[i][j])
