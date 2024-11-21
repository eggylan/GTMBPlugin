# -*- coding: utf-8 -*-

from common.mod import Mod
import mod.server.extraServerApi as serverApi


@Mod.Binding(name="NeteaseMod_TtCLQKGx", version="0.0.1")
class NeteaseMod_TtCLQKGx(object):

	def __init__(self):
		pass

	@Mod.InitServer()
	def NeteaseMod_TtCLQKGxServerInit(self):
		pass

	@Mod.DestroyServer()
	def NeteaseMod_TtCLQKGxServerDestroy(self):
		pass

	@Mod.InitClient()
	def NeteaseMod_TtCLQKGxClientInit(self):
		pass

	@Mod.DestroyClient()
	def NeteaseMod_TtCLQKGxClientDestroy(self):
		pass
