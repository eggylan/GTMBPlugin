# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
import json
CFServer = serverApi.GetEngineCompFactory()
serversystem = serverApi.GetSystem("Minecraft", "preset")
CFClient = clientApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compcmd = CFServer.CreateCommand(levelId)
compGame = CFServer.CreateGame(levelId)
compItemWorld = CFServer.CreateItem(levelId)

def unicode_convert(input):
	#type: (dict|str) -> dict|list|str|bool
	if isinstance(input, dict):
		return {unicode_convert(key): unicode_convert(value) for key, value in input.iteritems()}
	elif isinstance(input, list):
		return [unicode_convert(element) for element in input]
	elif isinstance(input, unicode): # type: ignore
		output = input.encode('utf-8')
		if output == 'True':
			return True
		elif output == 'False':
			return False
		else:
			return output
	else:
		return input

def intg(num):
	#type: (float) -> int
	if num >= 0:
		return int(num)
	else:
		return int(num)-1

@registerGenericClass("customcmdsPart")
class customcmdsPart(PartBase):
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "自定义指令零件"

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		clientsystem.ListenForEvent("Minecraft", "preset", "CustomCommandClient", self, self.OnCustomCommandClient)
		PartBase.InitClient(self)

	def OnCustomCommandClient(self, args):
		if args['cmd'] == 'setplayerinteracterange':
			clientApi.GetEngineCompFactory().CreatePlayer(args['target']).SetPickRange(args['cmdargs'][1])
			return
		if args['cmd'] == 'hideairsupplygui':
			clientApi.HideAirSupplyGUI(args['cmdargs'][1])
			return
		if args['cmd'] == 'hidearmorgui':
			clientApi.HideArmorGui(args['cmdargs'][1])
			return
		if args['cmd'] == 'hidecrosshairgui':
			clientApi.HideCrossHairGUI(args['cmdargs'][1])
			return
		if args['cmd'] == 'hideexpgui':
			clientApi.HideExpGui(args['cmdargs'][1])
			return
		if args['cmd'] == 'hidefoldgui':
			clientApi.HideFoldGUI(args['cmdargs'][1])
			return
		if args['cmd'] == 'hidehealthgui':
			clientApi.HideHealthGui(args['cmdargs'][1])
			return
		if args['cmd'] == 'hidehorsehealthgui':
			clientApi.HideHorseHealthGui(args['cmdargs'][1])
			return
		if args['cmd'] == 'hidehudgui':
			clientApi.HideHudGUI(args['cmdargs'][1])
			return
		if args['cmd'] == 'hidehungergui':
			clientApi.HideHungerGui(args['cmdargs'][1])
			return
		if args['cmd'] == 'hideslotbargui':
			clientApi.HideSlotBarGui(args['cmdargs'][1])
			return
		if args['cmd'] == 'openfoldgui':
			clientApi.OpenFoldGui()
			return
		
		# clientsystem.NotifyToServer("customCmdReturn", data)

	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "CustomCommandTriggerServerEvent", self, self.OnCustomCommand)
		serversystem.ListenForEvent("Minecraft", "preset", "customCmdReturn", self, self.OnReturn)
		PartBase.InitServer(self)

	def OnReturn(self, args):
		compMsg = CFServer.CreateMsg(args['target'])
		compName = CFServer.CreateName(args['__id__'])

	def OnCustomCommand(self, args):
		command = args['command']
		cmdargs = []
		for i in args["args"]:
			cmdargs.append(i["value"])

		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None
		
		if command == 'setentityonfire':
			for i in cmdargs[0]:
				CFServer.CreateAttr(i).SetEntityOnFire(cmdargs[1],cmdargs[2])
			args['return_msg_key'] = '成功设置实体着火'
			return
		
		if command == 'setplayerrespawnpos':
			x, y, z = cmdargs[1]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置重生点'
					return
				CFServer.CreatePlayer(i).SetPlayerRespawnPos((x,y,z),cmdargs[2])
			args['return_msg_key'] = '成功设置玩家重生点'
			return
		
		if command == 'setplayerhealthlevel':
			if cmdargs[1] < 0 or cmdargs[1] > 20:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的回血临界值'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置回血临界值'
					return
				CFServer.CreatePlayer(i).SetPlayerHealthLevel(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家回血临界值'
			return
		
		if command == 'setplayerstarvelevel':
			if cmdargs[1] < 0 or cmdargs[1] > 20:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的扣血临界值'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置扣血临界值'
					return
				CFServer.CreatePlayer(i).SetPlayerStarveLevel(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家扣血临界值'
			return
		
		if command == 'setplayerhunger':
			if cmdargs[1] < 0 or cmdargs[1] > 20:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的饥饿度'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置饥饿度'
					return
				CFServer.CreatePlayer(i).SetPlayerHunger(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家饥饿度'
			return
		
		if command == 'setplayerattackspeedamplifier':
			if cmdargs[1] < 0.5 or cmdargs[1] > 2.0:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的倍率'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置攻击速度倍率'
					return
				CFServer.CreatePlayer(i).SetPlayerAttackSpeedAmplifier(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家攻击速度倍率'
			return
		
		if command == 'setplayerjumpable':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置跳跃能力'
					return
				CFServer.CreatePlayer(i).SetPlayerJumpable(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家跳跃能力'
			return
		
		if command == 'setplayermovable':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置移动能力'
					return
				CFServer.CreatePlayer(i).SetPlayerMovable(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家移动能力'
			return
		
		if command == 'setplayernaturalstarve':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置是否饥饿掉血'
					return
				CFServer.CreatePlayer(i).SetPlayerNaturalStarve(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家是否饥饿掉血'
			return
		
		if command == 'setplayerprefixandsuffixname':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置前缀和后缀名'
					return
				CFServer.CreateName(i).SetPlayerPrefixAndSuffixName(cmdargs[1],'§r',cmdargs[2],'§r')
			args['return_msg_key'] = '成功设置前缀和后缀名'
			return
		
		if command == 'setplayermaxexhaustionvalue':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置饥饿最大消耗度'
					return
				CFServer.CreatePlayer(i).SetPlayerMaxExhaustionValue(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家饥饿最大消耗度'
			return
		
		if command == 'setplayerhealthtick':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置自然回血速度'
					return
				CFServer.CreatePlayer(i).SetPlayerHealthTick(cmdargs[1])
			args['return_msg_key'] = '成功设置玩家自然回血速度'
			return
		
		if command == 'sethurtcd':
			if compGame.SetHurtCD(cmdargs[0]):
				args['return_msg_key'] = '成功设置全局受击间隔CD'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置全局受击间隔CD失败'
				return
		
		if command == 'setattacktarget':
			if len(cmdargs[1]) != 1:
				args['return_failed'] = True
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				return
			attackTargetId = cmdargs[1][0]
			for i in cmdargs[0]:
				CFServer.CreateAction(i).SetAttackTarget(attackTargetId)
			args['return_msg_key'] = '成功设置仇恨目标'
			return
		
		if command == 'resetattacktarget':
			for i in cmdargs[0]:
				CFServer.CreateAction(i).ResetAttackTarget()
			args['return_msg_key'] = '成功重置仇恨目标'
			return
		
		if command == 'setbanplayerfishing':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置钓鱼能力'
					return
				CFServer.CreatePlayer(i).SetBanPlayerFishing(cmdargs[1])
			args['return_msg_key'] = '成功设置钓鱼能力'
			return
		
		if command == 'setactorcanpush':
			for i in cmdargs[0]:
				CFServer.CreateActorPushable(i).SetActorPushable(cmdargs[1])
			args['return_msg_key'] = '成功设置实体推动'
			return
		
		if command == 'setactorcollidable':
			for i in cmdargs[0]:
				CFServer.CreateActorCollidable(i).SetActorCollidable(cmdargs[1])
			args['return_msg_key'] = '成功设置实体碰撞'
			return
		
		if command == 'setmineability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置挖掘权限'
					return
				CFServer.CreatePlayer(i).SetMineAbility(cmdargs[1])
			args['return_msg_key'] = '成功设置挖掘权限'
			return
		
		if command == 'setbuildability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置放置权限'
					return
				CFServer.CreatePlayer(i).SetBuildAbility(cmdargs[1])
			args['return_msg_key'] = '成功设置放置权限'
			return
		
		if command == 'setcontrol':
			for i in cmdargs[0]:
				CFServer.CreateRide(i).SetControl(i,cmdargs[1])
			args['return_msg_key'] = '已设置'
		
		if command == 'setpickuparea':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置拾取范围'
					return
				CFServer.CreatePlayer(i).SetPickUpArea(cmdargs[1])
			args['return_msg_key'] = '成功设置拾取范围'
			return
		
		if command == 'setlevelgravity':
			compGame.SetLevelGravity(cmdargs[0])
			args['return_msg_key'] = '成功设置世界重力'
			return
		
		if command == 'setjumppower':
			for i in cmdargs[0]:
				CFServer.CreateGravity(i).SetJumpPower(cmdargs[1])
			args['return_msg_key'] = '成功设置跳跃力度'
		
		if command == 'setgravity':
			for i in cmdargs[0]:
				CFServer.CreateGravity(i).SetGravity(cmdargs[1])
			args['return_msg_key'] = '成功设置重力'
		
		if command == 'setworldspawnd':
			x, y, z = cmdargs[1]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			if compGame.SetSpawnDimensionAndPosition(cmdargs[0], (x,y,z)):
				args['return_msg_key'] = '成功设置世界出生点'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
				return
			
		if command == 'playeruseitemtopos':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法使用方块'
					return
			if cmdargs[2] not in [0,1,2,3,4,5]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的朝向'
				return
			x, y, z = cmdargs[1]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			for i in cmdargs[0]:
				CFServer.CreateBlockInfo(i).PlayerUseItemToPos((x,y,z),cmdargs[3],cmdargs[4],cmdargs[2])
			args['return_msg_key'] = '已尝试使用物品'
			return
		
		if command == 'playeruseitemtoentity':
			if len(cmdargs[1]) != 1:
				args['return_failed'] = True
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				return
			entityId = cmdargs[1][0]
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置使用物品'
					return
				CFServer.CreateBlockInfo(i).PlayerUseItemToEntity(entityId)
			args['return_msg_key'] = '已尝试使用物品'
			return
		
		if command == 'playerdestoryblock':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法破坏方块'
					return
			x, y, z = cmdargs[1]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			for i in cmdargs[0]:
				CFServer.CreateBlockInfo(i).PlayerDestoryBlock((x,y,z),cmdargs[2],cmdargs[3])
			args['return_msg_key'] = '已尝试破坏方块'
			return
		
		if command == 'openworkbench':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法打开工作台'
					return
			for i in cmdargs[0]:
				CFServer.CreateBlockInfo(i).OpenWorkBench()
			args['return_msg_key'] = '已打开工作台界面'
		
		if command == 'openfoldgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法打开下拉界面'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"openfoldgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将界面指令发送至客户端'
		
		if command == 'setimmunedamage':
			for i in cmdargs[0]:
				CFServer.CreateHurt(i).ImmuneDamage(cmdargs[1])
			args['return_msg_key'] = '设置免疫伤害成功'
		
		if command == 'hideslotbargui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hideslotbargui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hidehungergui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hidehungergui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hidehudgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hidehudgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hidehorsehealthgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hidehorsehealthgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hidehealthgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hidehealthgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hidefoldgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hidefoldgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hideexpgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hideexpgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hidecrosshairgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hidecrosshairgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hidearmorgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hidearmorgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'hideairsupplygui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法隐藏UI'
					return
			for i in cmdargs[0]:
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"hideairsupplygui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已将隐藏界面指令发送至客户端'
			return
		
		if command == 'setinvitemexchange':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SetInvItemExchange(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功交换物品'
			return	
		
		if command == 'setinvitemnum':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			if cmdargs[2] < 0 or cmdargs[2] > 64:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的物品数量'
				return
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SetInvItemNum(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功设置物品数量'
			return
		
		if command == 'setitemdefenceangle':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法抵挡'
					return
			if cmdargs[1] not in [0,1,2,3]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的位置id'
				return
			if cmdargs[3] < 0 or cmdargs[3] > 180 or cmdargs[4] < 0 or cmdargs[4] > 180:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的角度'
				return
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SetItemDefenceAngle(cmdargs[1],cmdargs[2],cmdargs[3],cmdargs[4])
			args['return_msg_key'] = '成功设置盾牌抵挡角度'
			return
		
		if command == 'setitemdurability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			if cmdargs[1] < 0 or cmdargs[1] > 32766:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的耐久度'
				return
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SetItemDurability(2,0,cmdargs[1])
			args['return_msg_key'] = '成功设置物品耐久度'
			return
				
		if command == 'setitemmaxdurability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			if cmdargs[1] < 0 or cmdargs[1] > 32766:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的耐久度'
				return
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SetItemMaxDurability(2,0,cmdargs[1],True)
			args['return_msg_key'] = '成功设置物品最大耐久度'
			return
			
		if command == 'setitemtierlevel':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			if cmdargs[1] not in [0,1,2,3,4]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的等级'
				return
			for i in cmdargs[0]:
				itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
				CFServer.CreateItem(i).SetItemTierLevel(itemdata,cmdargs[1])
				CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
			args['return_msg_key'] = '成功设置物品等级'
			return
		
		if command == 'setitemtierspeed':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			for i in cmdargs[0]:
				itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
				CFServer.CreateItem(i).SetItemTierSpeed(itemdata,cmdargs[1])
				CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
			args['return_msg_key'] = '成功设置物品挖掘速度'
			return
		
		if command == 'setmaxstacksize':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			if cmdargs[1] < 1 or cmdargs[1] > 64:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的堆叠数量'
				return
			for i in cmdargs[0]:
				itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
				CFServer.CreateItem(i).SetMaxStackSize(itemdata,cmdargs[1])
				CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
			args['return_msg_key'] = '成功设置最大堆叠数量'
			return
		
		if command == 'playerexhaustionratio':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			if cmdargs[1] not in [0, 1, 2, 3, 4, 9]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的行为id'
				return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerExhaustionRatioByType(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功设置玩家饥饿度消耗倍率'
			return
		
		if command == 'setsigntextstyle':
			x, y, z = cmdargs[0]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			r,g,b = cmdargs[2]
			a = cmdargs[3]
			lighting = cmdargs[4]
			if cmdargs[5] is True:
				side = 1
			else:
				side = 0
			if CFServer.CreateBlockEntity(levelId).SetSignTextStyle((x,y,z),cmdargs[1],(r,g,b,a),lighting,side):
				args['return_msg_key'] = '设置告示牌文本样式成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
				return
		
		if command == 'setsignblocktext':
			x, y, z = cmdargs[0]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			if cmdargs[3] is True:
				side = 1
			else:
				side = 0
			if CFServer.CreateBlockInfo(levelId).SetSignBlockText((x,y,z),cmdargs[1],cmdargs[2],side):
				args['return_msg_key'] = '设置告示牌文本成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
				return

		if command == 'setplayerinteracterange':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerInteracteRange(cmdargs[1])
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"setplayerinteracterange", 'target': i, 'cmdargs': cmdargs})
			args['return_msg_key'] = '成功设置触及距离'
			return
		
		if command == 'summonprojectile':
			try:
				targetlen = len(cmdargs[7])
				target = cmdargs[7][0]
			except:
				targetlen = 1
				target = None
			if not targetlen == 1:
				args['return_failed'] = True
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				return
			
			for i in cmdargs[0]:
				param = {
					'position': cmdargs[2],
					'direction': cmdargs[3],
					'power': cmdargs[4],
					'gravity': cmdargs[5],
					'damage': cmdargs[6],
					'targetId': target,
					'isDamageOwner': cmdargs[8],
					'auxValue': cmdargs[9]
				}
				
				CFServer.CreateProjectile(levelId).CreateProjectileEntity(i, cmdargs[1], param)
			args['return_msg_key'] = '成功生成抛射物'
			return
		
		if command == 'setstepheight':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置'
					return
			if cmdargs[0]:
				for i in cmdargs[0]:
					CFServer.CreateAttr(i).SetStepHeight(cmdargs[1])
				args['return_msg_key'] = '成功设置能迈过的最大高度'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		if command == 'setsize':
			if cmdargs[0]:
				for i in cmdargs[0]:
					CFServer.CreateCollisionBox(i).SetSize((cmdargs[1],cmdargs[2]))
				args['return_msg_key'] = '成功设置碰撞箱'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
			
		if command == 'playerchatprefix':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:player':
					CFServer.CreateExtraData(i).SetExtraData('chatprefix', cmdargs[1])
				else:
					CFServer.CreateMsg(i).NotifyOneMessage(playerId, '非玩家实体无法设置聊天前缀', "§c")
			args['return_msg_key'] = '成功设置玩家聊天前缀'
			return

		if command == 'writehealthtoscoreboard':
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CFServer.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				health = CFServer.CreateAttr(entity).GetAttrValue(0)
				health = int(round(health))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, health), False)
			args['return_msg_key'] = '成功将生命值写入计分板'
			return
			
		if command == 'writehungertoscoreboard':
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CFServer.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				hunger = CFServer.CreateAttr(entity).GetAttrValue(4)
				hunger = int(round(hunger))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, hunger), False)
			args['return_msg_key'] = '成功将饥饿值写入计分板'
			return	

		if command == 'writearmortoscoreboard':
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CFServer.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				armor = CFServer.CreateAttr(entity).GetAttrValue(12)
				armor = int(round(armor))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, armor), False)
			args['return_msg_key'] = '成功将盔甲值写入计分板'
			return
		
		if command == 'writespeedtoscoreboard':
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CFServer.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				speed = CFServer.CreateAttr(entity).GetAttrValue(1)
				speed = int(round(speed))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, speed), False)
			args['return_msg_key'] = '成功将速度值写入计分板'
			return
		
		if command == 'executecb':
			success = CFServer.CreateBlockEntity(levelId).ExecuteCommandBlock((cmdargs[0], cmdargs[1], cmdargs[2]), cmdargs[3])
			if success:
				args['return_msg_key'] = '成功执行命令方块'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '执行命令方块失败'
				return
		
		if command == 'setname':
			for i in cmdargs[0]:
				CFServer.CreateName(i).SetName(cmdargs[1])
			args['return_msg_key'] = '成功设置名称'
			return
		
		if command == 'aicontrol':
			for i in cmdargs[0]:
				CFServer.CreateControlAi(i).SetBlockControlAi(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功设置实体AI'
			return
		
		if command == 'master':
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				compExtra.SetExtraData("isMaster", True)
			args['return_msg_key'] = '锁定玩家权限成功'
			return

		if command == 'demaster':
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				compExtra.SetExtraData("isMaster", False)
			args['return_msg_key'] = '解锁玩家权限成功'
			return
		
		compExtra = CFServer.CreateExtraData(serverApi.GetLevelId())
		params = compExtra.GetExtraData('parameters')
		input1 = cmdargs[0]
		if command == 'param':
			if cmdargs[0] is None:
				args['return_msg_key'] = str(params)
				return
			else:
				if type(params) == dict and params.has_key(cmdargs[0]):
					args['return_msg_key'] = "变量\"%s\"为 %s" % (input1, params[input1])
					return
				else:
					args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
					args['return_failed'] = True
					return

		if command == 'paramdel':
			if type(params) == dict and params.has_key(cmdargs[0]):
				args['return_msg_key'] = '删除变量成功'
				del params[input1]
				compExtra.SetExtraData('parameters', params)
				return
			else:
				args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
				args['return_failed'] = True
				return

		if command == 'paramwrite':
			args['return_msg_key'] = '修改变量成功'
			input2 = cmdargs[1]
			if type(params) == dict:
				params[input1] = input2
			else:
				params = {input1: input2}
			compExtra.SetExtraData('parameters', params)
			return

		if command == 'kickt':
			for kickplayer in cmdargs[0]:
				CFServer.CreateCommand(serverApi.GetLevelId()).SetCommand('/kick ' + CFServer.CreateName(kickplayer).GetName() + ' ' + cmdargs[1], False)
			args['return_msg_key'] = '已踢出目标玩家'
			return
				
		if command == 'explode':
			for i in cmdargs[0]:
				position = CFServer.CreatePos(i).GetFootPos()
				CFServer.CreateExplosion(levelId).CreateExplosion(position,cmdargs[1],cmdargs[3],cmdargs[2],i,None)
			args['return_msg_key'] = '爆炸已成功创建'
			return
	
		if command == 'explodebypos':
			if CFServer.CreateExplosion(levelId).CreateExplosion(cmdargs[0],cmdargs[1],cmdargs[3],cmdargs[2],None,None):
				args['return_msg_key'] = '爆炸已成功创建'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '爆炸创建失败'
				return
	
		if command == "console":
			cmd = cmdargs[0]
			if cmd.startswith("/"):
				cmd = cmd[1:]
			cmd2 = ""
			if compExtra.GetExtraData('parameters'):
				for i in cmd.split(" "):
					for ii in compExtra.GetExtraData('parameters').keys():
						index = i.find("param:%s" % (ii))
						if not index == -1:
							i = compExtra.GetExtraData('parameters')[i[index+6:]]
					cmd2 = "%s %s" % (cmd2, i)
			else:
				cmd2 = cmd
			CFServer.CreateCommand(serverApi.GetLevelId()).SetCommand("/" + cmd2, False)
			args["return_msg_key"] = "已尝试将指令发送到控制台执行。"
			return
		
		if command == 'addaroundentitymotion' or command == 'addaroundpointmotion':
			if not len(cmdargs[1]) == 1 and command == 'addaroundentitymotion':
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				args['return_failed'] = True
				return
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				CompMotion = CFServer.CreateActorMotion(i)
				CompType = CFServer.CreateEngineType(i)
				EntityType = CompType.GetEngineTypeStr()
				if command == 'addaroundentitymotion':
					if EntityType == 'minecraft:player':
						addMotion = CompMotion.AddPlayerAroundEntityMotion
					else:
						addMotion = CompMotion.AddEntityAroundEntityMotion
					Mid = addMotion(cmdargs[1][0],
									cmdargs[2],
									cmdargs[3],
									cmdargs[4],
									cmdargs[5],
									cmdargs[6])
				else:
					if EntityType == 'minecraft:player':
						addMotion = CompMotion.AddPlayerAroundEntityMotion
					else:
						addMotion = CompMotion.AddEntityAroundEntityMotion
					Mid = addMotion(cmdargs[1],
									cmdargs[2],
									cmdargs[3],
									cmdargs[4],
									cmdargs[5])
				if Mid == -1:
					args['return_failed'] = True
					args['return_msg_key'] = '设置失败'
					return
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
			return

		if command == 'addvelocitymotion':
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				CompMotion = CFServer.CreateActorMotion(i)
				CompType = CFServer.CreateEngineType(i)
				EntityType = CompType.GetEngineTypeStr()
				if EntityType == 'minecraft:player':
					addMotion = CompMotion.AddPlayerVelocityMotion
				else:
					addMotion = CompMotion.AddEntityVelocityMotion
				Mid = addMotion(cmdargs[1],
								cmdargs[2],
								cmdargs[3])
				if Mid == -1:
					args['return_failed'] = True
					args['return_msg_key'] = '创建失败'
					return
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
			return
		
		if command == 'startmotion':
			args['return_msg_key'] = ''
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				CompMotion = CFServer.CreateActorMotion(i)
				CompType = CFServer.CreateEngineType(i)
				CompMsg = CFServer.CreateMsg(i)
				EntityType = CompType.GetEngineTypeStr()
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					if EntityType == 'minecraft:player':
						startMotion = CompMotion.StartPlayerMotion
					else:
						startMotion = CompMotion.StartEntityMotion
					for ii in Motions:
						startMotion(ii)
					CompMsg.NotifyOneMessage(playerId, '成功启用实体的运动器')
				else :
					args['return_failed'] = True
					CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
			return
		
		if command == 'stopmotion':
			args['return_msg_key'] = ''
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				CompMotion = CFServer.CreateActorMotion(i)
				CompType = CFServer.CreateEngineType(i)
				CompMsg = CFServer.CreateMsg(i)
				EntityType = CompType.GetEngineTypeStr()
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					if EntityType == 'minecraft:player':
						stopMotion = CompMotion.StopPlayerMotion
					else:
						stopMotion = CompMotion.StopEntityMotion
					for ii in Motions:
						stopMotion(ii)
					CompMsg.NotifyOneMessage(playerId, '成功停止实体的运动器')
				else:
					args['return_failed'] = True
					CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
			return
		
		if command == 'removemotion':
			args['return_msg_key'] = ''
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				CompMotion = CFServer.CreateActorMotion(i)
				Motions = compExtra.GetExtraData('Motions')
				CompType = CFServer.CreateEngineType(i)
				CompMsg = CFServer.CreateMsg(i)
				EntityType = CompType.GetEngineTypeStr()
				if Motions:
					if EntityType == 'minecraft:player':
						removeMotion = CompMotion.RemovePlayerMotion
					else:
						removeMotion = CompMotion.RemoveEntityMotion
					for ii in Motions:
						removeMotion(ii)
						Motions.remove(ii)
					compExtra.SetExtraData('Motions', Motions)
					CompMsg.NotifyOneMessage(playerId, '成功移除实体的运动器')
				else:
					args['return_failed'] = True
					CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
			return

		if command == 'addenchant':
			if cmdargs[0]:
				for i in cmdargs[0]:
					compItem = CFServer.CreateItem(i)
					if type(cmdargs[3]) == int:
						slotType = 0
						slot = cmdargs[3]
					else:
						slotType = 2
						slot = 0
					itemDict = compItem.GetPlayerItem(slotType, slot, True)
					if itemDict:
						if itemDict["userData"] is None:
							itemDict["userData"] = {}
						if itemDict["userData"].get('ench', None) is None:
							itemDict["userData"]['ench'] = []
						itemDict["userData"]['ench'].insert(0, {'lvl': {'__type__': 2, '__value__': cmdargs[2]}, 
											  					'id':  {'__type__': 2, '__value__': cmdargs[1]}, 
																'modEnchant': {'__type__': 8, '__value__': ''}})
						itemDict["enchantData"] = []
					else:
						args['return_failed'] = True
						args['return_msg_key'] = '该槽位没有物品或没有该槽位'
					if slotType == 0:
						compItem.SpawnItemToPlayerInv(itemDict, i, slot)
					else:
						compItem.SpawnItemToPlayerCarried(itemDict, i)
					args['return_msg_key'] = '添加附魔成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return

		if command == 'addtrackmotion':
			for i in cmdargs[0]:
				compExtra = CFServer.CreateExtraData(i)
				CompMotion = CFServer.CreateActorMotion(i)
				CompType = CFServer.CreateEngineType(i)
				EntityType = CompType.GetEngineType()
				if EntityType == 63:
					addMotion = CompMotion.AddPlayerTrackMotion
				else:
					addMotion = CompMotion.AddEntityTrackMotion
				Mid = addMotion(cmdargs[1],
								cmdargs[2],
								None,
								False,
								cmdargs[3],
								cmdargs[5],
								cmdargs[4],
								cmdargs[6])
				if Mid == -1:
					args['return_failed'] = True
					args['return_msg_key'] = '创建失败'
					return
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
			return

		if command == 'setactorcanburnbylightning':
			compGame.SetCanActorSetOnFireByLightning(cmdargs[0])
			args['return_msg_key'] = '设置成功'
			return

		if command == 'setblockcanburnbylightning':
			compGame.SetCanBlockSetOnFireByLightning(cmdargs[0])
			args['return_msg_key'] = '设置成功'
			return

		if command == 'cancelshearsdestoryblockspeedall':
			for i in cmdargs[0]:
				compItem = CFServer.CreateItem(i)
				compItem.CancelShearsDestoryBlockSpeedAll()
				args['return_msg_key'] = '取消成功'
			return

		if command == 'cancelshearsdestoryblockspeed':
			for i in cmdargs[0]:
				compItem = CFServer.CreateItem(i)
				if not compItem.CancelShearsDestoryBlockSpeed(cmdargs[1]):
					args['return_failed'] = True
					args['return_msg_key'] = '无效的命名空间id'
			args['return_msg_key'] = '取消成功'
			return

		if command == 'setshearsdestoryblockspeed':
			if cmdargs[2] < 1:
				args['return_failed'] = True
				args['return_msg_key'] = '速度必须大于1'
				return
			for i in cmdargs[0]:
				compItem = CFServer.CreateItem(i)
				if not compItem.SetShearsDestoryBlockSpeed(cmdargs[1], cmdargs[2]):
					args['return_failed'] = True
					args['return_msg_key'] = '无效的命名空间id'
					return
			args['return_msg_key'] = '设置成功'
			return

		if command == 'changeselectslot':
			for i in cmdargs[0]:
				CompType = CFServer.CreateEngineType(i)
				EntityType = CompType.GetEngineTypeStr()
				if EntityType != "minecraft:player":
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置选择槽位'
					return
			for i in cmdargs[0]:
				CompPlayer = CFServer.CreatePlayer(i)
				CompPlayer.ChangeSelectSlot(cmdargs[1])
			args['return_msg_key'] = '设置成功'
			return

		if command == 'forbidliquidflow':
			if compGame.ForbidLiquidFlow(cmdargs[0]):
				args['return_msg_key'] = '已成功修改液体流动性'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '修改失败'
				return

		if command == 'getuid':
			uid_dict = {}
			for i in cmdargs[0]:
				CompType = CFServer.CreateEngineType(i)
				if CompType.GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法获取uid'
					return
				playername = CFServer.CreateName(i).GetName()
				uid_dict[playername] = CFServer.CreateHttp(levelId).GetPlayerUid(i)
			args['return_msg_key'] = '获取到的UID为%s' % (uid_dict)
			return
			# serversystem.NotifyToMultiClients(list(cmdargs[0]), "CustomCommandClient", {'cmd':"getuid", 'origin': playerId})

		if command == 'givewithnbt':
			args['return_msg_key'] = '给予失败'
			args['return_failed'] = True
			try:
				itemDict = json.loads(cmdargs[1].replace("'",'"'))
			except:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的nbt'
				return
			print(unicode_convert(itemDict))
			for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
				itemDict.pop(i,False) #删去多余键值对(这些已被弃用)
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法给予物品'
					return
				CFServer.CreateItem(i).SpawnItemToPlayerInv(unicode_convert(itemDict), i)
				args['return_failed'] = False
				args['return_msg_key'] = '成功给予物品'
			return
			
		if command == 'spawnitemtocontainer':
			args['return_msg_key'] = '成功给予物品'
			x = intg(cmdargs[2][0])
			y = intg(cmdargs[2][1])
			z = intg(cmdargs[2][2])
			itemDict = compItemWorld.GetContainerItem((x, y, z,), cmdargs[1], cmdargs[3], True)
			try:itemDict2 = unicode_convert(json.loads(cmdargs[0].replace("'", '"')))
			except:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的Nbt'
				return
			for i in [('durability',0),('customTips',''),('extraId',''),('newAuxValue',0),('userData',None),('showInHand',True)]:
				if not itemDict2.has_key(i[0]):
					itemDict2[i[0]] = i[1]
			if itemDict:
				for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
					itemDict.pop(i) #删去多余键值对(这些已被弃用)
					itemDict2.pop(i, False)
				countOrign = itemDict.pop('count')
			else:countOrign = 0
			countAdd = itemDict2.pop('count')
			if ((not itemDict) or itemDict == itemDict2) and countOrign+countAdd<=64:
				itemDict2['count'] = countOrign+countAdd
				compItemWorld.SpawnItemToContainer(itemDict2, cmdargs[1], (x, y, z,), cmdargs[3])
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '槽位已满'
			return

		if command == 'removeenchant':
			args['return_msg_key'] = '删除失败'
			args['return_failed'] = True
			for i in cmdargs[0]:
				if CFServer.CreateItem(i).RemoveEnchantToInvItem(cmdargs[2], cmdargs[1]):
					args['return_msg_key'] = '删除成功'
					args['return_failed'] = False
			return

		if command == 'resetattacktarget':
			for i in cmdargs[0]:
				CFServer.CreateAction(i).ResetAttackTarget()
			args['return_msg_key'] = '清除仇恨成功'
			return
			
		if command == 'resetmotion':
			for i in cmdargs[0]:
				CompType = CFServer.CreateEngineType(i)
				CompMotion = CFServer.CreateActorMotion(i)
				if CompType.GetEngineTypeStr() == 'minecraft:player':
					CompMotion.SetPlayerMotion((0, 0, 0))
				else:
					CompMotion.ResetMotion()
			args['return_msg_key'] = '重置运动成功'
			return
	def TickClient(self):
		"""
		@description 客户端的零件对象逻辑驱动入口
		"""
		PartBase.TickClient(self)

	def TickServer(self):
		"""
		@description 服务端的零件对象逻辑驱动入口
		"""
		PartBase.TickServer(self)

	def DestroyClient(self):
		"""
		@description 客户端的零件对象销毁逻辑入口
		"""
		PartBase.DestroyClient(self)

	def DestroyServer(self):
		"""
		@description 服务端的零件对象销毁逻辑入口
		"""
		PartBase.DestroyServer(self)
