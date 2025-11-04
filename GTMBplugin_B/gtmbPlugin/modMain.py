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

	@Mod.DestroyServer()
	def ServerDestroy(self):
		serverApi.GetSystem(modName, 'mainServerSystem').__destroy__()

	@Mod.InitClient()
	def ClientInit(self):
		clientApi.RegisterSystem(modName, 'mainClientSystem', '%s.clientSystem.mainClientSystem' % modName)

	@Mod.DestroyClient()
	def ClientDestroy(self):
		pass
