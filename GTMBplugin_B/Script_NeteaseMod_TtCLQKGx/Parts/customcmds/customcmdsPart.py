# -*- coding: utf-8 -*-
from __future__ import print_function
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
import json
import random
CFServer = serverApi.GetEngineCompFactory()
CFClient = clientApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compcmd = CFServer.CreateCommand(levelId)
compGame = CFServer.CreateGame(levelId)
compItemWorld = CFServer.CreateItem(levelId)
compExtra = CFServer.CreateExtraData(levelId)

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
		# 客户端
		self.clientcustomcmd = {
			"setplayerinteracterange":self.client_setplayerinteracterange,
			"hideairsupplygui":self.client_hideairsupplygui,
			"hidearmorgui":self.client_hidearmorgui,
			"hidecrosshairgui":self.client_hidecrosshairgui,
			"hideexpgui":self.client_hideexpgui,
			"hidefoldgui":self.client_hidefoldgui,
			"hidehealthgui":self.client_hidehealthgui,
			"hidehorsehealthgui":self.client_hidehorsehealthgui,
			"hidehudgui":self.client_hidehudgui,
			"hidehungergui":self.client_hidehungergui,
			"hideslotbargui":self.client_hideslotbargui,
			"openfoldgui":self.client_openfoldgui,
			"setcanpausescreen":self.client_setcanpausescreen,
			"setcolorbrightness":self.client_setcolorbrightness,
			"setcolorcontrast":self.client_setcolorcontrast,
			"setcolorsaturation":self.client_setcolorsaturation,
			"setcolortint":self.client_setcolortint,
			"setcompassentity":self.client_setcompassentity,
			"setcompasstarget":self.client_setcompasstarget,
			"setvignettecenter":self.client_setvignettecenter,
			"setvignetteradius":self.client_setvignetteradius,
			"setvignettecolor":self.client_setvignettecolor,
			"setvignettesmooth":self.client_setvignettesmooth,
			"setvignette":self.client_setvignette
		}

		# 服务端
		self.servercustomcmd = {
			"setentityonfire":self.setentityonfire,
			"setcurrentairsupply":self.setcurrentairsupply,
			"setcompasstarget":self.setcompasstarget,
			"setcompassentity":self.setcompassentity,
			"setcolor":self.setcolor,
			"setchestitemnum":self.setchestitemnum,
			"setchestboxitemexchange":self.setchestboxitemexchange,
			"setcanpausescreen":self.setcanpausescreen,
			"setcanotherplayerride":self.setcanotherplayerride,
			"setattackplayersability":self.setattackplayersability,
			"setattackmobsability":self.setattackmobsability,
			"setattackdamage":self.setattackdamage,
			"setplayerrespawnpos":self.setplayerrespawnpos,
			"setplayerhealthlevel":self.setplayerhealthlevel,
			"setplayerstarvelevel":self.setplayerstarvelevel,
			"setplayerhunger":self.setplayerhunger,
			"setplayerattackspeedamplifier":self.setplayerattackspeedamplifier,
			"setplayerjumpable":self.setplayerjumpable,
			"setplayermovable":self.setplayermovable,
			"setplayernaturalstarve":self.setplayernaturalstarve,
			"setplayerprefixandsuffixname":self.setplayerprefixandsuffixname,
			"setplayermaxexhaustionvalue":self.setplayermaxexhaustionvalue,
			"setplayerhealthtick":self.setplayerhealthtick,
			"setplayerstarvetick":self.setplayerstarvetick,
			"sethurtcd":self.sethurtcd,
			"setattacktarget":self.setattacktarget,
			"resetattacktarget":self.resetattacktarget,
			"setbanplayerfishing":self.setbanplayerfishing,
			"setactorcanpush":self.setactorcanpush,
			"setactorcollidable":self.setactorcollidable,
			"setmineability":self.setmineability,
			"setbuildability":self.setbuildability,
			"setcontrol":self.setcontrol,
			"setpickuparea":self.setpickuparea,
			"setlevelgravity":self.setlevelgravity,
			"setjumppower":self.setjumppower,
			"setgravity":self.setgravity,
			"setworldspawnd":self.setworldspawnd,
			"playeruseitemtopos":self.playeruseitemtopos,
			"playeruseitemtoentity":self.playeruseitemtoentity,
			"playerdestoryblock": self.playerdestoryblock,
			"openworkbench":self.openworkbench,
			"openfoldgui":self.openfoldgui,
			"setimmunedamage":self.setimmunedamage,
			"hideslotbargui":self.hideslotbargui,
			"hidehungergui":self.hidehungergui,
			"hidehudgui":self.hidehudgui,
			"hidehorsehealthgui":self.hidehorsehealthgui,
			"hidehealthgui":self.hidehealthgui,
			"hidefoldgui":self.hidefoldgui,
			"hideexpgui":self.hideexpgui,
			"hidecrosshairgui":self.hidecrosshairgui,
			"hidearmorgui":self.hidearmorgui,
			"hideairsupplygui":self.hideairsupplygui,
			"setinvitemexchange":self.setinvitemexchange,
			"setinvitemnum":self.setinvitemnum,
			"setitemdefenceangle":self.setitemdefenceangle,
			"setitemdurability":self.setitemdurability,
			"setitemmaxdurability":self.setitemmaxdurability,
			"setitemtierlevel":self.setitemtierlevel,
			"setitemtierspeed":self.setitemtierspeed,
			"setmaxstacksize":self.setmaxstacksize,
			"playerexhaustionratio":self.playerexhaustionratio,
			"setsigntextstyle":self.setsigntextstyle,
			"setsignblocktext":self.setsignblocktext,
			"setplayerinteracterange":self.setplayerinteracterange,
			"summonprojectile":self.summonprojectile,
			"setstepheight":self.setstepheight,
			"setsize":self.setsize,
			"playerchatprefix":self.playerchatprefix,
			"writehealthtoscoreboard":self.writehealthtoscoreboard,
			"writehungertoscoreboard":self.writehungertoscoreboard,
			"writearmortoscoreboard":self.writearmortoscoreboard,
			"writespeedtoscoreboard":self.writespeedtoscoreboard,
			"executecb":self.executecb,
			"setname":self.setname,
			"aicontrol":self.aicontrol,
			"param":self.param,
			"kickt":self.kickt,
			"explode":self.explode,
			"explodebypos":self.explodebypos,
			"console":self.console,
			"addaroundentitymotion":self.addaroundentitymotion,
			"addaroundpointmotion":self.addaroundpointmotion,
			"addvelocitymotion":self.addvelocitymotion,
			"startmotion":self.startmotion,
			"stopmotion":self.stopmotion,
			"removemotion":self.removemotion,
			"addenchant":self.addenchant,
			"addtrackmotion":self.addtrackmotion,
			"setactorcanburnbylightning":self.setactorcanburnbylightning,
			"setblockcanburnbylightning":self.setblockcanburnbylightning,
			"cancelshearsdestoryblockspeedall":self.cancelshearsdestoryblockspeedall,
			"cancelshearsdestoryblockspeed":self.cancelshearsdestoryblockspeed,
			"setshearsdestoryblockspeed":self.setshearsdestoryblockspeed,
			"changeselectslot":self.changeselectslot,
			"forbidliquidflow":self.forbidliquidflow,
			"getuid":self.getuid,
			"givewithnbt":self.givewithnbt,
			"spawnitemtocontainer":self.spawnitemtocontainer,
			"spawnitemtoenderchest":self.spawnitemtoenderchest,
			"replaceitemtocarried":self.replaceitemtocarried,
			"removeenchant":self.removeenchant,
			"resetmotion":self.resetmotion,
			"setleashholder":self.setleashholder,
			"setleashholder":self.setleashholder,
			"setlootdropped":self.setlootdropped,
			"setmaxairsupply":self.setmaxairsupply,
			"knockback":self.knockback,
			"setmotion":self.setmotion,
			"setopencontainersability":self.setopencontainersability,
			"setoperatedoorability":self.setoperatedoorability,
			"setorbexperience":self.setorbexperience,
			"setpersistent":self.setpersistent,
			"setpistonmaxinteractioncount":self.setpistonmaxinteractioncount,
			"setplayeruiitem":self.setplayeruiitem,
			"if":self._if,
			"setteleportability":self.setteleportability,
			"settradelevel":self.settradelevel,
			"setvignette":self.setvignette,
		}
		
	
	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		global clientsystem
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
			data = handler(args)
		clientsystem.NotifyToServer("customCmdReturn", data)
	# 客户端函数部分由此开始
	def client_setplayerinteracterange(self, args):
		clientApi.GetEngineCompFactory().CreatePlayer(localPlayerId).SetPickRange(args['cmdargs'][1])
	def client_hideairsupplygui(self, args):
		clientApi.HideAirSupplyGUI(args['cmdargs'][1])
	def client_hidearmorgui(self, args):	
		clientApi.HideArmorGui(args['cmdargs'][1])
	def client_hidecrosshairgui(self, args):
		clientApi.HideCrossHairGUI(args['cmdargs'][1])
	def client_hideexpgui(self, args):
		clientApi.HideExpGui(args['cmdargs'][1])
	def client_hidefoldgui(self, args):
		clientApi.HideFoldGUI(args['cmdargs'][1])
	def client_hidehealthgui(self, args):
		clientApi.HideHealthGui(args['cmdargs'][1])
	def client_hidehorsehealthgui(self, args):
		clientApi.HideHorseHealthGui(args['cmdargs'][1])
	def client_hidehudgui(self, args):
		clientApi.HideHudGUI(args['cmdargs'][1])
	def client_hidehungergui(self, args):
		clientApi.HideHungerGui(args['cmdargs'][1])
	def client_hideslotbargui(self, args):
		clientApi.HideSlotBarGui(args['cmdargs'][1])
	def client_openfoldgui(self, args):
		clientApi.OpenFoldGui()
	def client_setcanpausescreen(self, args):
		CFClient.CreateOperation(levelId).SetCanPauseScreen(args['cmdargs'][1])
	def client_setcolorbrightness(self, args):
		CFClient.CreatePostProcess(levelId).SetColorAdjustmentBrightness(args['cmdargs'][2])
	def client_setcolorcontrast(self, args):
		CFClient.CreatePostProcess(levelId).SetColorAdjustmentContrast(args['cmdargs'][2])
	def client_setcolorsaturation(self, args):
		CFClient.CreatePostProcess(levelId).SetColorAdjustmentSaturation(args['cmdargs'][2])
	def client_setcolortint(self, args):
		CFClient.CreatePostProcess(levelId).SetColorAdjustmentTint(args['cmdargs'][2],args['cmdargs'][3])
	def client_setcompassentity(self, args):
		CFClient.CreateItem(localPlayerId).SetCompassEntity(args['cmdargs'][1][0])
	def client_setcompasstarget(self, args):
		CFClient.CreateItem(localPlayerId).SetCompassTarget(args['cmdargs']['x'],args['cmdargs']['y'],args['cmdargs']['z'])
	def client_setvignettecenter(self, args):
		CFClient.CreatePostProcess(levelId).SetVignetteCenter((args['cmdargs'][2], args['cmdargs'][3]))
	def client_setvignetteradius(self, args):
		CFClient.CreatePostProcess(levelId).SetVignetteRadius(args['cmdargs'][2])
	def client_setvignettecolor(self, args):
		CFClient.CreatePostProcess(levelId).SetVignetteRGB(args['cmdargs'][2])
	def client_setvignettesmooth(self, args):
		CFClient.CreatePostProcess(levelId).SetVignetteSmoothness(args['cmdargs'][2])
	def client_setvignette(self, args):
		CFClient.CreatePostProcess(levelId).SetEnableVignette(args['cmdargs'][2])
	# 客户端函数部分到此结束
	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		global serversystem
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "CustomCommandTriggerServerEvent", self, self.OnCustomCommand)
		serversystem.ListenForEvent("Minecraft", "preset", "customCmdReturn", self, self.OnReturn)
		PartBase.InitServer(self)

	def OnReturn(self, args):
		pass
		# 客户端返回
		#compMsg = CFServer.CreateMsg(args['target'])
		#compName = CFServer.CreateName(args['__id__'])

	def OnCustomCommand(self, args):
		cmdargs = []
		variant = args['variant']
		args_list = args["args"]
		cmdargs = [i["value"] for i in args_list]
		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None
		handler = self.servercustomcmd.get(args['command'])
		if handler:
			args['return_failed'],args['return_msg_key'] = handler(cmdargs,playerId,variant)

	# 服务端函数部分由此开始
	def setentityonfire(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateAttr(i).SetEntityOnFire(cmdargs[1],cmdargs[2])
		return False,'已设置实体着火'
	
	def setcurrentairsupply(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateBreath(i).SetCurrentAirSupply(cmdargs[1])
		return False,'已设置氧气储备值'
	
	def setcompasstarget(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置指南针指向'
		x,y,z = cmdargs[1]
		compassdata = {'x':intg(x),'y':int(y),'z':intg(z)}
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setcompasstarget",'cmdargs': compassdata})
		return False,'已设置指南针指向'

	def setcompassentity(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置指南针指向'
		if len(cmdargs[1]) > 1:
			return True,'只允许一个实体,但提供的选择器允许多个实体'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setcompassentity",'cmdargs': cmdargs})
		return False,'已设置指南针指向'
		
	def setcolor(self, cmdargs, playerId, variant):
		for i in cmdargs[1]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置屏幕色彩'
		if variant == 3:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolortint",'cmdargs': cmdargs})
			return False,'已设置玩家屏幕色调'
		elif variant == 2:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolorsaturation",'cmdargs': cmdargs})
			return False,'已设置玩家屏幕色彩饱和度'
		elif variant == 1:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolorcontrast",'cmdargs': cmdargs})
			return False,'已设置玩家屏幕色彩对比度'
		else:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setcolorbrightness",'cmdargs': cmdargs})
			return False,'已设置玩家屏幕色彩亮度'
	
	def setchestitemnum(self, cmdargs, playerId, variant):
		x,y,z = cmdargs[0]
		xyz = (intg(x),int(y),intg(z))
		if CFServer.CreateChestBlock(levelId).SetChestBoxItemNum(None,xyz,cmdargs[1],cmdargs[2],cmdargs[3]['id']):
			return False,'已设置箱子物品数量'
		else:
			return True,'设置失败'
	
	def setchestboxitemexchange(self, cmdargs, playerId, variant):
		x,y,z = cmdargs[0]
		pid = CFServer.CreateEntityComponent(levelId).GetEntitiesBySelector("@r")[0]
		if CFServer.CreateChestBlock(pid).SetChestBoxItemExchange(pid,(intg(x),int(y),intg(z)),cmdargs[1],cmdargs[2]):
			return False,'已交换箱子物品'
		else:
			return True,'交换失败'
	
	def setcanpausescreen(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置暂停权限'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setcanpausescreen",'cmdargs': cmdargs})
		return False,'已设置玩家暂停权限'

	def setcanotherplayerride(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateRide(i).SetCanOtherPlayerRide(i,cmdargs[1])
		return False,'已设置骑乘权限'
	
	def setattackplayersability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetAttackPlayersAbility(cmdargs[1])
		return False,'已设置玩家pvp权限'
	
	def setattackmobsability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetAttackMobsAbility(cmdargs[1])
		return False,'已设置玩家攻击生物权限'

	def setattackdamage(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			itemDict = compItem.GetPlayerItem(2, 0, True)
			if compItem.SetAttackDamage(itemDict, cmdargs[1]):
				compItem.SpawnItemToPlayerCarried(itemDict,i)
		return False,'已设置玩家手持物品攻击伤害'

	def setplayerrespawnpos(self, cmdargs, playerId, variant):
		x, y, z = cmdargs[1]
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置重生点'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerRespawnPos((intg(x),int(y),intg(z)),cmdargs[2]['id'])
		return False,'已设置玩家重生点'
	
	def setplayerhealthlevel(self, cmdargs, playerId, variant):
		if cmdargs[1] < 0 or cmdargs[1] > 20:
			return True,'无效的回血临界值'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置回血临界值'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerHealthLevel(cmdargs[1])
			return False,'已设置玩家回血临界值'
	
	def setplayerstarvelevel(self, cmdargs, playerId, variant):
		if cmdargs[1] < 0 or cmdargs[1] > 20:
			return True,'无效的扣血临界值'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置扣血临界值'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerStarveLevel(cmdargs[1])
		return False,'已设置玩家扣血临界值'
	
	def setplayerhunger(self, cmdargs, playerId, variant):
		if cmdargs[1] < 0 or cmdargs[1] > 20:
			return True,'无效的饥饿度'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置饥饿度'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerHunger(cmdargs[1])
		return False,'已设置玩家饥饿度'
	
	def setplayerattackspeedamplifier(self, cmdargs, playerId, variant):
		if cmdargs[1] < 0.5 or cmdargs[1] > 2.0:
			return True,'无效的倍率'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置攻击速度倍率'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerAttackSpeedAmplifier(cmdargs[1])
		return False,'已设置玩家攻击速度倍率'
	
	def setplayerjumpable(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置跳跃权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerJumpable(cmdargs[1])
		return False,'已设置玩家跳跃权限'
	
	def setplayermovable(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置移动权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerMovable(cmdargs[1])
		return False,'已设置玩家移动权限'
	
	def setplayernaturalstarve(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置是否饥饿掉血'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerNaturalStarve(cmdargs[1])
		return False,'已设置玩家是否饥饿掉血'
	
	def setplayerprefixandsuffixname(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置前缀和后缀名'
		for i in cmdargs[0]:
			CFServer.CreateName(i).SetPlayerPrefixAndSuffixName(cmdargs[1],'§r',cmdargs[2],'§r')
		return False,'已设置前缀和后缀名'
	
	def setplayermaxexhaustionvalue(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置饥饿最大消耗度'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerMaxExhaustionValue(cmdargs[1])
		return False,'已设置玩家饥饿最大消耗度'
	
	def setplayerhealthtick(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置自然回血速度'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerHealthTick(cmdargs[1])
		return False, '已设置玩家自然回血速度'

	def setplayerstarvetick(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置自然扣血速度'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerStarveTick(cmdargs[1])
		return False,'已设置玩家自然扣血速度'

	def sethurtcd(self, cmdargs, playerId, variant):
		if compGame.SetHurtCD(cmdargs[0]):
			return False,'已设置全局受击间隔'
		else:
			return True,'设置失败'
	
	def setattacktarget(self, cmdargs, playerId, variant):
		if len(cmdargs[1]) != 1:
			return True,'只允许一个实体,但提供的选择器允许多个实体'
		attackTargetId = cmdargs[1][0]
		for i in cmdargs[0]:
			CFServer.CreateAction(i).SetAttackTarget(attackTargetId)
		return False,'已设置仇恨目标'
	
	def resetattacktarget(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateAction(i).ResetAttackTarget()
		return False,'成功重置仇恨目标'
	
	def setbanplayerfishing(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置钓鱼权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetBanPlayerFishing(cmdargs[1])
		return False,'已设置钓鱼权限'
	
	def setactorcanpush(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateActorPushable(i).SetActorPushable(cmdargs[1])
		return False,'已设置实体推动行为'
	
	def	setactorcollidable(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateActorCollidable(i).SetActorCollidable(cmdargs[1])
		return True,'已设置实体碰撞行为'
	
	def setmineability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置挖掘权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetMineAbility(cmdargs[1])
		return False,'已设置挖掘权限'
	
	def setbuildability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置放置权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetBuildAbility(cmdargs[1])
		return False,'已设置放置权限'
	
	def setcontrol(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateRide(i).SetControl(i,cmdargs[1])
		return False,'已设置'
	
	def setpickuparea(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置拾取范围'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPickUpArea(cmdargs[1])
		return False,'已设置拾取范围'
	
	def setlevelgravity(self, cmdargs, playerId, variant):
		return not compGame.SetLevelGravity(cmdargs[0]),'已设置世界重力'
	
	def setjumppower(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateGravity(i).SetJumpPower(cmdargs[1])
		return False,'已设置跳跃力度'
	
	def setgravity(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateGravity(i).SetGravity(cmdargs[1])
		return False,'已设置重力'
	
	def setworldspawnd(self, cmdargs, playerId, variant):
		x, y, z = cmdargs[1]
		if compGame.SetSpawnDimensionAndPosition(cmdargs[0]['id'], (intg(x),int(y),intg(z))):
			return False, '已设置世界出生点'
		else:
			return True,'设置失败'
		
	def playeruseitemtopos(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法使用方块'
		if cmdargs[2] not in [0,1,2,3,4,5]:
			return True,'无效的朝向'
		x, y, z = cmdargs[1]
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).PlayerUseItemToPos((intg(x),int(y),intg(z)),cmdargs[3],cmdargs[4],cmdargs[2])
		return False,'已尝试使用物品'
	
	def playeruseitemtoentity(self, cmdargs, playerId, variant):
		if len(cmdargs[1]) != 1:
			return True,'只允许一个实体,但提供的选择器允许多个实体'
		entityId = cmdargs[1][0]
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置使用物品'
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).PlayerUseItemToEntity(entityId)
		return False,'已尝试使用物品'
	
	def playerdestoryblock(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法破坏方块'
		x, y, z = cmdargs[1]
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).PlayerDestoryBlock((intg(x),int(y),intg(z)),cmdargs[2],cmdargs[3])
		return False,'已尝试破坏方块'
	
	def openworkbench(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法打开工作台'
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).OpenWorkBench()
		return False,'已打开工作台界面'
	
	def openfoldgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法打开下拉界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"openfoldgui",'cmdargs': cmdargs})
		return False,'已打开下拉界面'
	
	def setimmunedamage(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateHurt(i).ImmuneDamage(cmdargs[1])
		return False,'设置伤害免疫成功'
	
	def hideslotbargui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hideslotbargui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏工具栏'
		else:
			return False,'已显示工具栏'
	
	def hidehungergui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehungergui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏饱食度栏'
		else:
			return False,'已显示饱食度栏'
	
	def hidehudgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehudgui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏所有界面'
		else:
			return False,'已显示所有界面'
	
	def hidehorsehealthgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehorsehealthgui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏坐骑血量界面'
		else:
			return False,'已显示坐骑血量界面'
	
	def hidehealthgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidehealthgui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False, '已隐藏血条'
		else:
			return False,'已显示血条'
	
	def hidefoldgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidefoldgui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False, '已隐藏下拉界面'
		else:
			return False, '已显示下拉界面'
	
	def hideexpgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hideexpgui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏经验条'
		else:
			return False,'已显示经验条'
	
	def hidecrosshairgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidecrosshairgui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏十字准星'
		else:
			return False,'已显示十字准星'
	
	def hidearmorgui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hidearmorgui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏盔甲栏'
		else:
			return False,'已显示盔甲栏'
	
	def hideairsupplygui(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法控制界面'
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"hideairsupplygui",'cmdargs': cmdargs})
		if cmdargs[1]:
			return False,'已隐藏氧气条'
		else:
			return False,'已显示氧气条'
	
	def setinvitemexchange(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetInvItemExchange(cmdargs[1], cmdargs[2])
		return False,'已交换物品'
	
	def setinvitemnum(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		if cmdargs[2] < 0 or cmdargs[2] > 64:
			return True,'无效的物品数量'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetInvItemNum(cmdargs[1], cmdargs[2])
		return False,'已设置物品数量'
	
	def setitemdefenceangle(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置盾牌抵挡角度'
		if cmdargs[1] not in [0,1,2,3]:
			return True,'无效的位置id'
		if cmdargs[3] < 0 or cmdargs[3] > 180 or cmdargs[4] < 0 or cmdargs[4] > 180:
			return True,'无效的角度'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetItemDefenceAngle(cmdargs[1],cmdargs[2],cmdargs[3],cmdargs[4])
		return False,'已设置盾牌抵挡角度'
	
	def setitemdurability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True,'无效的耐久度'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetItemDurability(2,0,cmdargs[1])
		return False,'已设置物品耐久度'
			
	def setitemmaxdurability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True,'无效的耐久度'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetItemMaxDurability(2,0,cmdargs[1],True)
		return False,'已设置物品最大耐久度'
		
	def setitemtierlevel(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		if cmdargs[1] not in [0,1,2,3,4]:
			return True,'无效的等级'
		for i in cmdargs[0]:
			itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
			CFServer.CreateItem(i).SetItemTierLevel(itemdata,cmdargs[1])
			CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False,'已设置物品等级'
	
	def setitemtierspeed(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		for i in cmdargs[0]:
			itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
			CFServer.CreateItem(i).SetItemTierSpeed(itemdata,cmdargs[1])
			CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False,'已设置物品挖掘速度'
	
	def setmaxstacksize(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		if cmdargs[1] < 1 or cmdargs[1] > 64:
			return True,'无效的堆叠数量'
		for i in cmdargs[0]:
			itemDict = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
			if itemDict:
				CFServer.CreateItem(i).SetMaxStackSize(itemDict,cmdargs[1])
				if CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i):
					return False,'已设置最大堆叠数量'
				else:
					return True,'设置失败'
			else:
				return False,'已设置最大堆叠数量'
	
	def playerexhaustionratio(self,cmdargs,playerId,variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置饥饿度消耗倍率'
		if cmdargs[1] not in [0, 1, 2, 3, 4, 9]:
			return True,'无效的行为id'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerExhaustionRatioByType(cmdargs[1], cmdargs[2])
		return False,'已设置玩家饥饿度消耗倍率'
	
	def setsigntextstyle(self, cmdargs, playerId, variant):
		x, y, z = cmdargs[0]
		r,g,b = cmdargs[2]
		lighting = cmdargs[4]
		if CFServer.CreateBlockEntity(levelId).SetSignTextStyle((intg(x), int(y), intg(z)), cmdargs[1]['id'], (r, g, b, cmdargs[3]), lighting, int(cmdargs[5])):
			return False, '设置告示牌文本样式成功'
		else:
			return True,'设置告示牌文本样式失败'
		
	def setsignblocktext(self, cmdargs, playerId, variant):
		x, y, z = cmdargs[0]
		if CFServer.CreateBlockInfo(levelId).SetSignBlockText((intg(x), int(y), intg(z)), cmdargs[1], cmdargs[2]['id'], int(cmdargs[3])):
			return False,'设置告示牌文本成功'
		else:
			return True,'设置告示牌文本失败'

	def setplayerinteracterange(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerInteracteRange(cmdargs[1])
		serversystem.NotifyToMultiClients(cmdargs[0], "CustomCommandClient", {'cmd':"setplayerinteracterange", 'cmdargs': cmdargs})
		return False,'已设置触及距离'
	
	def summonprojectile(self, cmdargs, playerId, variant):
		try:
			targetlen = len(cmdargs[7])
			target = cmdargs[7][0]
		except:
			targetlen = 1
			target = None
		if not targetlen == 1:
			return True,'只允许一个实体,但提供的选择器允许多个实体'
		
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
		return False,'成功生成抛射物'
	
	def setstepheight(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置'
		if cmdargs[0]:
			for i in cmdargs[0]:
				CFServer.CreateAttr(i).SetStepHeight(cmdargs[1])
			return False,'已设置能迈过的最大高度'
		else:
			return True,'没有与选择器匹配的目标'

	def setsize(self, cmdargs, playerId, variant):
		if cmdargs[0]:
			for i in cmdargs[0]:
				CFServer.CreateCollisionBox(i).SetSize((cmdargs[1],cmdargs[2]))
			return False,'已设置碰撞箱'
		else:
			return True,'没有与选择器匹配的目标'
		
	def playerchatprefix(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置聊天前缀'
		for i in cmdargs[0]:
			CFServer.CreateExtraData(i).SetExtraData('chatprefix', cmdargs[1])
		return False,'已设置玩家聊天前缀'

	def writehealthtoscoreboard(self, cmdargs, playerId, variant):
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True,'未找到该计分板对象'
		for entity in cmdargs[0]:
			name = CFServer.CreateName(entity).GetName()
			if name is None:
				name = '"' + str(entity) + '"'
			health = CFServer.CreateAttr(entity).GetAttrValue(0)
			health = int(round(health))
			compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, health), False)
		return False,'已将生命值写入计分板'
		
	def writehungertoscoreboard(self, cmdargs, playerId, variant):
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True,'未找到该计分板对象'
		for entity in cmdargs[0]:
			name = CFServer.CreateName(entity).GetName()
			if name is None:
				name = '"' + str(entity) + '"'
			hunger = CFServer.CreateAttr(entity).GetAttrValue(4)
			hunger = int(round(hunger))
			compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, hunger), False)
		return False,'已将饥饿值写入计分板'

	def writearmortoscoreboard(self, cmdargs, playerId, variant):
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True,'未找到该计分板对象'
		for entity in cmdargs[0]:
			name = CFServer.CreateName(entity).GetName()
			if name is None:
				name = '"' + str(entity) + '"'
			armor = CFServer.CreateAttr(entity).GetAttrValue(12)
			armor = int(round(armor))
			compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, armor), False)
		return False,'已将盔甲值写入计分板'
	
	def writespeedtoscoreboard(self, cmdargs, playerId, variant):
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True,'未找到该计分板对象'
		for entity in cmdargs[0]:
			name = CFServer.CreateName(entity).GetName()
			if name is None:
				name = '"' + str(entity) + '"'
			speed = CFServer.CreateAttr(entity).GetAttrValue(1)
			speed = int(round(speed))
			compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, speed), False)
		return False,'已将速度值写入计分板'
	
	def executecb(self, cmdargs, playerId, variant):
		success = CFServer.CreateBlockEntity(levelId).ExecuteCommandBlock((intg(cmdargs[0][0]), intg(cmdargs[0][1]), intg(cmdargs[0][2])), cmdargs[1]['id'])
		if success:
			return False,'已执行命令方块'
		else:
			return True,'执行命令方块失败'
		
	def setname(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateName(i).SetName(cmdargs[1])
		return False, '已设置名称'
	
	def aicontrol(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateControlAi(i).SetBlockControlAi(cmdargs[1], cmdargs[2])
		return False,'已设置实体AI'

	def param(self, cmdargs, playerId, variant):
		params = compExtra.GetExtraData('parameters')
		if variant == 0:
			if cmdargs[1] is None:
				return False, str(params)
			else:
				if type(params) == dict and params.has_key(cmdargs[1]):
					return False, "变量\"%s\"为 %s" % (cmdargs[1], params[cmdargs[1]])
				else:
					return True,"未知的变量\"%s\"" % (cmdargs[1])
				
		elif variant == 2:
			if type(params) == dict and params.has_key(cmdargs[1]):
				del params[cmdargs[1]]
				compExtra.SetExtraData('parameters', params)
				return False, '已删除变量'
			else:
				return True,"未知的变量\"%s\"" % (cmdargs[1])
		
		elif variant == 1:
			input2 = str(cmdargs[2])
			if type(params) == dict:
				params[cmdargs[1]] = input2
			else:
				params = {cmdargs[1]: input2}
			compExtra.SetExtraData('parameters', params)
			return False,'已将 %s 修改为 %s' % (cmdargs[1], input2)
		
		elif variant == 3:
			if not (type(params) == dict and params.has_key(cmdargs[1])):
				return True,"未知的变量\"%s\"" % (cmdargs[1])
			
			if params[cmdargs[1]].replace(".","",1).isdigit():
				params[cmdargs[1]] = float(params[cmdargs[1]])
			
			elif not cmdargs[2] in ['加','乘']:
				return True,'操作符\"%s\"无法参与字符串运算' % (cmdargs[2])
			
			if cmdargs[3].replace(".","",1).isdigit():
				cmdargs[3] = float(cmdargs[3])
			
			elif cmdargs[2] != "加":
				return True,'字符串\"%s\"无法参与%s运算' % (cmdargs[3], cmdargs[2])
			
			if cmdargs[2] == '加':
				if not type(params[cmdargs[1]]) == type(cmdargs[3]) == int:
					params[cmdargs[1]] = str(params[cmdargs[1]])
					cmdargs[3] = str(cmdargs[3])
				params[cmdargs[1]] += cmdargs[3]
			
			elif cmdargs[2] == '乘':
				if cmdargs[3] != int(cmdargs[3]):
					return True,'\"%s\"无法用于重复字符串' % (cmdargs[3])
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
			return False,'变量运算成功'

		elif variant == 4:
			if type(params) == dict:
				params[cmdargs[1]] = random.randint(cmdargs[2], cmdargs[3])
			else:
				params = {cmdargs[1]: random.randint(cmdargs[2], cmdargs[3])}
			compExtra.SetExtraData('parameters', params)
			return False,'已将 %s 修改为 %s' % (cmdargs[1], params[cmdargs[1]])		

	def kickt(self, cmdargs, playerId, variant):
		for kickplayer in cmdargs[0]:
			compcmd.SetCommand('/kick ' + CFServer.CreateName(kickplayer).GetName() + ' ' + cmdargs[1], False)
		return False,'已踢出目标玩家'
			
	def explode(self, cmdargs, playerId, variant):
		id = CFServer.CreateEntityComponent(playerId).GetEntitiesBySelector("@r")
		for i in cmdargs[0]:
			position = CFServer.CreatePos(i).GetFootPos()
			CFServer.CreateExplosion(levelId).CreateExplosion(position,cmdargs[1],cmdargs[3],cmdargs[2],id,id)
		return False,'爆炸已创建'

	def explodebypos(self, cmdargs, playerId, variant):
		id = CFServer.CreateEntityComponent(playerId).GetEntitiesBySelector("@r")
		if CFServer.CreateExplosion(levelId).CreateExplosion(cmdargs[0],cmdargs[1],cmdargs[3],cmdargs[2],id,id):
			return False,'爆炸已创建'
		else:
			return True,'爆炸创建失败'

	def console(self, cmdargs, playerId, variant):
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
		compcmd.SetCommand("/" + cmd2.replace("'",'"'), False)
		return False,"已将指令处理后执行"
	
	def addaroundentitymotion(self, cmdargs, playerId, variant):
		if len(cmdargs[1]) > 1:
			return True,'只允许一个实体,但提供的选择器允许多个实体'
		for i in cmdargs[0]:
			compExtra = CFServer.CreateExtraData(i)
			CompMotion = CFServer.CreateActorMotion(i)
			CompType = CFServer.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
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
			if Mid == -1:
				return True,'设置失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False,'已设置运动器'
	
	def addaroundpointmotion(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			compExtra = CFServer.CreateExtraData(i)
			CompMotion = CFServer.CreateActorMotion(i)
			CompType = CFServer.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				addMotion = CompMotion.AddPlayerAroundPointMotion
			else:
				addMotion = CompMotion.AddEntityAroundPointMotion
			Mid = addMotion(cmdargs[1],
							cmdargs[2],
							cmdargs[3],
							cmdargs[4],
							cmdargs[5])
			if Mid == -1:
				return True,'设置失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False,'已设置运动器'

	def addvelocitymotion(self, cmdargs, playerId, variant):
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
				return True,'创建失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False,'已设置运动器'
	
	def startmotion(self, cmdargs, playerId, variant):
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
				CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
		return False,''
	
	def stopmotion(self, cmdargs, playerId, variant):
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
				CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
		return False,'已停止运动器'
	
	def removemotion(self, cmdargs, playerId, variant):
		# args['return_msg_key'] = ''
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
				CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
		return False,'已移除运动器'

	def addenchant(self, cmdargs, playerId, variant):
		# args['return_msg_key'] = '添加失败'
		# args['return_failed'] = True
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
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
														'id':  {'__type__': 2, '__value__': cmdargs[1]['type']}, 
														'modEnchant': {'__type__': 8, '__value__': ''}})
				itemDict["enchantData"] = []
			else:
				return True,'该槽位没有物品或没有该槽位'
			if slotType == 0:
				if compItem.SpawnItemToPlayerInv(itemDict, i, slot):
					return False,'添加附魔成功'
			else:
				if compItem.SpawnItemToPlayerCarried(itemDict, i):
					return False,'添加附魔成功'

	def addtrackmotion(self, cmdargs, playerId, variant):
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
				return True,'创建失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False,'已设置运动器'

	def setactorcanburnbylightning(self, cmdargs, playerId, variant):
		return not compGame.SetCanActorSetOnFireByLightning(cmdargs[0]),'设置成功'

	def setblockcanburnbylightning(self, cmdargs, playerId, variant):
		return not compGame.SetCanBlockSetOnFireByLightning(cmdargs[0]),'设置成功'

	def cancelshearsdestoryblockspeedall(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			compItem.CancelShearsDestoryBlockSpeedAll()
		return False,'已取消'

	def cancelshearsdestoryblockspeed(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			if not compItem.CancelShearsDestoryBlockSpeed(cmdargs[1]):
				return True,'执行过程中发生错误： 无效的命名空间id'
		return False,'取消成功'

	def setshearsdestoryblockspeed(self, cmdargs, playerId, variant):
		if cmdargs[2] < 1:
			return True,'速度必须大于1'
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			if not compItem.SetShearsDestoryBlockSpeed(cmdargs[1], cmdargs[2]):
				return True,'无效的命名空间id'
		return False,'设置成功'

	def changeselectslot(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType != "minecraft:player":
				return True, '非玩家实体无法设置选择槽位'
		for i in cmdargs[0]:
			CompPlayer = CFServer.CreatePlayer(i)
			CompPlayer.ChangeSelectSlot(cmdargs[1])
		return False,'设置成功'

	def forbidliquidflow(self, cmdargs, playerId, variant):
		if compGame.ForbidLiquidFlow(cmdargs[0]):
			return False,'已成功修改液体流动性'
		else:
			return True,'修改失败'

	def getuid(self, cmdargs, playerId, variant):
		uid_dict = {}
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			if CompType.GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法获取uid'
		for i in cmdargs[0]:
			playername = CFServer.CreateName(i).GetName()
			uid_dict[playername] = CFServer.CreateHttp(levelId).GetPlayerUid(i)
		return False,'获取到的UID为%s' % (uid_dict)
		# serversystem.NotifyToMultiClients(list(cmdargs[0]), "CustomCommandClient", {'cmd':"getuid", 'origin': playerId})

	def givewithnbt(self, cmdargs, playerId, variant):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法给予物品'
		result = checkjson(cmdargs[1], playerId)
		if result[1]:
			return True,result[0]
		itemDict = result[0]
		for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
			itemDict.pop(i,False) #删去多余键值对(这些已被弃用)
		for i in cmdargs[0]:
			if not CFServer.CreateItem(i).SpawnItemToPlayerInv(unicode_convert(itemDict), i):
				return True,'命令执行过程中发生了错误。'
		return False,'成功给予物品'
		
	def spawnitemtocontainer(self, cmdargs, playerId, variant):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		x = intg(cmdargs[2][0])
		y = int(cmdargs[2][1])
		z = intg(cmdargs[2][2])
		itemDict = compItemWorld.GetContainerItem((x, y, z,), cmdargs[1], cmdargs[3]['id'], True)
		result = checkjson(cmdargs[0], playerId)
		if result[1]:
			return True,result[0]
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
			if compItemWorld.SpawnItemToContainer(itemDict2, cmdargs[1], (x, y, z),cmdargs[3]['id']):
				return False,'成功给予物品'
			else:
				return True, '给与物品失败'
		else:
			return True,'槽位已满'

	def spawnitemtoenderchest(self, cmdargs, playerId, variant):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		for player in cmdargs[2]:
			if CFServer.CreateEngineType(player).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法给予物品'
		result = checkjson(cmdargs[0], playerId)
		if result[1]:
			return True,result[0]
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
					return False,'成功给予物品'
			else:
				return True,'槽位已满'

	def replaceitemtocarried(self, cmdargs, playerId, variant):

		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法给予物品'
		result = checkjson(cmdargs[1], playerId)
		if result[1]:
			return True,result[0]
		itemDict = result[0]
		for i in cmdargs[0]:
			if CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i):
				return False,'成功替换物品'

	def removeenchant(self, cmdargs, playerId, variant):
		# args['return_msg_key'] = '删除失败'
		# args['return_failed'] = True
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法访问背包'
		for i in cmdargs[0]:
			if CFServer.CreateItem(i).RemoveEnchantToInvItem(cmdargs[2], cmdargs[1]):
				return False,'删除成功'

	def resetmotion(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			CompMotion = CFServer.CreateActorMotion(i)
			if CompType.GetEngineTypeStr() == 'minecraft:player':
				CompMotion.SetPlayerMotion((0, 0, 0))
			else:
				CompMotion.ResetMotion()
		return False,'已重置运动器'

	def setleashholder(self, cmdargs, playerId, variant):
		if len(cmdargs[0]) == 1:
			for i in cmdargs[1]:
				compEntityD = CFServer.CreateEntityDefinitions(i)
				compEntityD.SetLeashHolder(cmdargs[0])
			return False, '已尝试拴住实体'
		else:
			return True,'只允许一个实体,但提供的选择器允许多个实体'

	def setlootdropped(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			compEntityD = CFServer.CreateEntityDefinitions(i)
			compEntityD.SetLootDropped(cmdargs[1])
		return False,'设置成功'

	def setmaxairsupply(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			compBrea = CFServer.CreateBreath(i)
			compBrea.SetMaxAirSupply(cmdargs[1])
		return False,'设置成功'

	def knockback(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CFServer.CreateAction(i).SetMobKnockback(cmdargs[1], cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5])
		return False,'已击飞实体'

	def setmotion(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			CompMotion = CFServer.CreateActorMotion(i)
			if CompType.GetEngineTypeStr() == 'minecraft:player':
				CompMotion.SetPlayerMotion(cmdargs[1])
			else:
				CompMotion.SetMotion(cmdargs[1])
		return False,'设置动量成功'

	def setopencontainersability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置打开容器的权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetOpenContainersAbility(cmdargs[1])
		return False,'已设置打开容器的权限'
	
	def setoperatedoorability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置开门权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetOperateDoorsAndSwitchesAbility(cmdargs[1])
		return False,'已设置开门权限'

	def setorbexperience(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:xp_orb':
				return True,'非经验球实体无法设置经验值'
		for i in cmdargs[0]:
			compAttr = CFServer.CreateExp(i)
			compAttr.SetOrbExperience(cmdargs[1])
		return False,'设置成功'

	def setpersistent(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			compAttr = CFServer.CreateAttr(i)
			compAttr.SetPersistent(cmdargs[1])
		return False,'设置成功'

	def setpistonmaxinteractioncount(self, cmdargs, playerId, variant):
		if compGame.SetPistonMaxInteractionCount(cmdargs[0]):
			return False,'设置成功'
		else:
			return True, '无效的数值'

	def setplayeruiitem(self, cmdargs, playerId, variant):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置界面内物品'
		result = checkjson(cmdargs[2], playerId)
		if result[1]:
			return True,result[0]
		itemDict = result[0]
		for i in cmdargs[0]:
			if not CFServer.CreateItem(i).SetPlayerUIItem(i, cmdargs[1], itemDict, cmdargs[3]):
				return True,'命令执行过程中发生了错误。'
		return False,'已设置玩家界面内物品'

	def _if(self, cmdargs, playerId, variant):
		if variant == 0:
			if cmdargs[3] is None:
				result = [compcmd.SetCommand(cmdargs[1].replace("'",'"'), playerId), compcmd.SetCommand(cmdargs[3], playerId)]
			else:
				result = [compcmd.SetCommand(cmdargs[1].replace("'",'"'), playerId), compcmd.SetCommand(cmdargs[3].replace("'",'"'), playerId)]
			if cmdargs[2] == 'not':
				if result[0]:
					return True,'运算符成立(%s)' % (result[1])
				else:
					return False,'运算符不成立(%s)' % (result[1])
			elif cmdargs[2] == 'and':
				if result[0] and result[1]:
					return False,'运算符成立(%s,%s)' % (result[0], result[1])
				else:
					return True,'运算符不成立(%s,%s)' % (result[0], result[1])
			elif cmdargs[2] == 'or':
				if result[0] or result[1]:
					return False,'运算符成立(%s,%s)' % (result[0], result[1])
				else:
					return True,'运算符不成立(%s,%s)' % (result[0], result[1])
			elif cmdargs[2] == 'xor':
				if result[0] != result[1]:
					return False,'运算符成立(%s,%s)' % (result[0], result[1])
				else:
					return True,'运算符不成立(%s,%s)' % (result[0], result[1])
			else:
				return True,'未知的逻辑运算符'
		
		else:
			params = compExtra.GetExtraData('parameters')
			if type(params) == dict and params.has_key(cmdargs[1]):
				cmdargs[3] = round(cmdargs[3], 6)
				param = params[cmdargs[1]]
				try:
					param = float(param)
				except:
					return True,"\"%s\"不是一个数字变量" % (cmdargs[1])
				if cmdargs[2] == 'equals':
					if param == cmdargs[3]:
						return False,"表达式成立(%s == %s)" % (param, cmdargs[3])
					else:
						return True,"表达式不成立(%s == %s)" % (param, cmdargs[3])
				elif cmdargs[2] == 'not_equals':
					if param != cmdargs[3]:
						return False,"表达式成立(%s != %s)" % (param, cmdargs[3])
					else:
						return True,"表达式不成立(%s != %s)" % (param, cmdargs[3])
				elif cmdargs[2] == 'greater_than':
					if param > cmdargs[3]:
						return False,"表达式成立(%s > %s)" % (param, cmdargs[3])
					else:
						return True,"表达式不成立(%s > %s)" % (param, cmdargs[3])
				elif cmdargs[2] == 'less_than':
					if param < cmdargs[3]:
						return False,"表达式成立(%s < %s)" % (param, cmdargs[3])
					else:
						return True,"表达式不成立(%s < %s)" % (param, cmdargs[3])
				elif cmdargs[2] == 'not_less':
					if param >= cmdargs[3]:
						return False,"表达式成立(%s >= %s)" % (param, cmdargs[3])
					else:
						return True,"表达式不成立(%s >= %s)" % (param, cmdargs[3])
				elif cmdargs[2] == 'not_greater':
					if param <= cmdargs[3]:
						return False,"表达式成立(%s <= %s)" % (param, cmdargs[3])
					else:
						return True,"表达式不成立(%s <= %s)" % (param, cmdargs[3])
			else:
				return True,"未知的变量\"%s\"" % (cmdargs[1])
	
	def setteleportability(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法设置传送权限'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetTeleportAbility(cmdargs[1])
		return False,'已设置传送权限'

	def settradelevel(self, cmdargs, playerId, variant):
		for i in cmdargs[0]:
			if not CFServer.CreateEngineType(i).GetEngineTypeStr() in ['minecraft:villager', 'minecraft:villager_v2']:
				return True,'非村民实体无法设置交易等级'
		for i in cmdargs[0]:
			CFServer.CreateEntityDefinitions(i).SetTradeLevel(cmdargs[1])
		return False,'已设置交易等级'	
	
	def setvignette(self, cmdargs, playerId, variant):
		for i in cmdargs[1]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True,'非玩家实体无法拥有屏幕暗角'
		if variant == 0:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignettecenter",'cmdargs': cmdargs})
			return False,'已将玩家的屏幕暗角中心设为 %f, %f' % (cmdargs[2], cmdargs[3])
		elif variant == 1:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignetteradius",'cmdargs': cmdargs})
			return False,'已将玩家的屏幕暗角半径设为 %f' % (cmdargs[2])
		elif variant == 2:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignettecolor",'cmdargs': cmdargs})
			return False,'已将玩家的屏幕暗角颜色设为 %d, %d, %d' % (cmdargs[2][0], cmdargs[2][1], cmdargs[2][2])
		elif variant == 3:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignettesmooth",'cmdargs': cmdargs})
			return False,'已将玩家的屏幕暗角平滑度设为 %f' % (cmdargs[2])
		elif variant == 4:
			serversystem.NotifyToMultiClients(cmdargs[1], "CustomCommandClient", {'cmd':"setvignette",'cmdargs': cmdargs})
			return False,'已%s玩家的屏幕暗角' % ('启用' if cmdargs[2] else '禁用')
		
	# def setblockbasicinfo(self, cmdargs, playerId, variant):#暂时没得用
	# 	args['return_failed'] = True
	# 	args['return_msg_key'] = '设置失败'
	# 	if CFServer.CreateBlockInfo(levelId).SetBlockBasicInfo(cmdargs[0], {'destroyTime':cmdargs[1], 'explosionResistance':cmdargs[2]}, cmdargs[3]):
	# 		args['return_failed'] = False
	# 		args['return_msg_key'] = '设置成功'
	# 	return

	# def sit(self, cmdargs, playerId, variant):#病友
	# 	for i in cmdargs[0]:
	# 		if CFServer.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:panda':
	# 			args['return_failed'] = True
	# 			args['return_msg_key'] = '熊猫无法坐下'
	# 			return
	# 	for i in cmdargs[0]:
	# 		CFServer.CreateEntityDefinitions(i).SetSitting(cmdargs[1])
	# 	args['return_msg_key'] = '已设置坐下状态'

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
