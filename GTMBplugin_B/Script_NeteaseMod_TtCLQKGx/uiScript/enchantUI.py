# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class enchantUI(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.enchant)
		self.GetBaseUIControl("/panel/delench").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/delench").asButton().SetButtonTouchUpCallback(self.delenchant)
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)

	def enchant(self, args):
		if self.GetBaseUIControl("/panel/ID").asTextEditBox().GetEditText():
			enchantdata = {"id": self.GetBaseUIControl("/panel/ID").asTextEditBox().GetEditText(), "lvl": self.GetBaseUIControl("/panel/lvl").asTextEditBox().GetEditText()}
			import mod.client.extraClientApi as clientApi
			clientApi.GetSystem("Minecraft", "preset").NotifyToServer("enchant", enchantdata)

	def delenchant(self, args):
		enchantdata = {"id": "del", "lvl": "1"}
		import mod.client.extraClientApi as clientApi
		clientApi.GetSystem("Minecraft", "preset").NotifyToServer("enchant", enchantdata)

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
