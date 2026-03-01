# -*- coding: utf-8 -*-
from mod.common.mod import Mod

modName = 'gtmbPlugin'
@Mod.Binding(name=modName, version="0.0.1")
class gtmbPluginMod(object):
	@Mod.InitServer()
	def ServerInit(self):
		import mod.server.extraServerApi as serverApi
		serverApi.RegisterSystem(modName, 'mainServerSystem', '%s.serverSystem.mainServerSystem' % modName)
		serverApi.RegisterSystem(modName, 'cmdServerSystem', '%s.cmdServerSystem.cmdServerSystem' % modName)

	@Mod.DestroyServer()
	def ServerDestroy(self):
		#__destory__是一个自定义方法
		import mod.server.extraServerApi as serverApi
		serverApi.GetSystem(modName, 'mainServerSystem').__destroy__()

	@Mod.InitClient()
	def ClientInit(self):
		import mod.client.extraClientApi as clientApi
		clientApi.RegisterSystem(modName, 'mainClientSystem', '%s.clientSystem.mainClientSystem' % modName)
		clientApi.RegisterSystem(modName, 'cmdClientSystem', '%s.clientSystem.cmdClientSystem' % modName)

	@Mod.DestroyClient()
	def ClientDestroy(self):
		pass
