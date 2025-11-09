# -*- coding: utf-8 -*-
from common.mod import Mod
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi

modName = 'gtmbPlugin'
@Mod.Binding(name=modName, version="0.0.1")
class gtmbPluginMod(object):
	@Mod.InitServer()
	def ServerInit(self):
		serverApi.RegisterSystem(modName, 'mainServerSystem', '%s.serverSystem.mainServerSystem' % modName)
		serverApi.RegisterSystem(modName, 'cmdServerSystem', '%s.cmdServerSystem.cmdServerSystem' % modName)
		serverApi.RegisterSystem(modName, 'functionBlockServerSystem', '%s.serverSystem.functionBlockServerSystem' % modName)

	@Mod.DestroyServer()
	def ServerDestroy(self):
		#__destory__是一个自定义方法
		serverApi.GetSystem(modName, 'mainServerSystem').__destroy__()
		serverApi.GetSystem(modName, 'functionBlockServerSystem').__destroy__()

	@Mod.InitClient()
	def ClientInit(self):
		clientApi.RegisterSystem(modName, 'mainClientSystem', '%s.clientSystem.mainClientSystem' % modName)
		clientApi.RegisterSystem(modName, 'cmdClientSystem', '%s.clientSystem.cmdClientSystem' % modName)
		clientApi.RegisterSystem(modName, 'functionBlockClientSystem', '%s.clientSystem.functionBlockClientSystem' % modName)

	@Mod.DestroyClient()
	def ClientDestroy(self):
		pass
