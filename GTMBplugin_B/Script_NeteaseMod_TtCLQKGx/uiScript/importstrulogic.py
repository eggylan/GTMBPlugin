# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
import traceback
import wphnbt
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
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetButtonTouchUpCallback(self.import_path_mode)

	def close(self, args):
		clientApi.PopTopUI()
		
	def import_path_mode(self, args):
		notify_control = self.GetBaseUIControl('/panel/err')
		comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
		path = self.GetBaseUIControl("/panel/inputpath").asTextEditBox().GetEditText()
		path = path.decode('utf-8') if isinstance(path, str) else path
		
		if not path.endswith('.mcstructure'):
			notify_control.asLabel().SetText('§4⚠无效的文件，扩展名必须为mcstructure')
			notify_control.SetVisible(True)
			comp.AddTimer(1, notify_control.SetVisible, False)
			return
		try:
			notify_control.asLabel().SetText('§e正在处理文件，请稍候...')
			notify_control.SetVisible(True)
			self.UpdateScreen()
			self.Update()
			with open(path, 'rb') as f:
				structure = wphnbt.load(f)
				structureentitydata = structure['structure']['palette']['default']['block_position_data']
				structure['structure']['palette']['default']['block_position_data'] = wphnbt.unpack(structureentitydata, True)
				structureentitys = structure['structure']['entities']
				structure['structure']['entities'] = wphnbt.unpack(structureentitys, True)
				structure = wphnbt.unpack(structure)
		except:
			notify_control.asLabel().SetText('§4⚠ 加载失败,原因已输出至聊天框')
			notify_control.SetVisible(True)
			comp.AddTimer(1, notify_control.SetVisible, False)
			for i in traceback.format_exc().splitlines():
				clientApi.GetEngineCompFactory().CreateTextNotifyClient(clientApi.GetLocalPlayerId()).SetLeftCornerNotify("§c%s" % i)
			return
		Dimension = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetCurrentDimension()
		structuredata = {"structuredata": structure, "dimension": Dimension}
		notify_control.asLabel().SetText('§a✔ 文件处理完成, 正在发送给服务器...')
		comp.AddTimer(1, notify_control.SetVisible, False)
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
