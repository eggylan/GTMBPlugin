# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class cmdbatch(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.cmdbatch)
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)

	def cmdbatch(self, args):
		if self.GetBaseUIControl("/panel/cmds").asTextEditBox().GetEditText():
			cmds = self.GetBaseUIControl("/panel/cmds").asTextEditBox().GetEditText()
			import mod.client.extraClientApi as clientApi
			cmds = {"cmds": cmds}
			clientApi.GetSystem("Minecraft", "preset").NotifyToServer("cmdbatch", cmds)
	
	def close(self, args):
		import mod.client.extraClientApi as clientApi
		clientApi.PopTopUI()
	
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
