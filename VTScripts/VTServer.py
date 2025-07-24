# uncompyle6 version 3.9.2
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: VTScripts/VTServer.py
import __future__, mod.server.extraServerApi as sapi
from time import localtime
from .utils.CompFactory import ServerCompFactory as cr
from utils import *
from utils.FastListen import *
from utils.ServerFuncs import *
from config import *

class VTServerSys(sapi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(VTServerSys, self).__init__(namespace, name)
        InitFastListen(self)
        cr.Item(levelId).GetUserDataInEvent('ServerPlayerTryTouchEvent')
        comp = cr.Game(levelId)
        comp.AddRepeatedTimer(0.05, self.Tick)
        comp.AddRepeatedTimer(1, self.Second)
        self.tps=0
        setExData('VanillaTest', True)

    def Destroy(self):
        self.UnListenAllEvents()
        cleanExData('VanillaTest')

    def Tick(self):
        toScoreVirtual('daytime', cr.Time(levelId).GetTime() % 24000, 'value')
        compweather = cr.Weather(levelId)
        toScoreVirtual('weather', (2 if compweather.IsThunder() else 1) if compweather.IsRaining() else 0, 'value')

    def Second(self):
        t = localtime()
        toScoreVirtual('local_time', t.tm_year, 'year')
        toScoreVirtual('local_time', t.tm_mon, 'month')
        toScoreVirtual('local_time', t.tm_mday, 'day')
        toScoreVirtual('local_time', t.tm_hour, 'hour')
        toScoreVirtual('local_time', t.tm_min, 'minute')
        toScoreVirtual('local_time', t.tm_sec, 'second')
   
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def PlayerTickEvent(self, args):
        Id = args['__id__']
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        #Command(精度是小的)
        
        comp.SetCommand("tag @a remove forward")#传送指令
        comp.SetCommand("tag @a remove backward")#传送指令
        comp.SetCommand("tag @a remove leftward")#传送指令
        comp.SetCommand("tag @a remove rightward")
        comp.SetCommand("tag @a remove upward")#传送指令
        comp.SetCommand("tag @a remove downward")
        comp.SetCommand("tag @a remove is_inground")
        comp.SetCommand("tag @a remove is_onground")
        comp.SetCommand("tag @a remove is_inair")
        comp.SetCommand("tag @a remove is_onair")#
        comp.SetCommand("tag @a remove is_swim")
        comp.SetCommand("tag @a remove is_sitting")
        comp.SetCommand("tag @a remove is_starding")
        comp.SetCommand("execute as @a at @s anchored feet rotated ~ 0 positioned ^^^30.001 if entity @s[r=30] run tag @s add forward")#传送指令
        comp.SetCommand("execute as @a at @s anchored feet rotated ~ 0 positioned ^^^-30.001 if entity @s[r=30] run tag @s add backward")
        comp.SetCommand("execute as @a at @s anchored feet rotated ~ 0 positioned ^30.001^^ if entity @s[r=30] run tag @s add leftward")
        comp.SetCommand("execute as @a at @s anchored feet rotated ~ 0 positioned ^-30.001^^ if entity @s[r=30] run tag @s add rightward")
        comp.SetCommand("execute as @a at @s anchored feet rotated ~ 0 positioned ^^30.001^ if entity @s[r=30] run tag @s add upward")
        comp.SetCommand("execute as @a at @s anchored feet rotated ~ 0 positioned ^^-30.001^ if entity @s[r=30] run tag @s add downward")
        comp.SetCommand("execute as @a at @s unless block ~~~ air run tag @s add is_inground")
        comp.SetCommand("execute as @a at @s unless block ~~-1~ air run tag @s add is_onground")
        comp.SetCommand("execute as @a at @s if block ~~~ air run tag @s add is_inair")
        comp.SetCommand("execute as @a at @s if block ~~-1~ air run tag @s add is_onair")
        comp.SetCommand("execute as @a at @s if entity @s[x=~,y=~1.4,z=~,dx=0,dy=0,dz=0] run tag @s add is_starding")
        comp.SetCommand("execute as @a at @s if entity @s[x=~,y=~1.4,z=~,dx=0,dy=0,dz=0] unless entity @s[x=~,y=~1.7,z=~,dx=0,dy=0,dz=0] run tag @s add is_sitting")
        comp.SetCommand("execute as @a at @s unless entity @s[x=~,y=~1.4,z=~,dx=0,dy=0,dz=0] run tag @s add is_swim")
        #end;
        self.tps+=1 
        if(self.tps>=20):
            toScoreVirtual('tps', self.tps, 'tps')
            self.tps=0
        comp = sapi.GetEngineCompFactory().CreatePlayer(Id)
        if(comp.GetIsBlocking()):
            addTag('isBlocking',Id)
        else:
            removeTag('isBlocking', Id)
        comp = sapi.GetEngineCompFactory().CreateFly(Id)
        if(comp.IsPlayerFlying()):
            addTag('isFlying', Id)
        else:
            removeTag('isFlying', Id)


        map((lambda x: modifyTag(x, args['movements'][x], Id)), args['movements'].keys())
        toScore('fps', args['fps'], Id)
        toScore('Lcps', args['Lcps'], Id)
        toScore('Rcps', args['Rcps'], Id)
        input_vec = args['inputVec']
        if input_vec:
            for name, mode in input_vec.items():
                modifyTag('input.%s' % name, mode, Id)

        if getExData('onPickUpList', Id) is None:
            setExData('onPickUpList', [], Id)
        on_pick_up_list = getExData('onPickUpList', Id)
        if on_pick_up_list != []:
            for tag in getTagList(Id):
                if tag[:9] == 'onPickUp.':
                    removeTag(tag, Id)

            for tag in on_pick_up_list:
                addTag(tag, Id)

            setExData('onPickUpList', [], Id)
        compitem = cr.Item(Id)
        selected_slot = compitem.GetSelectSlotId()
        itemDict = compitem.GetPlayerItem(2, 0, True)
        if itemDict is None:
            itemDict = {'durability': (-1), 'count': (-1), 'newAuxValue': (-1)}
            removeTag(getExData('lastCarriedTag', Id), Id)
        else:
            if compitem.GetCustomName(itemDict) != '':
                tag = 'carried.%s.%s' % (itemDict['newItemName'].replace('minecraft:', ''), compitem.GetCustomName(itemDict))
            else:
                tag = 'carried.%s' % itemDict['newItemName'].replace('minecraft:', '')
            removeTag(getExData('lastCarriedTag', Id), Id)
            addTag(tag, Id)
            setExData('lastCarriedTag', tag, Id)
        pos = cr.Pos(Id).GetFootPos()
        rot = cr.Rot(Id).GetRot()
        compattr = cr.Attr(Id)
        compplayer = cr.Player(Id)
        respawn_pos = compplayer.GetPlayerRespawnPos()['pos']
        vX, vY, vZ = cr.ActorMotion(Id).GetMotion()
        vX, vY, vZ = round(vX, 3), round(vY, 3), round(vZ, 3)
        if vY == -0.078:
            vY = 0
        velocity = int(round((vX ** 2 + vY ** 2 + vZ ** 2) ** 0.5, 3) * 1000)
        velocityX= int(round(vX, 3) * 1000)
        velocityY = int(round(vY, 3) * 1000)
        velocityZ = int(round(vZ, 3) * 1000)
        comp = sapi.GetEngineCompFactory().CreateGravity(Id)
        JumpPower = int(comp.GetJumpPower()*10)
        toScore('PosX', pos[0], Id)
        toScore('PosY', pos[1], Id)
        toScore('PosZ', pos[2], Id)
        toScore('RotX', rot[0], Id)
        toScore('RotY', rot[1], Id)
        toScore('hunger', compattr.GetAttrValue(4), Id)
        toScore('saturation', compattr.GetAttrValue(5), Id)
        toScore('absorption', compattr.GetAttrValue(6), Id)
        toScore('armor', compattr.GetAttrValue(12), Id)
        toScore('experience', cr.Exp(Id).GetPlayerTotalExp(), Id)
        toScore('fall_distance', cr.EntityDefinitions(Id).GetEntityFallDistance(), Id)
        toScore('selected_slot', selected_slot, Id)
        toScore('respawnPosX', respawn_pos[0], Id)
        toScore('respawnPosY', respawn_pos[1], Id)
        toScore('respawnPosZ', respawn_pos[2], Id)
        toScore('velocity', velocity, Id)
        toScore('velocityX', velocityX, Id)
        toScore('velocityY', velocityY, Id)
        toScore('velocityZ', velocityZ, Id)
        toScore('jump_power', JumpPower, Id)
        toScore('permisson', compplayer.GetPlayerOperation(), Id)
        modifyTag('on_fire', compattr.IsEntityOnFire(), Id)
        removeTag('add_exp', Id)
        removeTag('add_level',Id)
        removeTag('hungerChange',Id)
        removeTag('Interact',Id)
        removeTag('FakeInteract',Id)
        return
    @Listen 
    def PlayerInteractServerEvent(self,args):
        addTag("FakeInteract",args['playerId'])
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def PlayerSecondEvent(self, args):
        Id = args['__id__']
        if args['options']:
            for name, value in args['options']['old'].items():
                removeTag('option.%s.%s' % (name, value), Id)

            for name, value in args['options']['changed'].items():
                addTag('option.%s.%s' % (name, value), Id)

        self.NotifyToClient(Id, 'PongEvent', {'pong': (args['pong'])})
        toScore('ping_check', args['ping'] * 1000, Id)
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def IsOnLadder(self,args):
        addTag('isOnLadder',args["Id"])
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def IsNotOnLadder(self,args):
        removeTag('isOnLadder',args["Id"])
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def IsInScaffolding(self,args):
        addTag('isInScaffolding',args["Id"])
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def IsNotInScaffolding(self,args):
        removeTag('isInScaffolding',args["Id"])
    @Listen
    def AddEntityServerEvent(self, args):
        Id = args['id']
        if args['engineTypeStr'].replace('minecraft:', '') in ('allay', 'armor_stand',
                                                               'axolotl', 'bat',
                                                               'bee', 'blaze', 'cat',
                                                               'cave_spider', 'chicken',
                                                               'cow', 'creeper',
                                                               'dolphin', 'donkey',
                                                               'drowned', 'elder_guardian',
                                                               'ender_dragon', 'enderman',
                                                               'endermite', 'evoker',
                                                               'fox', 'frog', 'ghast',
                                                               'glow_squid', 'guardian',
                                                               'hoglin', 'horse',
                                                               'husk', 'iron_golem',
                                                               'llama', 'magma_cube',
                                                               'mooshroom', 'mule',
                                                               'npc', 'ocelot', 'panda',
                                                               'parrot', 'phantom',
                                                               'pig', 'pillager',
                                                               'polar_bear', 'rabbit',
                                                               'ravager', 'sheep',
                                                               'shulker', 'silverfish',
                                                               'skeleton', 'skeleton_horse',
                                                               'slime', 'snow_golem',
                                                               'spider', 'squid',
                                                               'stray', 'strider',
                                                               'tadpole', 'trader_llama',
                                                               'tripod_camera', 'turtle',
                                                               'vex', 'villager',
                                                               'vindicator', 'wandering_trader',
                                                               'warden', 'witch',
                                                               'wither', 'wither_skeleton',
                                                               'wolf', 'zoglin',
                                                               'zombie', 'zombie_horse',
                                                               'zombie_pigman', 'zombie_villager'):
            comp_attr = cr.Attr(Id)
            toScoreEntity('health', comp_attr.GetAttrValue(0), Id)
            toScoreEntity('health_max', comp_attr.GetAttrMaxValue(0), Id)

    @Listen
    def PlayerRespawnFinishServerEvent(self, args):
        Id = args['playerId']
        comp = cr.Attr(Id)
        health = comp.GetAttrValue(0)
        health_max = comp.GetAttrMaxValue(0)
        toScore('health', health, Id)
        toScore('health_max', health_max, Id)

    @Listen
    def HealthChangeServerEvent(self, args):
        Id = args['entityId']
        health = args['to']
        if health < 0:
            health = 0
        health_max = cr.Attr(Id).GetAttrMaxValue(0)
        entity_type = getEntityType(Id)
        if entity_type == 'minecraft:player':
            toScore('health', health, Id)
            toScore('health_max', health_max, Id)
        else:
            toScoreEntity('health', health, Id)
            toScoreEntity('health_max', health_max, Id)

    @Listen
    def ActuallyHurtServerEvent(self, args):
        Id = args['entityId']
        source = args['srcId']
        entity_type = getEntityType(Id)
        if entity_type == 'minecraft:player':
            toScore('damage_taken', args['damage'], Id)
            toScore('on_damage', 1, Id, True)
        else:
            toScoreEntity('damage_taken', args['damage'], Id)
            toScoreEntity('on_damage', 1, Id, True)
        entity_type = getEntityType(source)
        if entity_type == 'minecraft:player':
            toScore('hit', 1, source, True)
        else:
            toScoreEntity('hit', 1, source, True)

    @Listen
    def PlayerHungerChangeServerEvent(self,args):
        addTag('hungerChange', args['Id'])

    @Listen
    def PlayerSleepServerEvent(self, args):
        addTag('sleep', args['playerId'])

    @Listen
    def PlayerStopSleepServerEvent(self, args):
        removeTag('sleep', args['playerId'])
    #Command to for/back/left/right/ward
    @Listen
    def ServerPlayerTryTouchEvent(self, args):
        Id = args['playerId']
        item_name = str(args['itemDict']['newItemName']).replace('minecraft:', '')
        aux_value = args['itemDict']['newAuxValue']
        durability = args['itemDict']['durability']
        count = args['itemDict']['count']
        item_custom_name = cr.Item(Id).GetCustomName(args['itemDict'])
        if item_custom_name != '' and durability == 0:
            tag = 'onPickUp.%s.%s.%s.%s' % (item_name, count, aux_value, item_custom_name)
        if item_custom_name != '' and durability != 0:
            tag = 'onPickUp.%s.%s.%s.%s' % (item_name, count, durability, item_custom_name)
        if item_custom_name == '' and durability == 0:
            tag = 'onPickUp.%s.%s.%s' % (item_name, count, aux_value)
        if item_custom_name == '' and durability != 0:
            tag = 'onPickUp.%s.%s.%s' % (item_name, count, durability)
        setExData('onPickUpList', getExData('onPickUpList', Id) + [tag], Id)

    @Listen
    def MobDieEvent(self, args):
        killer = args['attacker']
        entity_type = getEntityType(killer)
        if entity_type == 'minecraft:player':
            toScore('mobkillcount', 1, killer, True)
        else:
            toScoreEntity('mobkillcount', 1, killer, True)

    @Listen
    def PlayerDieEvent(self, args):
        killer = args['attacker']
        entity_type = getEntityType(killer)
        if entity_type == 'minecraft:player':
            toScore('killcount', 1, killer, True)
        else:
            toScoreEntity('killcount', 1, killer, True)

    @Listen
    def AddEffectServerEvent(self, args):
        Id = args['entityId']
        addTag('effect.%s' % args['effectName'], Id)

    @Listen
    def RemoveEffectServerEvent(self, args):
        Id = args['entityId']
        removeTag('effect.%s' % args['effectName'], Id)

    @Listen
    def EntityStartRidingEvent(self, args):
        addTag('ride', args['id'])

    @Listen
    def EntityStopRidingEvent(self, args):
        removeTag('ride', args['id'])

    @Listen
    def AddLevelEvent(self, args):
        toScore('level', args['newLevel'], args['id'])

    @Listen
    def DestroyBlockEvent(self, args):
        Id = args['playerId']
        toScore('destroyPosX', args['x'], Id)
        toScore('destroyPosY', args['y'], Id)
        toScore('destroyPosZ', args['z'], Id)
        tag = 'destroy.%s.%s.%s' % (args['fullName'].replace('minecraft:', ''), args['auxData'], args['face'])
        removeTag(getExData('lastDestTag', Id), Id)
        addTag(tag, Id)
        setExData('lastDestTag', tag, Id)

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnPlayerChangeViewmodeEvent(self, args):
        toScore('view_mode', args['to'], args['__id__'])

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnItemSlotButtonClickedEvent(self, args):
        toScore('clicked_slot', args['slotIndex'], args['__id__'])

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnPlayerRightClickEvent(self, args):
        modifyTag('Rclick', args['isClick'], args['__id__'])

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnPlayerLeftClickEvent(self, args):
        modifyTag('Lclick', args['isClick'], args['__id__'])

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def right_click_release(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s add right_click")#传送指令
    @Listen
    def AddExpEvent(self,args):
        addTag("add_exp",args['id'])
    @Listen
    def AddLevelEvent(self,args):
        addTag("add_level",args['id'])
    @Listen
    def PlayerDoInteractServerEvent(self,args):
        addTag("interact",args['id'])
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def right_click_before(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s remove right_click")#传送指令


    #left
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def left_click_release(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s add left_click")#传送指令
        
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def left_click_before(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s remove left_click")#传送指令
    @Listen
    def CommandEvent(self, args):
        Id = args['entityId']
        cmd = args['command']
        from VTScripts.data import vtinit
        if cmd == '/vtinit':
            vtinit(Id, True)
            args['cancel'] = True
        elif cmd == '/vtuninst':
            vtinit(Id, False)
            args['cancel'] = True
        elif cmd == '/vthelp':
            from VTScripts.data import vthelp
            vthelp(Id)
            args['cancel'] = True
        elif cmd[:4] == '/vth':
            from VTScripts.data import vth
            if cmd == '/vth':
                vth(True, Id)
            else:
                vth(cmd.split(' ', 1)[1], Id)
            args['cancel'] = True
        elif cmd == '/UPDATE':
            self.Destroy()
            InitFastListen(self)
            args['cancel'] = True
            showMsg('Hot update updated successfully.', Id)

    @Listen
    def ServerChatEvent(self, args):
        Id = args['playerId']
        message = args['message']
        if getExData('vthelp', Id):
            from data import vth
            vth(message, Id)
            args['cancel'] = True

    @Listen
    def EntityRemoveEvent(self, args):
        cr.remove(args['id'])

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnLocalPlayerStopLoading(self, args):
        Id = args['__id__']
        setExData('vthelp', False, Id)
        removeTag('PC', Id)
        removeTag('PE', Id)
        addTag(('PE', 'PC')[args['platform'] == 0], Id)
        comp = cr.Attr(Id)
        toScore('health', comp.GetAttrValue(0), Id)
        toScore('health_max', comp.GetAttrMaxValue(0), Id)
        from VTScripts.data import update, version
        update(Id)
        showMsg('[\xe5\x8e\x9f\xe7\x89\x88\xe6\xa3\x80\xe6\xb5\x8b V%s] \xe8\xbe\x93\xe5\x85\xa5\xc2\xa7e/vthelp\xc2\xa7f\xe8\x8e\xb7\xe5\x8f\x96\xe5\xb8\xae\xe5\x8a\xa9' % version, Id)

# okay decompiling D:/MCStudioDownload/work/z13416661916@163.com/Cpp/AddOn/113139c5d51142aeb8b5d6b9fc65e155/behavior_pack_QVpTfSxL/VTScripts/VTScripts\VTServer.pyc
