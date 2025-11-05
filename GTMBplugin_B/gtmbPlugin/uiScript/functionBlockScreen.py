# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from gtmbPlugin.function_nodes import nodes
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()
CFClient = clientApi.GetEngineCompFactory()
clientSystem = clientApi.GetSystem('Minecraft', 'preset')

class functionBlockScreen(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		clientSystem.NotifyToServer('getNodeBlock', {})
		clientSystem.ListenForEvent('Minecraft', 'preset', 'nodeBlockCallBack', self, self.gotNodeBlock)
			
		get_button = lambda path: self.GetBaseUIControl(path).asButton()
		exist_buttons = ['/background/close', 'background/close_dont_save']
		for i in exist_buttons:
			get_button(i).AddTouchEventParams({'Swallow': True})
		get_button('/background/close').SetButtonTouchUpCallback(self.save)
		get_button('background/close_dont_save').SetButtonTouchUpCallback(self.close)
		comboBox = self.GetBaseUIControl('/leftside_panel/node_selector').asNeteaseComboBox()
		for i in nodes.keys():
			comboBox.AddOption(i, None, {'tip': nodes.get(i, '无对应内容')})
		comboBox.RegisterSelectItemCallback(self.load_current_node)

	def save(self, args):
		selected = self.GetBaseUIControl('/leftside_panel/node_selector/comboBoxTitlePanel/titleContentPanel/titleLabel').asLabel().GetText()
		clientSystem.NotifyToServer('NodeBlockSave', {'nodeType': selected})
		self.close(None)

	def gotNodeBlock(self, args):
		if args['type']:
			self.load_current_node(None, args['type'], {'tip': nodes.get(args['type'], 'None')})
		else:
			self.load_current_node(None, '选择一个模式', {'tip': '选择一个模式并查看其说明...'})
		clientSystem.UnListenForEvent('Minecraft', 'preset', 'nodeBlockCallBack', self, self.gotNodeBlock)

	def load_current_node(self, index, showName, userData):
		self.GetBaseUIControl('/node_tip').asLabel().SetText(userData['tip'])
		self.GetBaseUIControl('/leftside_panel/node_selector/comboBoxTitlePanel/titleContentPanel/titleLabel').asLabel().SetText(showName)

	def close(self, args):
		clientSystem.NotifyToServer('NodeBlockExit', {})
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
