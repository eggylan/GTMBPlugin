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

compGame = CFServer.CreateGame(levelId)

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
		listenServerSysEvent('ServerPlaceBlockEntityEvent', self.OnPlacingBlock)
		listenServerSysEvent('BlockRemoveServerEvent', self.OnRemovingBlock)
		#以下为函数方块的监听内容
		listenServerSysEvent('PlayerJoinMessageEvent', self.FCB_join)
		listenServerSysEvent('OnScriptTickServer', self.FCB_tick)
		#注册函数方块
		compExtra = CFServer.CreateExtraData(levelId)
		if compExtra.GetExtraData('functionBlockByPos'):
			self.functionBlockByPos = compExtra.GetExtraData('functionBlockByPos')
			self.functionBlockByMode = compExtra.GetExtraData('functionBlockByMode')
		else:
			self.functionBlockByPos = {}
			self.functionBlockByMode = {}
			for i in ['tick', 'addPlayer']:
				self.functionBlockByMode[i] = []

	def onNodeBlockSave(self, nodeData):
		compExtra = CFServer.CreateExtraData(nodeData['__id__'])
		block = compExtra.GetExtraData('editingFunctionBlock')
		compBlockEntity = CFServer.CreateBlockEntityData(levelId)
		blockData = compBlockEntity.GetBlockEntityData(block['dimension'], block['pos'])
		if nodeData['nodeType'] != '选择一个模式':
			blockData['mode'] = nodeData['nodeType']
			CFServer.CreateMsg(nodeData['__id__']).NotifyOneMessage(nodeData['__id__'], '已设置模式: ' + nodeData['nodeType'])
			if block['type'] == 'listen':
				self.SaveBlockToSave(block['pos'], block['dimension'], nodeData['nodeType'])

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
				compExtra.SetExtraData('editingFunctionBlock', {'pos': (args['x'], args['y'], args['z']), 'dimension': args['dimensionId'], 'type': 'node'})
				serverSystem.NotifyToClient(playerId, 'openUI', {"ui": "functionBlockScreen"})
			else:
				args['cancel'] = True
		elif args['blockName'] == 'gtmb_plugin:function_block_listen':
			if compPlayer.GetPlayerAbilities()['op'] and not compExtra.GetExtraData('editingFunctionBlock'):
				compExtra.SetExtraData('editingFunctionBlock', {'pos': (args['x'], args['y'], args['z']), 'dimension': args['dimensionId'], 'type': 'listen'})
				serverSystem.NotifyToClient(playerId, 'openUI', {'ui': 'listenBlockScreen'})
			else:
				args['cancel'] = True

	def OnRemovingBlock(self, args):
		if args['fullName'] == 'gtmb_plugin:function_block_listen':
			self.RemoveBlockFromSave((args['x'], args['y'], args['z']), args['dimension'])

	def OnPlacingBlock(self, args):
		if args['blockName'] == 'gtmb_plugin:function_block_listen':
			compGame.AddTimer(0, self.GetNewBlock, {'pos': (args['posX'], args['posY'], args['posZ']), 'dimension': args['dimension']})

	def GetNewBlock(self, args):
		#wy诡异石山使我必须延迟1tick
		compBlockEntity = CFServer.CreateBlockEntityData(levelId)
		blockEntityData = compBlockEntity.GetBlockEntityData(args['dimension'], args['pos'])
		if blockEntityData['mode']:
			self.SaveBlockToSave(args['pos'], args['dimension'], blockEntityData['mode'])

	def SaveBlockToSave(self, pos, dim, mode): 
		self.functionBlockByPos[(dim, pos)] = mode
		if (dim, pos) not in self.functionBlockByMode[mode]:
			self.functionBlockByMode[mode].append((dim, pos))
		print('[INFO] %s 函数方块 已保存' % str((dim, pos)))

	def RemoveBlockFromSave(self, pos, dim):
		mode = self.functionBlockByPos.pop((dim, pos), None)
		if mode:
			if (dim, pos) in self.functionBlockByMode[mode]:
				self.functionBlockByMode[mode].remove((dim, pos))
		print('[INFO] %s 函数方块 已移除' % str((dim, pos)))

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
		#转储函数方块数据
		compExtra = CFServer.CreateExtraData(levelId)
		compExtra.SetExtraData('functionBlockByPos', self.functionBlockByPos)
		compExtra.SetExtraData('functionBlockByMode', self.functionBlockByMode)

	def CallListen(self, name, eventData):
		for i in self.functionBlockByMode[name]:
			compBlock = CFServer.CreateBlockInfo(levelId)
			blockInfo = compBlock.GetBlockNew(i[1], i[0])
			if blockInfo['name'] != 'gtmb_plugin:function_block_listen':
				self.RemoveBlockFromSave(i[1], i[0])
				continue
			print('[INFO] %s 函数方块 执行 %s 事件' % (str(i), name))

#以下为函数方块的监听函数
	def FCB_tick(self, args={}):
		self.CallListen('tick', args)

	def FCB_join(self, args={}):
		self.CallListen('player_join', args)