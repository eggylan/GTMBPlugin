# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class cmdblockimportui(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.cmdblockimport)
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetButtonTouchUpCallback(self.cmdblk_path_mode)

	def close(self, args):
		import mod.client.extraClientApi as clientApi
		clientApi.PopTopUI()

	def cmdblockimport(self, args):
		if self.GetBaseUIControl("/panel/jsoncmd").asTextEditBox().GetEditText():
			cmdblockcmdsjson = self.GetBaseUIControl("/panel/jsoncmd").asTextEditBox().GetEditText()
			import mod.client.extraClientApi as clientApi
			Dimension = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetCurrentDimension()
			cmdblockcmdsjson = {"cmdblockcmdsjson": cmdblockcmdsjson,"dimension":Dimension}
			clientApi.GetSystem("Minecraft", "preset").NotifyToServer("cmdblockimport", cmdblockcmdsjson)
	
	def cmdblk_path_mode(self, args):
		if self.GetBaseUIControl("/panel/inputpath").asTextEditBox().GetEditText():
			path = str(self.GetBaseUIControl("/panel/inputpath").asTextEditBox().GetEditText())
			with open(path, 'r') as file:
				cmdblockcmdsjson = file.read()
			import mod.client.extraClientApi as clientApi
			Dimension = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetCurrentDimension()
			cmdblockcmdsjson = {"cmdblockcmdsjson": cmdblockcmdsjson,"dimension":Dimension}
			clientApi.GetSystem("Minecraft", "preset").NotifyToServer("cmdblockimport", cmdblockcmdsjson)
	
	def Destroy(self):
		"""
		@description UI销毁时调用
		"""
		pass

	def OnActive(self):
		"""
		@description UI重新回到栈顶时调用
		"""
		pass

	def OnDeactive(self):
		"""
		@description 栈顶UI有其他UI入栈时调用
		"""
		pass
