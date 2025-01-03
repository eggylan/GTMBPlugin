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
		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None

		if args['command'] == 'master':
			if args['args'][0]['value']:
				args['return_msg_key'] = 'commands.master.success'
				for i in args['args'][0]['value']:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
					compExtra.SetExtraData("isMaster", True)
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True

		if args['command'] == 'demaster':
			if args['args'][0]['value']:
				args['return_msg_key'] = 'commands.demaster.success'
				for i in args['args'][0]['value']:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
					compExtra.SetExtraData("isMaster", False)
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True


		compMsg = serverApi.GetEngineCompFactory().CreateMsg(playerId)
		compExtra = serverApi.GetEngineCompFactory().CreateExtraData(serverApi.GetLevelId())
		params = compExtra.GetExtraData('parameters')
		input1 = args['args'][0]['value']
		if args['command'] == 'param':
			if args['args'][0]['value'] == None:
				args['return_msg_key'] = str(params)
			else:
				if type(params) == dict and params.has_key(args['args'][0]['value']):
					args['return_msg_key'] = "变量\"%s\"为 %s" % (input1, params[input1])
				else:
					args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
					args['return_failed'] = True

		if args['command'] == 'paramdel':
			if type(params) == dict and params.has_key(args['args'][0]['value']):
				args['return_msg_key'] = 'commands.paramdel.success'
				del params[input1]
				compExtra.SetExtraData('parameters', params)
			else:
				args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
				args['return_failed'] = True

		if args['command'] == 'paramwrite':
			args['return_msg_key'] = 'commands.paramwrt.success'
			input2 = args['args'][1]['value']
			if type(params) == dict:
				params[input1] = input2
			else:
				params = {input1: input2}
			compExtra.SetExtraData('parameters', params)

		if args['command'] == 'kickt':
			if args['args'][0]['value']:
				for kickplayer in args['args'][0]['value']:
					serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId()).SetCommand('/kick ' + serverApi.GetEngineCompFactory().CreateName(kickplayer).GetName() + ' ' + args['args'][1]['value'], False)
				args['return_msg_key'] = 'commands.kickt.success'
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				
		if args['command'] == 'explode':
			values = {arg['name']: arg['value']for arg in args['args']}
			if args['args'][0]['value'] == None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in args['args'][0]['value']:
				pos = serverApi.GetEngineCompFactory().CreatePos(i).GetFootPos()
				serverApi.GetEngineCompFactory().CreateExplosion(serverApi.GetLevelId()).CreateExplosion(pos, values['爆炸威力'], values['是否产生火焰'], values['是否破坏方块'], playerId, playerId)
	
		if args['command'] == 'explodebypos':
			values = {arg['name']: arg['value']for arg in args['args']}
			pos = args['args'][0]['value']
			serverApi.GetEngineCompFactory().CreateExplosion(serverApi.GetLevelId()).CreateExplosion(pos, values['爆炸威力'], values['是否产生火焰'], values['是否破坏方块'], playerId, playerId)
	
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
			if not len(args['args'][1]['value']) == 1 and args["command"] == 'addentityaroundentitymotion':
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				args['return_failed'] = True
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
		if args["command"] == 'startentitymotion':
			args['return_msg_key'] = ''
			for i in args['args'][0]['value']:
				compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
				CompMotion = serverApi.GetEngineCompFactory().CreateActorMotion(i)
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					for ii in Motions:
						CompMotion.StartEntityMotion(ii)
						Motions.remove(ii)
					compExtra.SetExtraData('Motions', Motions)
					compMsg.NotifyOneMessage(playerId, '成功启用实体的运动器')
				else:
					compMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")

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
