# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
CFServer = serverApi.GetEngineCompFactory()
CFClient = clientApi.GetEngineCompFactory()
serverSystem = serverApi.GetSystem('Minecraft', 'preset')
clientSystem = clientApi.GetSystem('Minecraft', 'preset')
levelId = serverApi.GetLevelId()

@registerGenericClass("FunctionBlockPart")
class FunctionBlockPart(PartBase):
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "空零件"

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		PartBase.InitClient(self)

	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		PartBase.InitServer(self)
		listenServerSysEvent = lambda eventName, func: serverSystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), eventName, self, func)
		serverSystem.ListenForEvent('Minecraft', 'preset', 'NodeBlockSave', self, self.onNodeBlockSave)
		serverSystem.ListenForEvent('Minecraft', 'preset', 'getNodeBlock', self, self.requestNodeBlock)
		serverSystem.ListenForEvent('Minecraft', 'preset', 'NodeBlockExit', self, self.onFunctionBlockExit)
		listenServerSysEvent("ServerBlockUseEvent", self.OnUseCustomBlock)

	def onNodeBlockSave(self, nodeData):
		compExtra = CFServer.CreateExtraData(nodeData['__id__'])
		block = compExtra.GetExtraData('editingFunctionBlock')
		compBlockEntity = CFServer.CreateBlockEntityData(levelId)
		blockData = compBlockEntity.GetBlockEntityData(block['dimension'], block['pos'])
		if nodeData['nodeType'] != '选择一个模式':
			blockData['mode'] = nodeData['nodeType']
			CFServer.CreateMsg(nodeData['__id__']).NotifyOneMessage(nodeData['__id__'], '已设置模式: ' + nodeData['nodeType'])

	def requestNodeBlock(self, args):
		compExtra = CFServer.CreateExtraData(args['__id__'])
		gettingBlock = compExtra.GetExtraData('editingFunctionBlock')
		compBlockEntity = CFServer.CreateBlockEntityData(levelId)
		blockData = compBlockEntity.GetBlockEntityData(gettingBlock['dimension'], gettingBlock['pos'])
		serverSystem.NotifyToClient(args['__id__'], 'nodeBlockCallBack', {'type': blockData['mode']})
	
	def onFunctionBlockExit(self, args):
		playerId = args['__id__']
		compExtra = CFServer.CreateExtraData(playerId)
		compExtra.CleanExtraData('editingFunctionBlock')

	def OnUseCustomBlock(self, args):
		playerId = args['playerId']
		compPlayer = CFServer.CreatePlayer(playerId)
		compExtra = CFServer.CreateExtraData(playerId)
		if args['blockName'] == 'gtmb_plugin:function_block':
			if compPlayer.GetPlayerAbilities()['op'] and not compExtra.GetExtraData('editingFunctionBlock'):
				compExtra.SetExtraData('editingFunctionBlock', {'pos': (args['x'], args['y'], args['z']), 'dimension': args['dimensionId']})
				serverSystem.NotifyToClient(playerId, 'openUI', {"ui": "functionBlockScreen"})
			else:
				args['cancel'] = True
		elif args['blockName'] == 'gtmb_plugin:function_block_listen':
			if compPlayer.GetPlayerAbilities()['op'] and not compExtra.GetExtraData('editingFunctionBlock'):
				compExtra.SetExtraData('editingFunctionBlock', {'pos': (args['x'], args['y'], args['z']), 'dimension': args['dimensionId']})
				serverSystem.NotifyToClient(playerId, 'openUI', {'ui': 'listenBlockScreen'})
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
		PartBase.DestroyClient(self)

	def DestroyServer(self):
		"""
		@description 服务端的零件对象销毁逻辑入口
		"""
		PartBase.DestroyServer(self)
