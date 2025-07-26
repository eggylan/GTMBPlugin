# -*- coding: utf-8 -*-
import __future__, mod.server.extraServerApi as serverApi
from time import localtime
from api.CompFactory import ServerCompFactory as cr
from api import *
from api.getapi import *
from api.ServerFuncs import *
from config import *
from api.some import * #感谢Eggylan团队
ServerSystem = serverApi.GetServerSystemCls()
com = serverApi.GetEngineCompFactory().CreatePlayer(Id)
class ConlaServerSystem(ServerSystem):
    def __init__(self, namespace, systemName):
        super(ServerSystem,self).__init__(namespace, systemName)
        #super(VTServerSys, self).__init__(namespace, name)
        InitFastListen(self)
        cr.Item(levelId).GetUserDataInEvent('ServerPlayerTryTouchEvent')
        comp = cr.Game(levelId)
        comp.AddRepeatedTimer(0.05, self.Tick)
        comp.AddRepeatedTimer(1, self.Second)
        self.tps=0
        print "ConlaServerSystem init"
        setExData('ConlaCheck', True)

    def ListenEvent(self):
        self.ListenForEvent(NAMESPACE, CLIENT_SYSTEM_NAME, 'right_click_release', self, self.right_click_release_server)

    # OnScriptTickServer的回调函数，会在引擎tick的时候调用，1秒30帧（被调用30次）
    def OnTickServer(self):
        """
        Driven by event, One tick way
        """
        pass

    # 这个Update函数是基类的方法，同样会在引擎tick的时候被调用，1秒30帧（被调用30次）
    def Update(self):
        """
        Driven by system manager, Two tick way
        """
        pass
    def Tick(self):
        pass

    def Second(self):
        pass

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

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def PlayerTickEvent(self, args):
        Id = args['__id__']
        
        compitem = cr.Item(Id)
        map((lambda x: modifyTag(x, args['register'][x], Id)), args['register'].keys())
        comdp = serverApi.GetEngineCompFactory().CreateBulletAttributes(Id)
        addTag("isSource",comdp.GetSourceEntityId())
        toScore('fps', args['fps'], Id)
        toScore('Lcps', args['Lcps'], Id)
        toScore('Rcps', args['Rcps'], Id)#CPS skidded
        selected_slot = compitem.GetSelectSlotId()
        comp = serverApi.GetEngineCompFactory().CreateCommand(Id)
        comp.SetCommand("tag @a remove forward")
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
        comp.SetCommand("tag @a add is_Player")
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
        self.tps+=1 
        comp = sapi.GetEngineCompFactory().CreatePlayer(Id)
        if(comp.GetIsBlocking()):
            addTag('isBlocking',Id)
        else:
            removeTag('isBlocking', Id)           #DEOBF??????????????????????????????
        comp = sapi.GetEngineCompFactory().CreateFly(Id)
        if(comp.IsPlayerFlying()):
            addTag('isFlying', Id)
        else:
            removeTag('isFlying', Id)#我自己拓展的。
        __co2mp = sapi.GetEngineCompFactory().CreateGravity(Id)
        JumpPower = int(__co2mp.GetJumpPower()*10)
        #打滑vt
        pos = cr.Pos(Id).GetFootPos()
        rot = cr.Rot(Id).GetRot()
        compattr = cr.Attr(Id)
        compplayer = cr.Player(Id)
        respawn_pos = compplayer.GetPlayerRespawnPos()['pos']
        vX, vY, vZ = cr.ActorMotion(Id).GetMotion()
        vX, vY, vZ = round(vX, 3), round(vY, 3), round(vZ, 3)
        if vY == -0.078:
            vY = 0
        import math
        allrot=int(math.sqrt(round((rot[0] ** 2 + rot[1] ** 2))))
        allxyz=int(math.sqrt(round((pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2))))
        velocity = int(round((vX ** 2 + vY ** 2 + vZ ** 2) ** 0.5, 3) * 1000)
        velocityX= int(round(vX, 3) * 1000)
        velocityY = int(round(vY, 3) * 1000)
        velocityZ = int(round(vZ, 3) * 1000)
        #以下为自写
        toScore("posx",pos[0],Id)#计分板为posx
        toScore("posy",pos[1],Id)#计分板为posy
        toScore("posz",pos[2],Id)#计分板为posz
        toScore("rotx",rot[0],Id)#计分板为rotx
        toScore("roty",rot[1],Id)#计分板为roty
        #Velocity
        toScore("velocity",velocity,Id)#计分板为velocity
        toScore("velocityX",velocityX,Id)#计分板为velocityX
        toScore("velocityY",velocityY,Id)#计分板为velocityY
        toScore("velocityZ",velocityZ,Id)#计分板为velocityZ
        #Compattr
        toScore('hunger', compattr.GetAttrValue(4), Id) #Skid From VtTest
        toScore('saturation', compattr.GetAttrValue(5), Id) #Skid From VtTest
        toScore('absorption', compattr.GetAttrValue(6), Id) #Skid From VtTest
        toScore('armor', compattr.GetAttrValue(12), Id) #Skid From VtTest
        #repos
        toScore('selected_slot', selected_slot, Id)
        toScore('respawnPosX', respawn_pos[0], Id)
        toScore('respawnPosY', respawn_pos[1], Id)
        toScore('respawnPosZ', respawn_pos[2], Id)
        modifyTag('on_fire', compattr.IsEntityOnFire(), Id)
        toScore('permisson', compplayer.GetPlayerOperation(), Id)#权限。
        toScore('fall_distance', cr.EntityDefinitions(Id).GetEntityFallDistance(), Id)#摔落的速度
        toScore("allxyz",allxyz,Id)
        toScore("allrot",allrot,Id)
        #以下是我自己写的tag
        removeTag('add_exp', Id)
        removeTag('add_level',Id)
        removeTag('hungerChange',Id)
        removeTag('Interact',Id)
        removeTag('FakeInteract',Id)
        removeTag("breaked", Id)
        removeTag("perspChange",Id)
        removeTag('attack', Id)
        removeTag('gameTypeChange',Id)
        removeTag('trySleep', Id)
        removeTag("teleport",Id)
        removeTag('action', Id)
        removeTag('climbing', Id)
        removeTag('chat',Id)
        removeTag('TryplaceBlock',Id)
        removeTag('placed',Id)
        removeTag('hurt',Id)
        removeTag("knockback",Id)
        removeTag('chestclosed', Id)
        removeTag('chestopen', Id)
        removeTag('entityId',Id)
        removeTag("isSource",Id)
        toScore('Jumppower', JumpPower, Id)

#以上的计分板共有:posx, posy, posz, rotx, roty, velocity, velocityX, velocityY, velocityZ, hunger, saturation, absorption, armor, selected_slot, respawnPosX, respawnPosY, respawnPosZ
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def PlayerSecondEvent(self, args):
        Id = args['__id__']
        if args['options']:
            for name, value in args['options']['old'].items():
                removeTag('option.%s.%s' % (name, value), Id)

            for name, value in args['options']['changed'].items():
                addTag('option.%s.%s' % (name, value), Id)
#平方根math:sqrt
    @Listen
    def PlayerRespawnFinishServerEvent(self, args):
        Id = args['playerId']
        comp = cr.Attr(Id)
        health = comp.GetAttrValue(0)
        health_max = comp.GetAttrMaxValue(0)
        toScore('health', health, Id)
        toScore('health_max', health_max, Id)
    @Listen
    def clienttps_finished(self,args):
        toscore("tps","tps",self.tps)
        self.tps=0
        #重置操作
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
    def PlayerInteractServerEvent(self,args):
        addTag("FakeInteract",args['playerId'])

    def Destroy(self):
        self.UnListenAllEvents()
        cleanExData('ConlaCheck')
    #THis;
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnPlayerRightClickEvent(self, args):
        modifyTag('using', args['isClick'], args['__id__'])

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnPlayerLeftClickEvent(self, args):
        modifyTag('swing', args['isClick'], args['__id__'])

    @Listen 
    def OnKnockBackServerEvent(self,args):
        addTag("knockback",args['id'])

    @Listen
    def AddExpEvent(self,args):
        addTag("add_exp",args['id'])
    @Listen
    def AddLevelEvent(self,args):
        addTag("add_level",args['id'])
    @Listen
    def PlayerDoInteractServerEvent(self,args):
        addTag("Interact",args['id'])
#?????
    def right_click_release_server(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s add right_click")#传送指令

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def right_click_before(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s remove right_click")#传送指令

    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def left_click_release(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s add left_click")#传送指令
        
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def left_click_before(self, args):
        comp = sapi.GetEngineCompFactory().CreateCommand(levelId)
        comp.SetCommand("/tag @s remove left_click")#传送指令
#?????    
    #这么强?
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
    @Listen(NAMESPACE, CLIENT_SYSTEM_NAME)
    def OnLocalPlayerStopLoading(self, args):
        Id = args['__id__']
        setExData('vthelp', False, Id)
        removeTag('PC', Id)
        removeTag('PE', Id)
        addTag(('PE', 'PC')[args['platform'] == 0], Id)
        comp = cr.Attr(Id)
        toScore('health', comp.GetAttrValue(0), Id)
        toScore('health_max', comp.GetAttrMaxValue(0), Id)#Skid from VT
    @Listen
    def DestroyBlockEvent(self, args):
        Id = args['playerId']
        toScore('destroyPosX', args['x'], Id)
        toScore('destroyPosY', args['y'], Id)
        toScore('destroyPosZ', args['z'], Id)
        tag = 'destroy.%s.%s.%s' % (args['fullName'].replace('minecraft:', ''), args['auxData'], args['face'])
        removeTag(getExData('lastDestTag', Id), Id)
        addTag(tag, Id)
        addTag("breaked", Id)#为什么没有BreakING?!
        setExData('lastDestTag', tag, Id)#我认为只是检测的话是不对的，所以我多写了Breaked
    @Listen
    def EntityStartRidingEvent(self, args):
        addTag('ride', args['id'])

    @Listen
    def EntityStopRidingEvent(self, args):
        removeTag('ride', args['id'])
    @Listen
    def PlayerHungerChangeServerEvent(self,args):
        addTag('hungerChange', args['playerId'])

    @Listen
    def PlayerSleepServerEvent(self, args):
        addTag('sleep', args['playerId'])

    @Listen
    def PlayerStopSleepServerEvent(self, args):
        removeTag('sleep', args['playerId'])
    @Listen
    def PerspChangeClientEvent(self,args):
        addTag('perspChange', args['playerId'])
    @Listen
    def PlayerAttackEntityEvent(self,args):
        addTag('attack', args['playerId'])
    @Listen 
    def GameTypeChangedServerEvent(self,args):
        addTag('gameTypeChange', args['playerId'])
    @Listen
    def PlayerTrySleepServerEvent(self,args):
        addTag('trySleep', args['playerId'])
    @Listen
    def PlayerTeleportEvent(self,args):
        addTag('teleport', args['Id'])
    @Listen
    def OnPlayerActionServerEvent(self,args):
        addTag('action', args['playerId'])
        if args['actionType'] == serverApi.GetMinecraftEnum().PlayerActionType.StartCrawling:
            addTag('climbing', args['playerId'])
    @Listen
    def ServerChatEvent(self, args):
        addTag('chat', args['playerId'])
        toScore("chat_speed",1, args['playerId'],True)
    @Listen
    def ServerEntityTryPlaceBlockEvent(self,args):
        addTag('TryplaceBlock', args['entityId'])
#UseAnimation
    @Listen
    def ActorHurtServerEvent(self,args):
        addTag('hurt', args['entityId'])
        toscore("damage_value",args['entityId'], int(round(args['damage'])))

    @Listen
    def EntityRemoveEvent(self, args):
        cr.remove(args['id'])
    @Listen
    def EntityPlaceBlockAfterServerEvent(self,args):
        addTag('placed', args['entityId'])
    @Listen(NAMESPACE,CLIENT_SYSTEM_NAME)
    def ClientChestCloseEvent(self,args):
        addTag('chestclosed',  args['playerId'])
        removeTag('hasGUIopen', args['playerId'])
    @Listen(NAMESPACE,CLIENT_SYSTEM_NAME)
    def ClientChestOpenEvent(self,args):
        addTag('chestopen', args['playerId'])
        addTag('hasGUIopen', args['playerId'])
    @Listen
    def EntityDroppedItemServerEvent(self,args):
        addTag('dropitem', args['entityId'])