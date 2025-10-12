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
		def hide_err():
			err_control.SetVisible(False)
		err_control = self.GetBaseUIControl('/panel/err')
		
		path = self.GetBaseUIControl("/panel/inputpath").asTextEditBox().GetEditText()
		path = path.decode('utf-8') if isinstance(path, str) else path
		
		if not path.endswith('.mcstructure'):
			err_control.asLabel().SetText('§4⚠无效的文件，扩展名必须为mcstructure')
			err_control.SetVisible(True)
			comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
			comp.AddTimer(1, hide_err)
			return
		try:
			err_control.asLabel().SetText('§e正在处理文件，请稍候...')
			with open(path, 'rb') as f:
				structure = wphnbt.load(f)
				structureentitydata = structure['structure']['palette']['default']['block_position_data']
				structure['structure']['palette']['default']['block_position_data'] = wphnbt.unpack(structureentitydata, True)
				structureentitys = structure['structure']['entities']
				structure['structure']['entities'] = wphnbt.unpack(structureentitys, True)
				structure = wphnbt.unpack(structure)
				err_control.SetVisible(True)
				comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
				comp.AddTimer(2, hide_err)
		except Exception as err:
			err_control.asLabel().SetText('§4⚠加载失败,原因已输出至聊天框')
			err_control.SetVisible(True)
			comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
			comp.AddTimer(1, hide_err)
			for i in traceback.format_exc().splitlines():
				clientApi.GetEngineCompFactory().CreateTextNotifyClient(clientApi.GetLocalPlayerId()).SetLeftCornerNotify("§c%s" % i)
			return
		Dimension = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetCurrentDimension()
		structuredata = {"structuredata": structure, "dimension": Dimension}
		err_control.asLabel().SetText('§a✔ 文件处理完成, 正在发送给服务器...')
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
