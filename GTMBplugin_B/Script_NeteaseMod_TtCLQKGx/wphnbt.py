# -*- coding: utf-8 -*-
from __future__ import print_function
import struct

def from_bytes(bytes):
    bytes = bytes[::-1]
    n = 0
    for x in bytes:
        n = (n << 8) + ord(x)
    if ord(bytes[-1]) & 0x80:
        n -= 1 << (8* len(bytes))
    return n

class Path(list):
    def __init__(self, data=[]):
        if isinstance(data, str):
            out = []
            data = data.split('.')
            for i in data:
                if i.startswith('[') and i.endswith(']'):
                    i = int(i[1:-1])
                    out.append(i)
                elif i.find('[') != -1 and i.endswith(']'):
                    i, j = i.split('[')
                    j = int(j[:-1])
                    out.append(i)
                    out.append(j)
                else:
                    out.append(i)
            super(Path, self).__init__(out)
        else:
            super(Path, self).__init__(data)
    def __repr__(self):
        out = []
        for i in self:
            if isinstance(i, int):
                out.append('[%d]' % i)
            else:
                out.append(i)
        return '.'.join(out)

class Compound(dict):
    length = None
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.length = 1
        for k, v in data.items():
            self.length += len(k.encode('utf-8')) + 3 + v.length
        super(Compound, self).__init__(data)
    def __repr__(self):
        return 'Compound(%s)' % super(Compound, self).__repr__()
    def __getitem__(self, key):
        if isinstance(key, Path):
            value = self
            if len(key) == 0:
                raise KeyError('Empty path is not allowed')
            for i in key:
                value = value[i]
            return value
        else:
            return super(Compound, self).__getitem__(key)
    def __setitem__(self, key, value):
        if isinstance(key, Path):
            if len(key) == 1:
                self[key[0]] = value
                return
            elif len(key) == 0:
                raise KeyError('Empty path is not allowed')
            self[key[0]][Path(key[1:])] = value
        else:
            super(Compound, self).__setitem__(key, value)
    def __delitem__(self, key):
        if isinstance(key, Path):
            if len(key) == 1:
                del self[key[0]]
                return
            elif len(key) == 0:
                raise KeyError('Empty path is not allowed')
            del self[key[0]][Path(key[1:])]
        else:
            super(Compound, self).__delitem__(key)
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {k: unpack(v, True) for k, v in self.items()}
        else:
            return {k: unpack(v) for k, v in self.items()}

class Byte(int):
    length = 1
    unpack_method = '<b'
    def __init__(self, value=None):
        if value is None:
            value = 0
        self.value = value
        self.length = 1
        super(Byte, self).__init__(value)
    def __repr__(self):
        return 'Byte(%d)' % self.value
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 1, '__value__': int(self)}
        else:
            return int(self)

class Short(int):
    length = 2
    unpack_method = '<h'
    def __init__(self, value=None):
        if value is None:
            value = 0
        self.value = value
        self.length = 2
        super(Short, self).__init__(value)
    def __repr__(self):
        return 'Short(%d)' % self.value
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 2, '__value__': int(self)}
        else:
            return int(self)

class Int(int):
    length = 4
    unpack_method = '<i'
    def __init__(self, value=None):
        if value is None:
            value = 0
        self.value = value
        self.length = 4
        super(Int, self).__init__(value)
    def __repr__(self):
        return 'Int(%d)' % self.value
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 3, '__value__': int(self)}
        else:
            return int(self)

class Long(long): #type: ignore
    length = 8
    unpack_method = '<q'
    def __init__(self, value=None):
        if value is None:
            value = 0
        self.value = value
        self.length = 8
        super(Long, self).__init__(value)
    def __repr__(self):
        return 'Long(%d)' % self.value
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 4, '__value__': int(self)}
        else:
            return int(self)

class Float(float):
    length = 4
    unpack_method = '<f'
    def __init__(self, value=None):
        if value is None:
            value = 0.0
        self.value = value
        self.length = 4
        super(Float, self).__init__(value)
    def __repr__(self):
        return 'Float(%f)' % self.value
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 5, '__value__': float(self)}
        else:
            return float(self)

class Double(float):
    length = 8
    unpack_method = '<d'
    def __init__(self, value=None):
        if value is None:
            value = 0.0
        self.value = value
        self.length = 8
        super(Double, self).__init__(value)
    def __repr__(self):
        return 'Double(%f)' % self.value
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 6, '__value__': float(self)}
        else:
            return float(self)

class String(str):
    length = None
    def __new__(self, value=''):
        obj = str.__new__(self, value)
        obj.length = 2 + len(value)
        return obj
    def __repr__(self):
        return 'String(%s)' % super(String, self).__repr__()
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 8, '__value__': str(self)}
        else:
            return str(self)
    
class ByteArray(bytearray):
    length = None
    subtype = Byte
    def __init__(self, data=None):
        if data is None:
            data = bytearray()
        self.length = 4 + len(self)
        super(ByteArray, self).__init__(data)
    def __repr__(self):
        return 'ByteArray(%s)' % super(ByteArray, self).__repr__()
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 7, '__value__': list(self)}
        else:
            return list(self)

class List(list):
    length = None
    def __init__(self, data=None):
        if data is None:
            data = []
        self.length = 5
        for i in data:
            self.length += i.length
        super(List, self).__init__(data)
    def __repr__(self):
        return 'List(%s)' % super(List, self).__repr__()
    def __getitem__(self, index):
        if isinstance(index, Path):
            if len(index) == 0:
                raise KeyError('Empty path is not allowed')
            value = self
            for i in index:
                try:
                    i = int(i)
                except:
                    pass
                value = value[i]
            return value
        else:
            return super(List, self).__getitem__(index)
    def __setitem__(self, index, value):
        if isinstance(index, Path):
            if len(index) == 1:
                self[index[0]] = value
                return
            elif len(index) == 0:
                raise KeyError('Empty path is not allowed')
            self[index[0]][Path(index[1:])] = value
        else:
            super(List, self).__setitem__(index, value)
    def __delitem__(self, index):
        if isinstance(index, Path):
            if len(index) == 1:
                del self[index[0]]
                return
            elif len(index) == 0:
                raise KeyError('Empty path is not allowed')
            del self[index[0]][Path(index[1:])]
        else:
            super(List, self).__delitem__(index)
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return [unpack(i, True) for i in self]
        else:
            return [unpack(i) for i in self]

class IntArray(list):
    length = None
    subtype = Int
    def __init__(self, data=None):
        if data is None:
            data = []
        self.length = 4 + len(data) * 4
        super(IntArray, self).__init__(data)
    def __repr__(self):
        return 'IntArray(%s)' % super(IntArray, self).__repr__()
    def unpack(self, keep_tag_type=False):
        if keep_tag_type:
            return {'__type__': 11, '__value__': list(self)}
        else:
            return list(self)

tags = {
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
    if tag_type in [Byte, Short, Int, Long, Float, Double]:
        value = reader.read(tag_type.length)
        value = tag_type(struct.unpack(tag_type.unpack_method, value)[0])
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
            if not tag_type_byte or not from_bytes(tag_type_byte):
                break
            child_tag_type = tags.get(from_bytes(tag_type_byte))
            tag_name_len = from_bytes(reader.read(2))
            tag_name = reader.read(tag_name_len)
            value[tag_name] = decode_bin(child_tag_type, reader)
    return tag_type(value)

def load(reader):
    reader.seek(0)
    return decode_bin(Compound, reader)['']

def unpack(value, keep_tag_type=False):
    if isinstance(value, dict):
        return {k: unpack(v, keep_tag_type) for k, v in value.items()}
    if isinstance(value, list):
        return [unpack(i, keep_tag_type) for i in value]
    if hasattr(value, 'unpack'):
        return value.unpack(keep_tag_type)
    return value

def dump(data):
    if isinstance(data, dict):
        return Compound({k: dump(v) for k, v in data.items()})
    if isinstance(data, list):
        return List([dump(i) for i in data])
    if isinstance(data, (int, long)): #type: ignore
        return Int(data)
    if isinstance(data, float):
        return Float(data)
    if isinstance(data, str):
        return String(data)
    
if __name__ == '__main__':
    with open("C:\Users\wangl\Downloads\work\\1.mcstructure", 'rb') as f:
        structure = load(f)
        structureentitydata = structure['structure']['palette']['default']['block_position_data']
        structure['structure']['palette']['default']['block_position_data'] = unpack(structureentitydata, True)
        structureentitys = structure['structure']['entities']
        structure['structure']['entities'] = unpack(structureentitys, True)
        structure = unpack(structure)
    print(structure)