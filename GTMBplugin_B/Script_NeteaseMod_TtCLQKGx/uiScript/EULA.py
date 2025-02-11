# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class EULA(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		self.GetBaseUIControl("/panel/exit").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/exit").asButton().SetButtonTouchUpCallback(self.exit)
		self.GetBaseUIControl("/panel/accept").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl('/panel/accept').asButton().SetButtonTouchUpCallback(self.accept)
		"""
		@description UI创建成功时调用
		"""

	def accept(self, args):
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		if self.GetBaseUIControl('/panel/switch_toggle').asSwitchToggle().GetToggleState():
			clientsystem.NotifyToServer('EULA', {'reason': ''})
			clientApi.PopTopUI()

	def exit(self, args):
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		clientApi.PopTopUI()
		clientsystem.NotifyToServer('EULA', {'reason': '您没有接受EULA协议'})

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
