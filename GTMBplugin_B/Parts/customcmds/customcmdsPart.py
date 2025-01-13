# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass


@registerGenericClass("customcmdsPart")
class customcmdsPart(PartBase):
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "自定义指令零件"

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		PartBase.InitClient(self)

	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "CustomCommandTriggerServerEvent", self, self.OnCustomCommand)
		PartBase.InitServer(self)

	def OnCustomCommand(self, args):
		import mod.server.extraServerApi as serverApi
		import json
		CF = serverApi.GetEngineCompFactory()
		levelId = serverApi.GetLevelId()
		compcmd = CF.CreateCommand(levelId)
		compGame = serverApi.GetEngineCompFactory().CreateGame(levelId)
		command = args['command']
		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None

		if command == 'summonprojectile':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			try:
				targetlen = len(args['args'][7]['value'])
				target = args['args'][7]['value'][0]
			except:
				targetlen = 1
				target = None
			if not targetlen == 1:
				args['return_failed'] = True
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				return
			
			for i in args['args'][0]['value']:
				param = {
					'position': args['args'][2]['value'],
					'direction': args['args'][3]['value'],
					'power': args['args'][4]['value'],
					'gravity': args['args'][5]['value'],
					'damage': args['args'][6]['value'],
					'targetId': target,
					'isDamageOwner': args['args'][8]['value'],
					'auxValue': args['args'][9]['value']
				}
				
				CF.CreateProjectile(levelId).CreateProjectileEntity(i, args['args'][1]['value'], param)
			args['return_msg_key'] = '成功生成抛射物'
			return
		
		if command == 'setstepheight':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					CF.CreateAttr(i).SetStepHeight(args['args'][1]['value'])
				args['return_msg_key'] = '成功设置能迈过的最大高度'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		if command == 'setsize':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					CF.CreateCollisionBox(i).SetSize((args['args'][1]['value'],args['args'][2]['value']))
				args['return_msg_key'] = '成功设置碰撞箱'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
		
		
		if command == 'playerchatprefix':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				if CF.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:player':
					CF.CreateExtraData(i).SetExtraData('chatprefix', args['args'][1]['value'])
				else:
					CF.CreateMsg(i).NotifyOneMessage(playerId, '非玩家实体无法设置聊天前缀', "§c")
			args['return_msg_key'] = '成功设置玩家聊天前缀'
		
		if command == 'writehealthtoscoreboard':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = args['args'][1]['value']
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in args['args'][0]['value']:
				name = CF.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				health = CF.CreateAttr(entity).GetAttrValue(0)
				health = int(round(health))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, health), False)
			args['return_msg_key'] = '成功将生命值写入计分板'
			
		if command == 'writehungertoscoreboard':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = args['args'][1]['value']
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in args['args'][0]['value']:
				name = CF.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				hunger = CF.CreateAttr(entity).GetAttrValue(4)
				hunger = int(round(hunger))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, hunger), False)
			args['return_msg_key'] = '成功将饥饿值写入计分板'	
		
		if command == 'executecb':
			success = CF.CreateBlockEntity(levelId).ExecuteCommandBlock((args['args'][0]['value'], args['args'][1]['value'], args['args'][2]['value']), args['args'][3]['value'])
			if success:
				args['return_msg_key'] = '成功执行命令方块'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '执行命令方块失败'
		
		if command == 'setname':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				CF.CreateName(i).SetName(args['args'][1]['value'])
			args['return_msg_key'] = '成功设置名称'
		
		if command == 'aicontrol':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				CF.CreateControlAi(i).SetBlockControlAi(args['args'][1]['value'], args['args'][2]['value'])
			args['return_msg_key'] = '成功设置实体AI'
		
		if command == 'master':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compExtra = CF.CreateExtraData(i)
					compExtra.SetExtraData("isMaster", True)
				args['return_msg_key'] = '锁定玩家权限成功'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return

		if command == 'demaster':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compExtra = CF.CreateExtraData(i)
					compExtra.SetExtraData("isMaster", False)
				args['return_msg_key'] = '解锁玩家权限成功'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return
		
		compExtra = CF.CreateExtraData(serverApi.GetLevelId())
		params = compExtra.GetExtraData('parameters')
		input1 = args['args'][0]['value']
		if command == 'param':
			if args['args'][0]['value'] is None:
				args['return_msg_key'] = str(params)
				return
			else:
				if type(params) == dict and params.has_key(args['args'][0]['value']):
					args['return_msg_key'] = "变量\"%s\"为 %s" % (input1, params[input1])
					return
				else:
					args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
					args['return_failed'] = True
					return

		if command == 'paramdel':
			if type(params) == dict and params.has_key(args['args'][0]['value']):
				args['return_msg_key'] = '删除变量成功'
				del params[input1]
				compExtra.SetExtraData('parameters', params)
				return
			else:
				args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
				args['return_failed'] = True
				return

		if command == 'paramwrite':
			args['return_msg_key'] = '修改变量成功'
			input2 = args['args'][1]['value']
			if type(params) == dict:
				params[input1] = input2
			else:
				params = {input1: input2}
			compExtra.SetExtraData('parameters', params)
			return

		if command == 'kickt':
			if args['args'][0]['value']:
				for kickplayer in args['args'][0]['value']:
					CF.CreateCommand(serverApi.GetLevelId()).SetCommand('/kick ' + CF.CreateName(kickplayer).GetName() + ' ' + args['args'][1]['value'], False)
				args['return_msg_key'] = '已踢出目标玩家'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return
				
		if command == 'explode':
			values = {arg['name']: arg['value']for arg in args['args']}
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				pos = CF.CreatePos(i).GetFootPos()
				CF.CreateExplosion(serverApi.GetLevelId()).CreateExplosion(pos, values['爆炸威力'], values['是否产生火焰'], values['是否破坏方块'], None, None)
			args['return_msg_key'] = '爆炸已成功创建'
	
		if command == 'explodebypos':
			values = {arg['name']: arg['value']for arg in args['args']}
			pos = args['args'][0]['value']
			CF.CreateExplosion(serverApi.GetLevelId()).CreateExplosion(pos, values['爆炸威力'], values['是否产生火焰'], values['是否破坏方块'], None, None)
			args['return_msg_key'] = '爆炸已成功创建'
	
		if command == "console":
			cmd = args['args'][0]['value']
			if cmd.startswith("/"):
				cmd = cmd[1:]
			cmd2 = ""
			if compExtra.GetExtraData('parameters'):
				for i in cmd.split(" "):
					for ii in compExtra.GetExtraData('parameters').keys():
						index = i.find("param:%s" % (ii))
						if not index == -1:
							i = compExtra.GetExtraData('parameters')[i[index+6:]]
					cmd2 = "%s %s" % (cmd2, i)
			else:
				cmd2 = cmd
			CF.CreateCommand(serverApi.GetLevelId()).SetCommand("/" + cmd2, False)
			args["return_msg_key"] = "已尝试将指令发送到控制台执行。"
		
		if command == 'addaroundentitymotion' or command == 'addaroundpointmotion':
			if args['args'][1]['value'] is None and command == 'addaroundentitymotion' or args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if not len(args['args'][1]['value']) == 1 and command == 'addaroundentitymotion':
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				args['return_failed'] = True
				return
			for i in args['args'][0]['value']:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				CompType = CF.CreateEngineType(i)
				EntityType = CompType.GetEngineTypeStr()
				if command == 'addaroundentitymotion':
					if EntityType == 'minecraft:player':
						addMotion = CompMotion.AddPlayerAroundEntityMotion
					else:
						addMotion = CompMotion.AddEntityAroundEntityMotion
					Mid = addMotion(args['args'][1]['value'][0],
									args['args'][2]['value'],
									args['args'][3]['value'],
									args['args'][4]['value'],
									args['args'][5]['value'],
									args['args'][6]['value'])
				else:
					if EntityType == 'minecraft:player':
						addMotion = CompMotion.AddPlayerAroundEntityMotion
					else:
						addMotion = CompMotion.AddEntityAroundEntityMotion
					Mid = addMotion(args['args'][1]['value'],
									args['args'][2]['value'],
									args['args'][3]['value'],
									args['args'][4]['value'],
									args['args'][5]['value'])
				if Mid == -1:
					args['return_failed'] = True
					args['return_msg_key'] = '设置失败'
					return
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'

		if command == 'addvelocitymotion':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				CompType = CF.CreateEngineType(i)
				EntityType = CompType.GetEngineTypeStr()
				if EntityType == 'minecraft:player':
					addMotion = CompMotion.AddPlayerVelocityMotion
				else:
					addMotion = CompMotion.AddEntityVelocityMotion
				Mid = addMotion(args['args'][1]['value'],
								args['args'][2]['value'],
								args['args'][3]['value'])
				if Mid == -1:
					args['return_failed'] = True
					args['return_msg_key'] = '创建失败'
					return
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
		
		if command == 'startmotion':
			args['return_msg_key'] = ''
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				CompType = CF.CreateEngineType(i)
				CompMsg = CF.CreateMsg(i)
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
		
		if command == 'stopmotion':
			args['return_msg_key'] = ''
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				CompType = CF.CreateEngineType(i)
				CompMsg = CF.CreateMsg(i)
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
		
		if command == 'removemotion':
			args['return_msg_key'] = ''
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				Motions = compExtra.GetExtraData('Motions')
				CompType = CF.CreateEngineType(i)
				CompMsg = CF.CreateMsg(i)
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

		if command == 'addenchant':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compItem = CF.CreateItem(i)
					if type(args['args'][3]['value']) == int:
						slotType = 0
						slot = args['args'][3]['value']
					else:
						slotType = 2
						slot = 0
					itemDict = compItem.GetPlayerItem(slotType, slot, True)
					if itemDict:
						if itemDict["userData"] is None:
							itemDict["userData"] = {}
						if itemDict["userData"].get('ench', None) is None:
							itemDict["userData"]['ench'] = []
						itemDict["userData"]['ench'].insert(0, {'lvl': {'__type__': 2, '__value__': args['args'][2]['value']}, 
											  					'id':  {'__type__': 2, '__value__': args['args'][1]['value']}, 
																'modEnchant': {'__type__': 8, '__value__': ''}})
						itemDict["enchantData"] = []
					else:
						args['return_failed'] = True
						args['return_msg_key'] = '该槽位没有物品或没有该槽位'
						return
					if slotType == 0:
						compItem.SpawnItemToPlayerInv(itemDict, i, slot)
					else:
						compItem.SpawnItemToPlayerCarried(itemDict, i)
					args['return_msg_key'] = '添加附魔成功'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		if command == 'addtrackmotion':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compExtra = CF.CreateExtraData(i)
					CompMotion = CF.CreateActorMotion(i)
					CompType = CF.CreateEngineType(i)
					EntityType = CompType.GetEngineType()
					if EntityType == 63:
						addMotion = CompMotion.AddPlayerTrackMotion
					else:
						addMotion = CompMotion.AddEntityTrackMotion
					Mid = addMotion(args['args'][1]['value'],
									args['args'][2]['value'],
									None,
									False,
									args['args'][3]['value'],
									args['args'][5]['value'],
									args['args'][4]['value'],
									args['args'][6]['value'])
					if Mid == -1:
						args['return_failed'] = True
						args['return_msg_key'] = '创建失败'
						return
					Motions = compExtra.GetExtraData('Motions')
					if not Motions:
						Motions = []
					Motions.append(Mid)
					compExtra.SetExtraData('Motions', Motions)
				args['return_msg_key'] = '成功设置运动器'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		if command == 'setactorcanburnbylightning':
			compGame.SetCanActorSetOnFireByLightning(args['args'][0]['value'])
			args['return_msg_key'] = '设置成功'

		if command == 'setblockcanburnbylightning':
			compGame.SetCanBlockSetOnFireByLightning(args['args'][0]['value'])
			args['return_msg_key'] = '设置成功'

		if command == 'cancelshearsdestoryblockspeedall':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compItem = CF.CreateItem(i)
					compItem.CancelShearsDestoryBlockSpeedAll()
				args['return_msg_key'] = '取消成功'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		if command == 'cancelshearsdestoryblockspeed':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compItem = CF.CreateItem(i)
					if not compItem.CancelShearsDestoryBlockSpeed(args['args'][1]['value']):
						args['return_failed'] = True
						args['return_msg_key'] = '无效的命名空间id'
				args['return_msg_key'] = '取消成功'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		if command == 'setshearsdestoryblockspeed':
			if args['args'][0]['value']:
				if args['args'][2]['value'] < 1:
					args['return_failed'] = True
					args['return_msg_key'] = '速度必须大于1'
					return
				for i in args['args'][0]['value']:
					compItem = CF.CreateItem(i)
					if not compItem.SetShearsDestoryBlockSpeed(args['args'][1]['value'], args['args'][2]['value']):
						args['return_failed'] = True
						args['return_msg_key'] = '无效的命名空间id'
				args['return_msg_key'] = '设置成功'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'


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
