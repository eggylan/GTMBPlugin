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

def checkjson(data, playerId):
	#type: (str, str|int) -> list
	try:
		itemDict = json.loads(data.replace("'",'"'))
	except ValueError as errordata:
		if str(errordata).find('char') == -1:
			return ['无效的nbt', True]
		if str(errordata).find('Extra') != 0:
			index = int(str(errordata)[str(errordata).find('char') + (5 if str(errordata).find('Extra') != 0 else 7): -1])
		if playerId is None:
			colors = ['§c', '§r']
		else:
			colors = ['§e', '§c']
		if index >= 15:
			return ['无效的nbt 位于 %s' % (data[index-15:index]+colors[0]+data[index]+colors[1]+data[index+1:index+15]), True]
		return ['无效的nbt 位于 %s' % (data[:index]+colors[0]+data[index]+colors[1]+data[index+1:index+15]), True]
	if type(itemDict) != dict:
		return['无效的nbt', True]
	return [itemDict, False]

@registerGenericClass("customcmdsPart")
class customcmdsPart(PartBase):
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "自定义指令零件"

		# 注册处理函数
		self.clientcustomcmd = {
			"setplayerinteracterange":self.setplayerinteracterange,
			"hideairsupplygui":self.hideairsupplygui
		}
		self.servercustomcmd = {}
		
	
	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		CFClient.CreatePostProcess(levelId).SetEnableColorAdjustment(True)
		clientsystem.ListenForEvent("Minecraft", "preset", "CustomCommandClient", self, self.OnCustomCommandClient)
		global localPlayerId
		localPlayerId = clientApi.GetLocalPlayerId()
		PartBase.InitClient(self)

	
	def OnCustomCommandClient(self, args):
		# 从dict中选取处理函数
		handler = self.clientcustomcmd.get(args['cmd'])
		if handler:
			handler(args)
	

	# 客户端函数部分
	def setplayerinteracterange(self, args):
		clientApi.GetEngineCompFactory().CreatePlayer(localPlayerId).SetPickRange(args['cmdargs'][1])
		return

	def hideairsupplygui(self, args):
		clientApi.HideAirSupplyGUI(args['cmdargs'][1])
		return


		# 以此类推...
		
		
		
		
		# if args['cmd'] == 'setplayerinteracterange':	
		# 	clientApi.GetEngineCompFactory().CreatePlayer(playerId).SetPickRange(args['cmdargs'][1])
		# elif args['cmd'] == 'hideairsupplygui':
		# 	clientApi.HideAirSupplyGUI(args['cmdargs'][1])
		# elif args['cmd'] == 'hidearmorgui':
		# 	clientApi.HideArmorGui(args['cmdargs'][1])
		# elif args['cmd'] == 'hidecrosshairgui':
		# 	clientApi.HideCrossHairGUI(args['cmdargs'][1])
		# elif args['cmd'] == 'hideexpgui':
		# 	clientApi.HideExpGui(args['cmdargs'][1])
		# elif args['cmd'] == 'hidefoldgui':
		# 	clientApi.HideFoldGUI(args['cmdargs'][1])
		# elif args['cmd'] == 'hidehealthgui':
		# 	clientApi.HideHealthGui(args['cmdargs'][1])
		# elif args['cmd'] == 'hidehorsehealthgui':
		# 	clientApi.HideHorseHealthGui(args['cmdargs'][1])
		# elif args['cmd'] == 'hidehudgui':
		# 	clientApi.HideHudGUI(args['cmdargs'][1])
		# elif args['cmd'] == 'hidehungergui':
		# 	clientApi.HideHungerGui(args['cmdargs'][1])
		# elif args['cmd'] == 'hideslotbargui':
		# 	clientApi.HideSlotBarGui(args['cmdargs'][1])
		# elif args['cmd'] == 'openfoldgui':
		# 	clientApi.OpenFoldGui()
		# elif args['cmd'] == 'setcanpausescreen':
		# 	CFClient.CreateOperation(levelId).SetCanPauseScreen(args['cmdargs'][1])
		# elif args['cmd'] == 'setcolorbrightness':
		# 	CFClient.CreatePostProcess(levelId).SetColorAdjustmentBrightness(args['cmdargs'][2])
		# elif args['cmd'] == 'setcolorcontrast':
		# 	CFClient.CreatePostProcess(levelId).SetColorAdjustmentContrast(args['cmdargs'][2])
		# elif args['cmd'] == 'setcolorsaturation':
		# 	CFClient.CreatePostProcess(levelId).SetColorAdjustmentSaturation(args['cmdargs'][2])
		# elif args['cmd'] == 'setcolortint':
		# 	CFClient.CreatePostProcess(levelId).SetColorAdjustmentTint(args['cmdargs'][2],args['cmdargs'][3])
		# elif args['cmd'] == 'setcompassentity':
		# 	CFClient.CreateItem(playerId).SetCompassEntity(args['cmdargs'][1][0])
		# elif args['cmd'] == 'setcompasstarget':
		# 	CFClient.CreateItem(playerId).SetCompassTarget(args['cmdargs']['x'],args['cmdargs']['y'],args['cmdargs']['z'])
		# elif args['cmd'] == 'setvignettecenter':
		# 	CFClient.CreatePostProcess(levelId).SetVignetteCenter((args['cmdargs'][2], args['cmdargs'][3]))
		# elif args['cmd'] == 'setvignetteradius':
		# 	CFClient.CreatePostProcess(levelId).SetVignetteRadius(args['cmdargs'][2])
		# elif args['cmd'] == 'setvignettecolor':
		# 	CFClient.CreatePostProcess(levelId).SetVignetteRGB(args['cmdargs'][2])
		# elif args['cmd'] == 'setvignettesmooth':
		# 	CFClient.CreatePostProcess(levelId).SetVignetteSmoothness(args['cmdargs'][2])
		# elif args['cmd'] == 'setvignette':
		# 	CFClient.CreatePostProcess(levelId).SetEnableVignette(args['cmdargs'][2])
		
		# clientsystem.NotifyToServer("customCmdReturn", data)

	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "CustomCommandTriggerServerEvent", self, self.OnCustomCommand)
		serversystem.ListenForEvent("Minecraft", "preset", "customCmdReturn", self, self.OnReturn)
		PartBase.InitServer(self)

	def OnReturn(self, args):
		pass
		#compMsg = CFServer.CreateMsg(args['target'])
		#compName = CFServer.CreateName(args['__id__'])

	def OnCustomCommand(self, args):
		command = args['command']
		cmdargs = []
		variant = args['variant']
		for i in args["args"]:
			cmdargs.append(i["value"])
		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None

		if command == 'setentityonfire':
			for i in cmdargs[0]:
				CFServer.CreateAttr(i).SetEntityOnFire(cmdargs[1],cmdargs[2])
			args['return_msg_key'] = '已设置实体着火'
		
		elif command == 'setcurrentairsupply':
			for i in cmdargs[0]:
				CFServer.CreateBreath(i).SetCurrentAirSupply(cmdargs[1])
			args['return_msg_key'] = '已设置氧气储备值'
		
		elif command == 'setcompasstarget':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置指南针指向'
					return
			x,y,z = cmdargs[1]
			compassdata = {'x':intg(x),'y':int(y),'z':intg(z)}
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setcompasstarget",'cmdargs': compassdata})
			args['return_msg_key'] = '已设置指南针指向'
		
		elif command == 'setcompassentity':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置指南针指向'
					return
			if len(cmdargs[1]) > 1:
				args['return_failed'] = True
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setcompassentity",'cmdargs': cmdargs})
			args['return_msg_key'] = '已设置指南针指向'
			
		elif command == 'setcolor':
			for i in cmdargs[1]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置屏幕色彩'
					return
			if variant == 3:
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolortint",'cmdargs': cmdargs})
				args['return_msg_key'] = '已设置玩家屏幕色调'
			elif variant == 2:
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolorsaturation",'cmdargs': cmdargs})
				args['return_msg_key'] = '已设置玩家屏幕色彩饱和度'
			elif variant == 1:
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolorcontrast",'cmdargs': cmdargs})
				args['return_msg_key'] = '已设置玩家屏幕色彩对比度'
			else:
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolorbrightness",'cmdargs': cmdargs})
				args['return_msg_key'] = '已设置玩家屏幕色彩亮度'
		
		elif command == 'setchestboxitemnum':
			x,y,z = cmdargs[0]
			xyz = (intg(x),int(y),intg(z))
			if CFServer.CreateChestBlock(levelId).SetChestBoxItemNum(None,xyz,cmdargs[1],cmdargs[2],cmdargs[3]):
				args['return_msg_key'] = '已设置箱子物品数量'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
		
		elif command == 'setchestboxitemexchange':
			x,y,z = cmdargs[0]
			pid = CFServer.CreateEntityComponent(levelId).GetEntitiesBySelector("@r")[0]
			if CFServer.CreateChestBlock(pid).SetChestBoxItemExchange(pid,(intg(x),int(y),intg(z)),cmdargs[1],cmdargs[2]):
				args['return_msg_key'] = '已交换箱子物品'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '交换失败'
		
		elif command == 'setcanpausescreen':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置暂停权限'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setcanpausescreen",'cmdargs': cmdargs})
			args['return_msg_key'] = '已设置玩家暂停权限'

		elif command == 'setcanotherplayerride':
			for i in cmdargs[0]:
				CFServer.CreateRide(i).SetCanOtherPlayerRide(i,cmdargs[1])
			args['return_msg_key'] = '已设置骑乘权限'
		
		elif command == 'setattackplayersability':
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetAttackPlayersAbility(cmdargs[1])
			args['return_msg_key'] = '已设置玩家pvp权限'
		
		elif command == 'setattackmobsability':
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetAttackMobsAbility(cmdargs[1])
			args['return_msg_key'] = '已设置玩家攻击生物权限'
	
		elif command == 'setattackdamage':
			for i in cmdargs[0]:
				compItem = CFServer.CreateItem(i)
				itemDict = compItem.GetPlayerItem(2, 0, True)
				if compItem.SetAttackDamage(itemDict, cmdargs[1]):
					compItem.SpawnItemToPlayerCarried(itemDict,i)
			args['return_msg_key'] = '已设置玩家手持物品攻击伤害'

		elif command == 'setplayerrespawnpos':
			x, y, z = cmdargs[1]
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置重生点'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerRespawnPos((intg(x),int(y),intg(z)),cmdargs[2])
			args['return_msg_key'] = '已设置玩家重生点'
		
		elif command == 'setplayerhealthlevel':
			if cmdargs[1] < 0 or cmdargs[1] > 20:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的回血临界值'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置回血临界值'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerHealthLevel(cmdargs[1])
			args['return_msg_key'] = '已设置玩家回血临界值'
		
		elif command == 'setplayerstarvelevel':
			if cmdargs[1] < 0 or cmdargs[1] > 20:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的扣血临界值'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置扣血临界值'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerStarveLevel(cmdargs[1])
			args['return_msg_key'] = '已设置玩家扣血临界值'
		
		elif command == 'setplayerhunger':
			if cmdargs[1] < 0 or cmdargs[1] > 20:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的饥饿度'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置饥饿度'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerHunger(cmdargs[1])
			args['return_msg_key'] = '已设置玩家饥饿度'
		
		elif command == 'setplayerattackspeedamplifier':
			if cmdargs[1] < 0.5 or cmdargs[1] > 2.0:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的倍率'
				return
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置攻击速度倍率'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerAttackSpeedAmplifier(cmdargs[1])
			args['return_msg_key'] = '已设置玩家攻击速度倍率'
		
		elif command == 'setplayerjumpable':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置跳跃权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerJumpable(cmdargs[1])
			args['return_msg_key'] = '已设置玩家跳跃权限'
		
		elif command == 'setplayermovable':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置移动权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerMovable(cmdargs[1])
			args['return_msg_key'] = '已设置玩家移动权限'
		
		elif command == 'setplayernaturalstarve':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置是否饥饿掉血'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerNaturalStarve(cmdargs[1])
			args['return_msg_key'] = '已设置玩家是否饥饿掉血'
		
		elif command == 'setplayerprefixandsuffixname':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置前缀和后缀名'
					return
			for i in cmdargs[0]:
				CFServer.CreateName(i).SetPlayerPrefixAndSuffixName(cmdargs[1],'§r',cmdargs[2],'§r')
			args['return_msg_key'] = '已设置前缀和后缀名'
		
		elif command == 'setplayermaxexhaustionvalue':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置饥饿最大消耗度'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerMaxExhaustionValue(cmdargs[1])
			args['return_msg_key'] = '已设置玩家饥饿最大消耗度'
		
		elif command == 'setplayerhealthtick':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置自然回血速度'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerHealthTick(cmdargs[1])
			args['return_msg_key'] = '已设置玩家自然回血速度'

		elif command == 'setplayerstarvetick':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置自然扣血速度'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerStarveTick(cmdargs[1])
			args['return_msg_key'] = '已设置玩家自然扣血速度'

		elif command == 'sethurtcd':
			if compGame.SetHurtCD(cmdargs[0]):
				args['return_msg_key'] = '已设置全局受击间隔'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
		
		elif command == 'setattacktarget':
			if len(cmdargs[1]) != 1:
				args['return_failed'] = True
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				return
			attackTargetId = cmdargs[1][0]
			for i in cmdargs[0]:
				CFServer.CreateAction(i).SetAttackTarget(attackTargetId)
			args['return_msg_key'] = '已设置仇恨目标'
		
		elif command == 'resetattacktarget':
			for i in cmdargs[0]:
				CFServer.CreateAction(i).ResetAttackTarget()
			args['return_msg_key'] = '成功重置仇恨目标'
		
		elif command == 'setbanplayerfishing':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置钓鱼权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetBanPlayerFishing(cmdargs[1])
			args['return_msg_key'] = '已设置钓鱼权限'
		
		elif command == 'setactorcanpush':
			for i in cmdargs[0]:
				CFServer.CreateActorPushable(i).SetActorPushable(cmdargs[1])
			args['return_msg_key'] = '已设置实体推动行为'
		
		elif command == 'setactorcollidable':
			for i in cmdargs[0]:
				CFServer.CreateActorCollidable(i).SetActorCollidable(cmdargs[1])
			args['return_msg_key'] = '已设置实体碰撞行为'
		
		elif command == 'setmineability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置挖掘权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetMineAbility(cmdargs[1])
			args['return_msg_key'] = '已设置挖掘权限'
		
		elif command == 'setbuildability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置放置权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetBuildAbility(cmdargs[1])
			args['return_msg_key'] = '已设置放置权限'
		
		elif command == 'setcontrol':
			for i in cmdargs[0]:
				CFServer.CreateRide(i).SetControl(i,cmdargs[1])
			args['return_msg_key'] = '已设置'
		
		elif command == 'setpickuparea':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置拾取范围'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPickUpArea(cmdargs[1])
			args['return_msg_key'] = '已设置拾取范围'
		
		elif command == 'setlevelgravity':
			compGame.SetLevelGravity(cmdargs[0])
			args['return_msg_key'] = '已设置世界重力'
		
		elif command == 'setjumppower':
			for i in cmdargs[0]:
				CFServer.CreateGravity(i).SetJumpPower(cmdargs[1])
			args['return_msg_key'] = '已设置跳跃力度'
		
		elif command == 'setgravity':
			for i in cmdargs[0]:
				CFServer.CreateGravity(i).SetGravity(cmdargs[1])
			args['return_msg_key'] = '已设置重力'
		
		elif command == 'setworldspawnd':
			x, y, z = cmdargs[1]
			if compGame.SetSpawnDimensionAndPosition(cmdargs[0], (intg(x),int(y),intg(z))):
				args['return_msg_key'] = '已设置世界出生点'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
			
		elif command == 'playeruseitemtopos':
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
			for i in cmdargs[0]:
				CFServer.CreateBlockInfo(i).PlayerUseItemToPos((intg(x),int(y),intg(z)),cmdargs[3],cmdargs[4],cmdargs[2])
			args['return_msg_key'] = '已尝试使用物品'
		
		elif command == 'playeruseitemtoentity':
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
			for i in cmdargs[0]:
				CFServer.CreateBlockInfo(i).PlayerUseItemToEntity(entityId)
			args['return_msg_key'] = '已尝试使用物品'
		
		elif command == 'playerdestoryblock':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法破坏方块'
					return
			x, y, z = cmdargs[1]
			for i in cmdargs[0]:
				CFServer.CreateBlockInfo(i).PlayerDestoryBlock((intg(x),int(y),intg(z)),cmdargs[2],cmdargs[3])
			args['return_msg_key'] = '已尝试破坏方块'
		
		elif command == 'openworkbench':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法打开工作台'
					return
			for i in cmdargs[0]:
				CFServer.CreateBlockInfo(i).OpenWorkBench()
			args['return_msg_key'] = '已打开工作台界面'
		
		elif command == 'openfoldgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法打开下拉界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"openfoldgui",'cmdargs': cmdargs})
			args['return_msg_key'] = '已打开下拉界面'
		
		elif command == 'setimmunedamage':
			for i in cmdargs[0]:
				CFServer.CreateHurt(i).ImmuneDamage(cmdargs[1])
			args['return_msg_key'] = '设置伤害免疫成功'
		
		elif command == 'hideslotbargui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hideslotbargui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏工具栏'
			else:
				args['return_msg_key'] = '已显示工具栏'
		
		elif command == 'hidehungergui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehungergui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏饱食度栏'
			else:
				args['return_msg_key'] = '已显示饱食度栏'
		
		elif command == 'hidehudgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehudgui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏所有界面'
			else:
				args['return_msg_key'] = '已显示所有界面'
		
		elif command == 'hidehorsehealthgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehorsehealthgui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏坐骑血量界面'
			else:
				args['return_msg_key'] = '已显示坐骑血量界面'
		
		elif command == 'hidehealthgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehealthgui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏血条'
			else:
				args['return_msg_key'] = '已显示血条'
		
		elif command == 'hidefoldgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidefoldgui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏下拉界面'
			else:
				args['return_msg_key'] = '已显示下拉界面'
		
		elif command == 'hideexpgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hideexpgui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏经验条'
			else:
				args['return_msg_key'] = '已显示经验条'
		
		elif command == 'hidecrosshairgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidecrosshairgui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏十字准星'
			else:
				args['return_msg_key'] = '已显示十字准星'
		
		elif command == 'hidearmorgui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidearmorgui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏盔甲栏'
			else:
				args['return_msg_key'] = '已显示盔甲栏'
		
		elif command == 'hideairsupplygui':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法控制界面'
					return
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hideairsupplygui",'cmdargs': cmdargs})
			if cmdargs[1]:
				args['return_msg_key'] = '已隐藏氧气条'
			else:
				args['return_msg_key'] = '已显示氧气条'
		
		elif command == 'setinvitemexchange':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SetInvItemExchange(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '已交换物品'
		
		elif command == 'setinvitemnum':
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
			args['return_msg_key'] = '已设置物品数量'
		
		elif command == 'setitemdefenceangle':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置盾牌抵挡角度'
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
			args['return_msg_key'] = '已设置盾牌抵挡角度'
		
		elif command == 'setitemdurability':
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
			args['return_msg_key'] = '已设置物品耐久度'
				
		elif command == 'setitemmaxdurability':
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
			args['return_msg_key'] = '已设置物品最大耐久度'
			
		elif command == 'setitemtierlevel':
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
			args['return_msg_key'] = '已设置物品等级'
		
		elif command == 'setitemtierspeed':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			for i in cmdargs[0]:
				itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
				CFServer.CreateItem(i).SetItemTierSpeed(itemdata,cmdargs[1])
				CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
			args['return_msg_key'] = '已设置物品挖掘速度'
		
		elif command == 'setmaxstacksize':
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
				itemDict = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
				if itemDict:
					CFServer.CreateItem(i).SetMaxStackSize(itemDict,cmdargs[1])
					if CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i):
						args['return_msg_key'] = '已设置最大堆叠数量'
					else:
						args['return_failed'] = True
						args['return_msg_key'] = '设置失败'
				else:
					args['return_msg_key'] = '已设置最大堆叠数量'
		
		elif command == 'playerexhaustionratio':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置饥饿度消耗倍率'
					return
			if cmdargs[1] not in [0, 1, 2, 3, 4, 9]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的行为id'
				return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerExhaustionRatioByType(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '已设置玩家饥饿度消耗倍率'
		
		elif command == 'setsigntextstyle':
			x, y, z = cmdargs[0]
			r,g,b = cmdargs[2]
			lighting = cmdargs[4]
			if cmdargs[5] is True:
				side = 1
			else:
				side = 0
			if CFServer.CreateBlockEntity(levelId).SetSignTextStyle((intg(x), int(y), intg(z)), cmdargs[1], (r, g, b, cmdargs[3]), lighting, side):
				args['return_msg_key'] = '设置告示牌文本样式成功'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
			
		elif command == 'setsignblocktext':
			x, y, z = cmdargs[0]
			if cmdargs[3] is True:
				side = 1
			else:
				side = 0
			if CFServer.CreateBlockInfo(levelId).SetSignBlockText((intg(x), int(y), intg(z)), cmdargs[1], cmdargs[2], side):
				args['return_msg_key'] = '设置告示牌文本成功'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'

		elif command == 'setplayerinteracterange':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetPlayerInteracteRange(cmdargs[1])
			serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setplayerinteracterange", 'cmdargs': cmdargs})
			args['return_msg_key'] = '已设置触及距离'
		
		elif command == 'summonprojectile':
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
		
		elif command == 'setstepheight':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置'
					return
			if cmdargs[0]:
				for i in cmdargs[0]:
					CFServer.CreateAttr(i).SetStepHeight(cmdargs[1])
				args['return_msg_key'] = '已设置能迈过的最大高度'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		elif command == 'setsize':
			if cmdargs[0]:
				for i in cmdargs[0]:
					CFServer.CreateCollisionBox(i).SetSize((cmdargs[1],cmdargs[2]))
				args['return_msg_key'] = '已设置碰撞箱'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
			
		elif command == 'playerchatprefix':
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
			args['return_msg_key'] = '已设置玩家聊天前缀'

		elif command == 'writehealthtoscoreboard':
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
			args['return_msg_key'] = '已将生命值写入计分板'
			
		elif command == 'writehungertoscoreboard':
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
			args['return_msg_key'] = '已将饥饿值写入计分板'
			return	

		elif command == 'writearmortoscoreboard':
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
			args['return_msg_key'] = '已将盔甲值写入计分板'
		
		elif command == 'writespeedtoscoreboard':
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
			args['return_msg_key'] = '已将速度值写入计分板'
		
		elif command == 'executecb':
			success = CFServer.CreateBlockEntity(levelId).ExecuteCommandBlock((cmdargs[0], cmdargs[1], cmdargs[2]), cmdargs[3])
			if success:
				args['return_msg_key'] = '已执行命令方块'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '执行命令方块失败'
			
		elif command == 'setname':
			for i in cmdargs[0]:
				CFServer.CreateName(i).SetName(cmdargs[1])
			args['return_msg_key'] = '已设置名称'
		
		elif command == 'aicontrol':
			for i in cmdargs[0]:
				CFServer.CreateControlAi(i).SetBlockControlAi(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '已设置实体AI'
		
		compExtra = CFServer.CreateExtraData(levelId)
		params = compExtra.GetExtraData('parameters')

		if command == 'param':
			if variant == 0:
				if cmdargs[1] is None:
					args['return_msg_key'] = str(params)
				else:
					if type(params) == dict and params.has_key(cmdargs[1]):
						args['return_msg_key'] = "变量\"%s\"为 %s" % (cmdargs[1], params[cmdargs[1]])
					else:
						args['return_msg_key'] = "未知的变量\"%s\"" % (cmdargs[1])
						args['return_failed'] = True
						return
			elif variant == 2:
				if type(params) == dict and params.has_key(cmdargs[1]):
					args['return_msg_key'] = '删除变量成功'
					del params[cmdargs[1]]
					compExtra.SetExtraData('parameters', params)
				else:
					args['return_msg_key'] = "未知的变量\"%s\"" % (cmdargs[1])
					args['return_failed'] = True
					return
			elif variant == 1:
				args['return_msg_key'] = '修改变量成功'
				input2 = str(cmdargs[2])
				if type(params) == dict:
					params[cmdargs[1]] = input2
				else:
					params = {cmdargs[1]: input2}
				compExtra.SetExtraData('parameters', params)
			elif variant == 3:
				if not (type(params) == dict and params.has_key(cmdargs[1])):
					args['return_msg_key'] = "未知的变量\"%s\"" % (cmdargs[1])
					args['return_failed'] = True
					return
				if params[cmdargs[1]].replace(".","",1).isdigit():
					params[cmdargs[1]] = float(params[cmdargs[1]])
				elif not cmdargs[2] in ['加','乘']:
					args['return_msg_key'] = '操作符\"%s\"无法参与字符串运算' % (cmdargs[2])
					args['return_failed'] = True
					return
				if cmdargs[3].replace(".","",1).isdigit():
					cmdargs[3] = float(cmdargs[3])
				elif cmdargs[2] != "加":
					args['return_msg_key'] = '字符串\"%s\"无法参与%s运算' % (cmdargs[3], cmdargs[2])
					args['return_failed'] = True
					return
				if cmdargs[2] == '加':
					if not type(params[cmdargs[1]]) == type(cmdargs[3]) == int:
						params[cmdargs[1]] = str(params[cmdargs[1]])
						cmdargs[3] = str(cmdargs[3])
					params[cmdargs[1]] += cmdargs[3]
				elif cmdargs[2] == '乘':
					if cmdargs[3] != int(cmdargs[3]):
						args['return_msg_key'] = '\"%s\"无法用于重复字符串' % (cmdargs[3])
						args['return_failed'] = True
						return
					params[cmdargs[1]] *= int(cmdargs[3])
				elif cmdargs[2] == '除':
					params[cmdargs[1]] /= cmdargs[3]
				elif cmdargs[2] == '减':
					params[cmdargs[1]] -= cmdargs[3]
				elif cmdargs[2] == '乘方':
					params[cmdargs[1]] **= cmdargs[3]
				elif cmdargs[2] == '取余':	
					params[cmdargs[1]] %= cmdargs[3]
				elif cmdargs[2] == '整除':
					params[cmdargs[1]] //= cmdargs[3]
				params[cmdargs[1]] = str(params[cmdargs[1]])
				compExtra.SetExtraData('parameters', params)
				args['return_msg_key'] = '变量运算成功'

		elif command == 'kickt':
			for kickplayer in cmdargs[0]:
				compcmd.SetCommand('/kick ' + CFServer.CreateName(kickplayer).GetName() + ' ' + cmdargs[1], False)
			args['return_msg_key'] = '已踢出目标玩家'
				
		elif command == 'explode':
			for i in cmdargs[0]:
				position = CFServer.CreatePos(i).GetFootPos()
				CFServer.CreateExplosion(levelId).CreateExplosion(position,cmdargs[1],cmdargs[3],cmdargs[2],i,None)
			args['return_msg_key'] = '爆炸已创建'
			return
	
		elif command == 'explodebypos':
			if CFServer.CreateExplosion(levelId).CreateExplosion(cmdargs[0],cmdargs[1],cmdargs[3],cmdargs[2],None,None):
				args['return_msg_key'] = '爆炸已创建'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '爆炸创建失败'
	
		elif command == "console":
			cmd = cmdargs[0]
			if cmd.startswith("/"):
				cmd = cmd[1:]
			cmd2 = ""
			if compExtra.GetExtraData('parameters'):
				for i in cmd.split(" "):
					for ii in compExtra.GetExtraData('parameters').keys():
						index = i.find("param:%s" % (ii))
						if not index == -1:
							i = i.replace("param:%s" % (ii),compExtra.GetExtraData('parameters')[ii])
					cmd2 = "%s %s" % (cmd2, i)
			else:
				cmd2 = cmd
			print(cmd2.replace("'",'"'))
			compcmd.SetCommand("/" + cmd2.replace("'",'"'), False)
			args["return_msg_key"] = "已将指令处理后执行"
		
		elif command == 'addaroundentitymotion' or command == 'addaroundpointmotion':
			if len(cmdargs[1]) > 1 and command == 'addaroundentitymotion':
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
			args['return_msg_key'] = '已设置运动器'

		elif command == 'addvelocitymotion':
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
			args['return_msg_key'] = '已设置运动器'
		
		elif command == 'startmotion':
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
		
		elif command == 'stopmotion':
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
		
		elif command == 'removemotion':
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

		elif command == 'addenchant':
			args['return_msg_key'] = '添加失败'
			args['return_failed'] = True
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
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
					return
				if slotType == 0:
					if compItem.SpawnItemToPlayerInv(itemDict, i, slot):
						args['return_msg_key'] = '添加附魔成功'
						args['return_failed'] = False
				else:
					if compItem.SpawnItemToPlayerCarried(itemDict, i):
						args['return_msg_key'] = '添加附魔成功'
						args['return_failed'] = False

		elif command == 'addtrackmotion':
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
			args['return_msg_key'] = '已设置运动器'

		elif command == 'setactorcanburnbylightning':
			compGame.SetCanActorSetOnFireByLightning(cmdargs[0])
			args['return_msg_key'] = '设置成功'

		elif command == 'setblockcanburnbylightning':
			compGame.SetCanBlockSetOnFireByLightning(cmdargs[0])
			args['return_msg_key'] = '设置成功'

		elif command == 'cancelshearsdestoryblockspeedall':
			for i in cmdargs[0]:
				compItem = CFServer.CreateItem(i)
				compItem.CancelShearsDestoryBlockSpeedAll()
				args['return_msg_key'] = '取消成功'

		elif command == 'cancelshearsdestoryblockspeed':
			for i in cmdargs[0]:
				compItem = CFServer.CreateItem(i)
				if not compItem.CancelShearsDestoryBlockSpeed(cmdargs[1]):
					args['return_failed'] = True
					args['return_msg_key'] = '无效的命名空间id'
			args['return_msg_key'] = '取消成功'

		elif command == 'setshearsdestoryblockspeed':
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

		elif command == 'changeselectslot':
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

		elif command == 'forbidliquidflow':
			if compGame.ForbidLiquidFlow(cmdargs[0]):
				args['return_msg_key'] = '已成功修改液体流动性'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '修改失败'

		elif command == 'getuid':
			uid_dict = {}
			for i in cmdargs[0]:
				CompType = CFServer.CreateEngineType(i)
				if CompType.GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法获取uid'
					return
			for i in cmdargs[0]:
				playername = CFServer.CreateName(i).GetName()
				uid_dict[playername] = CFServer.CreateHttp(levelId).GetPlayerUid(i)
			args['return_msg_key'] = '获取到的UID为%s' % (uid_dict)
			# serversystem.NotifyToMultiClients(list(cmdargs[0]), "CustomCommandClient", {'cmd':"getuid", 'origin': playerId})

		elif command == 'givewithnbt':
			args['return_msg_key'] = '给予失败'
			args['return_failed'] = True
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法给予物品'
					return
			result = checkjson(cmdargs[1], playerId)
			if result[1]:
				args['return_failed'] = result[1]
				args['return_msg_key'] = result[0]
				return
			itemDict = result[0]
			for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
				itemDict.pop(i,False) #删去多余键值对(这些已被弃用)
			for i in cmdargs[0]:
				if CFServer.CreateItem(i).SpawnItemToPlayerInv(unicode_convert(itemDict), i):
					args['return_failed'] = False
					args['return_msg_key'] = '成功给予物品'
			
		elif command == 'spawnitemtocontainer':
			args['return_msg_key'] = '给予失败'
			args['return_failed'] = True
			x = intg(cmdargs[2][0])
			y = int(cmdargs[2][1])
			z = intg(cmdargs[2][2])
			itemDict = compItemWorld.GetContainerItem((x, y, z,), cmdargs[1], cmdargs[3], True)
			result = checkjson(cmdargs[0], playerId)
			if result[1]:
				args['return_failed'] = result[1]
				args['return_msg_key'] = result[0]
				return
			itemDict2 = result[0]
			for i in [('durability',0),('customTips',''),('extraId',''),('newAuxValue',0),('userData',None),('showInHand',True)]:
				if not itemDict2.has_key(i[0]):
					itemDict2[i[0]] = i[1]
			if itemDict:
				for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
					itemDict.pop(i) #删去多余键值对(这些已被弃用)
					itemDict2.pop(i, False)
				countOrign = itemDict.pop('count')
			else: countOrign = 0
			countAdd = itemDict2.pop('count', 1)
			if ((not itemDict) or itemDict == itemDict2) and countOrign+countAdd <= 64:
				itemDict2['count'] = countOrign+countAdd
				if compItemWorld.SpawnItemToContainer(itemDict2, cmdargs[1], (x, y, z,), args['origin']['dimension'] if cmdargs[3] is None else cmdargs[3]):
					args['return_msg_key'] = '成功给予物品'
					args['return_failed'] = False
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '槽位已满'

		elif command == 'spawnitemtoenderchest':
			args['return_msg_key'] = '给予失败'
			args['return_failed'] = True
			for player in cmdargs[2]:
				if CFServer.CreateEngineType(player).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法给予物品'
					return
			result = checkjson(cmdargs[0], playerId)
			if result[1]:
				args['return_failed'] = True
				args['return_msg_key'] = result[0]
				return
			itemDict2 = result[0]
			for i in [('durability',0),('customTips',''),('extraId',''),('newAuxValue',0),('userData',None),('showInHand',True)]:
				if not itemDict2.has_key(i[0]):
					itemDict2[i[0]] = i[1]
			countAdd = itemDict2.pop('count', 1)
			for player in cmdargs[2]:
				compItem = CFServer.CreateItem(player)
				itemDict = compItem.GetEnderChestItem(player, cmdargs[1], True)
				if itemDict:
					for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
						itemDict.pop(i) #删去多余键值对(这些已被弃用)
						itemDict2.pop(i, False)
					countOrign = itemDict.pop('count')
				else: countOrign = 0
				if ((not itemDict) or itemDict == itemDict2) and countOrign+countAdd <= 64:
					itemDict2['count'] = countOrign+countAdd
					if compItem.SpawnItemToEnderChest(itemDict2, cmdargs[1]):
						args['return_msg_key'] = '成功给予物品'
						args['return_failed'] = False
				else:
					args['return_failed'] = True
					args['return_msg_key'] = '槽位已满'

		elif command == 'replaceitemtocarried':
			args['return_msg_key'] = '替换失败'
			args['return_failed'] = True
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法给予物品'
					return
			result = checkjson(cmdargs[1], playerId)
			if result[1]:
				args['return_failed'] = True
				args['return_msg_key'] = result[0]
				return
			itemDict = result[0]
			for i in cmdargs[0]:
				if CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i):
					args['return_msg_key'] = '成功替换物品'
					args['return_failed'] = False

		elif command == 'removeenchant':
			args['return_msg_key'] = '删除失败'
			args['return_failed'] = True
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法访问背包'
					return
			for i in cmdargs[0]:
				if CFServer.CreateItem(i).RemoveEnchantToInvItem(cmdargs[2], cmdargs[1]):
					args['return_msg_key'] = '删除成功'
					args['return_failed'] = False

		elif command == 'resetmotion':
			for i in cmdargs[0]:
				CompType = CFServer.CreateEngineType(i)
				CompMotion = CFServer.CreateActorMotion(i)
				if CompType.GetEngineTypeStr() == 'minecraft:player':
					CompMotion.SetPlayerMotion((0, 0, 0))
				else:
					CompMotion.ResetMotion()
			args['return_msg_key'] = '重置运动成功'
	
		elif command == 'setleashholder':
			if len(cmdargs[0]) == 1:
				for i in cmdargs[1]:
					compEntityD = CFServer.CreateEntityDefinitions(i)
					compEntityD.SetLeashHolder(cmdargs[0])
				args['return_msg_key'] = '正在尝试拴住实体'
			else:
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				args['return_failed'] = True
	
		elif command == 'setlootdropped':
			for i in cmdargs[0]:
				compEntityD = CFServer.CreateEntityDefinitions(i)
				compEntityD.SetLootDropped(cmdargs[1])
			args['return_msg_key'] = '设置成功'

		elif command == 'setmaxairsupply':
			for i in cmdargs[0]:
				compBrea = CFServer.CreateBreath(i)
				compBrea.SetMaxAirSupply(cmdargs[1])
			args['return_msg_key'] = '设置成功'

		elif command == 'knockback':
			for i in cmdargs[0]:
				CFServer.CreateAction(i).SetMobKnockback(cmdargs[1], cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5])
			args['return_msg_key'] = '已击飞实体'
	
		elif command == 'setmotion':
			for i in cmdargs[0]:
				CompType = CFServer.CreateEngineType(i)
				CompMotion = CFServer.CreateActorMotion(i)
				if CompType.GetEngineTypeStr() == 'minecraft:player':
					CompMotion.SetPlayerMotion(cmdargs[1])
				else:
					CompMotion.SetMotion(cmdargs[1])
			args['return_msg_key'] = '设置动量成功'
	
		elif command == 'setopencontainersability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置打开容器的权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetOpenContainersAbility(cmdargs[1])
			args['return_msg_key'] = '已设置打开容器的权限'
		
		elif command == 'setoperatedoorability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置开门权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetOperateDoorsAndSwitchesAbility(cmdargs[1])
			args['return_msg_key'] = '已设置开门权限'

		elif command == 'setorbexperience':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:xp_orb':
					args['return_failed'] = True
					args['return_msg_key'] = '非经验球实体无法设置经验值'
					return
			for i in cmdargs[0]:
				compAttr = CFServer.CreateExp(i)
				compAttr.SetOrbExperience(cmdargs[1])
			args['return_msg_key'] = '设置成功'
	
		elif command == 'setpersistent':
			for i in cmdargs[0]:
				compAttr = CFServer.CreateAttr(i)
				compAttr.SetPersistent(cmdargs[1])
			args['return_msg_key'] = '设置成功'

		elif command == 'setpistonmaxinteractioncount':
			if compGame.SetPistonMaxInteractionCount(cmdargs[0]):
				args['return_msg_key'] = '设置成功'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的数值'
	
		elif command == 'setplayeruiitem':
			args['return_msg_key'] = '给予失败'
			args['return_failed'] = True
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置界面内物品'
					return
			result = checkjson(cmdargs[2], playerId)
			if result[1]:
				args['return_failed'] = result[1]
				args['return_msg_key'] = result[0]
				return
			itemDict = result[0]
			for i in cmdargs[0]:
				if CFServer.CreateItem(i).SetPlayerUIItem(i, cmdargs[1], itemDict, cmdargs[3]):
					args['return_msg_key'] = '已设置玩家界面内物品'
					args['return_failed'] = False

		elif command == 'if':
			if cmdargs[2] is None:
				result = [compcmd.SetCommand(cmdargs[0].replace("'",'"'), playerId), compcmd.SetCommand(cmdargs[2], playerId)]
			else:
				result = [compcmd.SetCommand(cmdargs[0].replace("'",'"'), playerId), compcmd.SetCommand(cmdargs[2].replace("'",'"'), playerId)]
			if cmdargs[1] == 'not':
				if result[0]:
					args['return_failed'] = True
					args['return_msg_key'] = '运算符成立(%s)' % (result[0])
				else:
					args['return_msg_key'] = '运算符不成立(%s)' % (result[0])
			elif cmdargs[1] == 'and':
				if result[0] and result[1]:
					args['return_msg_key'] = '运算符成立(%s,%s)' % (result[0], result[1])
				else:
					args['return_failed'] = True
					args['return_msg_key'] = '运算符不成立(%s,%s)' % (result[0], result[1])
			elif cmdargs[1] == 'or':
				if result[0] or result[1]:
					args['return_msg_key'] = '运算符成立(%s,%s)' % (result[0], result[1])
				else:
					args['return_failed'] = True
					args['return_msg_key'] = '运算符不成立(%s,%s)' % (result[0], result[1])
			elif cmdargs[1] == 'xor':
				if result[0] != result[1]:
					args['return_msg_key'] = '运算符成立(%s,%s)' % (result[0], result[1])
				else:
					args['return_failed'] = True
					args['return_msg_key'] = '运算符不成立(%s,%s)' % (result[0], result[1])
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '未知的逻辑运算符'
			
		elif command == 'setteleportability':
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置传送权限'
					return
			for i in cmdargs[0]:
				CFServer.CreatePlayer(i).SetTeleportAbility(cmdargs[1])
			args['return_msg_key'] = '已设置传送权限'

		elif command == 'settradelevel':
			for i in cmdargs[0]:
				if not CFServer.CreateEngineType(i).GetEngineTypeStr() in ['minecraft:villager', 'minecraft:villager_v2']:
					args['return_failed'] = True
					args['return_msg_key'] = '非村民实体无法设置交易等级'
					return
			for i in cmdargs[0]:
				CFServer.CreateEntityDefinitions(i).SetTradeLevel(cmdargs[1])
			args['return_msg_key'] = '已设置交易等级'	
		
		elif command == 'setvignette':
			for i in cmdargs[1]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法拥有屏幕暗角'
					return	
			if variant == 0:
				args['return_msg_key'] = '已将玩家的屏幕暗角中心设为 %f, %f' % (cmdargs[2], cmdargs[3])
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignettecenter",'cmdargs': cmdargs})
			if variant == 1:
				args['return_msg_key'] = '已将玩家的屏幕暗角半径设为 %f' % (cmdargs[2])
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignetteradius",'cmdargs': cmdargs})
			if variant == 2:
				args['return_msg_key'] = '已将玩家的屏幕暗角颜色设为 %d, %d, %d' % (cmdargs[2][0], cmdargs[2][1], cmdargs[2][2])
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignettecolor",'cmdargs': cmdargs})
			if variant == 3:
				args['return_msg_key'] = '已将玩家的屏幕暗角平滑度设为 %f' % (cmdargs[2])
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignettesmooth",'cmdargs': cmdargs})
			if variant == 4:
				args['return_msg_key'] = '已%s玩家的屏幕暗角' % ('启用' if cmdargs[2] else '禁用')
				serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignette",'cmdargs': cmdargs})
		return
		
		if command == 'setblockbasicinfo':#暂时没得用
			args['return_failed'] = True
			args['return_msg_key'] = '设置失败'
			if CFServer.CreateBlockInfo(levelId).SetBlockBasicInfo(cmdargs[0], {'destroyTime':cmdargs[1], 'explosionResistance':cmdargs[2]}, cmdargs[3]):
				args['return_failed'] = False
				args['return_msg_key'] = '设置成功'
			return

		elif command == 'sit':#病友
			for i in cmdargs[0]:
				if CFServer.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:panda':
					args['return_failed'] = True
					args['return_msg_key'] = '熊猫无法坐下'
					return
			for i in cmdargs[0]:
				CFServer.CreateEntityDefinitions(i).SetSitting(cmdargs[1])
			args['return_msg_key'] = '已设置坐下状态'

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
