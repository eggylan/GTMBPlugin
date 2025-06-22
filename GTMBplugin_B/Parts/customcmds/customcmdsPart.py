# -*- coding: utf-8 -*-
from __future__ import print_function
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
import json
import random
import math
CFServer = serverApi.GetEngineCompFactory()
CFClient = clientApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compcmd = CFServer.CreateCommand(levelId)
compGame = CFServer.CreateGame(levelId)
compItemWorld = CFServer.CreateItem(levelId)
compExtra = CFServer.CreateExtraData(levelId)
compBlockEntity = CFServer.CreateBlockEntity(levelId)

serversystem = serverApi.GetSystem('Minecraft', 'preset')
copyrightInfo = "§b---------\n版本： v0.8a(2025/6):11.11\n© 2025 联机大厅服务器模板\n本项目采用 GNU General Public License v3.0 许可证。\n---------"

def create_players_str(players):
	#type: (list) -> str
	return ', '.join([CFServer.CreateName(item).GetName() for item in players])

def unicode_convert(input):
	#type: (dict|str) -> dict|list|str|bool
	if isinstance(input, dict):
		return {unicode_convert(key): unicode_convert(value) for key, value in input.items()}
	elif isinstance(input, list):
		return [unicode_convert(element) for element in input]
	elif isinstance(input, unicode): # type: ignore
		output = str(input)
		if output == 'True':
			return True
		elif output == 'False':
			return False
		return output
	return input

def intg(num):
	#type: (float) -> int
	return int(math.floor(num))

def checkjson(data):
	#type: (str) -> list
	try:
		itemDict = json.loads(data.replace("'", '"'))
	except ValueError as errordata:
		errordata = str(errordata)
		if errordata.find('char') == -1:
			return ['无效的nbt', True]
		if errordata.find('Extra') != -1:
			split = errordata.split(' - ')
			start = int(split[1][split[1].find('char') + 5:])
			end = int(split[2][0:-1])
		else:
			start = int(errordata[errordata.find('char') + 5:-1])
			end = start + 1
		return ['无效的nbt 位于 %s>>%s<<%s' % (data[:start], data[start:end], data[end:]), True]
	if isinstance(itemDict, dict):
		return [unicode_convert(itemDict), False]
	return['无效的nbt', True]
@registerGenericClass('customcmdsPart')
class customcmdsPart(PartBase):
		
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = '自定义指令零件'

		# 注册处理函数
		# 客户端
		self.clientcustomcmd = {
			'setplayerinteracterange':self.client_setplayerinteracterange,
			'hideairsupplygui':self.client_hideairsupplygui,
			'hidearmorgui':self.client_hidearmorgui,
			'hidecrosshairgui':self.client_hidecrosshairgui,
			'hideexpgui':self.client_hideexpgui,
			'hidefoldgui':self.client_hidefoldgui,
			'hidehealthgui':self.client_hidehealthgui,
			'hidehorsehealthgui':self.client_hidehorsehealthgui,
			'hidehudgui':self.client_hidehudgui,
			'hidehungergui':self.client_hidehungergui,
			'hideslotbargui':self.client_hideslotbargui,
			'openfoldgui':self.client_openfoldgui,
			'setcanpausescreen':self.client_setcanpausescreen,
			'setcolorbrightness':self.client_setcolorbrightness,
			'setcolorcontrast':self.client_setcolorcontrast,
			'setcolorsaturation':self.client_setcolorsaturation,
			'setcolortint':self.client_setcolortint,
			'setcompassentity':self.client_setcompassentity,
			'setcompasstarget':self.client_setcompasstarget,
			'setvignettecenter':self.client_setvignettecenter,
			'setvignetteradius':self.client_setvignetteradius,
			'setvignettecolor':self.client_setvignettecolor,
			'setvignettesmooth':self.client_setvignettesmooth,
			'setvignette':self.client_setvignette,
			'setgaussian':self.client_setgaussian,
			'setgaussianradius':self.client_setgaussianradius,
			'sethudchatstackposition':self.client_sethudchatstackposition,
			'sethudchatstackvisible':self.client_sethudchatstackvisible,
			'chatclear': self.client_chatclear,
			"openui": self.client_openui,

		}

		# 服务端
		self.servercustomcmd = {
			'setentityonfire':self.setentityonfire,
			'setcurrentairsupply':self.setcurrentairsupply,
			'setcompasstarget':self.setcompasstarget,
			'setcompassentity':self.setcompassentity,
			'setcolor':self.setcolor,
			'setchestitemnum':self.setchestitemnum,
			'setchestitemexchange':self.setchestitemexchange,
			'setcanpausescreen':self.setcanpausescreen,
			'setcanotherplayerride':self.setcanotherplayerride,
			'setattackplayersability':self.setattackplayersability,
			'setattackmobsability':self.setattackmobsability,
			'setattackdamage':self.setattackdamage,
			'setspawnpoint':self.setspawnpoint,
			'setplayerhealthlevel':self.setplayerhealthlevel,
			'setplayerstarvelevel':self.setplayerstarvelevel,
			'setplayerhunger':self.setplayerhunger,
			'setplayerattackspeedamplifier':self.setplayerattackspeedamplifier,
			'setplayerjumpable':self.setplayerjumpable,
			'setplayermovable':self.setplayermovable,
			'setplayernaturalstarve':self.setplayernaturalstarve,
			'setplayerprefixandsuffixname':self.setplayerprefixandsuffixname,
			'setplayermaxexhaustionvalue':self.setplayermaxexhaustionvalue,
			'setplayerhealthtick':self.setplayerhealthtick,
			'setplayerstarvetick':self.setplayerstarvetick,
			'sethurtcd':self.sethurtcd,
			'setattacktarget':self.setattacktarget,
			'resetattacktarget':self.resetattacktarget,
			'setbanplayerfishing':self.setbanplayerfishing,
			'setactorcanpush':self.setactorcanpush,
			'setactorcollidable':self.setactorcollidable,
			'setmineability':self.setmineability,
			'setbuildability':self.setbuildability,
			'setcontrol':self.setcontrol,
			'setpickuparea':self.setpickuparea,
			'setlevelgravity':self.setlevelgravity,
			'setjumppower':self.setjumppower,
			'setgravity':self.setgravity,
			'setworldspawnd':self.setworldspawnd,
			'playeruseitemtopos':self.playeruseitemtopos,
			'playeruseitemtoentity':self.playeruseitemtoentity,
			'playerdestoryblock': self.playerdestoryblock,
			'openworkbench':self.openworkbench,
			'openfoldgui':self.openfoldgui,
			'setimmunedamage':self.setimmunedamage,
			'hideslotbargui':self.hideslotbargui,
			'hidehungergui':self.hidehungergui,
			'hidehudgui':self.hidehudgui,
			'hidehorsehealthgui':self.hidehorsehealthgui,
			'hidehealthgui':self.hidehealthgui,
			'hidefoldgui':self.hidefoldgui,
			'hideexpgui':self.hideexpgui,
			'hidecrosshairgui':self.hidecrosshairgui,
			'hidearmorgui':self.hidearmorgui,
			'hideairsupplygui':self.hideairsupplygui,
			'setinvitemexchange':self.setinvitemexchange,
			'setinvitemnum':self.setinvitemnum,
			'setitemdurability':self.setitemdurability,
			'setitemmaxdurability':self.setitemmaxdurability,
			'setitemtierlevel':self.setitemtierlevel,
			'setitemtierspeed':self.setitemtierspeed,
			'setitemmaxstacksize':self.setitemmaxstacksize,
			'playerexhaustionratio':self.playerexhaustionratio,
			'setsigntextstyle':self.setsigntextstyle,
			'setsigntext':self.setsigntext,
			'setplayerinteracterange':self.setplayerinteracterange,
			'summonprojectile':self.summonprojectile,
			'setstepheight':self.setstepheight,
			'setsize':self.setsize,
			'playerchatprefix':self.playerchatprefix,
			'writehealthtoscoreboard':self.writehealthtoscoreboard,
			'writehungertoscoreboard':self.writehungertoscoreboard,
			'writearmortoscoreboard':self.writearmortoscoreboard,
			'writespeedtoscoreboard':self.writespeedtoscoreboard,
			'executecb':self.executecb,
			'setname':self.setname,
			'aicontrol':self.aicontrol,
			'param':self.param,
			'kickt':self.kickt,
			'explode':self.explode,
			'explodebypos':self.explodebypos,
			'console':self.console,
			'addaroundentitymotion':self.addaroundentitymotion,
			'addaroundpointmotion':self.addaroundpointmotion,
			'addvelocitymotion':self.addvelocitymotion,
			'startmotion':self.startmotion,
			'stopmotion':self.stopmotion,
			'removemotion':self.removemotion,
			'addenchant':self.addenchant,
			'addtrackmotion':self.addtrackmotion,
			'setactorcanburnbylightning':self.setactorcanburnbylightning,
			'setblockcanburnbylightning':self.setblockcanburnbylightning,
			'cancelshearsdestoryblockspeedall':self.cancelshearsdestoryblockspeedall,
			'cancelshearsdestoryblockspeed':self.cancelshearsdestoryblockspeed,
			'setshearsdestoryblockspeed':self.setshearsdestoryblockspeed,
			'changeselectslot':self.changeselectslot,
			'forbidliquidflow':self.forbidliquidflow,
			'getuid':self.getuid,
			'givewithnbt':self.givewithnbt,
			'spawnitemtocontainer':self.spawnitemtocontainer,
			'spawnitemtoenderchest':self.spawnitemtoenderchest,
			'replaceitemtocarried':self.replaceitemtocarried,
			'removeenchant':self.removeenchant,
			'resetmotion':self.resetmotion,
			'setleashholder':self.setleashholder,
			'setlootdropped':self.setlootdropped,
			'setmaxairsupply':self.setmaxairsupply,
			'knockback':self.knockback,
			'setmotion':self.setmotion,
			'setopencontainersability':self.setopencontainersability,
			'setoperatedoorability':self.setoperatedoorability,
			'setorbexperience':self.setorbexperience,
			'setpersistent':self.setpersistent,
			'setpistonmaxinteractioncount':self.setpistonmaxinteractioncount,
			'setplayeruiitem':self.setplayeruiitem,
			'if':self._if,
			'setteleportability':self.setteleportability,
			'settradelevel':self.settradelevel,
			'setvignette':self.setvignette,
			'setbrewingstandslotitem':self.setbrewingstandslotitem,
			'setdisablecontainers':self.setdisablecontainers,
			'setdisabledropitem':self.setdisabledropitem,
			'setdisablehunger':self.setdisablehunger,
			'setenchantmentseed':self.setenchantmentseed,
			'setentityitem':self.setentityitem,
			'setentityowner':self.setentityowner,
			'setentityride':self.setentityride,
			'setframeitemdropchange':self.setframeitemdropchange,
			'setframerotation':self.setframerotation,
			'sethopperspeed':self.sethopperspeed,
			'sethudchatstackposition':self.sethudchatstackposition,
			'sethudchatstackvisible':self.sethudchatstackvisible,
			'setshowrideui':self.setshowrideui,
			'summonitem':self.summonitem,
			'summonnbt':self.summonnbt,
			'setgaussian':self.setgaussian,
			'scoreparam': self.scoreparam,
			'mute': self.mute,
			"chatclear": self.chatclear,
			"openui": self.openui,
			"gettps": self.gettps,
			"copyright": self.copyright,
			"chatlimit":self.chatlimit,
			#'setblocknbt': self.setblocknbt
		}
		
	def InitClient(self):
		'''
		@description 客户端的零件对象初始化入口
		'''
		CFClient.CreatePostProcess(levelId).SetEnableColorAdjustment(True)
		global clientsystem
		clientsystem = clientApi.GetSystem('Minecraft', 'preset')
		clientsystem.ListenForEvent('Minecraft', 'preset', 'CustomCommandClient', self, self.OnCustomCommandClient)
		global localPlayerId
		localPlayerId = clientApi.GetLocalPlayerId()
		PartBase.InitClient(self)

	def OnCustomCommandClient(self, args):
		# 从dict中选取处理函数
		handler = self.clientcustomcmd.get(args['cmd'])
		if handler:
			handler(args)
		# clientsystem.NotifyToServer('customCmdReturn', data)

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
		CFClient.CreatePostProcess(levelId).SetColorAdjustmentTint(args['cmdargs'][2], (args['cmdargs'][3], args['cmdargs'][4], args['cmdargs'][5]))
	def client_setcompassentity(self, args):
		CFClient.CreateItem(localPlayerId).SetCompassEntity(args['cmdargs'][1][0])
	def client_setcompasstarget(self, args):
		CFClient.CreateItem(localPlayerId).SetCompassTarget(args['cmdargs'][0], args['cmdargs'][1], args['cmdargs'][2])
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
	def client_setgaussian(self, args):
		CFClient.CreatePostProcess(levelId).SetEnableGaussianBlur(args['cmdargs'][2])
	def client_setgaussianradius(self, args):
		CFClient.CreatePostProcess(levelId).SetGaussianBlurRadius(args['cmdargs'][2])
	def client_sethudchatstackposition(self, args):
		clientApi.SetHudChatStackPosition((args['cmdargs'][1], args['cmdargs'][2]))
	def client_sethudchatstackvisible(self, args):
		clientApi.SetHudChatStackVisible(args['cmdargs'][1])
	def client_chatclear(self, args):
		CFClient.CreateTextNotifyClient(levelId).SetLeftCornerNotify("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
	def client_openui(self, args):
		if args['cmdargs'][0] == "enchant":
			uiWillbeOpen = "enchant"
			uiWillbeOpenName = "自定义附魔"
		elif args['cmdargs'][0] == "getitem":
			uiWillbeOpen = "getitem"
			uiWillbeOpenName = "获取隐藏物品"
		elif args['cmdargs'][0] == "nbteditor":
			uiWillbeOpen = "nbteditor"
			uiWillbeOpenName = "NBT编辑器"
		elif args['cmdargs'][0] == "changetips":
			uiWillbeOpen = "itemTips"
			uiWillbeOpenName = "修改物品注释"
		elif args['cmdargs'][0] == "cmdbatch":
			uiWillbeOpen = "cmdbatch"
			uiWillbeOpenName = "指令批处理"
		elif args['cmdargs'][0] == "cmdblockimport":
			uiWillbeOpen = "cmdblockimportui"
			uiWillbeOpenName = "命令方块导入"
		elif args['cmdargs'][0] == "structureimport":
			uiWillbeOpen = "struimport"
			uiWillbeOpenName = "结构导入"
		uiNodePreset = self.GetParent().GetChildPresetsByName(uiWillbeOpen)[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)
		CFClient.CreateTextNotifyClient(levelId).SetLeftCornerNotify("已打开 %s 界面" % uiWillbeOpenName)
	# 客户端函数部分到此结束
	
	def InitServer(self):
		'''
		@description 服务端的零件对象初始化入口
		'''
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'CustomCommandTriggerServerEvent', self, self.OnCustomCommand)
		#serversystem.ListenForEvent('Minecraft', 'preset', 'customCmdReturn', self, self.OnReturn)
		PartBase.InitServer(self)

	# def OnReturn(self, args):
	# 	pass
	# 	# 客户端返回
	# 	#compMsg = CFServer.CreateMsg(args['target'])
	# 	#compName = CFServer.CreateName(args['__id__'])

	def OnCustomCommand(self, args):
		cmdargs = []
		variant = args['variant']
		args_list = args['args']
		cmdargs = [i['value'] for i in args_list]
		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None
		handler = self.servercustomcmd.get(args['command'])
		if handler:
			args['return_failed'], args['return_msg_key'] = handler(cmdargs, playerId, variant, args)
		#print(args)

	# 服务端函数部分由此开始
	def setentityonfire(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateAttr(i).SetEntityOnFire(cmdargs[1], cmdargs[2])
		return False, '已点燃 %s 个实体 %s 秒,伤害为 %s' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setcurrentairsupply(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateBreath(i).SetCurrentAirSupply(cmdargs[1])
		return False, '已设置 %s 个实体氧气储备值为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setcompasstarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		x, y, z = cmdargs[1]
		compassdata = [intg(x), int(y), intg(z)]
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcompasstarget', 'cmdargs': compassdata})
		return False, '将以下玩家的指南针指向 Pos%s:%s' % (str(tuple(compassdata)), create_players_str(cmdargs[0]))

	def setcompassentity(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcompassentity', 'cmdargs': cmdargs})
		return False, '将以下玩家的指南针指向 %s:%s' % (CFServer.CreateEngineType(cmdargs[1][0]).GetEngineTypeStr(), create_players_str(cmdargs[0]))
		
	def setcolor(self, cmdargs, playerId, variant, data):
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[1]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if variant == 3:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolortint', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色调为 %s(%s,%s,%s):%s' % (cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5], create_players_str(cmdargs[1]))
		elif variant == 2:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorsaturation', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩饱和度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
		elif variant == 1:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorcontrast', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩对比度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
		else:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorbrightness', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩亮度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
	
	def setchestitemnum(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if CFServer.CreateChestBlock(levelId).SetChestBoxItemNum(None, xyz, cmdargs[1], cmdargs[2], cmdargs[3]['id']):
			return False, '已设置槽位 %s 的物品数量为 %s' % (cmdargs[1], cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是箱子' % (xyz,)
	
	def setchestitemexchange(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if playerId is None:
			pid = serverApi.GetPlayerList()[random.randint(0, len(serverApi.GetPlayerList())-1)]
		else:
			pid = playerId #尽可能让命令在同维度执行
		if CFServer.CreateChestBlock(pid).SetChestBoxItemExchange(pid, xyz, cmdargs[1], cmdargs[2]):
			return False, '已交换槽位 %s 与槽位 %s 的物品' % (cmdargs[1], cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是箱子' % (xyz,)
	
	def setcanpausescreen(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcanpausescreen', 'cmdargs': cmdargs})
		return False, '已将 %s 的暂停权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setcanotherplayerride(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateRide(i).SetCanOtherPlayerRide(i, cmdargs[1])
		return False, '已%s %s 个实体被骑乘' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def setattackplayersability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetAttackPlayersAbility(cmdargs[1])
		return False, '已将 %s 的pvp权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setattackmobsability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetAttackMobsAbility(cmdargs[1])
		return False, '已将 %s 的攻击生物权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setattackdamage(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			itemDict = compItem.GetPlayerItem(2, 0, True)
			if compItem.SetAttackDamage(itemDict, cmdargs[1]):
				compItem.SpawnItemToPlayerCarried(itemDict, i)
		return False, '已将 %s 的手持物品攻击伤害设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setspawnpoint(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[0][0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[0] == "null(can't replace to null, will be a bug)":
			cmdargs[0] = playerId, #','用来创建tuple
		if cmdargs[1] is None:
			cmdargs[1] = data['origin']['blockPos']
		x, y, z = cmdargs[1]
		if cmdargs[2] is None:
			cmdargs[2] = {'name': data['origin']['dimension'], 'id': data['origin']['dimension']}
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerRespawnPos((intg(x), int(y), intg(z)), cmdargs[2]['id'])
		return False, '将 %s 的重生点设置为 %s in %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2]['name'])
	
	def setplayerhealthlevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0 :#or cmdargs[1] > 20:
			return True, '无效的回血临界值 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的回血临界值 (%s > 20)' % cmdargs[1]
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerHealthLevel(cmdargs[1])
		return False, '将 %s 的回血临界值设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerstarvelevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0:
			return True, '无效的扣血临界值 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的扣血临界值 (%s > 20)' % cmdargs[1]
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerStarveLevel(cmdargs[1])
		return False, '将 %s 的扣血临界值设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerhunger(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0 :
			return True, '无效的饥饿度 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的饥饿度 (%s > 20)' % cmdargs[1]
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerHunger(cmdargs[1])
		return False, '将 %s 的饥饿度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerattackspeedamplifier(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0.5:
			return True, '无效的倍率 (%s < 0.5)' % cmdargs[1]
		elif cmdargs[1] > 2.0:
			return True, '无效的倍率 (%s > 2.0)' % cmdargs[1]
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerAttackSpeedAmplifier(cmdargs[1])
		return False, '将 %s 的攻击速度倍率设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerjumpable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerJumpable(cmdargs[1])
		return False, '将 %s 的跳跃权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayermovable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerMovable(cmdargs[1])
		return False, '将 %s 个玩家的移动权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayernaturalstarve(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerNaturalStarve(cmdargs[1])
		return False, '将 %s 的饥饿掉血设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayerprefixandsuffixname(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateName(i).SetPlayerPrefixAndSuffixName(cmdargs[1], '§r', cmdargs[2], '§r')
		return False, '将 %s 玩家的前缀设置为 %s, 后缀设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setplayermaxexhaustionvalue(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerMaxExhaustionValue(cmdargs[1])
		return False, '将 %s 的饥饿最大消耗度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerhealthtick(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerHealthTick(cmdargs[1])
		return False, '将 %s 的自然回血速度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setplayerstarvetick(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerStarveTick(cmdargs[1])
		return False, '将 %s 的自然扣血速度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def sethurtcd(self, cmdargs, playerId, variant, data):
		if compGame.SetHurtCD(cmdargs[0]):
			return False, '将全局受击间隔设置为 %s' % (cmdargs[0])
		else:
			return True, '设置失败'
	
	def setattacktarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		attackTargetId = cmdargs[1][0]
		for i in cmdargs[0]:
			CFServer.CreateAction(i).SetAttackTarget(attackTargetId)
		return False, '将 %s 个实体的仇恨目标设置为 %s' % (len(cmdargs[0]), CFServer.CreateEngineType(attackTargetId).GetEngineTypeStr())
	
	def resetattacktarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateAction(i).ResetAttackTarget()
		return False, '成功重置 %s 个实体的仇恨目标' % (len(cmdargs[0]))
	
	def setbanplayerfishing(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetBanPlayerFishing(cmdargs[1])
		return False, '将 %s 的钓鱼权限设置为 %s' % (create_players_str(cmdargs[0]), '禁止' if cmdargs[1] else '允许')
	
	def setactorcanpush(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateActorPushable(i).SetActorPushable(cmdargs[1])
		return False, '已%s %s个 实体被推动' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def	setactorcollidable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateActorCollidable(i).SetActorCollidable(cmdargs[1])
		return False, '已%s %s 实体拥有固体碰撞箱' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def setmineability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetMineAbility(cmdargs[1])
		return False, '将 %s 的挖掘权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setbuildability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetBuildAbility(cmdargs[1])
		return False, '将 %s 的放置权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setcontrol(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateRide(i).SetControl(i, cmdargs[1])
		return False, '已设置 %s 个实体的控制权' % (len(cmdargs[0]))
	
	def setpickuparea(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPickUpArea(cmdargs[1])
		return False, '已将 %s 的拾取范围设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setlevelgravity(self, cmdargs, playerId, variant, data):
		compGame.SetLevelGravity(cmdargs[0])
		return False , '已将世界重力设置为 %s' % (cmdargs[0])
	
	def setjumppower(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateGravity(i).SetJumpPower(cmdargs[1])
		return False, '已设置 %s 个实体的跳跃力度为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setgravity(self, cmdargs, playerId, variant, data):
		for i in cmdargs[0]:
			CFServer.CreateGravity(i).SetGravity(cmdargs[1])
		return False, '已设置 %s 个实体的重力为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setworldspawnd(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		compGame.SetSpawnDimensionAndPosition(cmdargs[0]['id'], xyz)
		return False, '已设置世界出生点为 %s in %s' % (xyz, cmdargs[0]['name'])
		
	def playeruseitemtopos(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[2] not in [0, 1, 2, 3, 4, 5]:
			return True, '无效的朝向'
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).PlayerUseItemToPos(xyz, 2, 0, cmdargs[2])
		return False, '已尝试让 %s 向 %s 的 %s 面使用物品' % (create_players_str(cmdargs[0]), xyz, ['上', '下', '北', '南', '西', '东'][cmdargs[2]])
	
	def playeruseitemtoentity(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		entityId = cmdargs[1][0]
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).PlayerUseItemToEntity(entityId)
		return False, '已尝试让 %s 向 %s 使用物品' % (create_players_str(cmdargs[0]), CFServer.CreateEngineType(entityId).GetEngineTypeStr())
	
	def playerdestoryblock(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).PlayerDestoryBlock(xyz, cmdargs[2], cmdargs[3])
		return False, '已尝试让 %s 破坏 Pos%s 处的方块' % (create_players_str(cmdargs[0]), xyz)
	
	def openworkbench(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateBlockInfo(i).OpenWorkBench()
		return False, '已使 %s 打开工作台界面' % (create_players_str(cmdargs[0]))
	
	def openfoldgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'openfoldgui', 'cmdargs': cmdargs})
		return False, '已使 %s 打开下拉界面' % (create_players_str(cmdargs[0]))
	
	def setimmunedamage(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateHurt(i).ImmuneDamage(cmdargs[1])
		return False, '将 %s 个实体的伤害免疫设置为 %s' % (len(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def hideslotbargui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hideslotbargui', 'cmdargs': cmdargs})
		return False, '已%s %s 的工具栏' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hidehungergui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidehungergui', 'cmdargs': cmdargs})
		return False, '已%s %s 的饱食度栏' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hidehudgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidehudgui', 'cmdargs': cmdargs})
		return False, '已%s %s 的全部界面' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hidehorsehealthgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidehorsehealthgui', 'cmdargs': cmdargs})
		return False, '已%s %s 的坐骑血条' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hidehealthgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidehealthgui', 'cmdargs': cmdargs})
		return False, '已%s %s 的血条' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hidefoldgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidefoldgui', 'cmdargs': cmdargs})
		return False, '已%s %s 的下拉界面' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hideexpgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hideexpgui', 'cmdargs': cmdargs})
		return False, '已%s %s 的经验条' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hidecrosshairgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidecrosshairgui', 'cmdargs': cmdargs})
		return False, '已%s %s 的十字准星' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hidearmorgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidearmorgui', 'cmdargs': cmdargs})
		return False, '已%s %s 的盔甲栏' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def hideairsupplygui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hideairsupplygui', 'cmdargs': cmdargs})
		return False, '已%s %s 的氧气条' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))
	
	def setinvitemexchange(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetInvItemExchange(cmdargs[1], cmdargs[2])
		return False, '已交换 %s 物品栏槽位 %s 与槽位 %s 中的物品' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setinvitemnum(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[2] < 0 or cmdargs[2] > 64:
			return True, '无效的物品数量'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetInvItemNum(cmdargs[1], cmdargs[2])
		return False, '已将 %s 物品栏槽位 %s 中的物品数量设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setitemdurability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True, '无效的耐久度'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetItemDurability(2, 0, cmdargs[1])
		return False, '已设置 %s 的手持物品物品耐久度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
			
	def setitemmaxdurability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True, '无效的耐久度'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetItemMaxDurability(2, 0, cmdargs[1], True)
		return False, '已设置 %s 的手持物品最大耐久度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
		
	def setitemtierlevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] not in [0, 1, 2, 3, 4]:
			return True, '无效的挖掘等级'
		for i in cmdargs[0]:
			itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
			CFServer.CreateItem(i).SetItemTierLevel(itemdata, cmdargs[1])
			CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False, '已设置 %s 的手持物品挖掘等级为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setitemtierspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0:
			return True, '无效的挖掘速度'
		for i in cmdargs[0]:
			itemdata = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
			CFServer.CreateItem(i).SetItemTierSpeed(itemdata, cmdargs[1])
			CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False, '已设置 %s 的手持物品挖掘速度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setitemmaxstacksize(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 1:
			return True, '无效的堆叠数量 (%s < 1)' % (cmdargs[1])
		elif cmdargs[1] > 64:
			return True, '无效的堆叠数量 (%s > 64)' % (cmdargs[1])
		for i in cmdargs[0]:
			itemDict = CFServer.CreateItem(i).GetPlayerItem(2, 0, True)
			CFServer.CreateItem(i).SetMaxStackSize(itemDict, cmdargs[1])
			CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i)
		return False, '已设置 %s 的手持物品最大堆叠数量为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def playerexhaustionratio(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'	
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		exhaustion = {'heal': 0, 'jump':1, 'sprint_jump':2, 'mine':3, 'attack':4, 'global':9}
		exhaustiontype = exhaustion[cmdargs[1]]
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerExhaustionRatioByType(exhaustiontype, cmdargs[2])
		return False, '已设置 %s 的 %s 行为饥饿度消耗倍率为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setsigntextstyle(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		rgba = (cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5])
		lighting = cmdargs[6]
		if compBlockEntity.SetSignTextStyle(xyz, cmdargs[1]['id'], rgba, lighting, int(cmdargs[7])):
			return False, '将 Pos%s in %s 的告示牌 %s 文本样式设置为 %s' % (xyz, cmdargs[1]['name'], '反面' if cmdargs[7] else '正面', rgba)
		else:
			return True, '位于 Pos%s in %s 的方块不是告示牌' % (xyz, cmdargs[1]['name'])
		
	def setsigntext(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if CFServer.CreateBlockInfo(levelId).SetSignBlockText(xyz, cmdargs[1], cmdargs[2]['id'], int(cmdargs[3])):
			return False, '将 Pos%s in %s 的告示牌 %s 文本设置为 %s' % (xyz, cmdargs[2]['name'], '反面' if cmdargs[3] else '正面', cmdargs[1])
		else:
			return True, '位于 Pos%s in %s 的方块不是告示牌' % (xyz, cmdargs[2]['name'])

	def setplayerinteracterange(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型' 
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetPlayerInteracteRange(cmdargs[1])
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setplayerinteracterange', 'cmdargs': cmdargs})
		return False, '已设置 %s 的触及距离为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def summonprojectile(self, cmdargs, playerId, variant, data):
		try:
			targetlen = len(cmdargs[7])
			target = cmdargs[7][0]
		except:
			targetlen = 1
			target = None
		if not targetlen == 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		
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
		return False, '成功生成抛射物'
	
	def setstepheight(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateAttr(i).SetStepHeight(cmdargs[1])
		return False, '将 %s 能迈过的最大高度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setsize(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateCollisionBox(i).SetSize((cmdargs[1], cmdargs[2]))
		return False, '已设置 %s 个实体的碰撞箱为 (%s, %s)' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])
		
	def playerchatprefix(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateExtraData(i).SetExtraData('chatprefix', cmdargs[1])
		return False, '将 %s 的聊天前缀设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def writehealthtoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			health = CFServer.CreateAttr(entity).GetAttrValue(0)
			health = int(round(health))
			compcmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, health), entity, False)
		return False, '已将 %s 个实体的生命值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
		
	def writehungertoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			hunger = CFServer.CreateAttr(entity).GetAttrValue(4)
			hunger = int(round(hunger))
			compcmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, hunger), entity, False)
		return False, '已将 %s 个实体的饥饿值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)

	def writearmortoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			armor = CFServer.CreateAttr(entity).GetAttrValue(12)
			armor = int(round(armor))
			compcmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, armor), entity, False)
		return False, '已将 %s 个实体的盔甲值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
	
	def writespeedtoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			speed = CFServer.CreateActorMotion(entity).GetMotion()
			speed = (speed[0]**2 + speed[1]**2 + speed[2]**2)**0.5  # 计算速度
			speed = int(round(speed*20))
			compcmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, speed), entity, False)
		return False, '已将 %s 个实体的速度值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
	
	def executecb(self, cmdargs, playerId, variant, data):
		xyz = (intg(cmdargs[0][0]), int(cmdargs[0][1]), intg(cmdargs[0][2]))
		success = compBlockEntity.ExecuteCommandBlock(xyz, cmdargs[1]['id'])
		if success:
			return False, '已执行位于 Pos%s in %s 的命令方块' % (xyz, cmdargs[1]['name'])
		else:
			return True, '位于 Pos%s in %s 的方块不是命令方块' % (xyz, cmdargs[1]['name'])
		
	def setname(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateName(i).SetName(cmdargs[1])
		return False, '已设置 %s 个实体的名称为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def aicontrol(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateControlAi(i).SetBlockControlAi(cmdargs[1], cmdargs[2])
		return False, '已%s %s 个实体的AI' % ('启用' if cmdargs[1] else '禁用', len(cmdargs[0]))

	def param(self, cmdargs, playerId, variant, data):
		params = compExtra.GetExtraData('parameters')
		
		# 兼容旧版本
		if type(params) is dict:
			need_upgrade = False
			for key, value in params.items():
				if not isinstance(value, dict):
					if value.replace('.', '', 1).isdigit():
						params[key] = {'type': 'float', 'value': value} if '.' in value else {'type': 'int', 'value': value}
					else:
						params[key] = {'type': 'str', 'value': value}
					need_upgrade = True
			
			if need_upgrade:
				compExtra.SetExtraData('parameters', params)
		
		if variant == 0:  # show
			if cmdargs[1] is None:
				output = ['当前存储的变量:']
				if params and type(params) is dict:
					for key, value_info in params.items():
						output.append(' - %s (%s): %s' % (key, value_info.get('type', 'unknown'), value_info.get('value', '')))
				return False, '\n'.join(output)
			else:
				if type(params) == dict and params.get(cmdargs[1]) is not None:
					var_info = params[cmdargs[1]]
					return False, '变量 %s [%s] = %s' % (cmdargs[1], var_info.get('type', 'unknown'), var_info.get('value', ''))
				else:
					return True, '未知的变量 %s' % cmdargs[1]
					
		elif variant == 2:  # del
			if type(params) == dict and params.get(cmdargs[1]):
				del params[cmdargs[1]]
				compExtra.SetExtraData('parameters', params)
				return False, '已删除变量 %s' % cmdargs[1]
			else:
				return True, '未知的变量 %s ' % cmdargs[1]
		
		elif variant == 3:  # operation
			if not (type(params) == dict and params.get(cmdargs[1])):
				return True, '未知的变量 %s ' % cmdargs[1]	
			var_info = params[cmdargs[1]]
			var_type = var_info['type']
			current_value = var_info['value']
			
			if cmdargs[3].replace('.', '', 1).isdigit():
				if cmdargs[3].find('.') != -1:
					operand_value = float(cmdargs[3])
				else:
					operand_value = int(cmdargs[3])
			else:
				operand_value = cmdargs[3]
					
			if cmdargs[2] == '加':
				if isinstance(operand_value, (int, float)) and isinstance(current_value, (int, float)):
					result = current_value + operand_value
				else:
					result = str(current_value) + str(operand_value)
				
			elif cmdargs[2] == '乘':
				if isinstance(operand_value, (int, float)) and isinstance(current_value, (int, float)):
					result = current_value * operand_value
				else:
					if isinstance(operand_value, int) and isinstance(current_value, str):
						result = current_value * operand_value
					elif isinstance(operand_value, str) and isinstance(current_value, int):
						result = operand_value * current_value
					else:
						return True, '仅支持整数与字符串的乘法'
			
			elif var_type in ['int', 'float'] and isinstance(operand_value, (int, float)):
				if cmdargs[2] == '减':
					result = current_value - operand_value
				elif cmdargs[2] == '除':
					if operand_value == 0:
						return True, '除数不能为零'
					result = current_value / operand_value
				elif cmdargs[2] == '乘方':
					result = current_value ** operand_value
				elif cmdargs[2] == '取余':
					if operand_value == 0:
						return True, '取余操作数不能为零'
					result = current_value % operand_value
				elif cmdargs[2] == '整除':
					if operand_value == 0:
						return True, '除数不能为零'
					result = current_value // operand_value

			else:
				return True, '字符串不支持该操作'
			
			# 更新结果并转换类型
			if isinstance(result, int):
				var_newtype = 'int'
			elif isinstance(result, float):
				var_newtype = 'float'
			else:
				var_newtype = 'str'
		
			params[cmdargs[1]]['type'] = var_newtype
			params[cmdargs[1]]['value'] = result
			compExtra.SetExtraData('parameters', params)
			return False, '操作完成: 结果 %s' % result
		
		elif variant == 4:  # random
			if not type(params) == dict:
				params = {}
			
			params[cmdargs[1]] = {
				'type': 'int',
				'value': random.randint(cmdargs[2], cmdargs[3])
			}
			compExtra.SetExtraData('parameters', params)
			return False, '已将 %s 设置为随机值 %s' % (cmdargs[1], params[cmdargs[1]]['value'])
		
		elif variant == 1:  # set 
			if not type(params) == dict:
				params = {}
			
			if cmdargs[3] is not None:
				try:
					if cmdargs[2] == 'int':
						value = int(cmdargs[3])
					elif cmdargs[2] == 'float':
						value = float(cmdargs[3])
					else:  # str
						value = str(cmdargs[3])
				except:
					return True, '%s 无法转换为 %s 类型' % (cmdargs[3], cmdargs[2])
			else:
				value = 0 if cmdargs[2] == 'int' else 0.0 if cmdargs[2] == 'float' else ''
			
			params[cmdargs[1]] = {
				'type': cmdargs[2],
				'value': value
			}
			
			compExtra.SetExtraData('parameters', params)
			return False, '已修改 %s 类型变量 %s = %s' % (cmdargs[2], cmdargs[1], value)	

	def kickt(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for kickplayer in cmdargs[0]:
			compcmd.SetCommand('/kick %s %s' % (CFServer.CreateName(kickplayer).GetName(), cmdargs[1]))
		return False, '已将 %s 踢出游戏: %s' % (create_players_str(cmdargs[0]), cmdargs[1])
			
	def explode(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			position = CFServer.CreatePos(i).GetFootPos()
			CFServer.CreateExplosion(levelId).CreateExplosion(position, cmdargs[1], cmdargs[3], cmdargs[2], '', '')
		return False, '已引爆 %s 个实体' % len(cmdargs[0])

	def explodebypos(self, cmdargs, playerId, variant, data):
		if CFServer.CreateExplosion(levelId).CreateExplosion(cmdargs[0], cmdargs[1], cmdargs[3], cmdargs[2], '', ''):
			return False, '爆炸已创建于 Pos%s' % (cmdargs[0],)
		else:
			return True, '爆炸创建失败'

	def console(self, cmdargs, playerId, variant, data):
		cmd = cmdargs[0]
		if cmd.startswith('/'):
			cmd = cmd[1:]
		params = compExtra.GetExtraData('parameters')
		
		cmd2 = ''
		if params and isinstance(params, dict):
			for word in cmd.split(' '):
				if word.startswith('param:'):
					var_name = word.split(':', 1)[1]
					# 查找变量
					if var_name in params:
						var_info = params[var_name]
						# 根据变量类型格式化
						if var_info['type'] == 'str':
							word = '"%s"' % var_info['value']  # 字符串添加引号
						elif var_info['type'] == 'int' or var_info['type'] == 'float':
							word = str(var_info['value'])
						else:  # 未知类型保持原格式
							word = str(var_info['value'])
					else:
						pass
				
				cmd2 = ('%s %s' % (cmd2, word)).strip()
		
		if not cmd2:
			cmd2 = cmd
		
		final_cmd = '/' + cmd2.replace("'", '"')
		compcmd.SetCommand(final_cmd)
		return False, '已将指令处理后执行: %s' % final_cmd
	
	def addaroundentitymotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
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
				return True, '设置失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False, '已设置运动器'
	
	def addaroundpointmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
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
				return True, '设置失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False, '已设置运动器'

	def addvelocitymotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
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
				return True, '创建失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False, '已设置运动器'
	
	def startmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			compExtra = CFServer.CreateExtraData(i)
			CompMotion = CFServer.CreateActorMotion(i)
			CompType = CFServer.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			Motions = compExtra.GetExtraData('Motions')
			if Motions:
				if EntityType == 'minecraft:player':
					startMotion = CompMotion.StartPlayerMotion
				else:
					startMotion = CompMotion.StartEntityMotion
				for ii in Motions:
					startMotion(ii)
				tot += 1
		if tot:
			return False, '已启用 %s 个实体的运动器' % tot
		else:
			return True, '实体没有绑定运动器'
	
	def stopmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			compExtra = CFServer.CreateExtraData(i)
			CompMotion = CFServer.CreateActorMotion(i)
			CompType = CFServer.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			Motions = compExtra.GetExtraData('Motions')
			if Motions:
				if EntityType == 'minecraft:player':
					stopMotion = CompMotion.StopPlayerMotion
				else:
					stopMotion = CompMotion.StopEntityMotion
				for ii in Motions:
					stopMotion(ii)
				tot += 1
		if tot:
			return False, '已暂停 %s 个实体的运动器' % tot
		else:
			return True, '实体没有绑定运动器'
	
	def removemotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			compExtra = CFServer.CreateExtraData(i)
			CompMotion = CFServer.CreateActorMotion(i)
			Motions = compExtra.GetExtraData('Motions')
			CompType = CFServer.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if Motions:
				if EntityType == 'minecraft:player':
					removeMotion = CompMotion.RemovePlayerMotion
				else:
					removeMotion = CompMotion.RemoveEntityMotion
				for ii in Motions[:]:
					removeMotion(ii)
					Motions.remove(ii)
				compExtra.SetExtraData('Motions', Motions)
				tot += 1
		if tot:
			return False, '已移除 %s 个实体的运动器' % tot
		else:
			return True, '实体没有绑定运动器'

	def addenchant(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if isinstance(cmdargs[3], int):
			slotType = 0
			slot = cmdargs[3]
		else:
			slotType = 2
			slot = 0
		for i in cmdargs[0]:
			itemdict = CFServer.CreateItem(i).GetPlayerItem(slotType, slot, True)
			if itemdict:
				if itemdict['userData'] is None:
					itemdict['userData'] = {}
				if itemdict['userData'].get('ench', None) is None:
					itemdict['userData']['ench'] = []
				
				itemdict['userData']['ench'].insert(0, {
					'lvl': {'__type__': 2, '__value__': cmdargs[2]},
					'id':  {'__type__': 2, '__value__': cmdargs[1]['type']},
					'modEnchant': {'__type__': 8, '__value__': ''}
				})
				itemdict['enchantData'] = []
				
				if slotType == 0:
					CFServer.CreateItem(i).SpawnItemToPlayerInv(itemdict, i, slot)
				else:
					CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemdict, i)
		return False, '已为 %s 的%s物品添加附魔 %s' % (create_players_str(cmdargs[0]), '手持' if slotType else '背包', cmdargs[1]['identifier'])

	def addtrackmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
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
				return True, '创建失败'
			Motions = compExtra.GetExtraData('Motions')
			if not Motions:
				Motions = []
			Motions.append(Mid)
			compExtra.SetExtraData('Motions', Motions)
		return False, '已设置运动器'

	def setactorcanburnbylightning(self, cmdargs, playerId, variant, data):
		compGame.SetCanActorSetOnFireByLightning(cmdargs[0])
		return False, '已 %s 实体被闪电点燃' % ('允许' if cmdargs[1] else '禁止')

	def setblockcanburnbylightning(self, cmdargs, playerId, variant, data):
		compGame.SetCanBlockSetOnFireByLightning(cmdargs[0])
		return False, '已 %s 方块被闪电点燃' % ('允许' if cmdargs[1] else '禁止')

	def cancelshearsdestoryblockspeedall(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			compItem.CancelShearsDestoryBlockSpeedAll()
		return False, '已取消 %s 个实体剪刀破坏方块速度的所有设置' % (len(cmdargs[0]))

	def cancelshearsdestoryblockspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			compItem.CancelShearsDestoryBlockSpeed(cmdargs[1])
			#	return True, '无效的命名空间id'
		return False, '已取消 %s 个实体剪刀破坏 %s 速度的设置' % (len(cmdargs[0]), cmdargs[1])

	def setshearsdestoryblockspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[2] < 1:
			return True, '速度必须大于1'
		for i in cmdargs[0]:
			compItem = CFServer.CreateItem(i)
			compItem.SetShearsDestoryBlockSpeed(cmdargs[1], cmdargs[2])
			#	return True, '无效的命名空间id'
		return False, '已设置 %s 个实体剪刀破坏 %s 速度为 %s' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])

	def changeselectslot(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			if CompType.GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CompPlayer = CFServer.CreatePlayer(i)
			CompPlayer.ChangeSelectSlot(cmdargs[1])
		return False, '将 %s 的选择槽位设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def forbidliquidflow(self, cmdargs, playerId, variant, data):
		compGame.ForbidLiquidFlow(cmdargs[0])
		return False, '已 %s 液体流动' % ('禁止' if cmdargs[0] else '允许')

	def getuid(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		uid_dict = {}
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			if CompType.GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			playername = CFServer.CreateName(i).GetName()
			uid_dict[playername] = CFServer.CreateHttp(levelId).GetPlayerUid(i)
		return False, '获取到的UID为%s' % (uid_dict)
		# serversystem.NotifyToMultiClients(list(cmdargs[0]), 'CustomCommandClient', {'cmd':'getuid', 'origin': playerId})

	def givewithnbt(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[1])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			for i in ['isDiggerItem', 'enchantData', 'itemId', 'modEnchantData', 'modId', 'modItemId', 'itemName', 'auxValue']:
				itemDict.pop(i, False) #删去多余键值对(这些已被弃用)
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			for i in cmdargs[0]:
				if not CFServer.CreateItem(i).SpawnItemToPlayerInv(itemDict, i):
					return True, '此JSON生成物品失败'
			return False, '成功给予 %s 物品 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'
		
	def spawnitemtocontainer(self, cmdargs, playerId, variant, data):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		x = intg(cmdargs[2][0])
		y = int(cmdargs[2][1])
		z = intg(cmdargs[2][2])
		itemDict = compItemWorld.GetContainerItem((x, y, z), cmdargs[1], cmdargs[3]['id'], True)
		result = checkjson(cmdargs[0])
		if result[1] == True:
			return True, result[0]
		itemDict2 = result[0]
		if isinstance(itemDict2, dict):
			for k,v in [('durability', 0), ('customTips', ''), ('extraId', ''), ('newAuxValue', 0), ('userData', None), ('showInHand', True)]:
				itemDict2.setdefault(k, v)
			if itemDict is not None:
				for i in ['isDiggerItem', 'enchantData', 'itemId', 'modEnchantData', 'modId', 'modItemId', 'itemName', 'auxValue']:
					itemDict.pop(i) #删去多余键值对(这些已被弃用)
					itemDict2.pop(i, False)
				countOrign = itemDict.pop('count')
			else: countOrign = 0
			countAdd = itemDict2.pop('count', 1)
			if itemDict2.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if ((itemDict is None) or itemDict == itemDict2) and countOrign+countAdd <= 64:
				itemDict2.update({'count': countOrign+countAdd})
				if compItemWorld.SpawnItemToContainer(itemDict2, cmdargs[1], (x, y, z), cmdargs[3]['id']):
					return False, '向槽位 %s 添加 %s * %s' % (cmdargs[1], itemDict2.get('newItemName'), countAdd)
				else:
					return True, '位于 Pos(%s,%s,%s) 的方块不是容器' % (x,y,z)
			else:
				return True, '槽位已满'
		else:
			return True, '无效的nbt'

	def spawnitemtoenderchest(self, cmdargs, playerId, variant, data):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		for player in cmdargs[2]:
			if CFServer.CreateEngineType(player).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[0])
		if result[1] == True:
			return True, result[0]
		itemDict2 = result[0]
		if isinstance(itemDict2, dict):
			for k,v in [('durability', 0), ('customTips', ''), ('extraId', ''), ('newAuxValue', 0), ('userData', None), ('showInHand', True)]:
				itemDict2.setdefault(k, v)
			countAdd = itemDict2.pop('count', 1)
			for player in cmdargs[2]:
				compItem = CFServer.CreateItem(player)
				itemDict = compItem.GetEnderChestItem(player, cmdargs[1], True)
				if itemDict:
					for i in ['isDiggerItem', 'enchantData', 'itemId', 'modEnchantData', 'modId', 'modItemId', 'itemName', 'auxValue']:
						itemDict.pop(i) #删去多余键值对(这些已被弃用)
						itemDict2.pop(i, False)
					countOrign = itemDict.pop('count')
				else: countOrign = 0
				if itemDict2.get('newItemName') is None:
					return True, '物品数据中缺少 newItemName 键'
				if ((not itemDict) or itemDict == itemDict2) and countOrign+countAdd <= 64:
					itemDict2.update({'count': countOrign+countAdd})
					if compItem.SpawnItemToEnderChest(itemDict2, cmdargs[1]):
						return False, '向 %s 的末影箱中的槽位 %s 添加 %s * %s' % (create_players_str(cmdargs[2]), cmdargs[1], itemDict2.get('newItemName'), countAdd)
				else:
					return True, '槽位已满'
		else:
			return True, '无效的nbt'

	def replaceitemtocarried(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[1])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i)
			return False, '将 %s 的主手物品替换为 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'

	def removeenchant(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).RemoveEnchantToInvItem(cmdargs[2], cmdargs[1]['type'])
		return False, '将 %s 背包物品中的 %s 附魔移除' % (create_players_str(cmdargs[0]), cmdargs[1]['identifier'])

	def resetmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			CompMotion = CFServer.CreateActorMotion(i)
			if CompType.GetEngineTypeStr() == 'minecraft:player':
				CompMotion.SetPlayerMotion((0, 0, 0))
			else:
				CompMotion.ResetMotion()
		return False, '已重置 %s 个实体的运动状态' % len(cmdargs[0])

	def setleashholder(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[0]) == 1:
			for i in cmdargs[1]:
				compEntityD = CFServer.CreateEntityDefinitions(i)
				compEntityD.SetLeashHolder(cmdargs[0])
			return False, '已尝试拴住实体'
		else:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'

	def setlootdropped(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compEntityD = CFServer.CreateEntityDefinitions(i)
			compEntityD.SetLootDropped(cmdargs[1])
		return False, '将 %s 个实体的掉落概率设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def setmaxairsupply(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compBrea = CFServer.CreateBreath(i)
			compBrea.SetMaxAirSupply(cmdargs[1])
		return False, '将 %s 个实体的最大氧气量设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def knockback(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CFServer.CreateAction(i).SetMobKnockback(cmdargs[1], cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5])
		return False, '已击飞 %s 个实体' % (len(cmdargs[0]))

	def setmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CFServer.CreateEngineType(i)
			CompMotion = CFServer.CreateActorMotion(i)
			if CompType.GetEngineTypeStr() == 'minecraft:player':
				CompMotion.SetPlayerMotion(cmdargs[1])
			else:
				CompMotion.SetMotion(cmdargs[1])
		return False, '将 %s 个实体的动量设置为 %s' % (len(cmdargs[0]), str(cmdargs[1]))

	def setopencontainersability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetOpenContainersAbility(cmdargs[1])
		return False, '将 %s 的开箱权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setoperatedoorability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetOperateDoorsAndSwitchesAbility(cmdargs[1])
		return False, '将 %s 的开门权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setorbexperience(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:xp_orb':
				return True, '选择器必须为经验球类型'
		for i in cmdargs[0]:
			compAttr = CFServer.CreateExp(i)
			compAttr.SetOrbExperience(cmdargs[1])
		return False, '将 %s 个经验球的经验值设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def setpersistent(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compAttr = CFServer.CreateAttr(i)
			compAttr.SetPersistent(cmdargs[1])
		return False, '将 %s 个实体的自动清除设置为 %s' % (len(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setpistonmaxinteractioncount(self, cmdargs, playerId, variant, data):
		if compGame.SetPistonMaxInteractionCount(cmdargs[0]):
			return False, '将活塞最大推动数设置为 %s' % cmdargs[0]
		else:
			return True, '无效的数值'

	def setplayeruiitem(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[2])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			for i in cmdargs[0]:
				CFServer.CreateItem(i).SetPlayerUIItem(i, cmdargs[1], itemDict, cmdargs[3])
			return False, '将 %s 的UI物品设置为 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'

	def _if(self, cmdargs, playerId, variant, data):
		if variant == 0:  # cmd模式不变
			if cmdargs[3] is None:
				result = [compcmd.SetCommand(cmdargs[1].replace("'", '"'), playerId), False]
			else:
				result = [compcmd.SetCommand(cmdargs[1].replace("'", '"'), playerId), compcmd.SetCommand(cmdargs[3].replace("'", '"'), playerId)]
			if cmdargs[2] == 'not':
				if result[0]:
					return True, '运算符成立(%s)' % (result[1])
				else:
					return False, '运算符不成立(%s)' % (result[1])
			elif cmdargs[2] == 'and':
				if result[0] and result[1]:
					return False, '运算符成立(%s, %s)' % (result[0], result[1])
				else:
					return True, '运算符不成立(%s, %s)' % (result[0], result[1])
			elif cmdargs[2] == 'or':
				if result[0] or result[1]:
					return False, '运算符成立(%s, %s)' % (result[0], result[1])
				else:
					return True, '运算符不成立(%s, %s)' % (result[0], result[1])
			elif cmdargs[2] == 'xor':
				if result[0] != result[1]:
					return False, '运算符成立(%s, %s)' % (result[0], result[1])
				else:
					return True, '运算符不成立(%s, %s)' % (result[0], result[1])
			else:
				return True, '未知的逻辑运算符'
		
		else:  # param模式 (variant1)
			params = compExtra.GetExtraData('parameters')
			
			# 检查变量是否存在
			if not (type(params) == dict and cmdargs[1] in params):
				return True, '未知的变量\'%s\'' % cmdargs[1]
			
			var_info = params[cmdargs[1]]
			var_value = var_info['value']
			var_type = var_info['type']
			
			# 尝试将输入值转换为变量相应类型
			try:
				if var_type == 'int':
					input_value = int(cmdargs[3])
				elif var_type == 'float':
					input_value = float(cmdargs[3])
				else:  # str
					input_value = str(cmdargs[3])
			except:
				return True, '无法将 %s 转换为%s类型进行比较' % (cmdargs[3], var_type)
			
			# 执行比较操作
			if cmdargs[2] == 'equals':
				result = var_value == input_value
				symbol = '=='
			elif cmdargs[2] == 'not_equals':
				result = var_value != input_value
				symbol = '!='
			else:
				# 检查类型是否支持比较
				if var_type == 'str':
					return True, '字符串变量只支持等于(equals)和不等于(not_equals)比较'
				
				# 执行数值比较
				if cmdargs[2] == 'greater_than':
					result = var_value > input_value
					symbol = '>'
				elif cmdargs[2] == 'less_than':
					result = var_value < input_value
					symbol = '<'
				elif cmdargs[2] == 'not_less':
					result = var_value >= input_value
					symbol = '>='
				elif cmdargs[2] == 'not_greater':
					result = var_value <= input_value
					symbol = '<='
				else:
					return True, '未知的比较操作符'
			
			# 格式化显示值（避免浮点数精度问题）
			if var_type == 'float':
				display_value = round(var_value, 6)
				display_input = round(input_value, 6)
			else:
				display_value = var_value
				display_input = input_value
			
			return not result, '表达式%s成立(%s %s %s)' % ('' if result else '不', display_value, symbol, display_input)
	
	def setteleportability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetTeleportAbility(cmdargs[1])
		return False, '将 %s 的传送权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def settradelevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if not CFServer.CreateEngineType(i).GetEngineTypeStr() in ['minecraft:villager', 'minecraft:villager_v2']:
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateEntityDefinitions(i).SetTradeLevel(cmdargs[1])
		return False, '已设置 %s 个村民的交易等级为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setvignette(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[1]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if variant == 0:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettecenter', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角中心设置为 %s, %s' % (create_players_str(cmdargs[1]), cmdargs[2], cmdargs[3])
		elif variant == 1:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignetteradius', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角半径设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 2:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettecolor', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角颜色设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 3:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettesmooth', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角平滑度设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 4:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignette', 'cmdargs': cmdargs})
			return False, '已%s %s 的屏幕暗角' % ('启用' if cmdargs[2] else '禁用', create_players_str(cmdargs[1]))
		
	def setbrewingstandslotitem(self, cmdargs, playerId, variant, data):
		if cmdargs[1] not in range(5):
			return True, '无效的槽位'
		x, y, z = cmdargs[2]
		xyz = (intg(x), int(y), intg(z))
		result = checkjson(cmdargs[0])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			if compItemWorld.SetBrewingStandSlotItem(itemDict, cmdargs[1], xyz, cmdargs[3]['id']):
				return False, '将槽位 %s 的物品设置为 %s' % (cmdargs[1], itemDict.get('itemName'))
			else:
				return True, '设置 Pos%s 的方块时失败' % (xyz,)
		else:
			return True, '无效的nbt'

	def setdisablecontainers(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateGame(i).SetDisableContainers(cmdargs[1])
		return False, '将 %s 的容器权限设置为 %s' % (create_players_str(cmdargs[0]), '禁止' if cmdargs[1] else '允许')
		
	def setdisabledropitem(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateGame(i).SetDisableDropItem(cmdargs[1])
		return False, '将 %s 的丢弃物品权限设置为 %s' % (create_players_str(cmdargs[0]), '禁止' if cmdargs[1] else '允许')
		
	def setdisablehunger(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateGame(i).SetDisableHunger(cmdargs[1])
		return False, '将 %s 的饱食度设置为 %s' % (create_players_str(cmdargs[0]), '屏蔽' if cmdargs[1] else '生效')

	def setenchantmentseed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreatePlayer(i).SetEnchantmentSeed(cmdargs[1])
		return False, '将 %s 的附魔种子设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setentityitem(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		result = checkjson(cmdargs[2])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if not isinstance(itemDict, dict):
			return True, '无效的nbt'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:player':
				return True, '选择器必须为非玩家类型'
		if itemDict.get('newItemName') is None:
			return True, '物品数据中缺少 newItemName 键'
		if itemDict.get('count') is None:
			return True, '物品数据中缺少 count 键'
		for i in cmdargs[0]:
			CFServer.CreateItem(i).SetEntityItem(cmdargs[1], itemDict, cmdargs[3])
		return False, '已设置 %s 个实体的物品' % (len(cmdargs[0]))
		
	def setentityowner(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] is None:
			ownerid = None
		else:
			if len(cmdargs[1]) != 1:
				return True, '只允许一个实体, 但提供的选择器允许多个实体'
			ownerid = cmdargs[1][0]

		failed_entities = []
		
		for i in cmdargs[0]:
			if not CFServer.CreateActorOwner(i).SetEntityOwner(ownerid):
				failed_entities.append(CFServer.CreateEngineType(i).GetEngineTypeStr())
		
		if failed_entities:
			return True, '部分实体执行过程中出现错误: %s' % failed_entities,
		else:
			return False, '已设置 %s 个实体的属主' % (len(cmdargs[0]))
		
	def setentityride(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[0]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		failed_entities = []
		
		for i in cmdargs[1]:
			if not CFServer.CreateRide(i).SetEntityRide(cmdargs[0][0], i):
				failed_entities.append(CFServer.CreateEngineType(i).GetEngineTypeStr())
		
		if failed_entities:
			return True, '部分实体执行过程中出现错误: %s' % failed_entities,
		else:
			return False, '已驯服 %s 个生物' % (len(cmdargs[1]))
		
	def setframeitemdropchange(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if compBlockEntity.SetFrameItemDropChange(xyz, cmdargs[1]['id'], cmdargs[2]):
			return False, '已设置 Pos%s 的展示框掉落几率为 %s' % (xyz, cmdargs[2]*100)
		else:
			return True, '位于 Pos%s 的方块不是展示框' % (xyz,)
		
	def setframerotation(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if compBlockEntity.SetFrameRotation(xyz, cmdargs[1]['id'], cmdargs[2]):
			return False, '已设置 Pos%s 的展示框旋转角度为 %s 度' % (xyz, cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是展示框' % (xyz,)
		
	def sethopperspeed(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if compBlockEntity.SetHopperSpeed(xyz, cmdargs[1]['id'], cmdargs[2]):
			return False, '已设置 %s 的漏斗运输用时为 %s 红石刻' % (xyz, cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是漏斗' % (xyz,)
		
	def sethudchatstackposition(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'sethudchatstackposition', 'cmdargs': cmdargs})
		return False, '将 %s 的聊天UI位置设置为 %s, %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def sethudchatstackvisible(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		serversystem.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'sethudchatstackvisible', 'cmdargs': cmdargs})
		return False, '已%s %s 的聊天UI' % ('启用' if cmdargs[1] else '禁用', create_players_str(cmdargs[0]))
	
	def setshowrideui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateRide(i).SetShowRideUI(i, cmdargs[1])
		return False, '已%s %s 的骑乘UI' % ('启用' if cmdargs[1] else '禁用', create_players_str(cmdargs[0]))
	
	def setgaussian(self, cmdargs, playerId, variant, data):
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[1]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if variant == 0:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setgaussian', 'cmdargs': cmdargs})
			return False, '已 %s %s 的高斯模糊' % ('启用' if cmdargs[2] else '禁用', create_players_str(cmdargs[1]))
		elif variant == 1:
			serversystem.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setgaussianradius', 'cmdargs': cmdargs})
			return False, '已将 %s 的高斯模糊半径设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		
	def scoreparam(self, cmdargs, playerId, variant, data):
		scoreboard_name = cmdargs[1]
		
		objects = compGame.GetAllScoreboardObjects()
		found = False
		for obj in objects:
			if obj['name'] == scoreboard_name:
				found = True
				break
		
		if not found:
			return True, '未找到该计分板对象'
		
		target_name = cmdargs[0]
		params = compExtra.GetExtraData('parameters')
		
		if not (params and type(params) is dict and params.get(target_name)):
			return True, '未找到变量: %s' % target_name
		
		var_info = params[target_name]
		var_value = var_info.get('value', None)
		
		try:
			score = int(var_value)
		except (TypeError, ValueError):
			return True, '无法将变量值转换为整数: %s' % target_name
		
		command = '/scoreboard players set %s %s %s' % (target_name, scoreboard_name, score)
		
		if not compcmd.SetCommand(command):
			return True, '设置计分板失败'
		
		return False, '已将变量 %s 的值(%s)设置到计分板 %s 中' % (target_name, score, scoreboard_name)
	
	def setblocknbt(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if cmdargs[2] is None:
			return False, 'Pos%s 处的方块NBT为\n%s' % (xyz, CFServer.CreateBlockInfo(levelId).GetBlockEntityData(cmdargs[1]['id'], xyz))
		else:
			result = checkjson(cmdargs[2])
			if result[1] == True:
				return True, result[0]
			blockDict = result[0]
			CFServer.CreateBlockInfo(levelId).SetBlockEntityData(cmdargs[1]['id'], xyz, blockDict)
			return False, '已设置 Pos%s 的方块nbt' % (xyz,)

	def summonitem(self, cmdargs, playerId, variant, data):
		result = checkjson(cmdargs[1])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			x, y, z = cmdargs[0]
			xyz = (intg(x), int(y), intg(z))
			itemDict.setdefault('count', 1)
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if not serversystem.CreateEngineItemEntity(itemDict, data['origin']['dimension'], xyz):
				return True, '生成失败'
			return False, '已在 Pos%s 处生成 %s * %s' % (xyz, itemDict.get('newItemName'), itemDict.get('count'))
		return True, '无效的nbt'
	
	def mute(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CFServer.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CFServer.CreateExtraData(i).SetExtraData('mute', cmdargs[1])
		return False, '将 %s 的禁言状态设置为 %s' % (create_players_str(cmdargs[0]), '启用' if cmdargs[1] else '停用')
	
	def chatclear(self, cmdargs, playerId, variant, data):
		if playerId is None:
			return True, '该命令无法在命令方块或控制台执行'	
		serversystem.NotifyToClient(playerId, 'CustomCommandClient', {'cmd': 'chatclear'})
		return False, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
	
	def openui(self, cmdargs, playerId, variant, data):
		serversystem.NotifyToClient(playerId, 'CustomCommandClient', {'cmd': 'openui', 'cmdargs': cmdargs})
		return False, ''
	
	def gettps(self, cmdargs, playerId, variant, data):
		tick_time = serverApi.GetServerTickTime()
		TPS = "20.0*" if tick_time <= 50 else "%.1f" % (1000 / tick_time)
		return False,"§r§eTPS:%s mspt:%.2fms" % (TPS,tick_time)
	
	def copyright(self, cmdargs, playerId, variant, data):
		return False, copyrightInfo
	
	def chatlimit(self, cmdargs, playerId, variant, data):
		if cmdargs[0] < 0:
			return True, '发言间隔不能小于0'
		if compExtra.SetExtraData('limitFrequency', cmdargs[0]):
			return False, '已将发言间隔限制设置为 %.1f 秒' % cmdargs[0]
		else:
			return True, '设置失败'


	def summonnbt(self, cmdargs, playerId, variant, data):
		pass
		#result = checkjson(cmdargs[2])
		#if result[1] == True:
		#	return True, result[0]
		#entityDict = result[0]
		#entityDict['identifier'] = {'__type__': 8,'__value__': cmdargs[0]['entityType']}
		#if entityDict.get('Rotation') is None:
		#	rot = (0, 0)
		#else:
		#	rot = None
		#print(entityDict, cmdargs[1], rot, cmdargs[3]['id'], cmdargs[4])
		#serversystem.CreateEngineEntityByNBT(entityDict, cmdargs[1], rot, cmdargs[3]['id'], cmdargs[4])
		#return False, '已生成实体'


	# 服务端函数部分到此结束

	def TickClient(self):
		'''
		@description 客户端的零件对象逻辑驱动入口
		'''
		PartBase.TickClient(self)

	def TickServer(self):
		'''
		@description 服务端的零件对象逻辑驱动入口
		'''
		PartBase.TickServer(self)

	def DestroyClient(self):
		'''
		@description 客户端的零件对象销毁逻辑入口
		'''
		PartBase.DestroyClient(self)

	def DestroyServer(self):
		'''
		@description 服务端的零件对象销毁逻辑入口
		'''
		PartBase.DestroyServer(self)
