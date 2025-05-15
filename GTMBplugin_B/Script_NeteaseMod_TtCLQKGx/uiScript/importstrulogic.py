# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class importstrulogic(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.GetBaseUIControl("/panel/button").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/button").asButton().SetButtonTouchUpCallback(self.importstru)
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetButtonTouchUpCallback(self.import_path_mode)

	def close(self, args):
		clientApi.PopTopUI()

	def importstru(self, args):
		pass

	def import_path_mode(self, args):
		path = str(self.GetBaseUIControl("/panel/inputpath").asTextEditBox().GetEditText())
		try:
			with open(path, 'r') as file:
				structure = file.read()
		except:
			err_control = self.GetBaseUIControl('/panel/err')
			def hide_err():
				err_control.SetVisible(False)
			err_control.SetVisible(True)
			comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
			comp.AddTimer(1, hide_err)
			return
		Dimension = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetCurrentDimension()
		structuredata = {"structuredata": structure, "dimension": Dimension}
		#cmdblockcmdsjson = {"cmdblockcmdsjson": cmdblockcmdsjson,"dimension":Dimension}
		clientApi.GetSystem("Minecraft", "preset").NotifyToServer("loadstructure", structuredata)

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
