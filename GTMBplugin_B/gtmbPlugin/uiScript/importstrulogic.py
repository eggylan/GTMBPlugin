# -*- coding: utf-8 -*-
from __future__ import print_function
import mod.client.extraClientApi as clientApi
import traceback
import json
import threading
import hashlib


wphnbt = clientApi.ImportModule("gtmbPlugin.wphnbt")
compLocalData = clientApi.GetEngineCompFactory().CreateConfigClient(clientApi.GetLevelId())

ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()
clientsystem = clientApi.GetSystem("gtmbPlugin", "mainClientSystem")

def GetFileIdentifier(filepath):
	with open(filepath, 'rb') as f:
		data = f.read()
		hasher = hashlib.new('md5')
		hasher.update(data)
		base_id = hasher.hexdigest()
		
	return base_id


class importstrulogic(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self._worker_thread = None

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.compGame = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
		
		self.GetBaseUIControl("/panel/closebutton").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/closebutton").asButton().SetButtonTouchUpCallback(self.close)
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetButtonTouchUpCallback(self.import_path_mode)
		self.GetBaseUIControl("/panel/launch_path_mode/coroutine_help").asButton().AddTouchEventParams({"isSwallow": True})
		self.GetBaseUIControl("/panel/launch_path_mode/coroutine_help").asButton().SetButtonTouchUpCallback(self.show_coroutine_help)

		self.progressBarUIControl = self.GetBaseUIControl("/panel/progress_bar").asProgressBar()
		self.progressBarUITextControl = self.GetBaseUIControl("/panel/progress_bar/progress_bar_text").asLabel()
		self.progressBarUIControl.SetVisible(False)
		self.progressBarUIControl.SetValue(0)

		self.notify_control = self.GetBaseUIControl('/panel/err')
		self.notify_control_asLabel = self.notify_control.asLabel()

	def close(self, args):
		clientApi.PopTopUI()

	def check_input_number_valid(self, input_str):
		max_value = 1000000
		if not isinstance(input_str, str) or not input_str:
			return False

		if not input_str.isdigit():
			return False

		num = int(input_str)
		
		return 0 < num <= max_value
	
	def import_path_mode(self, args):
		#如果已有线程在运行，则不重复启动
		if self._worker_thread and self._worker_thread.is_alive():
			self.notify_control_asLabel.SetText('§c4⚠ 文件正在处理中，请稍候...')
			self.notify_control.SetVisible(True)
			return
		
		self.is_enable_coroutine = self.GetBaseUIControl("/panel/launch_path_mode/enable_coroutine_switch_toggle").asSwitchToggle().GetToggleState()
		if self.is_enable_coroutine:
			self.coroutine_per_yield = self.GetBaseUIControl("/panel/launch_path_mode/coroutine_per_yield_input").asTextEditBox().GetEditText()
			if not self.coroutine_per_yield:
				self.coroutine_per_yield = "100" # 默认值
			if not self.check_input_number_valid(self.coroutine_per_yield):
				self.notify_control_asLabel.SetText('§c⚠ 每帧处理数不合法！请输入正整数。')
				self.notify_control.SetVisible(True)
				self.compGame.AddTimer(1, self.notify_control.SetVisible, False)
				return
			self.coroutine_per_yield = int(self.coroutine_per_yield)


		self._timers = {}
		self._send_queue = []
		path = self.GetBaseUIControl("/panel/inputpath").asTextEditBox().GetEditText()
		path = path.decode('utf-8') if isinstance(path, str) else path

		if not path.endswith('.mcstructure'):
			self.notify_control_asLabel.SetText('§c⚠无效的文件，扩展名必须为mcstructure')
			self.notify_control.SetVisible(True)
			self.compGame.AddTimer(1, self.notify_control.SetVisible, False)
			return

		self.notify_control_asLabel.SetText('§e正在对结构文件进行预处理，请稍候...\n§f大型结构可能耗费更长时间。\n请勿关闭此界面。')
		self.notify_control.SetVisible(True)
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(False)
		self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(False)
		
		structure_cache = compLocalData.GetConfigData("GTMBPLUGIN_STRUCTURE_CACHE_"+GetFileIdentifier(path),True) or {}

		# 有缓存，且版本与当前客户端匹配
		if clientApi.GetEngineVersion() == structure_cache.get("version", ""):
			structure_data = structure_cache.get("structuredata", None)
			if structure_data:
				self._on_file_processed(True, structure=structure_data)
				return
		else:
			# 无缓存，启动一个后台线程来处理文件
			self._worker_thread = threading.Thread(
				target=self._process_file_in_thread,
				args=(path, self._on_file_processed)
			)
			self._worker_thread.daemon = True
			self._worker_thread.start()

	def _process_file_in_thread(self, path, callback):
		structure = None
		error = None
		success = False
		try:
			with open(path, 'rb') as f:
				structure = wphnbt.load(f)
				structureentitydata = structure['structure']['palette']['default']['block_position_data']
				structure['structure']['palette']['default']['block_position_data'] = wphnbt.unpack(structureentitydata, True)
				structureentitys = structure['structure']['entities']
				structure['structure']['entities'] = wphnbt.unpack(structureentitys, True)
				structure = wphnbt.unpack(structure)
				success = True
				# 存入缓存
				cache_data = {
					"version": clientApi.GetEngineVersion(),
					"structuredata": structure
				}
				compLocalData.SetConfigData("GTMBPLUGIN_STRUCTURE_CACHE_"+GetFileIdentifier(path), cache_data, True)
		except Exception as e:
			error = traceback.format_exc()
			success = False
		# 跳回主线程
		# 注意！绝对不要在非主线程中调用clientApi！！！
		self.compGame.AddTimer(0.01, callback, success, structure, error)

	# 文件处理完成
	def _on_file_processed(self, success, structure=None, error=None):
		if not success:
			self.notify_control_asLabel.SetText('§c⚠ 加载失败,原因已输出至聊天框')
			self.notify_control.SetVisible(True)
			self.compGame.AddTimer(1, self.notify_control.SetVisible, False)
			for i in error.splitlines():
				clientApi.GetEngineCompFactory().CreateTextNotifyClient(clientApi.GetLocalPlayerId()).SetLeftCornerNotify("§c%s" % i)
			return
		

		Dimension = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetCurrentDimension()
		self.structuredata = json.dumps({"structuredata": structure, "dimension": Dimension}, ensure_ascii=False)
		self.notify_control_asLabel.SetText('§a✔ 文件处理完成, 正在与服务端握手...')

		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(False)
		self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(False)

		self.localPlayerId = clientApi.GetLocalPlayerId()

		if self.is_enable_coroutine:
			handshake_packet = {
				"USE_COROUTINE": True,
				"COROUTINE_PER_YIELD": self.coroutine_per_yield
			}
		else:
			handshake_packet = {
				"USE_COROUTINE": False
			}
		clientsystem.NotifyToServer("loadstructure_handshake", handshake_packet)
		clientsystem.ListenForEvent('gtmbPlugin', 'mainServerSystem', 'HandShake_Success', self, self.handshake_success)

		# 等待服务端握手（超时：5秒）
		self._timers['handshake'] = self.compGame.AddTimer(5, self.handshake_timeout)

	def handshake_timeout(self):
		self.notify_control_asLabel.SetText('§c⚠与服务端握手超时')
		clientsystem.UnListenForEvent('gtmbPlugin', 'mainServerSystem', 'HandShake_Success', self, self.handshake_success)
		if 'handshake' in self._timers:
			self.compGame.CancelTimer(self._timers['handshake'])
			del self._timers['handshake']
		self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(True)
		self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(True)
		self.notify_control.SetVisible(True)
		self._timers['error'] = self.compGame.AddTimer(3, self.notify_control.SetVisible, False)
		return

	def handshake_success(self, args):
		clientsystem.UnListenForEvent('gtmbPlugin', 'mainServerSystem', 'HandShake_Success', self, self.handshake_success)
		self.compGame.CancelTimer(self._timers['handshake'])
		del self._timers['handshake']
		if args.get("REJECT", False):
			if args.get("reason","") == "SERVER_BUSY":
				self.notify_control_asLabel.SetText('§c⚠服务端正在处理上一个请求, 请稍后再试')
			elif args.get("reason","") == "NO_PERMISSION":
				self.notify_control_asLabel.SetText('§c⚠你没有权限执行此操作')
			self.notify_control.SetVisible(True)
			self.compGame.AddTimer(3, self.notify_control.SetVisible, False)
			self.GetBaseUIControl("/panel/launch_path_mode").asButton().SetVisible(True)
			self.GetBaseUIControl("/panel/closebutton").asButton().SetVisible(True)
			return
		self.notify_control_asLabel.SetText('§a✔ 与服务端握手成功, 正在传输数据...\n§e请勿关闭此界面')
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

		self._timers['send'] = self.compGame.AddRepeatedTimer(0.06, self.sendPacket)

	def sendPacket(self):
		if not self._send_queue:
			clientsystem.NotifyToServer("AllDataSend_"+ self.localPlayerId, {})
			self.notify_control_asLabel.SetText('§a✔ 数据传输完成, 正在等待服务端处理...\n§e现在可以关闭此界面')
			self.compGame.AddTimer(5, self.notify_control.SetVisible, False)
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
	
	def show_coroutine_help(self, args):
		help_text = (
			"§f启用协程可大幅提升大型结构处理的流畅度，\n"
			"§f但可能会增加所需的总时间。\n"
			"§f请根据实际需求选择是否启用此选项。\n\n"
		)
		self.notify_control_asLabel.SetText(help_text)
		self.notify_control.SetVisible(True)
		self.compGame.AddTimer(5, self.notify_control.SetVisible, False)

	def Destroy(self):
		"""
		@description UI销毁时调用
		"""
		self._worker_thread = None
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