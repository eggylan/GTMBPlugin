# uncompyle6 version 3.9.2
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: VTScripts/VTClient.py
import __future__
from time import time
import mod.client.extraClientApi as capi
from .utils.CompFactory import ClientCompFactory as cr
from utils import *
from utils.FastListen import *
from config import *
levelId = capi.GetLevelId()
Id = capi.GetLocalPlayerId()

class VTClientSys(capi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(VTClientSys, self).__init__(namespace, name)
        InitFastListen(self)
        self.ListenEvent()
        comp = cr.Game(levelId)
        comp.AddRepeatedTimer(0.05, self.Tick)
        comp.AddRepeatedTimer(1, self.Second)
        self.options = {}
        self.ping = 0
        self.input_vec = {}
        self.left_click_time_set = set()
        self.right_click_time_set = set()

    def ListenEvent(self):
        self.ListenEngineEvent = lambda eventName, callbackFunc: self.ListenForEvent(capi.GetEngineNamespace(), capi.GetEngineSystemName(), eventName, self, callbackFunc)
        self.ListenServerEvent = lambda eventName, callbackFunc: self.ListenForEvent('VanillaTest', 'VTServer', eventName, self, callbackFunc)
        self.ListenEngineEvent('HoldBeforeClientEvent', self.OnPlayerRightClick)
        self.ListenEngineEvent('RightClickBeforeClientEvent', self.OnPlayerRightClick)
        self.ListenEngineEvent('RightClickReleaseClientEvent', self.OnPlayerReleaseRightClick)
        self.ListenEngineEvent('TapOrHoldReleaseClientEvent', self.OnPlayerReleaseRightClick)
        self.ListenEngineEvent('TapOrHoldReleaseClientEvent', self.OnPlayerReleaseLeftClick)
        self.ListenEngineEvent('LeftClickBeforeClientEvent', self.OnPlayerLeftClick)
        self.ListenEngineEvent('LeftClickReleaseClientEvent', self.OnPlayerReleaseLeftClick)
        self.ListenEngineEvent('GetEntityByCoordEvent', self.OnPlayerLeftClick)
        self.ListenEngineEvent('GetEntityByCoordReleaseClientEvent', self.OnPlayerReleaseLeftClick)

    def Destroy(self):
        self.UnListenAllEvents()

    def Tick(self):
        comp = capi.GetEngineCompFactory().CreatePlayer(Id)
        if comp.IsOnLadder():
            self.NotifyToServer('IsOnLadder',{"Id":Id})
        else:
            self.NotifyToServer('IsNotOnLadder',{"Id":Id})
        if comp.IsInScaffolding():
            self.NotifyToServer('IsInScaffolding',{"Id":Id})
        else:
            self.NotifyToServer('IsNotInScaffolding',{"Id":Id})
        comp = cr.QueryVariable(Id)
        molang = lambda molangName: False if comp.GetMolangValue(molangName) == 0.0 else True
        movements = {'jump': (molang('query.is_jumping')), 
           'sneak': (molang('query.is_sneaking')), 
           'moving': (molang('query.is_moving')), 
           'sprinting': (molang('query.is_sprinting')), 
           'swim': (molang('query.is_swimming')), 
           'Lclick': (molang('variable.attack_time')),
            'using': (molang('query.is_using_item')),
            'ground': (molang('query.is_on_ground')),
            "inlava": (molang('query.is_in_lava')),
            "onfire": (molang('query.is_on_fire')),
            "breath": (molang('query.is_breathing')),
            "isclimbing": (molang('query.is_wall_climbing')),
            "hascollision":(molang('query.has_collision')),
            "is_levitating":(molang('query.is_levitating')),
            "is_gliding":(molang('query.is_gliding')),
            "is_in_water_or_rain":(molang('query.is_in_water_or_rain')),}#query.is_levitating
        left, forward = cr.ActorMotion(Id).GetInputVector()
        input_vec = {'forward': False, 'back': False, 'left': False, 'right': False}
        if forward != 0:
            input_vec['forward' if forward > 0 else 'back'] = True
        if left != 0:
            input_vec['left' if left > 0 else 'right'] = True
        input_vec_ = None if input_vec == self.input_vec else input_vec
        self.input_vec = input_vec
        now = time()
        for tim in self.left_click_time_set.copy():
            if now - tim >= 1:
                self.left_click_time_set.discard(tim)

        for tim in self.right_click_time_set.copy():
            if now - tim >= 1:
                self.right_click_time_set.discard(tim)

        comp = cr.Game(levelId)
        self.NotifyToServer('PlayerTickEvent', {'movements': movements, 
           'fps': (round(comp.GetFps())), 
           'inputVec': input_vec_, 
           'Lcps': (len(self.left_click_time_set)), 
           'Rcps': (len(self.right_click_time_set))})
        return

    def Second(self):
        comp = cr.PlayerView(Id)
        cmd = comp.GetToggleOption
        options = {'auto_jump': (cmd('AUTO_JUMP')), 
           'hide_paperdoll': (cmd('HIDE_PAPERDOLL')), 
           'hide_hand': (cmd('HIDE_HAND')), 
           'split_controls': (cmd('SPLIT_CONTROLS')), 
           'view_bobbing': (cmd('VIEW_BOBBING')), 
           'tradition_controls': (cmd('TRADITION_CONTROLS')), 
           'hide_hud': (cmd('HIDE_HUD')), 
           'camera_shake': (cmd('CAMERA_SHAKE')), 
           'transparentleaves': (cmd('TRANSPARENTLEAVES')), 
           'fancy_skies': (cmd('FANCY_SKIES')), 
           'smooth_lighting': (cmd('SMOOTH_LIGHTING')), 
           'graphics': (cmd('GRAPHICS')), 
           'render_clouds': (cmd('RENDER_CLOUDS')), 
           'input_mode': (cmd('INPUT_MODE')), 
           'UI_profile': (cr.PlayerView(Id).GetUIProfile())}
        changed_options = {k: v for k, v in options.items() if v != self.options.get(k)}
        old_options = {k: self.options.get(k) for k, v in changed_options.items()}
        self.options = options
        self.NotifyToServer('PlayerSecondEvent', {'options': {'changed': changed_options, 'old': old_options}, 
           'pong': (time()), 
           'ping': (self.ping)})

    @Listen
    def OnLocalPlayerStopLoading(self, args):
        self.NotifyToServer('OnLocalPlayerStopLoading', {'platform': (capi.GetPlatform())})

    @Listen
    def PerspChangeClientEvent(self, args):
        self.NotifyToServer('OnPlayerChangeViewmodeEvent', args)

    @Listen
    def OnItemSlotButtonClickedEvent(self, args):
        self.NotifyToServer('OnItemSlotButtonClickedEvent', args)
    

    def OnPlayerRightClick(self, args):
        self.NotifyToServer('OnPlayerRightClickEvent', {'isClick': True})
        self.NotifyToServer('right_click_release', {'isClick': False})
        self.right_click_time_set.add(time())

    def OnPlayerReleaseRightClick(self, args):
        self.NotifyToServer('OnPlayerRightClickEvent', {'isClick': False})
        self.NotifyToServer('right_click_before', {'isClick': False})

    def OnPlayerLeftClick(self, args):
        self.NotifyToServer('OnPlayerLeftClickEvent', {'isClick': True})
        self.NotifyToServer('left_click_before', {'isClick': False})
        self.left_click_time_set.add(time())

    def OnPlayerReleaseLeftClick(self, args):
        self.NotifyToServer('OnPlayerLeftClickEvent', {'isClick': False})
        self.NotifyToServer('left_click_release', {'isClick': False})

#  self.ListenEngineEvent('LeftClickBeforeClientEvent', self.OnPlayerLeftClick)
#self.ListenEngineEvent('LeftClickReleaseClientEvent', self.OnPlayerReleaseLeftClick

    @Listen(NAMESPACE, SERVER_SYSTEM_NAME)
    def PongEvent(self, args):
        self.ping = time() - args['pong']

# okay decompiling D:/MCStudioDownload/work/z13416661916@163.com/Cpp/AddOn/113139c5d51142aeb8b5d6b9fc65e155/behavior_pack_QVpTfSxL/VTScripts/VTScripts\VTClient.pyc
