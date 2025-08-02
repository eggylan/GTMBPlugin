# -*- coding: utf-8 -*-
from __future__ import print_function
import struct
import json

def from_bytes(bytes):
    bytes = bytes[::-1]
    n = 0
    for x in bytes:
        n = (n << 8) + ord(x)
    if ord(bytes[-1]) & 0x80:
        n -= 1 << (8* len(bytes))
    return n

class Compound(dict):
    length = None
    def __init__(self, data={}):
        self.length = 1
        for k, v in data.items():
            self.length += len(k.encode('utf-8')) + 3 + v.length
        super(Compound, self).__init__(data)
    def __repr__(self):
        return 'Compound(%s)' % super(Compound, self).__repr__()

class Byte(int):
    length = 1
    unpack_method = '<b'
    def __init__(self, value=0):
        self.value = value
        self.length = 1
        super(Byte, self).__init__(value)
    def __repr__(self):
        return 'Byte(%d)' % self.value

class Short(int):
    length = 2
    unpack_method = '<h'
    def __init__(self, value=0):
        self.value = value
        self.length = 2
        super(Short, self).__init__(value)
    def __repr__(self):
        return 'Short(%d)' % self.value

class Int(int):
    length = 4
    unpack_method = '<i'
    def __init__(self, value=0):
        self.value = value
        self.length = 4
        super(Int, self).__init__(value)
    def __repr__(self):
        return 'Int(%d)' % self.value

class Long(long): #type: ignore
    length = 8
    def __init__(self, value=0):
        self.value = value
        self.length = 8
        super(Long, self).__init__(value)
    def __repr__(self):
        return 'Long(%d)' % self.value

class Float(float):
    length = 4
    def __init__(self, value=0.0):
        self.value = value
        self.length = 4
        super(Float, self).__init__(value)
    def __repr__(self):
        return 'Float(%f)' % self.value

class Double(float):
    length = 8
    def __init__(self, value=0.0):
        self.value = value
        self.length = 8
        super(Double, self).__init__(value)
    def __repr__(self):
        return 'Double(%f)' % self.value

class String(str):
    length = None
    def __init__(self, value=''):
        self.length = 2 + len(value)
        super(String, self).__init__(value)
    def __repr__(self):
        return 'String(%s)' % super(String, self).__repr__()
    
class ByteArray(bytearray):
    length = None
    subtype = Byte
    def __init__(self, data=[]):
        self.length = 4 + len(self)
        super(ByteArray, self).__init__(data)
    def __repr__(self):
        return 'ByteArray(%s)' % super(ByteArray, self).__repr__()

class List(list):
    length = None
    def __init__(self, data=[]):
        self.length = 5
        for i in data:
            self.length += i.length
        super(List, self).__init__(data)
    def __repr__(self):
        return 'List(%s)' % super(List, self).__repr__()

class IntArray(list):
    length = None
    subltype = Int
    def __init__(self, data=[]):
        self.length = 4 + len(data) * 4
        super(IntArray, self).__init__(data)
    def __repr__(self):
        return 'IntArray(%s)' % super(IntArray, self).__repr__()

tags = {
    0: 'End',
    1: Byte,
    2: Short,
    3: Int,
    4: Long,
    5: Float,
    6: Double,
    7: ByteArray,
    8: String,
    9: List,
    10: Compound,
    11: IntArray
}

def decode_bin(tag_type, reader):
    if tag_type in [Byte, Short, Int]:
        value = reader.read(tag_type.length)
        value = tag_type(struct.unpack(tag_type.unpack_method, value)[0])
    elif tag_type == Long:
        value = Long(long(struct.unpack('<q', reader.read(8))[0])) #type: ignore
    elif tag_type == Float:
        value = Float(struct.unpack('<f', reader.read(4))[0])
    elif tag_type == Double:
        value = Double(struct.unpack('<d', reader.read(8))[0])
    elif tag_type == String:
        str_len = struct.unpack('<h', reader.read(2))[0]
        value = String(reader.read(str_len))
    elif tag_type in [ByteArray, IntArray]:
        array_len = struct.unpack('<i', reader.read(4))[0]
        value = tag_type()
        for _ in range(array_len):
            value.append(struct.unpack(tag_type.subtype.unpack_method, reader.read(tag_type.subtype.length))[0])
    elif tag_type == List:
        childtype = tags.get(struct.unpack('<b', reader.read(1))[0])
        child_num = struct.unpack('<i', reader.read(4))[0]#from_bytes(reader.read(4))
        value = List()
        for _ in range(child_num):
            value.append(decode_bin(childtype, reader))
    elif tag_type == Compound:
        value = Compound()
        while 1:
            tag_type_byte = reader.read(1)
            if not tag_type_byte:
                break
            child_tag_type = tags.get(from_bytes(tag_type_byte))
            if child_tag_type == 'End':
                break
            tag_name_len = from_bytes(reader.read(2))
            tag_name = reader.read(tag_name_len)
            value[tag_name] = decode_bin(child_tag_type, reader)
    else:
        print(tag_type)
    return tag_type(value)

def load(reader):
    #file_size = len(reader.read())
    reader.seek(0)
    data = Compound()
    while 1:
        tag_type_byte = reader.read(1)
        if not tag_type_byte:
            break
        tag_type = tags.get(from_bytes(tag_type_byte))
        tag_name_len = from_bytes(reader.read(2))
        tag_name = reader.read(tag_name_len)
        if tag_name:
            data[tag_name] = decode_bin(tag_type, reader)
        else:
            data = decode_bin(tag_type, reader)
    return data

def unpack(value, keep_tag_type=False):
    if keep_tag_type == True:
        if isinstance(value, Compound):
            return {k: unpack(v, True) for k, v in value.items()}
        elif isinstance(value, Byte):
            return {'__type__': 1, '__value__': int(value)}
        elif isinstance(value, Short):
            return {'__type__': 2, '__value__': int(value)}
        elif isinstance(value, Int):
            return {'__type__': 3, '__value__': int(value)}
        elif isinstance(value, Long):
            return {'__type__': 4, '__value__': int(value)}
        elif isinstance(value, Float):
            return {'__type__': 5, '__value__': float(value)}
        elif isinstance(value, Double):
            return {'__type__': 6, '__value__': float(value)}
        elif isinstance(value, ByteArray):
            return {'__type__': 7, '__value__': list(value)}
        elif isinstance(value, String):
            return {'__type__': 8, '__value__': str(value)}
        elif isinstance(value, List):
            return [unpack(i, True) for i in value]
        elif isinstance(value, IntArray):
            return {'__type__': 11, '__value__': list(value)}
        else:
            return value
    else:
        if isinstance(value, Compound):
            return {k: unpack(v, False) for k, v in value.items()}
        elif isinstance(value, (Byte, Short, Int, Long, Float, Double)):
            return int(value)
        elif isinstance(value, String):
            return str(value)
        elif isinstance(value, (List, IntArray, ByteArray)):
            return [unpack(i, False) for i in value]
        else:
            return value

if __name__ == '__main__':
    with open("C:\Users\wangl\Downloads\q.mcstructure", 'rb') as f:
        data = load(f)
        print(unpack(data))
            