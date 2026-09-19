# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
import ast
import math
import operator
import re
CF = clientApi.GetEngineCompFactory()
localPlayerId = clientApi.GetLocalPlayerId()
levelId = clientApi.GetLevelId()
compPostProcess = CF.CreatePostProcess(levelId)
compDrawing = CF.CreateDrawing(levelId)
compPlayer = CF.CreatePlayer(localPlayerId)
compItem = CF.CreateItem(localPlayerId)
compGame = CF.CreateGame(levelId)
compActorMotion = CF.CreateActorMotion(localPlayerId)
compPos = CF.CreatePos(localPlayerId)
compRot = CF.CreateRot(localPlayerId)
compCamera = CF.CreateCamera(localPlayerId)
compOperation = CF.CreateOperation(levelId)
compPlayerView = CF.CreatePlayerView(localPlayerId)
compAttr = CF.CreateAttr(localPlayerId)

from consts import UI_NAMES

PLATFORM_WINDOWS = 0
PLATFORM_IOS = 1
PLATFORM_ANDROID = 2

from consts import STATUS_MATH_FUNCTIONS, STATUS_MATH_BINOPS, STATUS_MATH_CMPOPS

class mainClientSystem(clientApi.GetClientSystemCls()):
	def __init__(self, modName, systemName):
		super(mainClientSystem, self).__init__(modName, systemName)
		listenClientSysEvent = lambda eventId, callback: self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), eventId, self, callback)
		listenClientSysEvent('OnKeyPressInGame', self.OnPressKey)
		listenClientSysEvent('UiInitFinished', self.OnUiInitFinished)
		self.ListenForEvent('gtmbPlugin', 'mainServerSystem', 'openUI', self, self.openUI)
		self.ListenForEvent('gtmbPlugin', 'functionBlockServerSystem', 'openUI', self, self.openUI)
		
		self.is_UI_First_Init = True

	def openUI(self, args):
		clientApi.PushScreen('gtmbPlugin', args['ui'], args.get('data'))

	def OnUiInitFinished(self, args):
		# if self.is_UI_First_Init:
		self.is_UI_First_Init = False
		for i in UI_NAMES:
			uiClsName = UI_NAMES[i][0]
			clientApi.RegisterUI('gtmbPlugin', i, 'gtmbPlugin.uiScript.%s.%s' % (uiClsName, uiClsName), UI_NAMES[i][1])
		self.NotifyToServer('TryOpenEULA', {})
			# self.openUI({'ui':'EULA'})

	def OnPressKey(self, args):
		if args['key'] == '27':
			if args['isDown']:
				if clientApi.GetTopUI().endswith('closable'): #这里只有插件可关闭的ui的画布叫做xxxx_closable
					clientApi.PopTopUI()


class cmdClientSystem(clientApi.GetClientSystemCls()):
	def __init__(self, modName, systemName):
		super(cmdClientSystem, self).__init__(modName, systemName)
		self.ListenForEvent('gtmbPlugin', 'cmdServerSystem', 'CustomCommandClient', self, self.OnCustomCommandClient)
		self.ListenForEvent('gtmbPlugin', 'cmdServerSystem', 'GetStatusClientRequest', self, self.OnGetStatusClientRequest)
		# 仅当 /get_status client.event.* 第一次访问时才注册对应事件监听。
		self._get_status_client_events = {}
		self._get_status_client_event_callbacks = {}
		self.clientCustomCmd = {
			'setplayerinteracterange':self.client_setplayerinteracterange,
			'openfoldgui':self.client_openfoldgui,
			'setcanpausescreen':self.client_setcanpausescreen,
			'setcolorbrightness':self.client_setcolorbrightness,
			'setcolorcontrast':self.client_setcolorcontrast,
			'setcolorsaturation':self.client_setcolorsaturation,
			'setcolortint':self.client_setcolortint,
			'setcompassentity':self.client_setcompassentity,
			'setcompasstarget':self.client_setcompasstarget,
			'setvignettecenter':self.client_setvignettecenter,
			'setvignetteradius':self.client_setvignetteradius,
			'setvignettecolor':self.client_setvignettecolor,
			'setvignettesmooth':self.client_setvignettesmooth,
			'setvignette':self.client_setvignette,
			'setgaussian':self.client_setgaussian,
			'setgaussianradius':self.client_setgaussianradius,
			'sethudchatstackposition':self.client_sethudchatstackposition,
			'sethudchatstackvisible':self.client_sethudchatstackvisible,
			'chatclear': self.client_chatclear,
			"openui": self.client_openui,
			"hidenametag": self.client_hidenametag,
			"eula": self.client_eula
		}
		compPostProcess.SetEnableColorAdjustment(True)

	def OnCustomCommandClient(self, args):
		# 从dict中选取处理函数
		handler = self.clientCustomCmd.get(args['cmd'])
		if handler:
			handler(args)

	def _get_status_client_event_value(self, status):
		parts = status.split('.')
		if len(parts) < 2 or not parts[1]:
			return False, None, '事件状态格式为 client.event.<事件名>[.<字段>]'
		event_name = parts[1]
		if not event_name.replace('_', '').isalnum() or event_name[0].isdigit():
			return False, None, '事件名只能包含字母、数字和下划线'
		if event_name not in self._get_status_client_event_callbacks:
			if len(self._get_status_client_event_callbacks) >= 32:
				return False, None, '客户端事件监听数量已达上限 32'
			def cache_event(args, cached_event_name=event_name):
				try:
					self._get_status_client_events[cached_event_name] = dict(args)
				except (TypeError, ValueError):
					self._get_status_client_events[cached_event_name] = args
			self._get_status_client_event_callbacks[event_name] = cache_event
			self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), event_name, self, cache_event)
		if event_name not in self._get_status_client_events:
			return False, None, '已开始监听客户端事件 %s；事件触发后再次执行本指令获取快照' % event_name
		value = self._get_status_client_events[event_name]
		for key in parts[2:]:
			if isinstance(value, dict) and key in value:
				value = value[key]
			elif isinstance(value, (list, tuple)) and key.isdigit() and int(key) < len(value):
				value = value[int(key)]
			else:
				return False, None, '字段路径 %s 无法继续读取' % key
		return True, value, None

	def _get_status_client_nested_value(self, value, path):
		for field in path:
			if isinstance(value, dict) and field in value:
				value = value[field]
			elif isinstance(value, (list, tuple)) and field.lstrip('-').isdigit() and -len(value) <= int(field) < len(value):
				value = value[int(field)]
			else:
				return False, None, '客户端字段路径 %s 无法继续读取' % field
		return True, value, None

	def _get_status_client_safe_call(self, component, method_name, default=None):
		try:
			return getattr(component, method_name)()
		except Exception:
			return default

	def _get_status_client_item_value(self, path):
		parts = path.split('.') if path else []
		if not parts:
			return False, None, '客户端物品状态不能为空'
		position = parts[0].lower()
		if position in ('carried', 'mainhand', 'held'):
			value = compItem.GetCarriedItem(True)
			parts = parts[1:]
		elif position == 'offhand':
			value = compItem.GetOffhandItem(True)
			parts = parts[1:]
		elif position in ('inventory', 'armor'):
			if len(parts) < 2 or not parts[1].isdigit():
				return True, compItem.GetPlayerAllItems(0 if position == 'inventory' else 3, True), None
			slot = int(parts[1])
			value = compItem.GetPlayerItem(0 if position == 'inventory' else 3, slot, True)
			parts = parts[2:]
		else:
			return False, None, '未知客户端物品位置 %s' % parts[0]
		if not parts:
			return True, value, None
		return self._get_status_client_nested_value(value, parts)

	def _get_status_client_math_value(self, expression):
		try:
			parsed = ast.parse(expression, mode='eval')
		except (SyntaxError, ValueError):
			return False, None, '客户端数学表达式语法错误'

		def evaluate(node):
			if isinstance(node, ast.Expression):
				return evaluate(node.body)
			if isinstance(node, ast.Num):
				return node.n
			if hasattr(ast, 'Constant') and isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
				return node.value
			if isinstance(node, ast.Name):
				if node.id == 'pi':
					return math.pi
				if node.id == 'e':
					return math.e
				found, value, error = self._get_status_client_value(node.id)
				if not found or not isinstance(value, (int, long, float)): #type: ignore
					raise ValueError(error or '状态不是数值')
				return value
			if isinstance(node, ast.Attribute):
				path = []
				current = node
				while isinstance(current, ast.Attribute):
					if not current.attr.replace('_', '').isalnum():
						raise ValueError('非法状态路径')
					path.insert(0, current.attr)
					current = current.value
				if not isinstance(current, ast.Name):
					raise ValueError('非法状态路径')
				path.insert(0, current.id)
				found, value, error = self._get_status_client_value('.'.join(path))
				if not found or not isinstance(value, (int, long, float)): #type: ignore
					raise ValueError(error or '状态不是数值')
				return value
			if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Invert, ast.Not)):
				value = evaluate(node.operand)
				return {ast.USub: operator.neg, ast.UAdd: operator.pos, ast.Invert: operator.invert, ast.Not: operator.not_}[type(node.op)](value)
			if isinstance(node, ast.BinOp) and type(node.op) in STATUS_MATH_BINOPS:
				return STATUS_MATH_BINOPS[type(node.op)](evaluate(node.left), evaluate(node.right))
			if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
				if isinstance(node.op, ast.And):
					result = True
					for item in node.values:
						result = evaluate(item)
						if not result:
							return False
					return result
				for item in node.values:
					result = evaluate(item)
					if result:
						return True
				return result
			if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators):
				left = evaluate(node.left)
				for index, comparator in enumerate(node.comparators):
					right = evaluate(comparator)
					if not STATUS_MATH_CMPOPS[type(node.ops[index])](left, right):
						return False
					left = right
				return True
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in STATUS_MATH_FUNCTIONS:
				return STATUS_MATH_FUNCTIONS[node.func.id](*[evaluate(arg) for arg in node.args])
			raise ValueError('客户端数学表达式包含不支持的语法')

		try:
			return True, evaluate(parsed), None
		except (ArithmeticError, TypeError, ValueError, OverflowError, KeyError):
			return False, None, '客户端数学表达式计算失败'

	def _get_status_client_value(self, status):
		status = str(status).strip()
		key = status.lower()
		if key.startswith('math.') or re.search(r'[+\-*/%&|^!<>=()]', status) or re.search(r'\b(and|or|not)\b', status):
			expression = status.split('.', 1)[1] if key.startswith('math.') else status
			return self._get_status_client_math_value(expression)
		# 向量状态统一支持 velocity.x、rotation.yaw 等直观分量写法。
		parts = key.split('.')
		if parts[0] in ('position', 'pos', 'xyz', 'foot_position', 'foot_pos', 'foot_xyz', 'velocity', 'motion', 'rotation', 'rot', 'rotxy', 'input_vector'):
			root = parts[0]
			if root in ('position', 'pos', 'xyz'):
				value = compPos.GetPos()
				fields = {'x': 0, 'y': 1, 'z': 2}
			elif root in ('foot_position', 'foot_pos', 'foot_xyz'):
				value = compPos.GetFootPos()
				fields = {'x': 0, 'y': 1, 'z': 2}
			elif root in ('rotation', 'rot', 'rotxy'):
				value = compRot.GetRot()
				fields = {'x': 0, 'pitch': 0, 'y': 1, 'yaw': 1}
			elif root == 'input_vector':
				value = compActorMotion.GetInputVector()
				fields = {'x': 0, 'forward': 0, 'y': 1, 'z': 1, 'strafe': 1}
			else:
				value = compActorMotion.GetMotion()
				fields = {'x': 0, 'y': 1, 'z': 2}
			if len(parts) == 1:
				return True, value, None
			if len(parts) == 2 and parts[1] in fields:
				return True, value[fields[parts[1]]], None
			return False, None, '客户端状态 %s 只支持 .x/.y/.z 或对应方向字段' % root
		if parts[0] in ('item', 'items'):
			if len(parts) == 1:
				return True, {
					'carried': compItem.GetCarriedItem(True), 'offhand': compItem.GetOffhandItem(True),
					'inventory': compItem.GetPlayerAllItems(0, True), 'armor': compItem.GetPlayerAllItems(3, True),
				}, None
			return self._get_status_client_item_value('.'.join(parts[1:]))
		if key in ('name', 'entity_name'):
			return True, CF.CreateName(localPlayerId).GetName(), None
		if key in ('type', 'entity_type'):
			return True, CF.CreateEngineType(localPlayerId).GetEngineTypeStr(), None
		if key in ('aux_value', 'aux'):
			return True, CF.CreateAuxValue(localPlayerId).GetAuxValue(), None
		if key in ('attack_target', 'target'):
			return True, CF.CreateAction(localPlayerId).GetAttackTarget(), None
		if key in ('collision_size', 'collision'):
			return True, CF.CreateCollisionBox(localPlayerId).GetSize(), None
		if key in ('quaternion', 'rotation_quaternion'):
			return True, CF.CreatePhysx(localPlayerId).GetQuaternion(), None
		if key in ('rider', 'rider_id'):
			return True, CF.CreateRide(localPlayerId).GetEntityRider(), None
		if key in ('tame_owner', 'owner'):
			return True, CF.CreateTame(localPlayerId).GetOwnerId(), None
		if key in ('local_time', 'dimension_time'):
			return True, CF.CreateDimension(localPlayerId).GetLocalTime(), None
		if key == 'time':
			return True, CF.CreateTime(levelId).GetTime(), None
		if key in ('is_alive', 'alive'):
			return True, compGame.IsEntityAlive(localPlayerId), None
		if key in ('effects', 'effect'):
			return True, CF.CreateEffect(localPlayerId).GetAllEffects() or [], None
		if key.startswith('effect.') or key.startswith('effects.'):
			parts = status.split('.')
			effects = CF.CreateEffect(localPlayerId).GetAllEffects() or []
			if parts[0].lower() == 'effects' and len(parts) > 1 and parts[1].isdigit():
				value = effects
				parts = parts[1:]
			else:
				value = None
				for effect in effects:
					if effect.get('effectName', '').lower() == parts[1].lower():
						value = effect
						break
				if value is None:
					if len(parts) > 2 and parts[2].lower() == 'active':
						return True, False, None
					return True, False, None
				parts = parts[2:]
				if len(parts) == 1 and parts[0].lower() == 'active':
					return True, True, None
			for field in parts:
				if isinstance(value, dict) and field in value:
					value = value[field]
				elif isinstance(value, (list, tuple)) and field.isdigit() and int(field) < len(value):
					value = value[int(field)]
				else:
					return False, None, '客户端效果字段 %s 无法读取' % field
			return True, value, None
		if key == 'event.all':
			return True, dict(self._get_status_client_events), None
		if key.startswith('event.'):
			return self._get_status_client_event_value(status)
		if key.startswith('query.'):
			value = CF.CreateQueryVariable(localPlayerId).GetMolangValue(status)
			if value is None:
				return False, None, '客户端 Molang query 没有返回值: %s' % status
			return True, value, None
		if key in ('dimension', 'dim'):
			return True, compGame.GetCurrentDimension(), None
		if key in ('body_rot', 'body_rotation'):
			return True, compRot.GetBodyRot(), None
		if key in ('on_ground', 'is_on_ground'):
			return True, compAttr.isEntityOnGround(), None
		if key in ('in_lava', 'is_in_lava'):
			return True, compAttr.isEntityInLava(), None
		if key in ('motion', 'velocity'):
			return True, compActorMotion.GetMotion(), None
		if key in ('input', 'input_vector'):
			return True, compActorMotion.GetInputVector(), None
		if key in ('position', 'pos', 'xyz'):
			return True, compPos.GetPos(), None
		if key in ('foot_position', 'foot_pos', 'foot_xyz'):
			return True, compPos.GetFootPos(), None
		if key in ('rotation', 'rot'):
			return True, compRot.GetRot(), None
		if key in ('is_gliding', 'gliding'):
			return True, compPlayer.isGliding(), None
		if key in ('is_sprinting', 'sprinting'):
			return True, compPlayer.isSprinting(), None
		if key in ('is_moving', 'moving'):
			return True, compPlayer.isMoving(), None
		if key in ('is_riding', 'riding'):
			return True, compPlayer.isRiding(), None
		if key in ('is_sneaking', 'sneaking'):
			return True, compPlayer.isSneaking(), None
		if key in ('is_in_water', 'in_water'):
			return True, compPlayer.isInWater(), None
		if key in ('is_on_ladder', 'on_ladder'):
			return True, compPlayer.IsOnLadder(), None
		if key in ('is_in_scaffolding', 'in_scaffolding'):
			return True, compPlayer.IsInScaffolding(), None
		if key in ('is_fishing', 'fishing'):
			return True, compPlayer.GetPlayerIsFishing(), None
		if key in ('hunger', 'player_hunger'):
			return True, compPlayer.GetPlayerHunger(), None
		if key in ('selected_slot', 'slot'):
			return True, compItem.GetSlotId(), None
		if key in ('all_enchants', 'enchants'):
			return True, compItem.GetAllEnchantsInfo(), None
		if key in ('fish_hook', 'fish_hook_entities'):
			return True, compItem.GetPlayerFishHookEntity(), None
		if key in ('fish_item', 'fishing_item'):
			return True, compItem.GetPlayerFishItem(True), None
		if key in ('drop_item_entities', 'client_drop_item_entities'):
			return True, compItem.GetClientDropItemEntityIdList(), None
		if key in ('pick_range', 'interaction_range'):
			return True, compPlayer.GetPickRange(), None
		if key in ('pick_center_offset', 'interaction_center_offset'):
			return True, compPlayer.GetPickCenterOffset(), None
		if key in ('uid', 'player_uid'):
			return True, compPlayer.getUid(), None
		if key in ('camera', 'camera.all'):
			return True, {
				'fov': self._get_status_client_safe_call(compCamera, 'GetFov'),
				'position': self._get_status_client_safe_call(compCamera, 'GetPosition'),
				'rotation': self._get_status_client_safe_call(compCamera, 'GetCameraRotation'),
				'forward': self._get_status_client_safe_call(compCamera, 'GetForward'),
				'offset': self._get_status_client_safe_call(compCamera, 'GetCameraOffset'),
				'anchor': self._get_status_client_safe_call(compCamera, 'GetCameraAnchor'),
				'pitch_limit': self._get_status_client_safe_call(compCamera, 'GetCameraPitchLimit'),
				'motions': self._get_status_client_safe_call(compCamera, 'GetCameraMotions'),
			}, None
		if key.startswith('camera.'):
			camera_fields = {
				'fov': 'GetFov', 'position': 'GetPosition', 'rotation': 'GetCameraRotation',
				'forward': 'GetForward', 'offset': 'GetCameraOffset', 'anchor': 'GetCameraAnchor',
				'pitch_limit': 'GetCameraPitchLimit', 'motions': 'GetCameraMotions',
				'chosen': 'GetChosen', 'chosen_entity': 'GetChosenEntity', 'pick_facing': 'PickFacing',
				'fp_height': 'GetFpHeight', 'lock_pitch': 'IsModCameraLockPitch',
				'lock_yaw': 'IsModCameraLockYaw',
			}
			field = key.split('.', 1)[1]
			method_name = camera_fields.get(field)
			if method_name:
				return True, self._get_status_client_safe_call(compCamera, method_name), None
		if key in ('fps', 'screen_fps'):
			return True, compGame.GetFps(), None
		if key in ('screen_size', 'resolution'):
			return True, compGame.GetScreenSize(), None
		if key in ('screen_view', 'screen_view_info'):
			return True, compGame.GetScreenViewInfo(), None
		if key.startswith('operation.'):
			operation_fields = {
				'can_move': 'IsCanMove', 'can_jump': 'IsCanJump', 'can_attack': 'IsCanAttack',
				'can_walk_mode': 'IsCanWalkMode', 'can_perspective': 'IsCanPerspective',
				'can_pause': 'IsCanPause', 'can_pause_screen': 'IsCanPauseScreen',
				'can_chat': 'IsCanChat', 'can_screenshot': 'IsCanScreenShot',
				'can_open_inventory': 'IsCanOpenInv', 'can_drag': 'IsCanDrag', 'can_inair': 'IsCanInair',
				'hold_time_ms': 'GetHoldTimeThresholdInMs',
			}
			method_name = operation_fields.get(key.split('.', 1)[1])
			if method_name:
				return True, self._get_status_client_safe_call(compOperation, method_name), None
		if key in ('perspective', 'view_perspective'):
			return True, compPlayerView.GetPerspective(), None
		if key in ('ui_profile', 'view_ui_profile'):
			return True, compPlayerView.GetUIProfile(), None
		if key == 'all':
			return True, {
				'id': localPlayerId,
				'name': self._get_status_client_safe_call(CF.CreateName(localPlayerId), 'GetName'),
				'type': self._get_status_client_safe_call(CF.CreateEngineType(localPlayerId), 'GetEngineTypeStr'),
				'position': compPos.GetPos(), 'foot_position': compPos.GetFootPos(),
				'rotation': compRot.GetRot(), 'body_rot': compRot.GetBodyRot(),
				'motion': compActorMotion.GetMotion(), 'input_vector': compActorMotion.GetInputVector(),
				'dimension': compGame.GetCurrentDimension(),
				'on_ground': compAttr.isEntityOnGround(),
				'in_lava': compAttr.isEntityInLava(),
				'effects': CF.CreateEffect(localPlayerId).GetAllEffects() or [],
				'hunger': compPlayer.GetPlayerHunger(),
				'states': {
					'gliding': compPlayer.isGliding(), 'sprinting': compPlayer.isSprinting(),
					'moving': compPlayer.isMoving(), 'riding': compPlayer.isRiding(),
					'sneaking': compPlayer.isSneaking(), 'in_water': compPlayer.isInWater(),
					'on_ladder': compPlayer.IsOnLadder(), 'in_scaffolding': compPlayer.IsInScaffolding(),
					'fishing': compPlayer.GetPlayerIsFishing(),
				},
				'items': {
					'carried': compItem.GetCarriedItem(True), 'offhand': compItem.GetOffhandItem(True),
					'inventory': compItem.GetPlayerAllItems(0, True), 'armor': compItem.GetPlayerAllItems(3, True),
				},
				'selected_slot': compItem.GetSlotId(), 'all_enchants': compItem.GetAllEnchantsInfo(),
				'fish_hook': compItem.GetPlayerFishHookEntity(), 'fps': compGame.GetFps(),
				'screen_size': compGame.GetScreenSize(), 'screen_view': compGame.GetScreenViewInfo(),
				'attack_target': self._get_status_client_safe_call(CF.CreateAction(localPlayerId), 'GetAttackTarget'),
				'collision_size': self._get_status_client_safe_call(CF.CreateCollisionBox(localPlayerId), 'GetSize'),
				'quaternion': self._get_status_client_safe_call(CF.CreatePhysx(localPlayerId), 'GetQuaternion'),
				'rider': self._get_status_client_safe_call(CF.CreateRide(localPlayerId), 'GetEntityRider'),
				'owner': self._get_status_client_safe_call(CF.CreateTame(localPlayerId), 'GetOwnerId'),
				'local_time': self._get_status_client_safe_call(CF.CreateDimension(localPlayerId), 'GetLocalTime'),
				'time': self._get_status_client_safe_call(CF.CreateTime(levelId), 'GetTime'),
				'perspective': self._get_status_client_safe_call(compPlayerView, 'GetPerspective'),
				'ui_profile': self._get_status_client_safe_call(compPlayerView, 'GetUIProfile'),
				'operation': {
					'can_move': self._get_status_client_safe_call(compOperation, 'IsCanMove'),
					'can_jump': self._get_status_client_safe_call(compOperation, 'IsCanJump'),
					'can_attack': self._get_status_client_safe_call(compOperation, 'IsCanAttack'),
					'can_pause': self._get_status_client_safe_call(compOperation, 'IsCanPause'),
					'can_chat': self._get_status_client_safe_call(compOperation, 'IsCanChat'),
				},
			}, None
		return False, None, '未知客户端状态 %s；可使用 client.query.*、client.event.*、client.dimension、client.body_rot、client.on_ground 或 client.all' % status

	def OnGetStatusClientRequest(self, args):
		request_id = args.get('requestId')
		try:
			found, value, error = self._get_status_client_value(args.get('status', ''))
			packet = {'requestId': request_id}
			if found:
				packet['value'] = value
			else:
				packet['error'] = error
		except Exception as error:
			packet = {'requestId': request_id, 'error': str(error)}
		packet['__id__'] = localPlayerId
		self.NotifyToServer('GetStatusClientResponse', packet)

	# 客户端函数部分由此开始
	def client_setplayerinteracterange(self, args):
		compPlayer.SetPickRange(args['cmdargs'][1])
	def client_openfoldgui(self, args):
		clientApi.OpenFoldGui()
	def client_setcanpausescreen(self, args):
		compOperation.SetCanPauseScreen(args['cmdargs'][1])
	def client_setcolorbrightness(self, args):
		compPostProcess.SetColorAdjustmentBrightness(args['cmdargs'][2])
	def client_setcolorcontrast(self, args):
		compPostProcess.SetColorAdjustmentContrast(args['cmdargs'][2])
	def client_setcolorsaturation(self, args):
		compPostProcess.SetColorAdjustmentSaturation(args['cmdargs'][2])
	def client_setcolortint(self, args):
		compPostProcess.SetColorAdjustmentTint(args['cmdargs'][2], (args['cmdargs'][3], args['cmdargs'][4], args['cmdargs'][5]))
	def client_setcompassentity(self, args):
		compItem.SetCompassEntity(args['cmdargs'][1][0])
	def client_setcompasstarget(self, args):
		compItem.SetCompassTarget(args['cmdargs'][0], args['cmdargs'][1], args['cmdargs'][2])
	def client_setvignettecenter(self, args):
		compPostProcess.SetVignetteCenter((args['cmdargs'][2], args['cmdargs'][3]))
	def client_setvignetteradius(self, args):
		compPostProcess.SetVignetteRadius(args['cmdargs'][2])
	def client_setvignettecolor(self, args):
		compPostProcess.SetVignetteRGB(args['cmdargs'][2])
	def client_setvignettesmooth(self, args):
		compPostProcess.SetVignetteSmoothness(args['cmdargs'][2])
	def client_setvignette(self, args):
		compPostProcess.SetEnableVignette(args['cmdargs'][2])
	def client_setgaussian(self, args):
		compPostProcess.SetEnableGaussianBlur(args['cmdargs'][2])
	def client_setgaussianradius(self, args):
		compPostProcess.SetGaussianBlurRadius(args['cmdargs'][2])
	def client_sethudchatstackposition(self, args):
		clientApi.SetHudChatStackPosition((args['cmdargs'][1], args['cmdargs'][2]))
	def client_sethudchatstackvisible(self, args):
		clientApi.SetHudChatStackVisible(args['cmdargs'][1])
	def client_chatclear(self, args):
		compClientTextNotify = CF.CreateTextNotifyClient(localPlayerId)
		for _ in range(35):	 # type: ignore
			compClientTextNotify.SetLeftCornerNotify("\n\n\n\n\n")
	def client_openui(self, args):
		compClientTextNotify = CF.CreateTextNotifyClient(localPlayerId)
		if args['cmdargs'][0] == "enchant":
			uiWillbeOpen = "enchant"
			uiWillbeOpenName = "自定义附魔"
		elif args['cmdargs'][0] == "getitem":
			uiWillbeOpen = "getitem"
			uiWillbeOpenName = "获取隐藏物品"
		elif args['cmdargs'][0] == "nbteditor":
			uiWillbeOpen = "nbteditor"
			uiWillbeOpenName = "NBT编辑器"
		elif args['cmdargs'][0] == "changetips":
			uiWillbeOpen = "itemTips"
			uiWillbeOpenName = "修改物品注释"
		elif args['cmdargs'][0] == "cmdbatch":
			uiWillbeOpen = "cmdbatch"
			uiWillbeOpenName = "指令批处理"
		elif args['cmdargs'][0] == "structureimport":
			if clientApi.GetPlatform() == PLATFORM_WINDOWS:
				uiWillbeOpen = "struimport"
				uiWillbeOpenName = "结构处理"
			else:
				compClientTextNotify.SetLeftCornerNotify("§e您的设备暂不支持此功能，请前往电脑端使用")
				return
		elif args['cmdargs'][0] == "nbteditornew":
			uiWillbeOpen = "nbteditornew"
			uiWillbeOpenName = "NBT编辑器(新)"
		clientApi.PushScreen('gtmbPlugin', uiWillbeOpen)
		compClientTextNotify.SetLeftCornerNotify("已打开 %s 界面" % uiWillbeOpenName)
	def client_hidenametag(self, args):
		clientApi.HideNameTag(args['cmdargs'][1])
	def client_eula(self, args):
		clientApi.PushScreen('gtmbPlugin', 'EULA')
	# 客户端函数部分到此结束
