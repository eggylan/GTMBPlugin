# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
import traceback
import wphnbt
import json
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()
clientsystem = clientApi.GetSystem("Minecraft", "preset")


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


		self.progressBarUIControl = self.GetBaseUIControl("/panel/progress_bar").asProgressBar()
		self.progressBarUITextControl = self.GetBaseUIControl("/panel/progress_bar/progress_bar_text").asLabel()
		self.progressBarUIControl.SetVisible(False)
		self.progressBarUIControl.SetValue(0)

	def close(self, args):
		clientApi.PopTopUI()

	def hide_err(self):
		self.notify_control.SetVisible(False)

	def import_path_mode(self, args):
		self._timers = {}
		self._send_queue = []
		
		self.notify_control = self.GetBaseUIControl('/panel/err')
		path = self.GetBaseUIControl("/panel/inputpath").asTextEditBox().GetEditText()
		path = path.decode('utf-8') if isinstance(path, str) else path

		self.compGame = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
		
		if not path.endswith('.mcstructure'):
			self.notify_control.asLabel().SetText('§4⚠无效的文件，扩展名必须为mcstructure')
			self.notify_control.SetVisible(True)
			self.compGame.AddTimer(1, self.hide_err)
			return
		
		try:
			self.notify_control.asLabel().SetText('§e正在处理文件，请稍候...')
			self.notify_control.SetVisible(True)
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
			self.notify_control.asLabel().SetText('§4⚠ 加载失败,原因已输出至聊天框')
			self.notify_control.SetVisible(True)
			self.compGame.AddTimer(1, self.notify_control.SetVisible, False)
			for i in traceback.format_exc().splitlines():
				clientApi.GetEngineCompFactory().CreateTextNotifyClient(clientApi.GetLocalPlayerId()).SetLeftCornerNotify("§c%s" % i)
			return
		
		Dimension = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetCurrentDimension()
		self.structuredata = json.dumps({"structuredata": structure, "dimension": Dimension}, ensure_ascii=False)
		self.notify_control.asLabel().SetText('§a✔ 文件处理完成, 正在与服务端握手...')
		
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(False)
		self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(False)
		
		self.localPlayerId = clientApi.GetLocalPlayerId()
		
		clientsystem.NotifyToServer("loadstructure_handshake", {})
		clientsystem.ListenForEvent('Minecraft', 'preset', 'HandShake_Success', self, self.handshake_success)
		
		# 等待服务端握手（超时：5秒）
		self._timers['handshake'] = self.compGame.AddTimer(5, self.handshake_timeout)

	def handshake_timeout(self):
		self.notify_control.asLabel().SetText('§4⚠与服务端握手超时')
		clientsystem.UnListenForEvent('Minecraft', 'preset', 'HandShake_Success', self, self.handshake_success)
		if 'handshake' in self._timers:
			self.compGame.CancelTimer(self._timers['handshake'])
			del self._timers['handshake']
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(True)
		self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(True)
		self.notify_control.SetVisible(True)
		self._timers['error'] = self.compGame.AddTimer(3, self.hide_err)
		return

	def handshake_success(self, args):
		clientsystem.UnListenForEvent('Minecraft', 'preset', 'HandShake_Success', self, self.handshake_success)
		self.compGame.CancelTimer(self._timers['handshake'])
		del self._timers['handshake']
		if args.get("REJECT", False):
			if args.get("reason","") == "SERVER_BUSY":	
				self.notify_control.asLabel().SetText('§4⚠服务端正在处理上一个请求, 请稍后再试')
			elif args.get("reason","") == "NO_PERMISSION":
				self.notify_control.asLabel().SetText('§4⚠你没有权限执行此操作')
			self.notify_control.SetVisible(True)
			self.compGame.AddTimer(3, self.hide_err)
			self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(True)
			self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(True)
			return
		self.notify_control.asLabel().SetText('§a✔ 与服务端握手成功, 正在传输数据...\n§e请勿关闭此界面')
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(False)
		self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(False)
		self.notify_control.SetVisible(True)
		self.progressBarUIControl.SetVisible(True)
		
		# 分割数据
		def split_string_by_length(s, n):
			return [s[i:i+n] for i in range(0, len(s), n)]
		
		chunk_size = 100000  # 每个数据包的大小
		chunks = split_string_by_length(self.structuredata, chunk_size)
		self._total_chunks = len(chunks)
		
		# 构建数据包
		for index, chunk in enumerate(chunks):
			is_last = index == len(chunks) - 1
			packet = {
				"sequence": index,  # 数据包的序号，从0开始
				"total_chunks": self._total_chunks,  # 总数据包数量
				"data": chunk,
				"is_last": is_last  # 是否为最后一个数据包
			}
			# 将数据包加入发送队列
			self._send_queue.append(packet)

		self._timers['send'] = self.compGame.AddRepeatedTimer(0.2, self.sendPacket)

	def sendPacket(self):
		if not self._send_queue:
			clientsystem.NotifyToServer("AllDataSend_"+ self.localPlayerId, {})
			self.notify_control.asLabel().SetText('§a✔ 数据传输完成, 正在等待服务端处理...\n§e现在可以关闭此界面')
			self.compGame.AddTimer(5, self.hide_err)
			self.compGame.CancelTimer(self._timers['send'])
			self._send_queue = []
			self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(True)
			self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(True)
			self.progressBarUIControl.SetVisible(False)
			return
		packet = self._send_queue.pop(0)
		clientsystem.NotifyToServer("ReceiveStructureData_"+ self.localPlayerId, packet)

		self.progressBarUIControl.SetValue(1.0 - (float(len(self._send_queue)) / float(self._total_chunks)))
		self.progressBarUITextControl.SetText("传输进度: %.1f%%%%" % (100 - (float(len(self._send_queue)) / float(self._total_chunks) * 100)))

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
