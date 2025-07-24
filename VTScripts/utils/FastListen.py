# uncompyle6 version 3.9.2
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: VTScripts/utils/FastListen.py
import mod.server.extraServerApi as sapi, mod.client.extraClientApi as capi
from types import FunctionType
fast_listen_list = []
system = {'class_type': None, 'instance': None}

def Listen(namespace='engine', systemName='engine'):
    """
    \xe5\xbf\xab\xe9\x80\x9f\xe7\x9b\x91\xe5\x90\xac\xe4\xba\x8b\xe4\xbb\xb6,\xe8\xa3\x85\xe9\xa5\xb0\xe5\x9b\x9e\xe8\xb0\x83\xe6\x96\xb9\xe6\xb3\x95\xe5\x8d\xb3\xe5\x8f\xaf

    \xe7\x9b\x91\xe5\x90\xac\xe5\xbc\x95\xe6\x93\x8e\xe7\xb3\xbb\xe7\xbb\x9f\xe4\xba\x8b\xe4\xbb\xb6:
    
    @Listen
    
    def eventName(instance, args):

    \xe7\x9b\x91\xe5\x90\xac\xe5\x85\xb6\xe5\xae\x83\xe7\xb3\xbb\xe7\xbb\x9f\xe4\xba\x8b\xe4\xbb\xb6:
    
    @Listen(namespace, systemName):
    
    def eventName(instance, args):
    """
    global system
    func = None
    if isinstance(namespace, FunctionType):
        func = namespace
        namespace = sapi.GetEngineNamespace() if system.get('class_type') == 'server' else capi.GetEngineNamespace()
    if systemName == 'engine':
        systemName = sapi.GetEngineSystemName() if system.get('class_type') == 'server' else capi.GetEngineSystemName()

    def wrapper(func):
        global fast_listen_list
        fast_listen_list.append((namespace, systemName, func.__name__, func, func.__module__))
        return func

    if func is None:
        return wrapper
    else:
        return wrapper(func)


def InitFastListen(instance):
    """
    \xe5\x88\x9d\xe5\xa7\x8b\xe5\x8c\x96\xe5\xbf\xab\xe9\x80\x9f\xe7\x9b\x91\xe5\x90\xac\xe4\xba\x8b\xe4\xbb\xb6,\xe9\x9c\x80\xe8\xa6\x81\xe6\x94\xbe\xe5\x9c\xa8\xe8\x84\x9a\xe6\x9c\xac\xe7\xb3\xbb\xe7\xbb\x9f\xe7\x9a\x84__init__\xe6\x96\xb9\xe6\xb3\x95\xe4\xb8\xad,\xe5\xb9\xb6\xe4\xbc\xa0\xe5\x85\xa5instance
    """
    global system
    system = {'class_type': ('server' if issubclass(instance.__class__, sapi.GetServerSystemCls()) else 'client'), 'instance': instance}
    instance_module = instance.__class__.__module__
    for namespace, systemName, eventName, callbackFunc, func_module in fast_listen_list:
        if instance_module == func_module:
            instance.ListenForEvent(namespace, systemName, eventName, instance, callbackFunc)


__all__ = [
 'InitFastListen', 'Listen']

# okay decompiling D:/MCStudioDownload/work/z13416661916@163.com/Cpp/AddOn/113139c5d51142aeb8b5d6b9fc65e155/behavior_pack_QVpTfSxL/VTScripts/VTScripts/utils\FastListen.pyc
