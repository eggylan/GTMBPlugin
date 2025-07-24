# uncompyle6 version 3.9.2
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: VTScripts/utils/__init__.py
import __future__
from uuid import uuid4

def index_get(data, indexes):
    """
    :param indexes: \xe7\xb4\xa2\xe5\xbc\x95\xe5\x8f\xa0\xe5\x8a\xa0,\xe7\xb4\xa2\xe5\xbc\x95\xe7\xb1\xbb\xe5\x9e\x8b\xe6\x94\xaf\xe6\x8c\x81\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2\xe5\x92\x8c\xe6\x95\xb4\xe6\x95\xb0,\xe5\x8f\xaf\xe4\xbb\xa5\xe6\x98\xaf\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2,\xe4\xbb\xa5","\xe5\x88\x86\xe5\x89\xb2,\xe5\x88\x97\xe8\xa1\xa8\xe7\xb4\xa2\xe5\xbc\x95\xe7\x94\xa8"[]\xe6\x89\xa9\xe8\xb5\xb7",\xe5\xa6\x82``foo,bar[0],a``,\xe4\xb9\x9f\xe5\x8f\xaf\xe4\xbb\xa5\xe6\x98\xaf\xe5\x88\x97\xe8\xa1\xa8,\xe5\xa6\x82``['foo', 'bar[0]', 'a']``
    """
    indexs = (indexes if isinstance(indexes, str) else (',').join(indexes)).replace('][', '[').replace('[', ',').replace(']', ',').replace(',,', ',').split(',')
    if indexs[-1] == '':
        del indexs[-1]
    for index in indexs:
        try:
            data = data[index]
        except:
            data = data[int(index)]

    return data


def index_set(data, value, indexes):
    """
    :param indexes: \xe7\xb4\xa2\xe5\xbc\x95\xe5\x8f\xa0\xe5\x8a\xa0,\xe7\xb4\xa2\xe5\xbc\x95\xe7\xb1\xbb\xe5\x9e\x8b\xe6\x94\xaf\xe6\x8c\x81\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2\xe5\x92\x8c\xe6\x95\xb4\xe6\x95\xb0,\xe5\x8f\xaf\xe4\xbb\xa5\xe6\x98\xaf\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2,\xe4\xbb\xa5","\xe5\x88\x86\xe5\x89\xb2,\xe5\x88\x97\xe8\xa1\xa8\xe7\xb4\xa2\xe5\xbc\x95\xe7\x94\xa8"[]\xe6\x89\xa9\xe8\xb5\xb7",\xe5\xa6\x82``foo,bar[0],a``,\xe4\xb9\x9f\xe5\x8f\xaf\xe4\xbb\xa5\xe6\x98\xaf\xe5\x88\x97\xe8\xa1\xa8,\xe5\xa6\x82``['foo', 'bar[0]', 'a']``
    """
    indexs = (indexes if isinstance(indexes, str) else (',').join(indexes)).replace('][', '[').replace('[', ',').replace(']', ',').replace(',,', ',').split(',')
    if indexs[-1] == '':
        del indexs[-1]
    for index in indexs[:-1]:
        try:
            data = data[index]
        except:
            data = data[int(index)]

    try:
        data[indexs[-1]] = value
    except:
        data[int(indexs[-1])] = value


def index_del(data, indexes):
    """
    :param indexes: \xe7\xb4\xa2\xe5\xbc\x95\xe5\x8f\xa0\xe5\x8a\xa0,\xe7\xb4\xa2\xe5\xbc\x95\xe7\xb1\xbb\xe5\x9e\x8b\xe6\x94\xaf\xe6\x8c\x81\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2\xe5\x92\x8c\xe6\x95\xb4\xe6\x95\xb0,\xe5\x8f\xaf\xe4\xbb\xa5\xe6\x98\xaf\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2,\xe4\xbb\xa5","\xe5\x88\x86\xe5\x89\xb2,\xe5\x88\x97\xe8\xa1\xa8\xe7\xb4\xa2\xe5\xbc\x95\xe7\x94\xa8"[]\xe6\x89\xa9\xe8\xb5\xb7",\xe5\xa6\x82``foo,bar[0],a``,\xe4\xb9\x9f\xe5\x8f\xaf\xe4\xbb\xa5\xe6\x98\xaf\xe5\x88\x97\xe8\xa1\xa8,\xe5\xa6\x82``['foo', 'bar[0]', 'a']``
    """
    indexs = (indexes if isinstance(indexes, str) else (',').join(indexes)).replace('][', '[').replace('[', ',').replace(']', ',').replace(',,', ',').split(',')
    if indexs[-1] == '':
        del indexs[-1]
    for index in indexs[:-1]:
        try:
            data = data[index]
        except:
            data = data[int(index)]

    try:
        del data[indexs[-1]]
    except:
        del data[int(indexs[-1])]


def to_bool(value):
    if value == 'True':
        return True
    return False


def clean(target, remove=' '):
    return target.replace(remove, '')


def uuid():
    return str(uuid4())


def clean_itemDict(itemDict):
    keys = ('isDiggerItem', 'enchantData', 'itemId', 'durability', 'itemName', 'auxValue',
            'showInHand')
    map(itemDict.pop, keys)


def number(value):
    try:
        if value.replace('-', '').isdigit():
            return int(value)
        else:
            return float(value)

    except ValueError:
        return value

# okay decompiling D:/MCStudioDownload/work/z13416661916@163.com/Cpp/AddOn/113139c5d51142aeb8b5d6b9fc65e155/behavior_pack_QVpTfSxL/VTScripts/VTScripts/utils\__init__.pyc
