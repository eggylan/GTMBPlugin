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
		levelId = serverApi.GetLevelId()
		compcmd = serverApi.GetEngineCompFactory().CreateCommand(levelId)
		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None

		if args['command'] == 'writehealthtoscoreboard':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = serverApi.GetEngineCompFactory().CreateGame(levelId).GetAllScoreboardObjects()
			scoreboard_name = args['args'][1]['value']
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in args['args'][0]['value']:
				name = serverApi.GetEngineCompFactory().CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				health = serverApi.GetEngineCompFactory().CreateAttr(entity).GetAttrValue(0)
				health = int(round(health))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, health), False)
			args['return_msg_key'] = '成功将生命值写入计分板'
			
		if args['command'] == 'writehungertoscoreboard':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = serverApi.GetEngineCompFactory().CreateGame(levelId).GetAllScoreboardObjects()
			scoreboard_name = args['args'][1]['value']
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in args['args'][0]['value']:
				name = serverApi.GetEngineCompFactory().CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				hunger = serverApi.GetEngineCompFactory().CreateAttr(entity).GetAttrValue(4)
				hunger = int(round(hunger))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, hunger), False)
			args['return_msg_key'] = '成功将饥饿值写入计分板'
				
				
		
		if args['command'] == 'executecb':
			success = serverApi.GetEngineCompFactory().CreateBlockEntity(levelId).ExecuteCommandBlock((args['args'][0]['value'], args['args'][1]['value'], args['args'][2]['value']), args['args'][3]['value'])
			if success:
				args['return_msg_key'] = '成功执行命令方块'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '执行命令方块失败'
		
		if args['command'] == 'setname':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				serverApi.GetEngineCompFactory().CreateName(i).SetName(args['args'][1]['value'])
			args['return_msg_key'] = '成功设置名称'
		
		if args['command'] == 'aicontrol':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				serverApi.GetEngineCompFactory().CreateControlAi(i).SetBlockControlAi(args['args'][1]['value'], args['args'][2]['value'])
			args['return_msg_key'] = '成功设置实体AI'
		
		if args['command'] == 'master':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
					compExtra.SetExtraData("isMaster", True)
				args['return_msg_key'] = '锁定玩家权限成功'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return

		if args['command'] == 'demaster':
			if args['args'][0]['value']:
				for i in args['args'][0]['value']:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
					compExtra.SetExtraData("isMaster", False)
				args['return_msg_key'] = '解锁玩家权限成功'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return
		
		compExtra = serverApi.GetEngineCompFactory().CreateExtraData(serverApi.GetLevelId())
		params = compExtra.GetExtraData('parameters')
		input1 = args['args'][0]['value']
		if args['command'] == 'param':
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

		if args['command'] == 'paramdel':
			if type(params) == dict and params.has_key(args['args'][0]['value']):
				args['return_msg_key'] = '删除变量成功'
				del params[input1]
				compExtra.SetExtraData('parameters', params)
				return
			else:
				args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
				args['return_failed'] = True
				return

		if args['command'] == 'paramwrite':
			args['return_msg_key'] = '修改变量成功'
			input2 = args['args'][1]['value']
			if type(params) == dict:
				params[input1] = input2
			else:
				params = {input1: input2}
			compExtra.SetExtraData('parameters', params)
			return

		if args['command'] == 'kickt':
			if args['args'][0]['value']:
				for kickplayer in args['args'][0]['value']:
					serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId()).SetCommand('/kick ' + serverApi.GetEngineCompFactory().CreateName(kickplayer).GetName() + ' ' + args['args'][1]['value'], False)
				args['return_msg_key'] = '已踢出目标玩家'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return
				
		if args['command'] == 'explode':
			values = {arg['name']: arg['value']for arg in args['args']}
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				pos = serverApi.GetEngineCompFactory().CreatePos(i).GetFootPos()
				serverApi.GetEngineCompFactory().CreateExplosion(serverApi.GetLevelId()).CreateExplosion(pos, values['爆炸威力'], values['是否产生火焰'], values['是否破坏方块'], None, None)
			args['return_msg_key'] = '爆炸已成功创建'
	
		if args['command'] == 'explodebypos':
			values = {arg['name']: arg['value']for arg in args['args']}
			pos = args['args'][0]['value']
			serverApi.GetEngineCompFactory().CreateExplosion(serverApi.GetLevelId()).CreateExplosion(pos, values['爆炸威力'], values['是否产生火焰'], values['是否破坏方块'], None, None)
			args['return_msg_key'] = '爆炸已成功创建'
	
		if args["command"] == "console":
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
			serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId()).SetCommand("/" + cmd2, False)
			args["return_msg_key"] = "已尝试将指令发送到控制台执行。"
		
		if args["command"] == 'addentityaroundentitymotion' or args["command"] == 'addentityaroundpointmotion':
			if args['args'][1]['value'] is None and args["command"] == 'addentityaroundentitymotion':
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if not len(args['args'][1]['value']) == 1 and args["command"] == 'addentityaroundentitymotion':
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				args['return_failed'] = True
				return
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
				CompMotion = serverApi.GetEngineCompFactory().CreateActorMotion(i)
				if args["command"] == 'addentityaroundentitymotion':
					Mid = CompMotion.AddEntityAroundEntityMotion(args['args'][1]['value'][0],
																args['args'][2]['value'],
																args['args'][3]['value'],
																args['args'][4]['value'],
																args['args'][5]['value'],
																args['args'][6]['value'])
				else:
					Mid = CompMotion.AddEntityAroundPointMotion(args['args'][1]['value'],
																args['args'][2]['value'],
																args['args'][3]['value'],
																args['args'][4]['value'],
																args['args'][5]['value'])
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
		
		if args['command'] == 'addentitytrackmotion':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
				CompMotion = serverApi.GetEngineCompFactory().CreateActorMotion(i)
				Mid = CompMotion.AddEntityTrackMotion(args['args'][1]['value'],
														args['args'][2]['value'],
														None,
														False,
														args['args'][3]['value'],
														args['args'][4]['value'],
														args['args'][5]['value'],
														args['args'][6]['value'],
														serverApi.GetMinecraftEnum().TimeEaseType.linear)
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'

		if args['command'] == 'addentityvelocitymotion':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
				CompMotion = serverApi.GetEngineCompFactory().CreateActorMotion(i)
				Mid = CompMotion.AddEntityVelocityMotion(args['args'][1]['value'],
														args['args'][2]['value'],
														args['args'][3]['value'])
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
		
		if args["command"] == 'startentitymotion':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
				CompMotion = serverApi.GetEngineCompFactory().CreateActorMotion(i)
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					for ii in Motions:
						CompMotion.StartEntityMotion(ii)
					args['return_msg_key'] = "成功启用实体的运动器"
				else:
					args['return_failed'] = True
					args['return_msg_key'] = '实体没有绑定运动器'
		
		if args['command'] == 'stopentitymotion':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
				CompMotion = serverApi.GetEngineCompFactory().CreateActorMotion(i)
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					for ii in Motions:
						CompMotion.StopEntityMotion(ii)
					args['return_msg_key'] = "成功停止实体的运动器"
				else:
					args['return_failed'] = True
					args['return_msg_key'] = '实体没有绑定运动器'
		
		if args['command'] == 'removeentitymotion':
			if args['args'][0]['value'] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
				CompMotion = serverApi.GetEngineCompFactory().CreateActorMotion(i)
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					for ii in Motions:
						CompMotion.RemoveEntityMotion(ii)
						Motions.remove(ii)
					compExtra.SetExtraData('Motions', Motions)
					args['return_msg_key'] = "成功移除实体的运动器"
				else:
					args['return_failed'] = True
					args['return_msg_key'] = '实体没有绑定运动器'
		
		

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
