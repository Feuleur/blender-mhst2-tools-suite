import struct
import os
from glob import glob
import json
import logging
logger = logging.getLogger("mhst2_import")

class Reader():
    def __init__(self, data):
        self.offset = 0
        self.data = data

    def read(self, kind, size):
        result = struct.unpack(kind, self.data[self.offset:self.offset+size])[0]
        self.offset += size
        return result

    def seek(self, offset, start = None):
        if start is None:
            self.offset = offset
        else:
            self.offset += offset

    def readUInt(self):
        return self.read("I", 4)

    def readInt(self):
        return self.read("i", 4)

    def readUInt64(self):
        return self.read("Q", 8)

    def readHalf(self):
        return self.read("e", 2)

    def readFloat(self):
        return self.read("f", 4)

    def readShort(self):
        return self.read("h", 2)

    def readUShort(self):
        return self.read("H", 2)

    def readByte(self):
        return self.read("b", 1)

    def readBytes(self, size):
        return self.data[self.offset:self.offset + size]

    def readUByte(self):
        return self.read("B", 1)

    def readString(self):
        text = ""
        while True:
            char = self.readUByte()
            if char == 0:
                break
            else:
                text += chr(char)
        return text

    def readStringUTFAt(self, offset):
        previous_offset = self.tell()
        self.seek(offset)
        text = ""
        while True:
            char = self.readUShort()
            if char == 0:
                break
            else:
                text += chr(char)
        self.seek(previous_offset)
        return text

    def readStringUTF(self):
        text = ""
        while True:
            char = self.readUShort()
            if char == 0:
                break
            else:
                text += chr(char)
        return text

    def allign(self, size):
        self.offset = (int((self.offset)/size)*size)+size

    def tell(self):
        return self.offset

    def getSize(self):
        return len(self.data)

class ClcParser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)

    def read(self):
        self.magic = self.bs.readUInt()
        if self.magic != 4410435:
            raise RuntimeError(str(self.path) + " is not a clc file (magic = " + str(self.magic) + ")")
        _ = self.bs.readUInt()

        _ = self.bs.readUByte()
        _ = self.bs.readUByte()
        _ = self.bs.readUByte()

        R = self.bs.readUByte()
        G = self.bs.readUByte()
        B = self.bs.readUByte()

        return {"color":[R/255.0, G/255.0, B/255.0]}

if __name__ == "__main__":
    from glob import glob
    clc_files = glob("./*.clc", recursive=True)

    for clc_file in clc_files:
        parser = ClcParser(path=clc_file)

        datas = parser.read()
        print(datas)

