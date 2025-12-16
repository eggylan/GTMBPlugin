# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class EULA(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.mainClientSystem = clientApi.GetSystem("gtmbPlugin", "mainClientSystem")

	def Create(self):
		# self.GetBaseUIControl("/panel/exit").asButton().AddTouchEventParams({"isSwallow": True})
		# self.GetBaseUIControl("/panel/exit").asButton().SetButtonTouchUpCallback(self.exit)
		self.GetBaseUIControl("/panel/accept").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl('/panel/accept').asButton().SetButtonTouchUpCallback(self.accept)
		"""
		@description UI创建成功时调用
		"""

	def accept(self, args):
		# if self.GetBaseUIControl('/panel/switch_toggle').asSwitchToggle().GetToggleState():
			# self.mainClientSystem.NotifyToServer('EULA', {'reason': 'EULA_AGREED'})
		clientApi.PopTopUI()

	# def exit(self, args):
	# 	clientApi.PopTopUI()
	# 	self.mainClientSystem.NotifyToServer('EULA', {'reason': 'EULA_FAILED_ERROR'})

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
