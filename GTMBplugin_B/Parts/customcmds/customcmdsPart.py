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
		playerId = args['origin']['entityId']
		compMsg = serverApi.GetEngineCompFactory().CreateMsg(playerId)
		if args['command'] == 'master':
			if args['args'][0]['value']:
				args['return_msg_key'] = 'commands.master.success'
				for i in args['args'][0]['value']:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
					compExtra.SetExtraData("isMaster", True)
			else:
				args['return_msg_key'] = 'commands.master.faild'
				args['return_failed'] = True
		if args['command'] == 'demaster':
			if args['args'][0]['value']:
				args['return_msg_key'] = 'commands.demaster.success'
				for i in args['args'][0]['value']:
					compExtra = serverApi.GetEngineCompFactory().CreateExtraData(i)
					compExtra.SetExtraData("isMaster", False)
			else:
				args['return_msg_key'] = 'commands.master.faild'
				args['return_failed'] = True
		compExtra = serverApi.GetEngineCompFactory().CreateExtraData(serverApi.GetLevelId())
		params = compExtra.GetExtraData('parameters')
		input1 = args['args'][0]['value']
		if args['command'] == 'param':
			if type(params) == dict and params.has_key(args['args'][0]['value']):
				args['return_msg_key'] = ''
				compMsg.NotifyOneMessage(playerId, "变量\"%s\"为 %s" % (input1, params[input1]))
			else:
				args['return_msg_key'] = ''
				compMsg.NotifyOneMessage(playerId, "未知的变量\"%s\"" % (input1), "§c")
				args['return_failed'] = True
		if args['command'] == 'paramdel':
			if type(params) == dict and params.has_key(args['args'][0]['value']):
				args['return_msg_key'] = 'commands.paramdel.success'
				del params[input1]
				compExtra.SetExtraData('parameters', params)
			else:
				args['return_msg_key'] = ''
				compMsg.NotifyOneMessage(playerId, "未知的变量\"%s\"" % (input1), "§c")
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
			kicklist = serverApi.GetEngineCompFactory().CreateEntityComponent(serverApi.GetLevelId()).GetEntitiesBySelector(args['args'][0]['value'])
			for kickplayer in kicklist:
				serverApi.GetEngineCompFactory().CreateCommand(serverApi.GetLevelId()).SetCommand('/kick ' + serverApi.GetEngineCompFactory().CreateName(kickplayer).GetName() + ' ' + args['args'][1]['value'], False)
			args['return_msg_key'] = 'commands.kickt.success'

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
