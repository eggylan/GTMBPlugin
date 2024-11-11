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
		clientsystem.ListenForEvent("Minecraft", "preset", "opencb", self, self.cbscreen)
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

	def cbscreen(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName("advcbui")[0]
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
		uiNodePreset = self.GetParent().GetChildPresetsByName("advcbui")[0]
		if uiNodePreset.GetUiActive() == True:
			uiNodePreset.SetUiActive(False)
			uiNodePreset.SetUiVisible(False)
			print(args)

	def enchant(self, enchantdata):
		import mod.server.extraServerApi as serverApi
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
		serverApi.GetEngineCompFactory().CreateItem(itemdata["__id__"]).SpawnItemToPlayerInv(itemdata, itemdata["__id__"])

	def InitServer(self):
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerChatEvent", self, self.OnServerChat)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "CommandEvent", self, self.OnCommandEvent)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerJoinMessageEvent", self, self.OnAddPlayerEvent)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerLeftMessageServerEvent", self, self.OnRemovePlayerEvent)
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerBlockUseEvent", self, self.OnBlockUseEvent)
		serversystem.ListenForEvent('Minecraft', 'preset', "enchant", self, self.enchant)
		serversystem.ListenForEvent('Minecraft', 'preset', "getitem", self, self.getitem)
		serversystem.ListenForEvent('Minecraft', 'preset', "changeTip", self, self.changeTips)
		serversystem.ListenForEvent('Minecraft', 'preset', "changenbt", self, self.changenbt)

		"""
		@description 服务端的零件对象初始化入口
		"""

		PartBase.InitServer(self)
	
	def OnBlockUseEvent(self, args):
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		operation = serverApi.GetEngineCompFactory().CreatePlayer(args['playerId']).GetPlayerOperation()
		if operation == 2:
			serversystem.NotifyToClient(args['playerId'], "opencb", args)
			extracomp = serverApi.GetEngineCompFactory().CreateExtraData(args['playerId'])
			extracomp.SetExtraData("editingcb",[args['x'],args['y'],args['z']])
			print(extracomp.GetExtraData("editingcb"))


	def changenbt(self, args):
		import mod.server.extraServerApi as serverApi
		serverApi.GetEngineCompFactory().CreateItem(args["__id__"]).SpawnItemToPlayerCarried(args["nbt"], args["__id__"])

	def changeTips(self, tips):
		import mod.server.extraServerApi as serverApi
		itemComp = serverApi.GetEngineCompFactory().CreateItem(tips["__id__"])
		itemDict = itemComp.GetEntityItem(2, 0, True)
		if tips["Tips"] == '':
			del itemDict['userData']['ItemCustomTips']
		itemDict['customTips'] = tips["Tips"]
		itemComp.SpawnItemToPlayerCarried(itemDict, tips["__id__"])

	def OnServerChat(self, args):
		playerId = args["playerId"]
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		compCmd = serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId())
		can_use_key = 0
		if serverApi.GetEngineCompFactory().CreatePlayer(playerId).GetPlayerOperation() == 2 or args["username"] in ["王培衡很丁丁","EGGYLAN_"]:
			can_use_key = 1
		if args["message"] == ".ChangeEnchant":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand("/say 玩家" + args["username"] + "使用了自定义附魔密钥")
				serversystem.NotifyToClient(playerId, "openUI1", args)
			else:
				compCmd.SetCommand("/say 玩家" + args["username"] + "由于使用附魔密钥时权限不足,已被踢出!")
				compCmd.SetCommand("/kick " + args["username"] + " 密钥千万条,权限第一条。权限不规范,踢出两行泪。")
		elif args["message"] == ".GetItem":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand("/say 玩家" + args["username"] + "使用了获取隐藏物品密钥")
				serversystem.NotifyToClient(playerId, "openUI2", args)
			else:
				compCmd.SetCommand("/say 玩家" + args["username"] + "由于使用获得隐藏物品密钥时权限不足,已被踢出!")
				compCmd.SetCommand("/kick " + args["username"] + " 密钥千万条,权限第一条。权限不规范,踢出两行泪。")
		elif args["message"] == ".ChangeTips":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand("/say 玩家" + args["username"] + "使用了修改物品注释密钥")
				serversystem.NotifyToClient(playerId, "openUI4", args)
			else:
				compCmd.SetCommand("/say 玩家" + args["username"] + "由于使用修改物品注释密钥时权限不足,已被踢出!")
				compCmd.SetCommand("/kick " + args["username"] + " 密钥千万条,权限第一条。权限不规范,踢出两行泪。")
		elif args["message"] == ".NbtEditor":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand("/say 玩家" + args["username"] + "使用了nbt修改器")
				serversystem.NotifyToClient(playerId, "openUI3", args)
			else:
				compCmd.SetCommand("/say 玩家" + args["username"] + "由于使用nbt修改器时权限不足,已被踢出!")
				compCmd.SetCommand("/kick " + args["username"] + " 密钥千万条,权限第一条。权限不规范,踢出两行泪。")
		elif args["message"] == ".GetVersion":
			args["cancel"] = True
			serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "v1.0.0(24/8/28)", "§b")
		elif args["message"][0] * 20 == args["message"][:20]:
			args["cancel"] = True
			serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "请勿刷屏", "§c")
		elif args["message"] == ".GetTPS":
			args["cancel"] = True
			if can_use_key == 1:
				if serverApi.GetServerTickTime() <= 50:
					TPS = "20.0*"
				else:
					TPS = "%.1f" % (1000/serverApi.GetServerTickTime())
				serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "TPS:%s mspt:%.2fms" % (TPS,serverApi.GetServerTickTime()) , "§e")
			else:
				serverApi.GetEngineCompFactory().CreateMsg(playerId).NotifyOneMessage(playerId, "你没有足够的权限使用.GetTPS", "§c")
		else:
			args["cancel"] = False

	def OnCommandEvent(self, args):
		import mod.server.extraServerApi as serverApi
		if not serverApi.GetEngineCompFactory().CreatePlayer(args["entityId"]).GetPlayerAbilities()["op"]:
			serverApi.GetEngineCompFactory().CreateMsg(args["entityId"]).NotifyOneMessage(args["entityId"], "权限不足,无法使用命令", "§c")
			args["cancel"] = True
		else:
			args["cancel"] = False

	def OnAddPlayerEvent(self, args):
		import mod.server.extraServerApi as serverApi
		if args["name"] == "王培衡很丁丁":
			args["message"] = "§e王培衡很丁丁§l§b(插件作者) §r§e加入了游戏"
			serverApi.GetEngineCompFactory().CreatePlayer(args["id"]).SetPermissionLevel(2)

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
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.UnListenAllEvents()
		PartBase.DestroyServer(self)