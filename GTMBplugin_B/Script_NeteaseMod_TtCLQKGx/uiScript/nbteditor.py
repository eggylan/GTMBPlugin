# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()
import json

class nbteditor(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def resetText(self):
		self.GetBaseUIControl("/panel/tip").asLabel().SetText("")

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.change)
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)
		comp = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLocalPlayerId())
		carriedData = comp.GetCarriedItem(True)
		for i in ['isDiggerItem','enchantData','itemId','modEnchantData','modId','modItemId','itemName','auxValue']:
			carriedData.pop(i) #删去多余键值对(这些已被弃用)
		userData = carriedData.pop('userData')
		if userData:
			carriedData['userData'] = userData
		carriedData = json.dumps(carriedData, ensure_ascii=False)
		self.GetBaseUIControl("/panel/nbt").asTextEditBox().SetEditText(carriedData)#.replace('\\xa7', '§').replace('\\\\','\\'))

	def change(self, args):
		strnbt = self.GetBaseUIControl("/panel/nbt").asTextEditBox().GetEditText()
		try:
			nbt = json.loads(strnbt)
		except ValueError as err:
			self.GetBaseUIControl("/panel/tip").asLabel().SetText("§c⚠数据错误: %s" % (err))
			clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).AddTimer(2, self.resetText)
			return
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
