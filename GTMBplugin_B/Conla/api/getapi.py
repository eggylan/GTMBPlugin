import mod.server.extraServerApi as sapi, mod.client.extraClientApi as capi
from types import FunctionType
fast_listen_list = []
system = {'class_type': None, 'instance': None}

def Listen(namespace='engine', systemName='engine'):
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
    global system
    system = {'class_type': ('server' if issubclass(instance.__class__, sapi.GetServerSystemCls()) else 'client'), 'instance': instance}
    instance_module = instance.__class__.__module__
    for namespace, systemName, eventName, callbackFunc, func_module in fast_listen_list:
        if instance_module == func_module:
            instance.ListenForEvent(namespace, systemName, eventName, instance, callbackFunc)


__all__ = [
 'InitFastListen', 'Listen']
