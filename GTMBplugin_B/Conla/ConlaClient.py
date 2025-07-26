# -*- coding: utf-8 -*-

import __future__
from time import time
import mod.client.extraClientApi as Capi
from api.CompFactory import ClientCompFactory as cr
from api import *
from api.getapi import *
from config import *
levelId = Capi.GetLevelId()
Id = Capi.GetLocalPlayerId()
comp = cr.Game(levelId)
com = Capi.GetEngineCompFactory().CreatePlayer(Id)
ClientSystem = Capi.GetClientSystemCls()

class ConlaClientSystem(ClientSystem):
    def __init__(self, namespace, systemName):
        print "ConlaClientSystem init"
        super(ConlaClientSystem, self).__init__(namespace, systemName)
        InitFastListen(self)
        self.ListenEvent()
        comp = cr.Game(levelId)
        comp.AddRepeatedTimer(0.05, self.Tick)
        comp.AddRepeatedTimer(1, self.Second)
        self.options = {}
        self.ping = 0
        self.input_vec = {}
        self.left_click_time_set = set()
        self.tick_tps = 0
        self.right_click_time_set = set()
        
    
    def ListenEvent(self):
        self.ListenEngineEvent = lambda eventName, callbackFunc: self.ListenForEvent(Capi.GetEngineNamespace(), Capi.GetEngineSystemName(), eventName, self, callbackFunc)
        self.ListenServerEvent = lambda eventName, callbackFunc: self.ListenForEvent('ConlaCheck', 'ConlaServer', eventName, self, callbackFunc)
        self.ListenEngineEvent('HoldBeforeClientEvent',self.OnPlayerRightClick)
        self.ListenEngineEvent('RightClickBeforeClientEvent',self.OnPlayerRightClick)
        self.ListenEngineEvent('RightClickReleaseClientEvent',self.OnPlayerReleaseRightClick)
        self.ListenEngineEvent('TapOrHoldReleaseClientEvent', self.OnPlayerReleaseRightClick)
        self.ListenEngineEvent('TapOrHoldReleaseClientEvent', self.OnPlayerReleaseLeftClick)
        self.ListenEngineEvent('LeftClickBeforeClientEvent', self.OnPlayerLeftClick)
        self.ListenEngineEvent('LeftClickReleaseClientEvent', self.OnPlayerReleaseLeftClick)
        self.ListenEngineEvent('GetEntityByCoordEvent', self.OnPlayerLeftClick)
        self.ListenEngineEvent('GetEntityByCoordReleaseClientEvent', self.OnPlayerReleaseLeftClick)

    def Tick(self):
        global comp
        self.tick_tps+=1
        if self.tick_tps>=20:
            self.NotifyToServer("clienttps_finished",{"Id":Id})
        compM = cr.QueryVariable(Id)
        molang = lambda molangName: False if compM.GetMolangValue(molangName) == 0.0 else True
        register_move = {'jump': (molang('query.is_jumping')), 
           'sneak': (molang('query.is_sneaking')), 
           'moving': (molang('query.is_moving')), 
           'sprinting': (molang('query.is_sprinting')), 
           'swim': (molang('query.is_swimming')), 
           'swing': (molang('variable.attack_time')),
            'using': (molang('query.is_using_item')),
            'ground': (molang('query.is_on_ground')),
            "inlava": (molang('query.is_in_lava')),
            "onfire": (molang('query.is_on_fire')),
            "breath": (molang('query.is_breathing')),
            "isclimbing": (molang('query.is_wall_climbing')),
            "hascollision":(molang('query.has_collision')),
            "is_levitating":(molang('query.is_levitating')),
            "is_gliding":(molang('query.is_gliding')),
            "is_in_water_or_rain":(molang('query.is_in_water_or_rain')),}
        now = time()
        for tim in self.left_click_time_set.copy():
            if now - tim >= 1:
                self.left_click_time_set.discard(tim)

        for tim in self.right_click_time_set.copy():
            if now - tim >= 1:
                self.right_click_time_set.discard(tim)
        if com.IsOnLadder():
            self.NotifyToServer('IsOnLadder',{"Id":Id})
        else:
            self.NotifyToServer('IsNotOnLadder',{"Id":Id})
        if com.IsInScaffolding():
            self.NotifyToServer('IsInScaffolding',{"Id":Id})
        else:
            self.NotifyToServer('IsNotInScaffolding',{"Id":Id})
        self.NotifyToServer('PlayerTickEvent', {
           'fps': (round(comp.GetFps())), 
           'Lcps': (len(self.left_click_time_set)), 
           'Rcps': (len(self.right_click_time_set)),
           "register": register_move})
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
        
    # 被引擎直接执行的父类的重写函数，引擎会执行该Update回调，1秒钟30帧
    def Update(self):
        """
        Driven by system manager, Two tick way
        """
        pass

    def Destroy(self):
        self.UnListenAllEvents()

    def OnPlayerRightClick(self, args):
        self.NotifyToServer('right_click_release', {'isClick': False})
        self.right_click_time_set.add(time())
        print("test4")

    def OnPlayerReleaseRightClick(self, args):
        self.NotifyToServer('right_click_before', {'isClick': False})
        print("test3")

    def OnPlayerLeftClick(self, args):
        self.NotifyToServer('left_click_before', {'isClick': False})
        self.left_click_time_set.add(time())
        print("test2")

    def OnPlayerReleaseLeftClick(self, args):
        self.NotifyToServer('left_click_release', {'isClick': False})
        print("test1")
    
    @Listen
    def OnLocalPlayerStopLoading(self, args):
        self.NotifyToServer('OnLocalPlayerStopLoading', {'platform': (Capi.GetPlatform())})

    @Listen#欢迎语
    def LoadClientAddonScriptsAfter(self,args):
        comp = Capi.GetEngineCompFactory().CreateGame(levelId)
        comp.SetTipMessage("§a欢迎使用ConlaCheck(更多检测)!")
    @Listen
    def ClientChestOpenEvent(self,args):
        self.NotifyToServer('ClientChestOpenEvent', {'playerId': args['playerId']})
    @Listen
    def ClientChestCloseEvent(self,args):
        self.NotifyToServer('ClientChestCloseEvent',{"playerId": Id})