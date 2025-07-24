# uncompyle6 version 3.9.2
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: VTScripts/modMain.py
import __future__
from config import *
from mod.common.mod import Mod
import mod.client.extraClientApi as capi, mod.server.extraServerApi as sapi

@Mod.Binding(name=NAMESPACE, version='1.0')
class VanillaTestMod(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def initMod(self):
        sapi.RegisterSystem(NAMESPACE, SERVER_SYSTEM_NAME, SERVER_SYSTEM_PATH)

    @Mod.InitClient()
    def init(self):
        capi.RegisterSystem(NAMESPACE, CLIENT_SYSTEM_NAME, CLIENT_SYSTEM_PATH)

# okay decompiling D:/MCStudioDownload/work/z13416661916@163.com/Cpp/AddOn/113139c5d51142aeb8b5d6b9fc65e155/behavior_pack_QVpTfSxL/VTScripts/VTScripts\modMain.pyc
