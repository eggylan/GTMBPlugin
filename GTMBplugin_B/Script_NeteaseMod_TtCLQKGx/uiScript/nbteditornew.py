# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class nbteditornew(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	#def refresh(self):
	#	#控件命名标准: /panel/items/{index}
	#	if isinstance(self.displaying, list):
	#		for i in range(len(self.displaying)):
	#			item = self.GetBaseUIControl(f'/panel/items/{i}')
	#			if item:
	#				self.RemoveChildControl(item)
	#	elif isinstance(self.displaying, dict):
	#		for k,_ in self.displaying:
	#			item = self.GetBaseUIControl(f'/panel/items/{k}')
	#			if item:
	#				self.RemoveChildControl(item)
	#	else:
	#		item = self.GetBaseUIControl(f'/panel/items/current')
	#		if item:
	#			self.RemoveChildControl(item)
	#	self.displaying = self.itemDict
	#	for i in self.displaying_path:
	#		self.displaying = self.displaying[i]
	#	for i in self.displaying:
	#		pass
#
	#def back(self):
	#	if len(self.displaying_path) > 0:
	#		self.displaying_path.pop()
	#	self.refresh()

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
	#	self.GetBaseUIControl('/panel/return').asButton().AddTouchEventParams({"isSwallow": True})
	#	self.GetBaseUIControl('/panel/return').asButton().SetButtonTouchUpCallback(self.back)
	#	self.itemDict = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLocalPlayerId()).GetCarriedItem(True)
	#	self.displaying_path = []
	#	self.refresh()

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