# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class nbteditor(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.change)
		import mod.client.extraClientApi as clientApi
		import json
		comp = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLocalPlayerId())
		carriedData = comp.GetCarriedItem(True)
		carriedData.pop('enchantData')
		userData = carriedData.pop('userData')
		carriedData = str(carriedData)
		if userData:
			if userData.has_key('display'):
				if userData['display'].has_key('Name'):
					userData['display']['Name']['__value__'] = userData['display']['Name']['__value__'].encode('raw_unicode_escape')
			carriedData = carriedData[:-1]+", \"userData\": "+str(userData)+"}"
		carriedData = carriedData.replace("'",'"').replace(": False",": \"False\"").replace(": True",": \"True\"")
		self.GetBaseUIControl("/panel/nbt").asTextEditBox().SetEditText(carriedData)

	def change(self, args):
		import json
		import mod.client.extraClientApi as clientApi
		strnbt = self.GetBaseUIControl("/panel/nbt").asTextEditBox().GetEditText()
		nbt = json.loads(strnbt)
		nbtdata = {"nbt": nbt}
		clientApi.GetSystem("Minecraft", "preset").NotifyToServer("changenbt", nbtdata)

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
