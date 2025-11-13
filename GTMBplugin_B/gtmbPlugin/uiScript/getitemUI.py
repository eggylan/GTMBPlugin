# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class getitemUI(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.get)
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)

	def get(self, args):
		itemData = {"newItemName": "minecraft:" + self.GetBaseUIControl("/panel/id").asTextEditBox().GetEditText(), "newAuxValue": 0, "count": 1}
		if self.GetBaseUIControl("/panel/aux").asTextEditBox().GetEditText() == "":
			itemData["newAuxValue"] = 0
		else:
			itemData["newAuxValue"] = int(self.GetBaseUIControl("/panel/aux").asTextEditBox().GetEditText())
		clientApi.GetSystem("gtmbPlugin", "mainClientSystem").NotifyToServer("getitem", itemData)

	def close(self, args):	
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
