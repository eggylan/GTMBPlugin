# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class function_block_screen(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.node_count = 0
		for i in ["/background/close",
				"/nodes/scroll_view/scroll_mouse/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content/button",
				"/nodes/nodes_in",
				"/nodes_out"]:
			print(i)
			self.GetBaseUIControl(i).asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/background/close").asButton().SetButtonTouchUpCallback(self.close)
		self.GetBaseUIControl("/nodes/scroll_view/scroll_mouse/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content/button").asButton().SetButtonTouchUpCallback(self.spawn)
		self.GetBaseUIControl("/nodes/nodes_in").asButton().SetButtonTouchUpCallback(self.hide_nodes)
		self.GetBaseUIControl("/nodes_out").asButton().SetButtonTouchUpCallback(self.show_nodes)

	def close(self, args):
		clientApi.PopTopUI()
	def spawn(self, args):
		if args['ButtonPath'].startswith("/nodes/scroll_view"):
			self.node_count += 1
			self.Clone(args['ButtonPath'], "/exist_nodes", "%s" % self.node_count)
			pos = self.GetBaseUIControl(args['ButtonPath']).GetPosition()
			self.GetBaseUIControl(args['ButtonPath']).SetPosition((0, 0))
			self.GetBaseUIControl("/exist_nodes/%s" % self.node_count).SetPropertyBag({'ButtonPath':"/exist_nodes/%s" % self.node_count})
			self.GetBaseUIControl("/exist_nodes/%s" % self.node_count).SetPosition(pos)

	def hide_nodes(self, args):
		nodesControl = self.GetBaseUIControl('/nodes')
		nodesControl.SetVisible(False)

	def show_nodes(self, args):
		nodesControl = self.GetBaseUIControl('/nodes')
		nodesControl.SetVisible(True)

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
