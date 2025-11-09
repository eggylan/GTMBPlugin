# -*- coding: utf-8 -*-
import server.extraServerApi as serverApi
from math import sqrt, floor
import time
import traceback
import json
CF = serverApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
compCmd = CF.CreateCommand(levelId)
compExtra = CF.CreateExtraData(levelId)
compGame = CF.CreateGame(levelId)
compHttp = CF.CreateHttp(levelId)
compItemWorld = CF.CreateItem(levelId)
compBlockEntity = CF.CreateBlockEntity(levelId)
compBlockEntityData = CF.CreateBlockEntityData(levelId)
compBlockInfo = CF.CreateBlockInfo(levelId)

intg = lambda x: int(floor(x))

def unicode_convert(input):
	#type: (dict|str) -> dict|list|str|bool
	if isinstance(input, dict):
		return {unicode_convert(key): unicode_convert(value) for key, value in input.items()}
	elif isinstance(input, list):
		return [unicode_convert(element) for element in input]
	elif isinstance(input, unicode): # type: ignore
		return input.encode('utf-8')
	return input

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
		self.ListenForEvent('gtmbPlugin', 'mainClientSystem', 'ReceiveStructureData_'+str(self.structure_loading_playerid), self, self._process_packet)
		
		self._structure_receive_timeout_counter = 0
		self._structure_receive_timeout_timer_object = compGame.AddRepeatedTimer(1, self._structure_receive_timeout_timer) # 计时器，发包间隔超过10秒则视为超时

	def _structure_receive_timeout_timer(self):
		self._structure_receive_timeout_counter = self._structure_receive_timeout_counter + 1
		if self._structure_receive_timeout_counter >= 10:
			print("取消结构加载，原因：接收数据超时")
			self._structure_receive_timeout_counter = 0
			self._is_Structure_Loading = False
			self._buffer.clear()
			self.UnListenForEvent('gtmbPlugin', 'mainClientSystem', 'ReceiveStructureData_'+str(self.structure_loading_playerid), self, self._process_packet)
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
				self.UnListenForEvent('gtmbPlugin', 'mainClientSystem', 'ReceiveStructureData_'+str(playerid), self, self._process_packet)
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
				self.UnListenForEvent('gtmbPlugin', 'mainClientSystem', 'ReceiveStructureData_'+str(playerid), self, self._process_packet)
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

class functionBlockServerSystem(serverApi.GetServerSystemCls()):
	def __init__(self, namespace, systemName):
		super(functionBlockServerSystem, self).__init__(namespace, systemName)
		listenServerSysEvent = lambda eventName, func: self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), eventName, self, func)
		self.ListenForEvent('gtmbPlugin', 'functionBlockClientSystem', 'NodeBlockSave', self, self.onNodeBlockSave)
		self.ListenForEvent('gtmbPlugin', 'functionBlockClientSystem', 'NodeBlockExit', self, self.onFunctionBlockExit)
		self.ListenForEvent('gtmbPlugin', 'functionBlockClientSystem', 'RequestRenders', self, self.SendRenders)
		listenServerSysEvent("ServerBlockUseEvent", self.OnUseCustomBlock)
		listenServerSysEvent('ServerPlaceBlockEntityEvent', self.OnPlacingBlock)
		listenServerSysEvent('BlockRemoveServerEvent', self.OnRemovingBlock)
		#以下为函数方块的监听内容
		listenServerSysEvent('PlayerJoinMessageEvent', self.FCB_join)
		listenServerSysEvent('OnScriptTickServer', self.FCB_tick)
		#注册函数方块
		compExtra = CF.CreateExtraData(levelId)
		if compExtra.GetExtraData('functionBlockByPos'):
			self.functionBlockByPos = compExtra.GetExtraData('functionBlockByPos')
			self.functionBlockByMode = compExtra.GetExtraData('functionBlockByMode')
		else:
			self.functionBlockByPos = {}
			self.functionBlockByMode = {}
			for i in ['tick', 'addPlayer']:
				self.functionBlockByMode[i] = []
		#注册渲染物
		'''
		[{'type':'arrow'/'circle'/'line'/'text'/'box'/'sphere',
		  'data':{}}]
		'''
		self.renders = [{'type': 'text',
						 'data': {'pos': (0, 10, 0), 'text': '123455'}},]
		
	def __destroy__(self):
		#转储函数方块数据
		compExtra.SetExtraData('functionBlockByPos', self.functionBlockByPos)
		compExtra.SetExtraData('functionBlockByMode', self.functionBlockByMode)

	def SendRenders(self, args):
		playerId = args['__id__']
		pos = CF.CreatePos(playerId).GetFootPos()
		outputs = []
		for i in self.renders:
			renderPos = i['data']['pos']
			distance = sqrt((pos[0]-renderPos[0])**2+
				   			(pos[1]-renderPos[1])**2+
				   			(pos[2]-renderPos[2])**2)
			if distance <= 50:
				outputs.append(i)
		self.NotifyToClient(playerId, 'rendersFromServer', {'renders': outputs})
			

	def onNodeBlockSave(self, nodeData):
		compExtra = CF.CreateExtraData(nodeData['__id__'])
		block = compExtra.GetExtraData('editingFunctionBlock')
		blockData = compBlockEntityData.GetBlockEntityData(block['dimension'], block['pos'])
		if nodeData['nodeType'] != '选择一个模式':
			blockData['mode'] = nodeData['nodeType']
			CF.CreateMsg(nodeData['__id__']).NotifyOneMessage(nodeData['__id__'], '已设置模式: ' + nodeData['nodeType'])
			if block['type'] == 'listen':
				self.RemoveBlockFromSave(block['pos'], block['dimension'])
				self.SaveBlockToSave(block['pos'], block['dimension'], nodeData['nodeType'])
	
	def onFunctionBlockExit(self, args):
		playerId = args['__id__']
		compExtra = CF.CreateExtraData(playerId)
		compExtra.CleanExtraData('editingFunctionBlock')

	def OnUseCustomBlock(self, args):
		playerId = args['playerId']
		compPlayer = CF.CreatePlayer(playerId)
		compExtra = CF.CreateExtraData(playerId)
		pos = (args['x'], args['y'], args['z'])
		if args['blockName'] == 'gtmb_plugin:function_block':
			if compPlayer.GetPlayerAbilities()['op'] and not compExtra.GetExtraData('editingFunctionBlock'):
				blockEntityData = compBlockEntityData.GetBlockEntityData(args['dimensionId'], pos)
				compExtra.SetExtraData('editingFunctionBlock', {'pos': pos, 'dimension': args['dimensionId'], 'type': 'node'})
				self.NotifyToClient(playerId, 'openUI', {"ui": "functionBlockScreen", 'data': {'mode': blockEntityData['mode']}})
				args['cancel'] = True
		elif args['blockName'] == 'gtmb_plugin:function_block_listen':
			if compPlayer.GetPlayerAbilities()['op'] and not compExtra.GetExtraData('editingFunctionBlock'):
				blockEntityData = compBlockEntityData.GetBlockEntityData(args['dimensionId'], pos)
				compExtra.SetExtraData('editingFunctionBlock', {'pos': pos, 'dimension': args['dimensionId'], 'type': 'listen'})
				self.NotifyToClient(playerId, 'openUI', {'ui': 'listenBlockScreen', 'data': {'mode': blockEntityData['mode']}})
				args['cancel'] = True

	def OnRemovingBlock(self, args):
		if args['fullName'] == 'gtmb_plugin:function_block_listen':
			self.RemoveBlockFromSave((args['x'], args['y'], args['z']), args['dimension'])

	def OnPlacingBlock(self, args):
		if args['blockName'] == 'gtmb_plugin:function_block_listen':
			compGame.AddTimer(0, self.GetNewBlock, {'pos': (args['posX'], args['posY'], args['posZ']), 'dimension': args['dimension']})

	def GetNewBlock(self, args):
		#wy诡异石山使我必须延迟1tick
		blockEntityData = compBlockEntityData.GetBlockEntityData(args['dimension'], args['pos'])
		if blockEntityData['mode']:
			self.SaveBlockToSave(args['pos'], args['dimension'], blockEntityData['mode'])

	def SaveBlockToSave(self, pos, dim, mode): 
		self.functionBlockByPos[(dim, pos)] = mode
		if (dim, pos) not in self.functionBlockByMode[mode]:
			self.functionBlockByMode[mode].append((dim, pos))
		print('[INFO] %s 函数方块 已保存' % str((dim, pos)))

	def RemoveBlockFromSave(self, pos, dim):
		self.functionBlockByPos.pop((dim, pos), None)
		for i in self.functionBlockByMode:
			if (dim, pos) in self.functionBlockByMode[i]:
				self.functionBlockByMode[i].remove((dim, pos))
		print('[INFO] %s 函数方块 已移除 %s' % (str((dim, pos)), self.functionBlockByPos))

	def CallListen(self, name, eventData):
		for i in self.functionBlockByMode[name]:
			blockInfo = compBlockInfo.GetBlockNew(i[1], i[0])
			if blockInfo['name'] != 'gtmb_plugin:function_block_listen':
				self.RemoveBlockFromSave(i[1], i[0])
				continue
			blockEntityData = compBlockEntityData.GetBlockEntityData(i[0], i[1])
			blockEntityData['lastOutput'] = eventData
			print('[INFO] %s 函数方块 执行 %s 事件' % (str(i), name))

	#以下为函数方块的监听函数
	def FCB_tick(self, args={}):
		self.CallListen('tick', args)

	def FCB_join(self, args={}):
		self.CallListen('addPlayer', args)