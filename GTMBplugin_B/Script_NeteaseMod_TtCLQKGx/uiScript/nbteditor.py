# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

def encoder(input):
	if isinstance(input, dict):
		return {encoder(key): encoder(value) for key, value in input.iteritems()}
	if isinstance(input, list):
		return [encoder(element) for element in input]
	if isinstance(input, str):
		if input == 'True':
			return True
		elif input == 'False':
			return False
		return input.encode('raw_unicode_escape')
	return input


class nbteditor(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.change)
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)
		comp = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLocalPlayerId())
		carriedData = encoder(comp.GetCarriedItem(True))
		for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
			carriedData.pop(i) #删去多余键值对(这些已被弃用)
		userData = carriedData.pop('userData')
		carriedData = str(carriedData)
		if userData:
			carriedData = carriedData[:-1]+", \"userData\": "+str(userData)+"}"
		carriedData = carriedData.replace("'",'"').replace(": False",": \"False\"").replace(": True",": \"True\"")
		self.GetBaseUIControl("/panel/nbt").asTextEditBox().SetEditText(carriedData.replace('\\xa7', '§').replace('\\\\','\\'))

	def change(self, args):
		import json
		strnbt = self.GetBaseUIControl("/panel/nbt").asTextEditBox().GetEditText()
		nbt = json.loads(strnbt)
		nbtdata = {"nbt": nbt}
		clientApi.GetSystem("Minecraft", "preset").NotifyToServer("changenbt", nbtdata)

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
