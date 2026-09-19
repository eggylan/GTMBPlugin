# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi
import traceback
import random
import re
import json
import time
import math
import ast
import operator
from serverSystem import unicode_convert, intg

from metaData import copyRightInfo

levelId = serverApi.GetLevelId()
CF = serverApi.GetEngineCompFactory()
compGame = CF.CreateGame(levelId)
compBlockInfo = CF.CreateBlockInfo(levelId)
compCmd = CF.CreateCommand(levelId)
compBlockEntity = CF.CreateBlockEntity(levelId)
compExtra = CF.CreateExtraData(levelId)
compItemWorld = CF.CreateItem(levelId)
compTime = CF.CreateTime(levelId)
compWeather = CF.CreateWeather(levelId)
compItemBanned = CF.CreateItemBanned(levelId)
compBlockWorld = CF.CreateBlock(levelId)
compChunkSource = CF.CreateChunkSource(levelId)
compDomainGame = CF.CreateDomainGame(levelId)

# Bedrock 计分板目标名不能包含空白或命令分隔符。输出前先做严格校验，
# 同时避免把用户输入拼进游戏命令后造成命令解析歧义。
SCORE_OBJECTIVE_RE = re.compile(r'^[A-Za-z0-9_.-]+$')

create_players_str = lambda players: ', '.join(CF.CreateName(player).GetName() for player in players)

check_entities_type = lambda typeName, ids: all(CF.CreateEngineType(id).GetEngineTypeStr() == typeName for id in ids)

is_player = lambda entity_id: CF.CreateEngineType(entity_id).GetEngineTypeStr() == 'minecraft:player'	

# GetStatus 使用整数常量而非在每次指令中查文档/创建临时表。该表与 ModSDK 3.9
# AttrType 保持一致，键名同时是 /get_status 可使用的短名称。
from consts import STATUS_ATTRS

STATUS_MAX_EVENT_WATCHERS = 32
STATUS_MAX_PENDING_CLIENT_REQUESTS = 128
STATUS_PENDING_TTL = 20.0

# 直接使用 Python math 只负责常用标量函数；表达式仍先经过安全的白名单解析，
# 不执行 eval/exec。Molang 原生 query.* 仍交给引擎处理。
from consts import STATUS_MATH_FUNCTIONS
from consts import STATUS_MATH_BINOPS
from consts import STATUS_MATH_CMPOPS

# 点路径的第一段与引擎返回向量的映射。公开写法统一采用可读的
# position.x / velocity.x / rotation.yaw，而旧短名称仍保留兼容。
from consts import STATUS_VECTOR_ROOTS

# (PlayerComponent 方法名, 输入类型)。放在模块常量中，避免批量选择器每个实体
# 都重新构造同一张分发表。
from consts import STATUS_PLAYER_SETTERS

from consts import ABILITY_ALIASES

# ModSDK ItemPosType：背包 / 副手 / 主手 / 盔甲。item.* 查询始终读取
# userData，确保附魔、自定义名称和自定义耐久等字段不会丢失。
ITEM_POSITIONS = {'inventory': 0, 'offhand': 1, 'carried': 2, 'mainhand': 2, 'held': 2, 'armor': 3}

# ModSDK 3.9 中不需要额外参数的实体状态接口。统一走此表，避免不断增长的
# if/elif，同时让 all 能覆盖每一个可直接读取的实体组件状态。
from consts import STATUS_SIMPLE_ENTITY_READERS as GET_STATUS_SIMPLE_ENTITY_READERS

STATUS_WORLD_READERS = {
	'time': compTime.GetTime,
	'raining': compWeather.IsRaining,
	'thunder': compWeather.IsThunder,
	'game_type': compGame.GetGameType,
	'difficulty': compGame.GetGameDiffculty,
	'difficulty_locked': compGame.IsLockDifficulty,
	'game_rules': compGame.GetGameRulesInfoServer,
	'game_rules_locked': compGame.IsLockGameRulesInfo,
	'game_type_locked': compGame.IsLockGameType,
	'gravity': compGame.GetLevelGravity,
	'seed': compGame.GetSeed,
	'spawn_position': compGame.GetSpawnPosition,
	'spawn_dimension': compGame.GetSpawnDimension,
	'piston_max_interaction_count': compGame.GetPistonMaxInteractionCount,
	'disable_command_minecart': compGame.IsDisableCommandMinecart,
	'scoreboard_objects': compGame.GetAllScoreboardObjects,
	'player_scoreboard_objects': compGame.GetAllPlayerScoreboardObjects,
	'loaded_actors': compGame.GetLoadActors,
	'loaded_blocks': compBlockInfo.GetLoadBlocks,
	'banned_items': compItemBanned.GetBannedItemList,
	'command_permission': compCmd.GetCommandPermissionLevel,
	'default_player_permission': compCmd.GetDefaultPlayerPermissionLevel,
	'loaded_area_keys': compChunkSource.GetAllAreaKeys,
	'host_player_uid': compDomainGame.GetHostPlayerUid,
	'blank_block_palette': compBlockWorld.GetBlankBlockPalette,
}

from consts import SIMPLE_ENTITY_BOOL_SETTERS

from consts import STATUS_EXTERN_NAMES

def checkjson(data):
	#type: (str) -> list
	try:
		itemDict = json.loads(data.replace("'", '"'))
	except ValueError as errordata:
		errordata = str(errordata)
		if errordata.find('char') == -1:
			return ['无效的nbt', True]
		if errordata.find('Extra') != -1:
			split = errordata.split(' - ')
			start = int(split[1][split[1].find('char') + 5:])
			end = int(split[2][0:-1])
		else:
			start = int(errordata[errordata.find('char') + 5:-1])
			end = start + 1
		return ['无效的nbt 位于 %s>>%s<<%s' % (data[:start], data[start:end], data[end:]), True]
	if isinstance(itemDict, dict):
		return [unicode_convert(itemDict), False]
	return['无效的nbt', True]

class cmdServerSystem(serverApi.GetServerSystemCls()):
	def __init__(self, namespace, systemName):
		super(cmdServerSystem, self).__init__(namespace, systemName)
		# 事件监听完全按需注册；空闲时 get_status 不产生 Tick、Timer 或轮询开销。
		self._status_server_events = {}
		self._status_server_event_callbacks = {}
		self._status_pending_clients = {}
		self._status_request_sequence = 0
		self.serverCustomCmds = {
			'get_status': self.get_status,
			'set_status': self.set_status,
			'setentityonfire':self.setentityonfire,
			'setcurrentairsupply':self.setcurrentairsupply,
			'setcompasstarget':self.setcompasstarget,
			'setcompassentity':self.setcompassentity,
			'setcolor':self.setcolor,
			'setchestitemnum':self.setchestitemnum,
			'setchestitemexchange':self.setchestitemexchange,
			'setcanpausescreen':self.setcanpausescreen,
			'setcanotherplayerride':self.setcanotherplayerride,
			'setattackplayersability':self.setattackplayersability,
			'setattackmobsability':self.setattackmobsability,
			'setattackdamage':self.setattackdamage,
			'setspawnpoint':self.setspawnpoint,
			'setplayerhealthlevel':self.setplayerhealthlevel,
			'setplayerstarvelevel':self.setplayerstarvelevel,
			'setplayerhunger':self.setplayerhunger,
			'setplayerattackspeedamplifier':self.setplayerattackspeedamplifier,
			'setplayerjumpable':self.setplayerjumpable,
			'setplayermovable':self.setplayermovable,
			'setplayernaturalstarve':self.setplayernaturalstarve,
			'setplayerprefixandsuffixname':self.setplayerprefixandsuffixname,
			'setplayermaxexhaustionvalue':self.setplayermaxexhaustionvalue,
			'setplayerhealthtick':self.setplayerhealthtick,
			'setplayerstarvetick':self.setplayerstarvetick,
			'sethurtcd':self.sethurtcd,
			'setattacktarget':self.setattacktarget,
			'resetattacktarget':self.resetattacktarget,
			'setbanplayerfishing':self.setbanplayerfishing,
			'setactorcanpush':self.setactorcanpush,
			'setactorcollidable':self.setactorcollidable,
			'setmineability':self.setmineability,
			'setbuildability':self.setbuildability,
			'setcontrol':self.setcontrol,
			'setpickuparea':self.setpickuparea,
			'setlevelgravity':self.setlevelgravity,
			'setjumppower':self.setjumppower,
			'setgravity':self.setgravity,
			'setworldspawnd':self.setworldspawnd,
			'playeruseitemtopos':self.playeruseitemtopos,
			'playeruseitemtoentity':self.playeruseitemtoentity,
			'playerdestoryblock': self.playerdestoryblock,
			'openworkbench':self.openworkbench,
			'openfoldgui':self.openfoldgui,
			'setimmunedamage':self.setimmunedamage,
			'setinvitemexchange':self.setinvitemexchange,
			'setinvitemnum':self.setinvitemnum,
			'setitemdurability':self.setitemdurability,
			'setitemmaxdurability':self.setitemmaxdurability,
			'setitemtierlevel':self.setitemtierlevel,
			'setitemtierspeed':self.setitemtierspeed,
			'setitemmaxstacksize':self.setitemmaxstacksize,
			'playerexhaustionratio':self.playerexhaustionratio,
			'setsigntextstyle':self.setsigntextstyle,
			'setsigntext':self.setsigntext,
			'setplayerinteracterange':self.setplayerinteracterange,
			'summonprojectile':self.summonprojectile,
			'setstepheight':self.setstepheight,
			'setsize':self.setsize,
			'playerchatprefix':self.playerchatprefix,
			'writehealthtoscoreboard':self.writehealthtoscoreboard,
			'writehungertoscoreboard':self.writehungertoscoreboard,
			'writearmortoscoreboard':self.writearmortoscoreboard,
			'writespeedtoscoreboard':self.writespeedtoscoreboard,
			'executecb':self.executecb,
			'setname':self.setname,
			'aicontrol':self.aicontrol,
			'param':self.param,
			'param_private':self.param_private,
			'kickt':self.kickt,
			'explode':self.explode,
			'explodebypos':self.explodebypos,
			'console':self.console,
			'addaroundentitymotion':self.addaroundentitymotion,
			'addaroundpointmotion':self.addaroundpointmotion,
			'addvelocitymotion':self.addvelocitymotion,
			'startmotion':self.startmotion,
			'stopmotion':self.stopmotion,
			'removemotion':self.removemotion,
			'addenchant':self.addenchant,
			'addtrackmotion':self.addtrackmotion,
			'setactorcanburnbylightning':self.setactorcanburnbylightning,
			'setblockcanburnbylightning':self.setblockcanburnbylightning,
			'cancelshearsdestoryblockspeedall':self.cancelshearsdestoryblockspeedall,
			'cancelshearsdestoryblockspeed':self.cancelshearsdestoryblockspeed,
			'setshearsdestoryblockspeed':self.setshearsdestoryblockspeed,
			'changeselectslot':self.changeselectslot,
			'forbidliquidflow':self.forbidliquidflow,
			'getuid':self.getuid,
			'givewithnbt':self.givewithnbt,
			'spawnitemtocontainer':self.spawnitemtocontainer,
			'spawnitemtoenderchest':self.spawnitemtoenderchest,
			'replaceitemtocarried':self.replaceitemtocarried,
			'removeenchant':self.removeenchant,
			'resetmotion':self.resetmotion,
			'setleashholder':self.setleashholder,
			'setlootdropped':self.setlootdropped,
			'setmaxairsupply':self.setmaxairsupply,
			'knockback':self.knockback,
			'setmotion':self.setmotion,
			'setopencontainersability':self.setopencontainersability,
			'setoperatedoorability':self.setoperatedoorability,
			'setorbexperience':self.setorbexperience,
			'setpersistent':self.setpersistent,
			'setpistonmaxinteractioncount':self.setpistonmaxinteractioncount,
			'setplayeruiitem':self.setplayeruiitem,
			'if':self._if,
			'setteleportability':self.setteleportability,
			'settradelevel':self.settradelevel,
			'setvignette':self.setvignette,
			'setbrewingstandslotitem':self.setbrewingstandslotitem,
			'setdisablecontainers':self.setdisablecontainers,
			'setdisabledropitem':self.setdisabledropitem,
			'setdisablehunger':self.setdisablehunger,
			'setenchantmentseed':self.setenchantmentseed,
			'setentityitem':self.setentityitem,
			'setentityowner':self.setentityowner,
			'setentityride':self.setentityride,
			'setframeitemdropchange':self.setframeitemdropchange,
			'setframerotation':self.setframerotation,
			'sethopperspeed':self.sethopperspeed,
			'sethudchatstackposition':self.sethudchatstackposition,
			'sethudchatstackvisible':self.sethudchatstackvisible,
			'setshowrideui':self.setshowrideui,
			'summonitem':self.summonitem,
			#'summonnbt':self.summonnbt,
			'setgaussian':self.setgaussian,
			'scoreparam': self.scoreparam,
			'mute': self.mute,
			"chatclear": self.chatclear,
			"openui": self.openui,
			"gettps": self.gettps,
			"copyright": self.copyright,
			"chatlimit":self.chatlimit,
			"allowmsg":self.allowmsg,
			"hidenametag": self.hidenametag,
			"cancel_structure_load": self.Cancel_Structure_Loading,
			"setoplevel": self.setoplevel,
			"opset": self.opset,
			"setlobbymod": self.setlobbymod,
			"eula": self.eula,
			"hub": self.hub,
			"lobby": self.lobby,
			"setplayercanfly": self.setplayercanfly,
			#'setblocknbt': self.setblocknbt
			"§r§r§rgtmbdebug": self.debug,
		}
		self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), 'CustomCommandTriggerServerEvent', self, self.OnCustomCommandServer)
		self.ListenForEvent('gtmbPlugin', 'cmdClientSystem', 'GetStatusClientResponse', self, self.OnGetStatusClientResponse)

	def OnCustomCommandServer(self, args):
		cmdargs = []
		variant = args['variant']
		args_list = args.get('args', [])
		cmdargs = [i['value'] for i in args_list] if args_list else [] # 空值检查
		try:
			try:
				playerId = args['origin']['entityId']
			except KeyError:
				playerId = None
			handler = self.serverCustomCmds.get(args['command'])
			if handler is not None:
				return_value = handler(cmdargs, playerId, variant, args)
				if return_value is not None:
					args['return_failed'], args['return_msg_key'] = return_value
		except:
			args['return_failed'] = True
			args['return_msg_key'] = '出现意外错误, 原因见上。请截图保留此信息并联系开发者。'
			tracebacks = traceback.format_exc().splitlines()
			compMsg = CF.CreateMsg(playerId)
			if playerId:
				for i in tracebacks:
					compMsg.NotifyOneMessage(playerId, i, '§c')

	# 服务端函数部分由此开始

	def _get_status_event_value(self, status):
		#type: (str) -> tuple[bool, dict, str | None]
		"""读取 event.<EngineEvent>[.<field>...] 的最近一次服务端事件数据。"""
		parts = status.split('.')
		if len(parts) < 2 or not parts[1]:
			return False, None, '事件状态格式为 event.<事件名>[.<字段>]'
		event_name = parts[1]
		if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', event_name):
			return False, None, '事件名只能包含字母、数字和下划线'
		if event_name not in self._status_server_event_callbacks:
			if len(self._status_server_event_callbacks) >= STATUS_MAX_EVENT_WATCHERS:
				return False, None, '事件监听数量已达上限 %s' % STATUS_MAX_EVENT_WATCHERS
			def cache_event(args, cached_event_name=event_name):
				try:
					self._status_server_events[cached_event_name] = dict(args)
				except (TypeError, ValueError):
					self._status_server_events[cached_event_name] = args
			self._status_server_event_callbacks[event_name] = cache_event
			self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), event_name, self, cache_event)
		if event_name not in self._status_server_events:
			return False, None, '已开始监听 %s；事件触发后再次执行本指令获取快照' % event_name
		value = self._status_server_events[event_name]
		for key in parts[2:]:
			if isinstance(value, dict):
				if key not in value:
					return False, None, '事件 %s 中不存在字段 %s' % (event_name, key)
				value = value[key]
			elif isinstance(value, (list, tuple)) and key.isdigit() and int(key) < len(value):
				value = value[int(key)]
			else:
				return False, None, '字段路径 %s 无法继续读取' % key
		return True, value, None

	def _get_status_nested_value(self, value, path):
		for key in path:
			if isinstance(value, dict) and key in value:
				value = value[key]
			elif isinstance(value, (list, tuple)) and key.lstrip('-').isdigit() and -len(value) <= int(key) < len(value):
				value = value[int(key)]
			else:
				return False, None, '字段路径 %s 无法继续读取' % key
		return True, value, None

	def _get_status_vector_value(self, entity_id, root, field):
		base_status, fields = STATUS_VECTOR_ROOTS[root]
		if field not in fields:
			return False, None, '%s 不存在分量 %s' % (root, field)
		found, value, error = self._get_status_server_value(entity_id, base_status)
		if not found:
			return False, None, error
		return True, value[fields[field]], None

	def _get_status_math_value(self, entity_id, expression):
		"""安全计算数学表达式；变量可引用 velocity.x 等状态路径。"""
		try:
			parsed = ast.parse(expression, mode='eval')
		except (SyntaxError, ValueError):
			return False, None, '数学表达式语法错误'
		values = {'pi': math.pi, 'e': math.e}

		def evaluate(node):
			if isinstance(node, ast.Expression):
				return evaluate(node.body)
			if isinstance(node, ast.Num):
				return node.n
			if hasattr(ast, 'Constant') and isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
				return node.value
			if isinstance(node, ast.Name):
				if node.id in values:
					return values[node.id]
				found, value, error = self._get_status_server_value(entity_id, node.id)
				if not found:
					raise ValueError('数学变量 %s 无法读取: %s' % (node.id, error))
				if not isinstance(value, (int, long, float)): #type: ignore
					raise TypeError('数学变量 %s 不是数值' % node.id)
				values[node.id] = value
				return value
			if isinstance(node, ast.Attribute):
				# 只允许读取状态路径，例如 velocity.x、rotation.yaw；不允许
				# __class__、__dict__ 等 Python 对象属性，避免表达式越权。
				path_parts = []
				current = node
				while isinstance(current, ast.Attribute):
					if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', current.attr):
						raise ValueError('非法状态路径')
					path_parts.insert(0, current.attr)
					current = current.value
				if not isinstance(current, ast.Name) or not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', current.id):
					raise ValueError('非法状态路径')
				path_parts.insert(0, current.id)
				path = '.'.join(path_parts)
				found, value, error = self._get_status_server_value(entity_id, path)
				if not found:
					raise ValueError('数学变量 %s 无法读取: %s' % (path, error))
				if not isinstance(value, (int, long, float)): #type: ignore
					raise TypeError('数学变量 %s 不是数值' % path)
				values[path] = value
				return value
			if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Invert, ast.Not)):
				value = evaluate(node.operand)
				return {ast.USub: operator.neg, ast.UAdd: operator.pos, ast.Invert: operator.invert, ast.Not: operator.not_}[type(node.op)](value)
			if isinstance(node, ast.BinOp) and type(node.op) in STATUS_MATH_BINOPS:
				return STATUS_MATH_BINOPS[type(node.op)](evaluate(node.left), evaluate(node.right))
			if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
				# 短路计算，避免 `0 and sqrt(-1)` 这类无意义的异常。
				if isinstance(node.op, ast.And):
					result = True
					for item in node.values:
						result = evaluate(item)
						if not result:
							return False
					return result
				result = False
				for item in node.values:
					result = evaluate(item)
					if result:
						return True
				return result
			if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators):
				left = evaluate(node.left)
				return all(STATUS_MATH_CMPOPS[type(op)](left if index == 0 else evaluate(node.comparators[index - 1]), evaluate(comparator)) for index, (op, comparator) in enumerate(zip(node.ops, node.comparators)))
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in STATUS_MATH_FUNCTIONS:
				return STATUS_MATH_FUNCTIONS[node.func.id](*[evaluate(arg) for arg in node.args])
			if isinstance(node, (ast.Tuple, ast.List)):
				return tuple(evaluate(item) for item in node.elts)
			raise ValueError('数学表达式包含不支持的语法')

		try:
			return True, evaluate(parsed), None
		except (ArithmeticError, TypeError, ValueError, OverflowError, KeyError):
			return False, None, '数学表达式计算失败'

	def _get_status_effect_value(self, entity_id, effect_name=None, path=None):
		effects = CF.CreateEffect(entity_id).GetAllEffects() or []
		if effect_name is None:
			return True, effects, None
		for effect in effects:
			if effect.get('effectName', '').lower() == effect_name.lower():
				if not path:
					return True, effect, None
				return self._get_status_nested_value(effect, path)
		# active 是一个稳定的布尔查询；其它字段在没有该效果时没有值。
		if path == ['active']:
			return True, False, None
		return True, False, None

	def _get_status_item_value(self, entity_id, position_name, path=None):
		if not is_player(entity_id):
			return False, None, '仅支持获取玩家物品'
		position_name = position_name.lower()
		if position_name not in ITEM_POSITIONS:
			return False, None, '物品位置应为 carried、offhand、inventory 或 armor'
		pos_type = ITEM_POSITIONS[position_name]
		item_comp = CF.CreateItem(entity_id)
		path = path or []
		if pos_type in (0, 3):
			if not path:
				return True, item_comp.GetPlayerAllItems(pos_type, True), None
			if not path[0].isdigit():
				return False, None, '%s 需要槽位，例如 item.%s.0' % (position_name, position_name)
			slot = int(path[0])
			path = path[1:]
		else:
			slot = 0
		item = item_comp.GetPlayerItem(pos_type, slot, True)
		if path and path[0] in ('durability', 'max_durability'):
			if path[0] == 'durability':
				return True, item_comp.GetItemDurability(pos_type, slot), None
			return True, item_comp.GetItemMaxDurability(pos_type, slot, False), None
		# 专用附魔/盾牌接口比物品字典中的兼容字段更完整。背包和盔甲
		# 槽位支持原版附魔与 Mod 自定义附魔，主手/副手仍读取原始物品字典。
		if path and len(path) == 1 and pos_type in (0, 3):
			field = path[0].lower()
			if field in ('enchantments', 'enchants', 'enchant'):
				reader = item_comp.GetInvItemEnchantData if pos_type == 0 else item_comp.GetEquItemEnchant
				return True, reader(slot), None
			if field in ('mod_enchantments', 'mod_enchants', 'custom_enchantments', 'custom_enchants'):
				reader = item_comp.GetInvItemModEnchantData if pos_type == 0 else item_comp.GetEquItemModEnchant
				return True, reader(slot), None
			if field in ('defence_angle', 'defense_angle'):
				return True, item_comp.GetItemDefenceAngle(pos_type, slot), None
		if not path:
			return True, item, None
		return self._get_status_nested_value(item, path)

	def _get_status_all_player_items(self, entity_id):
		if not is_player(entity_id):
			return False, None, '仅支持获取玩家物品'
		compItem = CF.CreateItem(entity_id)
		return True, {
			'carried': compItem.GetPlayerItem(2, 0, True),
			'offhand': compItem.GetPlayerItem(1, 0, True),
			'inventory': compItem.GetPlayerAllItems(0, True),
			'armor': compItem.GetPlayerAllItems(3, True),
		}, None

	def _get_status_valid_scoreboard_objective(self, objective):
		"""只接受可直接放进 Bedrock scoreboard 命令的目标名。"""
		if not isinstance(objective, str) or not objective:
			return False
		try:
			return SCORE_OBJECTIVE_RE.match(str(objective)) is not None
		except (TypeError, UnicodeEncodeError):
			return False

	def _get_status_score_value(self, entity_id, objective, holder_id=None):
		#type: (int, str, int | None) -> tuple[bool, int | None, str | None]
		"""读取实体在指定计分项中的值。ModSDK 3.9 返回 scoreList 嵌套结构。"""
		holder_id = holder_id or entity_id
		try:
			score_data = CF.CreateGame(holder_id).GetAllPlayerScoreboardObjects() or []
		except Exception:
			return False, None, '无法读取实体计分板数据'
		if isinstance(score_data, dict):
			score_data = [score_data]
		# GetAllPlayerScoreboardObjects 通常返回所有玩家记录；当实现只
		# 返回当前 holder 的 scoreList 时，也接受扁平 scoreList 结果。
		if score_data and isinstance(score_data[0], dict) and ('scoreList' not in score_data[0] and 'scores' not in score_data[0]) and ('name' in score_data[0] or 'objective' in score_data[0]):
			score_data = [{'playerId': holder_id, 'scoreList': score_data}]
		for player_data in score_data:
			if not isinstance(player_data, dict):
				continue
			player_id = player_data.get('playerId', player_data.get('entityId'))
			if player_id is not None and player_id != holder_id:
				continue
			score_list = player_data.get('scoreList', player_data.get('scores', []))
			if isinstance(score_list, dict):
				score_list = [score_list]
			for score in score_list or []:
				if not isinstance(score, dict):
					continue
				if score.get('name', score.get('objective')) == objective:
					if 'value' not in score:
						return False, None, '计分项 %s 返回记录但没有 value' % objective
					try:
						return True, int(score['value']), None
					except (TypeError, ValueError):
						return False, None, '计分项 %s 的 value 不是整数' % objective
		return False, None, '实体 %s 没有计分项 %s' % (holder_id, objective)

	def _get_status_simple_entity_value(self, entity_id, key):
		factory_name, method_name = GET_STATUS_SIMPLE_ENTITY_READERS[key]
		component = getattr(CF, factory_name)(entity_id)
		return True, getattr(component, method_name)(), None

	def _get_status_extern_values(self, entity_id):
		#type: (str) -> dict[str, int | bool]
		"""一次读取并计算全部派生状态，避免 all 命令重复创建组件。"""
		result = {}
		try:
			motion = CF.CreateActorMotion(entity_id).GetMotion()
			vx, vy, vz = float(motion[0]), float(motion[1]), float(motion[2])
			result['rising'] = max(vy, 0.0)
			result['falling'] = max(-vy, 0.0)
			result['downing'] = result['falling']
		except Exception:
			result['rising'] = result['falling'] = result['downing'] = 0.0
		try:
			rotation = CF.CreateRot(entity_id).GetRot()
			yaw = math.radians(float(rotation[1]))
			# Bedrock yaw=0 时朝向 +Z：forward=(-sin(yaw), 0, cos(yaw))。
			forward_component = -math.sin(yaw) * vx + math.cos(yaw) * vz
			left_component = -math.cos(yaw) * vx - math.sin(yaw) * vz
			result['forward'] = max(forward_component, 0.0)
			result['backward'] = max(-forward_component, 0.0)
			result['leftward'] = max(left_component, 0.0)
			result['rightward'] = max(-left_component, 0.0)
		except Exception:
			pass
		for name in STATUS_EXTERN_NAMES:
			if name not in result:
				result[name] = False if name == 'climbing' else 0.0
		try:
			query_result = CF.CreateQueryVariable(entity_id).EvalMolangExpression('query.is_on_ladder')
			if isinstance(query_result, dict):
				result['climbing'] = False if query_result.get('error') else self._get_status_truthy(query_result.get('value', 0))
			else:
				result['climbing'] = self._get_status_truthy(query_result)
		except Exception:
			result['climbing'] = False
		return result

	def _get_status_extern_value(self, entity_id, name=None):
		#type: (str, str | None) -> tuple[bool, dict | None, str | None]
		"""读取本插件计算的派生状态，不向 ModSDK 注册额外组件或轮询。"""
		if name is None or str(name).lower() in ('', 'all'):
			return True, self._get_status_extern_values(entity_id), None
		name = str(name).lower()
		if name not in STATUS_EXTERN_NAMES:
			return False, None, '未知 extern 状态: %s' % name
		values = self._get_status_extern_values(entity_id)
		if name not in values:
			return False, None, '无法计算 extern.%s' % name
		return True, values[name], None

	def _get_status_world_value(self, key):
		if key == 'all':
			result = {}
			for world_key, reader in STATUS_WORLD_READERS.items():
				try:
					result[world_key] = reader()
				except Exception:
					pass
			return True, result, None
		reader = STATUS_WORLD_READERS.get(key)
		if reader is None:
			return False, None, '未知世界状态 world.%s' % key
		return True, reader(), None

	def _get_status_server_value(self, entity_id, status):
		#type: (str, str) -> tuple[bool, dict | bool | None, str | None]
		"""以实体上下文读取一个服务端状态或 Molang 表达式。"""
		if not status:
			return False, None, '状态不能为空'
		status = status.strip() if isinstance(status, str) else str(status).strip()
		key = status.lower()
		is_math_expression = bool(re.search(r'[+\-*/%&|^!<>=()]', status) or re.search(r'\b(and|or|not)\b', status))
		if key == 'extern' or key == 'extern.all':
			return self._get_status_extern_value(entity_id)
		if key.startswith('extern.'):
			return self._get_status_extern_value(entity_id, key.split('.', 1)[1])
		if key in STATUS_EXTERN_NAMES:
			return self._get_status_extern_value(entity_id, key)
		if key.startswith('damage_to.') or key.startswith('entity_damage.'):
			target_id = status.split('.', 1)[1]
			if not target_id:
				return False, None, 'damage_to.<target> 缺少目标实体'
			return True, compGame.GetEntityDamage(entity_id, target_id), None
		if key.startswith('world.'):
			world_parts = status.split('.')
			if len(world_parts) == 3 and world_parts[1].lower() in ('loaded_chunks', 'chunks'):
				try:
					dimension = int(world_parts[2])
				except (TypeError, ValueError):
					return False, None, 'world.loaded_chunks.<dimension> 的维度必须是整数'
				return True, compChunkSource.GetLoadedChunks(dimension), None
			if len(world_parts) == 6 and world_parts[1].lower() in ('chunk_state', 'chunk_loaded'):
				try:
					dimension, x, y, z = [int(item) for item in world_parts[2:6]]
				except (TypeError, ValueError):
					return False, None, 'world.chunk_state.<dimension>.<x>.<y>.<z> 参数必须是整数'
				return True, compChunkSource.CheckChunkState(dimension, (x, y, z)), None
			if len(world_parts) == 6 and world_parts[1].lower() in ('chunk_entities', 'chunk_entity_ids'):
				try:
					dimension, x, y, z = [int(item) for item in world_parts[2:6]]
				except (TypeError, ValueError):
					return False, None, 'world.chunk_entities.<dimension>.<x>.<y>.<z> 参数必须是整数'
				return True, compChunkSource.GetChunkEntites(dimension, (x, y, z)), None
			if len(world_parts) == 3 and world_parts[1].lower() in ('player_game_type', 'player_gametype'):
				return True, compGame.GetPlayerGameType(world_parts[2]), None
			return self._get_status_world_value(key.split('.', 1)[1])
		if key.startswith('destroy_time.'):
			if not is_player(entity_id):
				return False, None, 'destroy_time.* 仅支持玩家'
			return True, CF.CreatePlayer(entity_id).GetPlayerDestroyTotalTime(status.split('.', 1)[1]), None
		if key.startswith('exhaustion_ratio.'):
			if not is_player(entity_id):
				return False, None, 'exhaustion_ratio.* 仅支持玩家'
			try:
				exhaustion_type = int(status.split('.', 1)[1])
			except ValueError:
				return False, None, 'exhaustion_ratio.<行为枚举> 需要整数枚举值'
			return True, CF.CreatePlayer(entity_id).GetPlayerExhaustionRatioByType(exhaustion_type), None
		if key.startswith('event.') or key.startswith('server_event.'):
			if key in ('event.all', 'server_event.all'):
				return True, dict(self._status_server_events), None
			if key.startswith('server_event.'):
				event_status = status[len('server_event.'):]
				if not event_status.lower().startswith('event.'):
					event_status = 'event.' + event_status
				return self._get_status_event_value(event_status)
			return self._get_status_event_value(status)
		# 表达式中的 `velocity.x` / `rotation.yaw` 不能先按普通路径拦截，
		# 否则会在这里递归回到同一个表达式；由下方安全 AST 统一解析。
		if '.' in key and not is_math_expression:
			raw_path = status.split('.')
			path = key.split('.')
			root = path[0]
			if root in STATUS_VECTOR_ROOTS:
				if len(path) == 2:
					return self._get_status_vector_value(entity_id, root, path[1])
				return False, None, '%s 只支持一个分量，例如 %s.x' % (root, root)
			if root in ('extra', 'extra_data'):
				return self._get_status_nested_value(CF.CreateExtraData(entity_id).GetExtraData(raw_path[1]), raw_path[2:])
			if root in ('mod', 'mod_attr', 'modattr'):
				if len(raw_path) < 2 or not raw_path[1]:
					return False, None, 'mod 状态格式为 mod.<键>[.<嵌套键>]'
				return self._get_status_nested_value(CF.CreateModAttr(entity_id).GetAttr(raw_path[1], None), raw_path[2:])
			if root in ('nbt', 'entity_nbt'):
				return self._get_status_nested_value(CF.CreateEntityDefinitions(entity_id).GetEntityNBTTags(), raw_path[1:])
			if root in ('tag', 'tags') and len(path) == 2:
				return True, CF.CreateTag(entity_id).EntityHasTag(status.split('.', 1)[1]), None
			if root in ('effect', 'effects'):
				if root == 'effects' and path[1].isdigit():
					return self._get_status_nested_value(CF.CreateEffect(entity_id).GetAllEffects() or [], path[1:])
				return self._get_status_effect_value(entity_id, raw_path[1], path[2:])
			if root in ('item', 'items'):
				if len(path) < 2:
					return self._get_status_all_player_items(entity_id)
				return self._get_status_item_value(entity_id, path[1], path[2:])
			if root in ('modifier', 'modifiers', 'attribute_modifiers') and len(path) == 2:
				attr_name = path[1][4:] if path[1].startswith('max_') else path[1]
				if attr_name not in STATUS_ATTRS:
					return False, None, '未知属性 %s' % path[1]
				return True, CF.CreateAttr(entity_id).GetAllModifiers(STATUS_ATTRS[attr_name]), None
			if root in ('attribute', 'attributes') and len(path) == 2:
				return self._get_status_server_value(entity_id, path[1])
			if root == 'player' and len(path) == 2:
				if not is_player(entity_id):
					return False, None, 'player.* 仅支持玩家'
				return self._get_status_server_value(entity_id, path[1])
			if root == 'air' and len(path) == 2:
				if path[1] in ('current', 'value'):
					return self._get_status_server_value(entity_id, 'air')
				if path[1] == 'max':
					return self._get_status_server_value(entity_id, 'max_air')
				return False, None, 'air 只支持 current 或 max'
			if root in ('abilities', 'ability'):
				if not is_player(entity_id):
					return False, None, 'abilities.* 仅支持玩家'
				ability_status = ABILITY_ALIASES.get(path[1]) if len(path) == 2 else None
				if ability_status:
					return self._get_status_server_value(entity_id, ability_status)
				return self._get_status_nested_value(CF.CreatePlayer(entity_id).GetPlayerAbilities(), raw_path[1:])

		is_player = is_player(entity_id)
		compEngineType = CF.CreateEngineType(entity_id)
		compName = CF.CreateName(entity_id)
		compPos = CF.CreatePos(entity_id)
		compRot = CF.CreateRot(entity_id)
		compActorMotion = CF.CreateActorMotion(entity_id)
		compDimension = CF.CreateDimension(entity_id)
		compTag = CF.CreateTag(entity_id)
		compEffect = CF.CreateEffect(entity_id)
		if key in ('id', 'entity_id'):
			return True, entity_id, None
		if key in ('type', 'entity_type'):
			return True, compEngineType.GetEngineTypeStr(), None
		if key == 'name':
			return True, compName.GetName(), None
		if key in ('pos', 'position', 'xyz'):
			return True, compPos.GetPos(), None
		if key in ('x', 'y', 'z'):
			return True, compPos.GetPos()['xyz'.index(key)], None
		if key in ('foot_pos', 'foot_position', 'foot_xyz'):
			return True, compPos.GetFootPos(), None
		if key in ('foot_x', 'foot_y', 'foot_z'):
			return True, compPos.GetFootPos()['foot_xyz'.index(key[-1])], None
		if key in ('rot', 'rotation', 'rotxy'):
			return True, compRot.GetRot(), None
		if key in ('pitch', 'rot_x'):
			return True, compRot.GetRot()[0], None
		if key in ('yaw', 'rot_y'):
			return True, compRot.GetRot()[1], None
		if key in ('motion', 'velocity', 'motion_xyz', 'velocity_xyz'):
			return True, compActorMotion.GetMotion(), None
		if key in ('vx', 'vy', 'vz'):
			return True, compActorMotion.GetMotion()['xyz'.index(key[-1])], None
		if key in ('dimension', 'dim'):
			return True, compDimension.GetEntityDimensionId(), None
		if key in ('is_player', 'player'):
			return True, is_player, None
		if key in ('tags', 'tag'):
			return True, compTag.GetEntityTags(), None
		if key in ('effects', 'effect'):
			return self._get_status_effect_value(entity_id)
		if key in ('loaded_effects', 'effect_list'):
			return True, compEffect.GetLoadEffects(), None
		if key in ('item', 'items'):
			return self._get_status_all_player_items(entity_id)
		if key in ('held_item', 'carried_item', 'mainhand_item'):
			return self._get_status_item_value(entity_id, 'carried')
		if key == 'offhand_item':
			return self._get_status_item_value(entity_id, 'offhand')
		if key in ('inventory', 'inventory_items'):
			return self._get_status_item_value(entity_id, 'inventory')
		if key in ('armor_items', 'armor_inventory'):
			return self._get_status_item_value(entity_id, 'armor')
		if key in ('nbt', 'entity_nbt'):
			return True, CF.CreateEntityDefinitions(entity_id).GetEntityNBTTags(), None
		if key in ('extra', 'extra_data'):
			return True, CF.CreateExtraData(entity_id).GetWholeExtraData(), None
		if key in ('components', 'component'):
			return True, CF.CreateEntityComponent(entity_id).GetAllComponentsName(), None
		if key in ('alive', 'is_alive'):
			return True, compGame.IsEntityAlive(entity_id), None
		if key in GET_STATUS_SIMPLE_ENTITY_READERS:
			return self._get_status_simple_entity_value(entity_id, key)
		if key in ('on_fire', 'is_on_fire'):
			return True, CF.CreateAttr(entity_id).IsEntityOnFire(), None
		if key == 'step_height':
			return True, CF.CreateAttr(entity_id).GetStepHeight(), None
		if key in ('air', 'air_current', 'current_air'):
			return True, CF.CreateBreath(entity_id).GetCurrentAirSupply(), None
		if key in ('max_air', 'air_max'):
			return True, CF.CreateBreath(entity_id).GetMaxAirSupply(), None
		if key in ('motions', 'entity_motions'):
			motion = CF.CreateActorMotion(entity_id)
			return True, motion.GetPlayerMotions() if is_player else motion.GetEntityMotions(), None
		if key in ('properties', 'property'):
			return True, CF.CreateQueryVariable(entity_id).GetAllProperties(), None

		is_max = key.startswith('max_')
		attr_name = key[4:] if is_max else key
		if attr_name in STATUS_ATTRS:
			compAttr = CF.CreateAttr(entity_id)
			attr_type = STATUS_ATTRS[attr_name]
			return True, compAttr.GetAttrMaxValue(attr_type) if is_max else compAttr.GetAttrValue(attr_type), None

		if is_player:
			compPlayer = CF.CreatePlayer(entity_id)
			compFly = CF.CreateFly(entity_id)
			compExp = CF.CreateExp(entity_id)
			compItem = CF.CreateItem(entity_id)
			compLv = CF.CreateLv(entity_id)
			if key == 'enchantment_seed':
				return True, compPlayer.GetEnchantmentSeed(), None
			if key in ('interact_center_offset', 'interaction_center_offset'):
				return True, compPlayer.GetInteracteCenterOffset(), None
			if key in ('nearby_players', 'relevant_players'):
				return True, compPlayer.GetRelevantPlayer(None), None
			if key in ('can_fly', 'canfly', 'fly', 'is_player_can_fly'):
				return True, compFly.IsPlayerCanFly(), None
			if key in ('is_flying', 'flying', 'isflying'):
				return True, compFly.IsPlayerFlying(), None
			if key in ('xp', 'exp', 'experience'):
				return True, compExp.GetPlayerExp(False), None
			if key in ('xp_percent', 'exp_percent', 'experience_percent'):
				return True, compExp.GetPlayerExp(True), None
			if key in ('total_xp', 'total_exp', 'total_experience'):
				return True, compExp.GetPlayerTotalExp(), None
			if key in ('level', 'xp_level', 'experience_level'):
				return True, compLv.GetPlayerLevel(), None
			if key == 'hunger':
				return True, compPlayer.GetPlayerHunger(), None
			if key in ('exhaustion', 'current_exhaustion'):
				return True, compPlayer.GetPlayerCurrentExhaustionValue(), None
			if key == 'max_exhaustion':
				return True, compPlayer.GetPlayerMaxExhaustionValue(), None
			if key in ('health_level', 'natural_regen_level'):
				return True, compPlayer.GetPlayerHealthLevel(), None
			if key in ('starve_level', 'natural_starve_level'):
				return True, compPlayer.GetPlayerStarveLevel(), None
			if key in ('health_tick', 'natural_regen_tick'):
				return True, compPlayer.GetPlayerHealthTick(), None
			if key in ('starve_tick', 'natural_starve_tick'):
				return True, compPlayer.GetPlayerStarveTick(), None
			if key in ('natural_regen', 'is_natural_regen'):
				return True, compPlayer.IsPlayerNaturalRegen(), None
			if key in ('natural_starve', 'is_natural_starve'):
				return True, compPlayer.IsPlayerNaturalStarve(), None
			if key in ('abilities', 'ability'):
				return True, compPlayer.GetPlayerAbilities(), None
			if key in ('operation', 'permission'):
				return True, compPlayer.GetPlayerOperation(), None
			if key in ('sneaking', 'is_sneaking'):
				return True, compPlayer.isSneaking(), None
			if key in ('swimming', 'is_swimming'):
				return True, compPlayer.isSwimming(), None
			if key in ('blocking', 'is_blocking'):
				return True, compPlayer.GetIsBlocking(), None
			if key in ('fishing', 'is_fishing'):
				return True, compPlayer.GetPlayerIsFishing(), None
			if key in ('interact_range', 'interacte_range'):
				return True, compPlayer.GetPlayerInteracteRange(), None
			if key in ('respawn_pos', 'respawn_position'):
				return True, compPlayer.GetPlayerRespawnPos(), None
			if key in ('game_type', 'gametype'):
				return True, compGame.GetPlayerGameType(entity_id), None

		if key == 'all':
			compAttr = CF.CreateAttr(entity_id)
			attributes = {}
			for attr_name, attr_type in STATUS_ATTRS.items():
				try:
					attributes[attr_name] = compAttr.GetAttrValue(attr_type)
					attributes['max_' + attr_name] = compAttr.GetAttrMaxValue(attr_type)
				except Exception:
					pass
			breath = CF.CreateBreath(entity_id)
			motion = CF.CreateActorMotion(entity_id)
			simple_states = {}
			for state_name in GET_STATUS_SIMPLE_ENTITY_READERS:
				try:
					simple_states[state_name] = self._get_status_simple_entity_value(entity_id, state_name)[1]
				except Exception:
					# 某些状态只适用于特定实体（例如驴的 chest、玩家的选中槽）。
					pass
			result = {
				'id': entity_id, 'name': CF.CreateName(entity_id).GetName(),
				'type': CF.CreateEngineType(entity_id).GetEngineTypeStr(),
				'pos': CF.CreatePos(entity_id).GetPos(), 'foot_pos': CF.CreatePos(entity_id).GetFootPos(),
				'rot': CF.CreateRot(entity_id).GetRot(), 'motion': motion.GetMotion(),
				'dimension': CF.CreateDimension(entity_id).GetEntityDimensionId(),
				'tags': CF.CreateTag(entity_id).GetEntityTags(), 'attributes': attributes,
				'properties': CF.CreateQueryVariable(entity_id).GetAllProperties(),
				'effects': CF.CreateEffect(entity_id).GetAllEffects() or [],
				'loaded_effects': CF.CreateEffect(entity_id).GetLoadEffects(),
				'air': {'current': breath.GetCurrentAirSupply(), 'max': breath.GetMaxAirSupply()},
				'nbt': CF.CreateEntityDefinitions(entity_id).GetEntityNBTTags(),
				'extra': CF.CreateExtraData(entity_id).GetWholeExtraData(),
				'components': CF.CreateEntityComponent(entity_id).GetAllComponentsName(),
				'motions': motion.GetPlayerMotions() if is_player else motion.GetEntityMotions(),
				'entity_states': simple_states,
				'extern': self._get_status_extern_value(entity_id)[1],
			}
			if is_player:
				result['player'] = {
					'name': CF.CreateName(entity_id).GetName(), 
					'xp': compExp.GetPlayerExp(False),
					'total_xp': compExp.GetPlayerTotalExp(),
					'level': compLv.GetPlayerLevel(),
					'hunger': compPlayer.GetPlayerHunger(),
					'exhaustion': compPlayer.GetPlayerCurrentExhaustionValue(),
					'max_exhaustion': compPlayer.GetPlayerMaxExhaustionValue(),
					'abilities': compPlayer.GetPlayerAbilities(),
					'can_fly': compFly.IsPlayerCanFly(),
					'is_flying': compFly.IsPlayerFlying(),
					'health_level': compPlayer.GetPlayerHealthLevel(), 'starve_level': compPlayer.GetPlayerStarveLevel(),
					'health_tick': compPlayer.GetPlayerHealthTick(), 'starve_tick': compPlayer.GetPlayerStarveTick(),
					'natural_regen': compPlayer.IsPlayerNaturalRegen(), 'natural_starve': compPlayer.IsPlayerNaturalStarve(),
					'game_type': compGame.GetPlayerGameType(entity_id),
					'operation': compPlayer.GetPlayerOperation(),
					'sneaking': compPlayer.isSneaking(),
					'swimming': compPlayer.isSwimming(),
					'blocking': compPlayer.GetIsBlocking(),
					'fishing': compPlayer.GetPlayerIsFishing(),
					'interact_range': compPlayer.GetPlayerInteracteRange(),
					'respawn_position': compPlayer.GetPlayerRespawnPos(),
					'enchantment_seed': compPlayer.GetEnchantmentSeed(),
					'interact_center_offset': compPlayer.GetInteracteCenterOffset(),
					'nearby_players': compPlayer.GetRelevantPlayer(None),
					'items': self._get_status_all_player_items(entity_id)[1],
					'selected_slot': compItem.GetSelectSlotId(),
					'all_enchants': compItem.GetAllEnchantsInfo(),
					'fish_hook': compItem.GetPlayerFishHookEntity(),
				}
			return True, result, None

		# query.* / variable.* 保持交给 Molang；普通算术表达式走白名单 AST，
		# 因而支持 sqrt(velocity.x * velocity.x) 以及位运算、比较和逻辑运算。
		if key.startswith(('query.', 'variable.', 'temp.')) or '&&' in status or '||' in status or re.search(r'!(?!=)', status):
			evaluated = CF.CreateQueryVariable(entity_id).EvalMolangExpression(status)
			if not isinstance(evaluated, dict):
				return False, None, 'Molang 求值没有返回结果'
			if evaluated.get('error'):
				return False, None, 'Molang 错误: %s' % evaluated.get('error')
			if 'value' not in evaluated:
				return False, None, 'Molang 结果中不存在 value'
			return True, evaluated['value'], None
		if key.startswith('math.'):
			return self._get_status_math_value(entity_id, status.split('.', 1)[1])
		if is_math_expression:
			return self._get_status_math_value(entity_id, status)
		return False, None, '未知状态 %s；可使用直接状态名、query.*、Molang 表达式、all 或 event.<事件名>' % status

	def _get_status_truthy(self, value):
		if value is None or value is False or value == 0:
			return False
		if isinstance(value, str) and value.strip().lower() in ('', '0', 'false', 'none', 'null'):
			return False
		return True

	def _get_status_parse_value(self, value):
		"""将自定义命令的 str 参数转成 ModSDK setter 可用的基础类型。"""
		if not isinstance(value, str):
			return value
		raw = value.strip()
		lower = raw.lower()
		if lower in ('true', 'yes', 'on'):
			return True
		if lower in ('false', 'no', 'off'):
			return False
		if lower in ('null', 'none'):
			return None
		try:
			# 数组/对象/带引号字符串统一使用 JSON；如 [1,2,3]。
			if raw[:1] in ('[', '{', '"'):
				return json.loads(raw)
			if ',' in raw:
				return tuple(float(part.strip()) for part in raw.split(','))
			if '.' in raw or 'e' in lower:
				return float(raw)
			return int(raw)
		except (TypeError, ValueError):
			return value

	def _get_status_as_bool(self, value):
		if isinstance(value, str):
			lower = value.strip().lower()
			if lower in ('true', '1', 'yes', 'on'):
				return True
			if lower in ('false', '0', 'no', 'off', ''):
				return False
			return None
		if isinstance(value, (int, long, float)): #type: ignore
			return value != 0
		if isinstance(value, bool):
			return value
		return None

	def _get_status_vector_input(self, value, size, name):
		if not isinstance(value, (list, tuple)) or len(value) != size:
			return None, '%s 需要 %s 个数值，例如 %s' % (name, size, ','.join(['0'] * size))
		try:
			return tuple(float(item) for item in value), None
		except (TypeError, ValueError):
			return None, '%s 的每个分量必须是数值' % name

	def _set_status_vector(self, entity_id, root, field, value):
		base_status, fields = STATUS_VECTOR_ROOTS[root]
		if base_status == 'foot_xyz':
			return False, 'foot_position 是只读坐标；请设置 position'
		if base_status == 'xyz':
			component = CF.CreatePos(entity_id)
			current = component.GetPos()
			setter = component.SetPos
		elif base_status == 'rotxy':
			component = CF.CreateRot(entity_id)
			current = component.GetRot()
			setter = component.SetRot
		else:
			component = CF.CreateActorMotion(entity_id)
			current = component.GetMotion()
			setter = component.SetPlayerMotion if is_player(entity_id) else component.SetMotion

		size = len(current)
		if field is None:
			new_value, error = self._get_status_vector_input(value, size, root)
			if error:
				return False, error
		else:
			if field not in fields:
				return False, '%s 不存在分量 %s' % (root, field)
			try:
				new_item = float(value)
			except (TypeError, ValueError):
				return False, '%s.%s 必须为数值' % (root, field)
			new_value = list(current)
			new_value[fields[field]] = new_item
			new_value = tuple(new_value)
		result = setter(new_value)
		return (False, '%s 设置失败' % root) if result is False else (True, '%s 已设置为 %s' % (root, new_value))

	def _set_status_extra_path(self, entity_id, path, value):
		if len(path) < 2 or not path[1]:
			return False, 'extra 状态格式为 extra.<键>[.<嵌套键>]'
		extra = CF.CreateExtraData(entity_id)
		root_key = path[1]
		if len(path) == 2:
			extra.SetExtraData(root_key, value)
			return True, 'extra.%s 已设置' % root_key
		root_value = extra.GetExtraData(root_key)
		if not isinstance(root_value, dict):
			return False, 'extra.%s 不是字典，不能写入嵌套字段' % root_key
		container = root_value
		for key in path[2:-1]:
			if key not in container or not isinstance(container[key], dict):
				container[key] = {}
			container = container[key]
		container[path[-1]] = value
		extra.SetExtraData(root_key, root_value)
		return True, 'extra.%s 已设置' % '.'.join(path[1:])

	def _set_status_effect(self, entity_id, effect_name, value):
		"""effect.<名称>：0 删除；秒数或 duration,amplifier,particles 添加/刷新。"""
		effect = CF.CreateEffect(entity_id)
		if value is False or value == 0:
			result = effect.RemoveEffectFromEntity(effect_name)
			return (False, '状态效果 %s 删除失败' % effect_name) if result is False else (True, '状态效果 %s 已删除' % effect_name)
		duration, amplifier, particles = value, 0, True
		if isinstance(value, dict):
			duration = value.get('duration', value.get('duration_f'))
			amplifier = value.get('amplifier', 0)
			particles = value.get('showParticles', value.get('particles', True))
		elif isinstance(value, (list, tuple)):
			if len(value) not in (2, 3):
				return False, '效果值格式为 秒数,等级[,粒子]，例如 30,1,1'
			duration, amplifier = value[0], value[1]
			if len(value) == 3:
				particles = value[2]
		try:
			duration = float(duration)
			amplifier = int(amplifier)
		except (TypeError, ValueError):
			return False, '效果持续时间和等级必须为数值'
		particles = self._get_status_as_bool(particles)
		if duration <= 0 or amplifier < 0 or amplifier > 255 or particles is None:
			return False, '效果要求持续时间大于 0、等级 0~255、粒子为 bool'
		result = effect.AddEffectToEntity(effect_name, duration, amplifier, particles)
		return (False, '状态效果 %s 设置失败' % effect_name) if result is False else (True, '状态效果 %s 已设置' % effect_name)

	def _set_status_item_path(self, entity_id, raw_path, value):
		if not is_player(entity_id):
			return False, 'item.* 仅支持玩家'
		if len(raw_path) < 2 or raw_path[1].lower() not in ITEM_POSITIONS:
			return False, '物品状态格式为 item.<carried|offhand|inventory|armor>[.<槽位>][.<字段>]'
		position_name = raw_path[1].lower()
		pos_type = ITEM_POSITIONS[position_name]
		path = raw_path[2:]
		if pos_type in (0, 3):
			if not path or not path[0].isdigit():
				return False, '%s 需要槽位，例如 item.%s.0.count' % (position_name, position_name)
			slot = int(path[0])
			path = path[1:]
		else:
			slot = 0
		item_comp = CF.CreateItem(entity_id)
		if path and path[0] == 'durability':
			try:
				result = item_comp.SetItemDurability(pos_type, slot, int(value))
			except (TypeError, ValueError):
				return False, 'durability 必须为整数'
			return (False, '物品耐久设置失败') if result is False else (True, '物品耐久已设置')
		if path and path[0] in ('max_durability', 'maxDurability'):
			try:
				result = item_comp.SetItemMaxDurability(pos_type, slot, int(value), True)
			except (TypeError, ValueError):
				return False, 'max_durability 必须为整数'
			return (False, '物品最大耐久设置失败') if result is False else (True, '物品最大耐久已设置')
		if not path:
			item_data = value
			if item_data is not None and not isinstance(item_data, dict):
				return False, '替换物品需要 JSON 物品字典或 null'
		else:
			item_data = item_comp.GetPlayerItem(pos_type, slot, True)
			if not isinstance(item_data, dict):
				return False, '目标槽没有物品，不能设置其字段'
			container = item_data
			for key in path[:-1]:
				if key not in container or not isinstance(container[key], dict):
					container[key] = {}
				container = container[key]
			container[path[-1]] = value
		result = item_comp.SetEntityItem(pos_type, item_data, slot)
		return (False, '物品设置失败') if result is False else (True, 'item.%s 已设置' % '.'.join(raw_path[1:]))

	def _set_status_server_value(self, entity_id, status, value):
		"""设置有 ModSDK 写接口的状态。只读 query、事件和 NBT 会明确拒绝。"""
		if not status:
			return False, '状态不能为空'
		status = status.strip() if isinstance(status, str) else str(status).strip()
		key = status.lower()
		value = self._get_status_parse_value(value)
		path = key.split('.')
		raw_path = status.split('.')
		root = path[0]

		if root in ('effect', 'effects'):
			if len(path) != 2 or not raw_path[1]:
				return False, '效果状态格式为 effect.<效果名>'
			return self._set_status_effect(entity_id, raw_path[1], value)
		if root in ('item', 'items'):
			return self._set_status_item_path(entity_id, raw_path, value)
		if root in STATUS_VECTOR_ROOTS:
			if len(path) > 2:
				return False, '%s 只支持一个分量，例如 %s.x' % (root, root)
			return self._set_status_vector(entity_id, root, path[1] if len(path) == 2 else None, value)
		if root in ('extra', 'extra_data'):
			return self._set_status_extra_path(entity_id, raw_path, value)
		if root in ('mod', 'mod_attr', 'modattr'):
			if len(raw_path) != 2 or not raw_path[1]:
				return False, 'mod 状态格式为 mod.<键>'
			CF.CreateModAttr(entity_id).SetAttr(raw_path[1], value, False, True)
			return True, 'mod.%s 已设置' % raw_path[1]
		if root in ('attribute', 'attributes'):
			if len(path) != 2:
				return False, 'attributes 状态格式为 attributes.<属性名>'
			key = path[1]
			path = [key]
			root = key
		elif root == 'player':
			if len(path) != 2:
				return False, 'player 状态格式为 player.<状态名>'
			key = path[1]
			path = [key]
			root = key
		elif root == 'air':
			if len(path) != 2 or path[1] not in ('current', 'value', 'max'):
				return False, 'air 状态格式为 air.current 或 air.max'
			key = 'air' if path[1] in ('current', 'value') else 'max_air'
			path = [key]
			root = key
		elif root in ('ability', 'abilities'):
			if len(path) != 2:
				return False, 'abilities 状态格式为 abilities.<能力名>'
			key = ABILITY_ALIASES.get(path[1], path[1])
			path = [key]
			root = key
		if root in ('tag', 'tags'):
			if len(path) != 2 or not path[1]:
				return False, '标签状态格式为 tag.<标签名>'
			bool_value = self._get_status_as_bool(value)
			if bool_value is None:
				return False, 'tag.<标签名> 的值必须为 bool，1 为 true、0 为 false'
			tag_name = raw_path[1]
			tag = CF.CreateTag(entity_id)
			if bool_value:
				tag.AddEntityTag(tag_name)
			else:
				tag.RemoveEntityTag(tag_name)
			return True, '标签 %s 已%s' % (tag_name, '添加' if bool_value else '删除')
		if key in ('name', 'entity_name'):
			CF.CreateName(entity_id).SetName(value if isinstance(value, str) else str(value))
			return True, '名称已设置为 %s' % value
		if key == 'step_height':
			try:
				result = CF.CreateAttr(entity_id).SetStepHeight(float(value))
			except (TypeError, ValueError):
				return False, 'step_height 必须为数值'
			return (False, 'step_height 设置失败') if result is False else (True, 'step_height 已设置')
		if key in ('air', 'air_current', 'current_air'):
			try:
				result = CF.CreateBreath(entity_id).SetCurrentAirSupply(int(value))
			except (TypeError, ValueError):
				return False, 'air 必须为整数'
			return (False, 'air 设置失败') if result is False else (True, 'air 已设置')
		if key in ('max_air', 'air_max'):
			try:
				result = CF.CreateBreath(entity_id).SetMaxAirSupply(int(value))
			except (TypeError, ValueError):
				return False, 'max_air 必须为整数'
			return (False, 'max_air 设置失败') if result is False else (True, 'max_air 已设置')
		if key in SIMPLE_ENTITY_BOOL_SETTERS:
			converted = self._get_status_as_bool(value)
			if converted is None:
				return False, '%s 必须为 bool，1 为 true、0 为 false' % key
			factory_name, method_name = SIMPLE_ENTITY_BOOL_SETTERS[key]
			result = getattr(getattr(CF, factory_name)(entity_id), method_name)(converted)
			return (False, '%s 设置失败' % key) if result is False else (True, '%s 已设置' % key)
		if key == 'ai_blocked':
			converted = self._get_status_as_bool(value)
			if converted is None:
				return False, 'ai_blocked 必须为 bool，1 为 true、0 为 false'
			result = CF.CreateControlAi(entity_id).SetBlockControlAi(converted, False)
			return (False, 'ai_blocked 设置失败') if result is False else (True, 'ai_blocked 已设置')
		if key in ('gravity', 'jump_power', 'entity_scale', 'orb_experience'):
			try:
				converted = float(value) if key != 'orb_experience' else int(value)
			except (TypeError, ValueError):
				return False, '%s 必须为数值' % key
			if key == 'gravity':
				result = CF.CreateGravity(entity_id).SetGravity(converted)
			elif key == 'jump_power':
				result = CF.CreateGravity(entity_id).SetJumpPower(converted)
			elif key == 'entity_scale':
				result = CF.CreateScale(entity_id).SetEntityScale(entity_id, converted)
			else:
				result = CF.CreateExp(entity_id).SetOrbExperience(converted)
			return (False, '%s 设置失败' % key) if result is False or result == -1 else (True, '%s 已设置' % key)

		is_player = is_player(entity_id)
		if is_player:
			player = CF.CreatePlayer(entity_id)
			if key == 'hunger':
				try:
					result = player.SetPlayerHunger(int(value))
				except (TypeError, ValueError):
					return False, 'hunger 必须为整数'
				return (False, 'hunger 设置失败') if result is False else (True, 'hunger 已设置')
			if key == 'enchantment_seed':
				try:
					result = player.SetEnchantmentSeed(int(value))
				except (TypeError, ValueError):
					return False, 'enchantment_seed 必须为整数'
				return (False, 'enchantment_seed 设置失败') if result is False else (True, 'enchantment_seed 已设置')
			setting = STATUS_PLAYER_SETTERS.get(key)
			if setting:
				method_name, value_type = setting
				if value_type == 'bool':
					converted = self._get_status_as_bool(value)
					if converted is None:
						return False, '%s 必须为 bool，1 为 true、0 为 false' % key
				elif value_type == 'integer':
					try:
						converted = int(value)
					except (TypeError, ValueError):
						return False, '%s 必须为整数' % key
				else:
					try:
						converted = float(value)
					except (TypeError, ValueError):
						return False, '%s 必须为数值' % key
				result = getattr(player, method_name)(converted)
				return (False, '%s 设置失败' % key) if result is False else (True, '%s 已设置为 %s' % (key, converted))
			if key in ('can_fly', 'canfly', 'fly', 'is_player_can_fly'):
				converted = self._get_status_as_bool(value)
				if converted is None:
					return False, 'can_fly 必须为 bool，1 为 true、0 为 false'
				result = CF.CreateFly(entity_id).ChangePlayerFlyState(converted, False)
				return (False, 'can_fly 设置失败') if result is False else (True, 'can_fly 已设置')
			if key in ('is_flying', 'flying', 'isflying'):
				converted = self._get_status_as_bool(value)
				if converted is None:
					return False, 'is_flying 必须为 bool，1 为 true、0 为 false'
				# 保留飞行能力，仅切换当前是否进入飞行状态。
				result = CF.CreateFly(entity_id).ChangePlayerFlyState(True, converted)
				return (False, 'is_flying 设置失败') if result is False else (True, 'is_flying 已设置')

		is_max = key.startswith('max_')
		attr_name = key[4:] if is_max else key
		if attr_name in STATUS_ATTRS:
			try:
				converted = float(value)
			except (TypeError, ValueError):
				return False, '%s 必须为数值' % key
			attr = CF.CreateAttr(entity_id)
			result = attr.SetAttrMaxValue(STATUS_ATTRS[attr_name], converted) if is_max else attr.SetAttrValue(STATUS_ATTRS[attr_name], converted, 0)
			return (False, '%s 设置失败' % key) if result is False else (True, '%s 已设置为 %s' % (key, converted))
		if key == 'extern' or key == 'extern.all' or key in STATUS_EXTERN_NAMES or key.startswith('extern.'):
			return False, 'extern.* 是只读派生状态'
		if key.startswith(('query.', 'variable.', 'temp.', 'math.', 'event.', 'server_event.')) or key in ('nbt', 'entity_nbt', 'all', 'components', 'properties'):
			return False, '%s 是只读状态' % status
		return False, '未知或不可写状态 %s；可设置 position、rotation、velocity、属性、玩家设置、tag.<标签>、extra.<键>' % status

	def _get_status_display_value(self, value):
		try:
			text = json.dumps(value, ensure_ascii=False, sort_keys=True)
		except (TypeError, ValueError):
			text = repr(value)
		return text if len(text) <= 1024 else text[:1021] + '...'

	def _get_status_apply_output(self, entity_id, value, output):
		if output['kind'] == 'totag':
			tag_comp = CF.CreateTag(entity_id)
			if self._get_status_truthy(value):
				tag_comp.AddEntityTag(output['tag'])
				return True, 'tag %s 已添加' % output['tag']
			if output['remove_false']:
				tag_comp.RemoveEntityTag(output['tag'])
				return True, 'tag %s 已删除' % output['tag']
			return True, '结果为 false，tag %s 保持不变' % output['tag']

		if not isinstance(value, (int, long, float)): #type: ignore
			return False, '积分榜输出要求数值，当前结果为 %s' % self._get_status_display_value(value)
		try:
			score = int(round(float(value) * output['scale']))
		except (TypeError, ValueError, OverflowError):
			return False, 'scale 后的积分榜结果无效'
		mode = output['mode']
		if score < 0 and mode in ('add', 'remove'):
			mode = 'remove' if mode == 'add' else 'add'
			score = -score
		command = '/scoreboard players %s @s %s %s' % (mode, output['objective'], score)
		if not compCmd.SetCommand(command, entity_id, False):
			return False, '积分榜写入失败: %s' % output['objective']
		return True, '积分榜 %s %s %s' % (output['objective'], mode, score)

	def _get_status_cleanup_expired(self):
		deadline = time.time() - STATUS_PENDING_TTL
		for request_id, request in list(self._status_pending_clients.items()):
			if request['created_at'] < deadline:
				del self._status_pending_clients[request_id]

	def _get_status_notify_origin(self, player_id, message, color='§a'):
		if player_id:
			CF.CreateMsg(player_id).NotifyOneMessage(player_id, message, color)

	def OnGetStatusClientResponse(self, args):
		request_id = args.get('requestId')
		request = self._status_pending_clients.get(request_id)
		if request is None:
			return
		if args.get('__id__') != request['entity_id']:
			return
		del self._status_pending_clients[request_id]
		if args.get('error'):
			self._get_status_notify_origin(request['origin'], '客户端状态失败: %s' % args['error'], '§c')
			return
		value = args.get('value')
		if request['output'] is None:
			self._get_status_notify_origin(request['origin'], '%s = %s' % (request['name'], self._get_status_display_value(value)))
			return
		success, message = self._get_status_apply_output(request['entity_id'], value, request['output'])
		self._get_status_notify_origin(request['origin'], '%s: %s (结果=%s)' % (request['name'], message, self._get_status_display_value(value)), '§a' if success else '§c')

	def get_status(self, cmdargs, playerId, variant, data):
		targets = cmdargs[0]
		if targets is None:
			return True, '没有与选择器匹配的目标'
		status = cmdargs[1]
		output = None
		if cmdargs[2] == 'toscore':
			if not cmdargs[3]:
				return True, '计分板目标名不能为空'
			if not self._get_status_valid_scoreboard_objective(cmdargs[3]):
				return True, '积分榜目标名无效'
			try:
				objects = compGame.GetAllScoreboardObjects() or []
			except:
				objects = []
			if not any(isinstance(item, dict) and item.get('name') == cmdargs[3] for item in objects):
				return True, '积分榜目标不存在: %s' % cmdargs[3]
			output = {'kind': 'toscore', 'objective': cmdargs[3], 'mode': cmdargs[4], 'scale': cmdargs[5]}
		elif cmdargs[2] == 'totag':
			if not cmdargs[3]:
				return True, '标签名不能为空'
			output = {'kind': 'totag', 'tag': cmdargs[3], 'remove_false': cmdargs[4]}

		self._get_status_cleanup_expired()
		messages = []
		client_requests = 0
		for entity_id in targets:
			name = CF.CreateName(entity_id).GetName() or entity_id
			if str(status).lower().startswith('client.'):
				if not is_player(entity_id):
					messages.append('%s: client.* 仅支持玩家' % name)
					continue
				if len(self._status_pending_clients) >= STATUS_MAX_PENDING_CLIENT_REQUESTS:
					messages.append('%s: 客户端请求队列已满' % name)
					continue
				self._status_request_sequence += 1
				request_id = '%s:%s' % (entity_id, self._status_request_sequence)
				self._status_pending_clients[request_id] = {'entity_id': entity_id, 'origin': playerId, 'output': output, 'name': name, 'created_at': time.time()}
				self.NotifyToClient(entity_id, 'GetStatusClientRequest', {'requestId': request_id, 'status': str(status)[7:]})
				client_requests += 1
				continue
			try:
				found, value, error = self._get_status_server_value(entity_id, status)
			except Exception:
				found, value, error = False, None, '读取失败: %s' % traceback.format_exc().splitlines()[-1]
			if not found:
				messages.append('%s: %s' % (name, error))
				continue
			if output is None:
				messages.append('%s = %s' % (name, self._get_status_display_value(value)))
			else:
				success, message = self._get_status_apply_output(entity_id, value, output)
				messages.append('%s: %s (结果=%s)' % (name, message, self._get_status_display_value(value)))
		if client_requests:
			messages.append('已向 %s 个客户端请求状态，结果会异步返回' % client_requests)
		if not messages:
			return True, '没有可处理的目标'
		shown = messages[:24]
		if len(messages) > len(shown):
			shown.append('...%s 条结果已省略' % (len(messages) - len(shown)))
		return False, '; '.join(shown)

	def set_status(self, cmdargs, playerId, variant, data):
		"""通用状态写入；normal 为手动值，toscore 从实体计分板取值。"""
		if not cmdargs[0]:
			return True, '没有与选择器匹配的目标'
		targets, status = cmdargs[0], cmdargs[1]

		if variant == 0:
			value = cmdargs[2]
		elif variant == 1:
			if not cmdargs[3]:
				return True, '计分板名称不能为空'
			score_objective = str(cmdargs[3])
			score_holders = cmdargs[4]

			if not self._get_status_valid_scoreboard_objective(score_objective):
				return True, '积分榜目标名无效'
			try:
				objects = compGame.GetAllScoreboardObjects() or []
			except Exception:
				objects = []
			if not any(isinstance(item, dict) and item.get('name') == score_objective for item in objects):
				return True, '计分项不存在: %s' % score_objective
		messages = []
		success_count = 0
		for index, entity_id in enumerate(targets):
			name = CF.CreateName(entity_id).GetName() or entity_id
			write_value = value
			if variant == 1:
				holder_id = entity_id
				if score_holders:
					if len(score_holders) == 1:
						holder_id = score_holders[0]
					elif len(score_holders) == len(targets):
						holder_id = score_holders[index]
					else:
						messages.append('%s: toscore 实体数量必须为 1 或与目标数量相同' % name)
						continue
				found, write_value, error = self._get_status_score_value(entity_id, score_objective, holder_id)
				if not found:
					messages.append('%s: %s' % (name, error))
					continue
			try:
				success, message = self._set_status_server_value(entity_id, status, write_value)
			except Exception:
				success, message = False, '设置失败: %s' % traceback.format_exc().splitlines()[-1]
			if success:
				success_count += 1
			if variant == 1 and success:
				message = '%s（读取 %s=%s）' % (message, score_objective, write_value)
			messages.append('%s: %s' % (name, message))
		shown = messages[:24]
		if len(messages) > len(shown):
			shown.append('其余 %s 条结果已省略' % (len(messages) - len(shown)))
		return success_count == 0, '; '.join(shown)

	def setentityonfire(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateAttr(i).SetEntityOnFire(cmdargs[1], cmdargs[2])
		return False, '已点燃 %s 个实体 %s 秒,伤害为 %s' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setcurrentairsupply(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateBreath(i).SetCurrentAirSupply(cmdargs[1])
		return False, '已设置 %s 个实体氧气储备值为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setcompasstarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		x, y, z = cmdargs[1]
		compassdata = [intg(x), int(y), intg(z)]
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcompasstarget', 'cmdargs': compassdata})
		return False, '将以下玩家的指南针指向 Pos%s:%s' % (str(tuple(compassdata)), create_players_str(cmdargs[0]))

	def setcompassentity(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcompassentity', 'cmdargs': cmdargs})
		return False, '将以下玩家的指南针指向 %s:%s' % (CF.CreateEngineType(cmdargs[1][0]).GetEngineTypeStr(), create_players_str(cmdargs[0]))
		
	def setcolor(self, cmdargs, playerId, variant, data):
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[1]):
			return True, '选择器必须为玩家类型'
		if variant == 3:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolortint', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色调为 %s(%s,%s,%s):%s' % (cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5], create_players_str(cmdargs[1]))
		elif variant == 2:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorsaturation', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩饱和度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
		elif variant == 1:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorcontrast', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩对比度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
		else:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setcolorbrightness', 'cmdargs': cmdargs})
			return False, '已设置以下玩家的屏幕色彩亮度为 %s:%s' % (cmdargs[2], create_players_str(cmdargs[1]))
	
	def setchestitemnum(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if CF.CreateChestBlock(levelId).SetChestBoxItemNum(None, xyz, cmdargs[1], cmdargs[2], cmdargs[3]['id']):
			return False, '已设置槽位 %s 的物品数量为 %s' % (cmdargs[1], cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是箱子' % (xyz,)
	
	def setchestitemexchange(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if playerId is None:
			pid = serverApi.GetPlayerList()[random.randint(0, len(serverApi.GetPlayerList())-1)]
		else:
			pid = playerId #尽可能让命令在同维度执行
		if CF.CreateChestBlock(pid).SetChestBoxItemExchange(pid, xyz, cmdargs[1], cmdargs[2]):
			return False, '已交换槽位 %s 与槽位 %s 的物品' % (cmdargs[1], cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是箱子' % (xyz,)
	
	def setcanpausescreen(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setcanpausescreen', 'cmdargs': cmdargs})
		return False, '已将 %s 的暂停权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setcanotherplayerride(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateRide(i).SetCanOtherPlayerRide(i, cmdargs[1])
		return False, '已%s %s 个实体被骑乘' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def setattackplayersability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetAttackPlayersAbility(cmdargs[1])
		return False, '已将 %s 的pvp权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setattackmobsability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetAttackMobsAbility(cmdargs[1])
		return False, '已将 %s 的攻击生物权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setattackdamage(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			itemDict = compItem.GetPlayerItem(2, 0, True)
			if compItem.SetAttackDamage(itemDict, cmdargs[1]):
				compItem.SpawnItemToPlayerCarried(itemDict, i)
		return False, '已将 %s 的手持物品攻击伤害设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setspawnpoint(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[0][0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[0] == "null(can't replace to null, will be a bug)":
			cmdargs[0] = playerId, #','用来创建tuple
		if cmdargs[1] is None:
			cmdargs[1] = data['origin']['blockPos']
		x, y, z = cmdargs[1]
		if cmdargs[2] is None:
			cmdargs[2] = {'name': data['origin']['dimension'], 'id': data['origin']['dimension']}
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerRespawnPos((intg(x), int(y), intg(z)), cmdargs[2]['id'])
		return False, '将 %s 的重生点设置为 %s in %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2]['name'])
	
	def setplayerhealthlevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0 :#or cmdargs[1] > 20:
			return True, '无效的回血临界值 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的回血临界值 (%s > 20)' % cmdargs[1]
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerHealthLevel(cmdargs[1])
		return False, '将 %s 的回血临界值设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerstarvelevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0:
			return True, '无效的扣血临界值 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的扣血临界值 (%s > 20)' % cmdargs[1]
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerStarveLevel(cmdargs[1])
		return False, '将 %s 的扣血临界值设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerhunger(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0 :
			return True, '无效的饥饿度 (%s < 0)' % cmdargs[1]
		elif cmdargs[1] > 20:
			return True, '无效的饥饿度 (%s > 20)' % cmdargs[1]
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerHunger(cmdargs[1])
		return False, '将 %s 的饥饿度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerattackspeedamplifier(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] < 0.5:
			return True, '无效的倍率 (%s < 0.5)' % cmdargs[1]
		elif cmdargs[1] > 2.0:
			return True, '无效的倍率 (%s > 2.0)' % cmdargs[1]
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerAttackSpeedAmplifier(cmdargs[1])
		return False, '将 %s 的攻击速度倍率设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerjumpable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerJumpable(cmdargs[1])
		return False, '将 %s 的跳跃权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayermovable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerMovable(cmdargs[1])
		return False, '将 %s 个玩家的移动权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayernaturalstarve(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerNaturalStarve(cmdargs[1])
		return False, '将 %s 的饥饿掉血设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setplayerprefixandsuffixname(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateName(i).SetPlayerPrefixAndSuffixName(cmdargs[1], '§f', cmdargs[2], '§f')
		return False, '将 %s 的前缀设置为 %s, 后缀设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setplayermaxexhaustionvalue(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerMaxExhaustionValue(cmdargs[1])
		return False, '将 %s 的饥饿最大消耗度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setplayerhealthtick(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerHealthTick(cmdargs[1])
		return False, '将 %s 的自然回血速度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setplayerstarvetick(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerStarveTick(cmdargs[1])
		return False, '将 %s 的自然扣血速度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def sethurtcd(self, cmdargs, playerId, variant, data):
		if compGame.SetHurtCD(cmdargs[0]):
			return False, '将全局受击间隔设置为 %s' % (cmdargs[0])
		else:
			return True, '设置失败'
	
	def setattacktarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		attackTargetId = cmdargs[1][0]
		for i in cmdargs[0]:
			CF.CreateAction(i).SetAttackTarget(attackTargetId)
		return False, '将 %s 个实体的仇恨目标设置为 %s' % (len(cmdargs[0]), CF.CreateEngineType(attackTargetId).GetEngineTypeStr())
	
	def resetattacktarget(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateAction(i).ResetAttackTarget()
		return False, '成功重置 %s 个实体的仇恨目标' % (len(cmdargs[0]))
	
	def setbanplayerfishing(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetBanPlayerFishing(cmdargs[1])
		return False, '将 %s 的钓鱼权限设置为 %s' % (create_players_str(cmdargs[0]), '禁止' if cmdargs[1] else '允许')
	
	def setactorcanpush(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateActorPushable(i).SetActorPushable(cmdargs[1])
		return False, '已%s %s个 实体被推动' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def	setactorcollidable(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateActorCollidable(i).SetActorCollidable(cmdargs[1])
		return False, '已%s %s 实体拥有固体碰撞箱' % ('允许' if cmdargs[1] else '禁止', len(cmdargs[0]))
	
	def setmineability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetMineAbility(cmdargs[1])
		return False, '将 %s 的挖掘权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setbuildability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetBuildAbility(cmdargs[1])
		return False, '将 %s 的放置权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setcontrol(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateRide(i).SetControl(i, cmdargs[1])
		return False, '已设置 %s 个实体的控制权' % (len(cmdargs[0]))
	
	def setpickuparea(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPickUpArea(cmdargs[1])
		return False, '已将 %s 的拾取范围设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setlevelgravity(self, cmdargs, playerId, variant, data):
		compGame.SetLevelGravity(cmdargs[0])
		return False , '已将世界重力设置为 %s' % (cmdargs[0])
	
	def setjumppower(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateGravity(i).SetJumpPower(cmdargs[1])
		return False, '已设置 %s 个实体的跳跃力度为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setgravity(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateGravity(i).SetGravity(cmdargs[1])
		return False, '已设置 %s 个实体的重力为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setworldspawnd(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		compGame.SetSpawnDimensionAndPosition(cmdargs[0]['id'], xyz)
		return False, '已设置世界出生点为 %s in %s' % (xyz, cmdargs[0]['name'])
		
	def playeruseitemtopos(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[2] not in [0, 1, 2, 3, 4, 5]:
			return True, '无效的朝向'
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).PlayerUseItemToPos(xyz, 2, 0, cmdargs[2])
		return False, '已尝试让 %s 向 %s 的 %s 面使用物品' % (create_players_str(cmdargs[0]), xyz, ['上', '下', '北', '南', '西', '东'][cmdargs[2]])
	
	def playeruseitemtoentity(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		entityId = cmdargs[1][0]
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).PlayerUseItemToEntity(entityId)
		return False, '已尝试让 %s 向 %s 使用物品' % (create_players_str(cmdargs[0]), CF.CreateEngineType(entityId).GetEngineTypeStr())
	
	def playerdestoryblock(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		x, y, z = cmdargs[1]
		xyz = (intg(x), int(y), intg(z))
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).PlayerDestoryBlock(xyz, cmdargs[2], cmdargs[3])
		return False, '已尝试让 %s 破坏 Pos%s 处的方块' % (create_players_str(cmdargs[0]), xyz)
	
	def openworkbench(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateBlockInfo(i).OpenWorkBench()
		return False, '已使 %s 打开工作台界面' % (create_players_str(cmdargs[0]))
	
	def openfoldgui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'openfoldgui', 'cmdargs': cmdargs})
		return False, '已使 %s 打开下拉界面' % (create_players_str(cmdargs[0]))
	
	def setimmunedamage(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateHurt(i).ImmuneDamage(cmdargs[1])
		return False, '将 %s 个实体的伤害免疫设置为 %s' % (len(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setinvitemexchange(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetInvItemExchange(cmdargs[1], cmdargs[2])
		return False, '已交换 %s 物品栏槽位 %s 与槽位 %s 中的物品' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setinvitemnum(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[2] < 0 or cmdargs[2] > 64:
			return True, '无效的物品数量'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetInvItemNum(cmdargs[1], cmdargs[2])
		return False, '已将 %s 物品栏槽位 %s 中的物品数量设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setitemdurability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True, '无效的耐久度'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetItemDurability(2, 0, cmdargs[1])
		return False, '已设置 %s 的手持物品物品耐久度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
			
	def setitemmaxdurability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0 or cmdargs[1] > 32766:
			return True, '无效的耐久度'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetItemMaxDurability(2, 0, cmdargs[1], True)
		return False, '已设置 %s 的手持物品最大耐久度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
		
	def setitemtierlevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[1] not in [0, 1, 2, 3, 4]:
			return True, '无效的挖掘等级'
		for i in cmdargs[0]:
			itemdata = CF.CreateItem(i).GetPlayerItem(2, 0, True)
			CF.CreateItem(i).SetItemTierLevel(itemdata, cmdargs[1])
			CF.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False, '已设置 %s 的手持物品挖掘等级为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setitemtierspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[1] < 0:
			return True, '无效的挖掘速度'
		for i in cmdargs[0]:
			itemdata = CF.CreateItem(i).GetPlayerItem(2, 0, True)
			CF.CreateItem(i).SetItemTierSpeed(itemdata, cmdargs[1])
			CF.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
		return False, '已设置 %s 的手持物品挖掘速度为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def setitemmaxstacksize(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[1] < 1:
			return True, '无效的堆叠数量 (%s < 1)' % (cmdargs[1])
		elif cmdargs[1] > 64:
			return True, '无效的堆叠数量 (%s > 64)' % (cmdargs[1])
		for i in cmdargs[0]:
			itemDict = CF.CreateItem(i).GetPlayerItem(2, 0, True)
			CF.CreateItem(i).SetMaxStackSize(itemDict, cmdargs[1])
			CF.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i)
		return False, '已设置 %s 的手持物品最大堆叠数量为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def playerexhaustionratio(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'	
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		exhaustion = {'heal': 0, 'jump':1, 'sprint_jump':2, 'mine':3, 'attack':4, 'global':9}
		exhaustiontype = exhaustion[cmdargs[1]]
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerExhaustionRatioByType(exhaustiontype, cmdargs[2])
		return False, '已设置 %s 的 %s 行为饥饿度消耗倍率为 %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def setsigntextstyle(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		rgba = (cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5])
		lighting = cmdargs[6]
		if compBlockEntity.SetSignTextStyle(xyz, cmdargs[1]['id'], rgba, lighting, int(cmdargs[7])):
			return False, '将 Pos%s in %s 的告示牌 %s 文本样式设置为 %s' % (xyz, cmdargs[1]['name'], '反面' if cmdargs[7] else '正面', rgba)
		else:
			return True, '位于 Pos%s in %s 的方块不是告示牌' % (xyz, cmdargs[1]['name'])
		
	def setsigntext(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if compBlockInfo.SetSignBlockText(xyz, cmdargs[1], cmdargs[2]['id'], int(cmdargs[3])):
			return False, '将 Pos%s in %s 的告示牌 %s 文本设置为 %s' % (xyz, cmdargs[2]['name'], '反面' if cmdargs[3] else '正面', cmdargs[1])
		else:
			return True, '位于 Pos%s in %s 的方块不是告示牌' % (xyz, cmdargs[2]['name'])

	def setplayerinteracterange(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetPlayerInteracteRange(cmdargs[1])
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'setplayerinteracterange', 'cmdargs': cmdargs})
		return False, '已设置 %s 的触及距离为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])
	
	def summonprojectile(self, cmdargs, playerId, variant, data):
		if not len(cmdargs[7]) == 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		
		for i in cmdargs[0]:
			param = {
				'position': cmdargs[2],
				'direction': cmdargs[3],
				'power': cmdargs[4],
				'gravity': cmdargs[5],
				'damage': cmdargs[6],
				'targetId': cmdargs[7][0],
				'isDamageOwner': cmdargs[8],
				'auxValue': cmdargs[9]
			}
			
			CF.CreateProjectile(levelId).CreateProjectileEntity(i, cmdargs[1], param)
		return False, '成功生成抛射物'
	
	def setstepheight(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateAttr(i).SetStepHeight(cmdargs[1])
		return False, '将 %s 能迈过的最大高度设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setsize(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateCollisionBox(i).SetSize((cmdargs[1], cmdargs[2]))
		return False, '已设置 %s 个实体的碰撞箱为 (%s, %s)' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])
		
	def playerchatprefix(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateExtraData(i).SetExtraData('chatprefix', cmdargs[1])
		return False, '将 %s 的聊天前缀设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def writehealthtoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			health = CF.CreateAttr(entity).GetAttrValue(0)
			health = int(round(health))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, health), entity, False)
		return False, '已将 %s 个实体的生命值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
		
	def writehungertoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			hunger = CF.CreateAttr(entity).GetAttrValue(4)
			hunger = int(round(hunger))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, hunger), entity, False)
		return False, '已将 %s 个实体的饥饿值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)

	def writearmortoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			armor = CF.CreateAttr(entity).GetAttrValue(12)
			armor = int(round(armor))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, armor), entity, False)
		return False, '已将 %s 个实体的盔甲值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
	
	def writespeedtoscoreboard(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		objects = compGame.GetAllScoreboardObjects()
		scoreboard_name = cmdargs[1]
		if not any(obj['name'] == scoreboard_name for obj in objects):
			return True, '未找到该计分板对象'
		for entity in cmdargs[0]:
			speed = CF.CreateActorMotion(entity).GetMotion()
			speed = (speed[0]**2 + speed[1]**2 + speed[2]**2)**0.5  # 计算速度
			speed = int(round(speed*20))
			compCmd.SetCommand('/scoreboard players set @s %s %s' % (scoreboard_name, speed), entity, False)
		return False, '已将 %s 个实体的速度值写入计分板 %s' % (len(cmdargs[0]), scoreboard_name)
	
	def executecb(self, cmdargs, playerId, variant, data):
		xyz = (intg(cmdargs[0][0]), int(cmdargs[0][1]), intg(cmdargs[0][2]))
		success = compBlockEntity.ExecuteCommandBlock(xyz, cmdargs[1]['id'])
		if success:
			return False, '已执行位于 Pos%s in %s 的命令方块' % (xyz, cmdargs[1]['name'])
		else:
			return True, '位于 Pos%s in %s 的方块不是命令方块' % (xyz, cmdargs[1]['name'])
		
	def setname(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateName(i).SetName(cmdargs[1])
		return False, '已设置 %s 个实体的名称为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def aicontrol(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateControlAi(i).SetBlockControlAi(cmdargs[1], cmdargs[2])
		return False, '已%s %s 个实体的AI' % ('启用' if cmdargs[1] else '禁用', len(cmdargs[0]))

	def param(self, cmdargs, playerId, variant, data):
		params = compExtra.GetExtraData('parameters')
		# 兼容旧版本
		if type(params) is dict:
			need_upgrade = False
			for key, value in params.items():
				if not isinstance(value, dict):
					if value.replace('.', '', 1).isdigit():
						params[key] = {'type': 'float', 'value': value} if '.' in value else {'type': 'int', 'value': value}
					else:
						params[key] = {'type': 'str', 'value': value}
					need_upgrade = True
			
			if need_upgrade:
				compExtra.SetExtraData('parameters', params)
		
		if variant == 0:  # show
			if cmdargs[1] is None:
				output = ['当前存储的变量:']
				if params and type(params) is dict:
					for key, value_info in params.items():
						output.append(' - %s (%s): %s' % (key, value_info.get('type', 'unknown'), value_info.get('value', '')))
				return False, '\n'.join(output)
			else:
				if type(params) == dict and params.get(cmdargs[1]) is not None:
					var_info = params[cmdargs[1]]
					return False, '变量 %s [%s] = %s' % (cmdargs[1], var_info.get('type', 'unknown'), var_info.get('value', ''))
				else:
					return True, '未知的变量 %s' % cmdargs[1]
					
		elif variant == 2:  # del
			if type(params) == dict and params.get(cmdargs[1]):
				del params[cmdargs[1]]
				compExtra.SetExtraData('parameters', params)
				return False, '已删除变量 %s' % cmdargs[1]
			else:
				return True, '未知的变量 %s ' % cmdargs[1]
		
		elif variant == 3:  # operation
			if not (type(params) == dict and params.get(cmdargs[1])):
				return True, '未知的变量 %s ' % cmdargs[1]	
			var_info = params[cmdargs[1]]
			var_type = var_info['type']
			current_value = var_info['value']
			if cmdargs[3].replace('.', '', 1).isdigit():
				if cmdargs[3].find('.') != -1:
					operand_value = float(cmdargs[3])
				else:
					operand_value = int(cmdargs[3])
			else:
				operand_value = cmdargs[3]	
			if cmdargs[2] == '加':
				if isinstance(operand_value, (int, float)) and isinstance(current_value, (int, float)):
					result = current_value + operand_value
				else:
					result = str(current_value) + str(operand_value)
			elif cmdargs[2] == '乘':
				if isinstance(operand_value, (int, float)) and isinstance(current_value, (int, float)):
					result = current_value * operand_value
				else:
					if isinstance(operand_value, int) and isinstance(current_value, str):
						result = current_value * operand_value
					elif isinstance(operand_value, str) and isinstance(current_value, int):
						result = operand_value * current_value
					else:
						return True, '仅支持整数与字符串的乘法'
			elif var_type in ['int', 'float'] and isinstance(operand_value, (int, float)):
				if cmdargs[2] == '减':
					result = current_value - operand_value
				elif cmdargs[2] == '除':
					if operand_value == 0:
						return True, '除数不能为零'
					result = current_value / operand_value
				elif cmdargs[2] == '乘方':
					result = current_value ** operand_value
				elif cmdargs[2] == '取余':
					if operand_value == 0:
						return True, '取余操作数不能为零'
					result = current_value % operand_value
				elif cmdargs[2] == '整除':
					if operand_value == 0:
						return True, '除数不能为零'
					result = current_value // operand_value
			else:
				return True, '字符串不支持该操作'
			# 更新结果并转换类型
			if isinstance(result, int):
				var_newtype = 'int'
			elif isinstance(result, float):
				var_newtype = 'float'
			else:
				var_newtype = 'str'
			params[cmdargs[1]]['type'] = var_newtype
			params[cmdargs[1]]['value'] = result
			compExtra.SetExtraData('parameters', params)
			return False, '操作完成: 结果 %s' % result
		
		elif variant == 4:  # random
			if not type(params) == dict:
				params = {}
			params[cmdargs[1]] = {
				'type': 'int',
				'value': random.randint(cmdargs[2], cmdargs[3])
			}
			compExtra.SetExtraData('parameters', params)
			return False, '已将 %s 设置为随机值 %s' % (cmdargs[1], params[cmdargs[1]]['value'])
		
		elif variant == 1:  # set
			if '{' in cmdargs[1] or '}' in cmdargs[1]:
				return True, '变量名不能包含 "{" 或 "}"'
			if not type(params) == dict:
				params = {}
			if cmdargs[3] is not None:
				try:
					if cmdargs[2] == 'int':
						value = int(cmdargs[3])
					elif cmdargs[2] == 'float':
						value = float(cmdargs[3])
					else:  # str
						value = str(cmdargs[3])
				except ValueError:
					return True, '%s 无法转换为 %s 类型' % (cmdargs[3], cmdargs[2])
			else:
				value = 0 if cmdargs[2] == 'int' else 0.0 if cmdargs[2] == 'float' else ''
			params[cmdargs[1]] = {
				'type': cmdargs[2],
				'value': value
			}
			compExtra.SetExtraData('parameters', params)
			return False, '已修改 %s 类型变量 %s = %s' % (cmdargs[2], cmdargs[1], value)

	def param_private(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		outputs = []
		faild = True
		if variant == 0:  # show
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				params = compExtra.GetExtraData('parameters')
				entityTypeStr = CF.CreateEngineType(i).GetEngineTypeStr()
				if cmdargs[2] is None:
					output = ['§r%s 当前存储的变量:' % entityTypeStr]
					if params and type(params) is dict:
						for key, value_info in params.items():
							output.append('§r - %s (%s): %s' % (key, value_info.get('type', 'unknown'), value_info.get('value', '')))
					faild = False
					outputs.append('\n'.join(output))
					continue
				else:
					if type(params) == dict and params.get(cmdargs[2]) is not None:
						var_info = params[cmdargs[2]]
						outputs.append('§r%s 存储的变量 %s [%s] = %s' % (entityTypeStr, cmdargs[2], var_info.get('type', 'unknown'), var_info.get('value', '')))
						faild = False
						continue
					else:
						outputs.append(('§c' if playerId else '')+'%s 中未存储变量 %s' % (entityTypeStr, cmdargs[2]))
						continue
			return faild, '\n'.join(outputs)
				
		elif variant == 2:  # del
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				params = compExtra.GetExtraData('parameters')
				entityTypeStr = CF.CreateEngineType(i).GetEngineTypeStr()
				if type(params) == dict and params.get(cmdargs[2]):
					del params[cmdargs[2]]
					compExtra.SetExtraData('parameters', params)
					outputs.append('§r已删除 %s 中存储的变量 %s' % (entityTypeStr, cmdargs[2]))
					faild = False
					continue
				else:
					outputs.append(('§c' if playerId else '')+'%s 中未存储变量 %s' % (entityTypeStr, cmdargs[2]))
					continue
			return faild, '\n'.join(outputs)
			
		elif variant == 3:  # operation
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				params = compExtra.GetExtraData('parameters')
				entityTypeStr = CF.CreateEngineType(i).GetEngineTypeStr()
				if not (type(params) == dict and params.get(cmdargs[2])):
					outputs.append(('§c' if playerId else '')+'%s 中未存储变量 %s' % (entityTypeStr, cmdargs[2]))
					continue
				var_info = params[cmdargs[2]]
				var_type = var_info['type']
				current_value = var_info['value']
				if cmdargs[4].replace('.', '', 1).isdigit():
					if cmdargs[4].find('.') != -1:
						operand_value = float(cmdargs[4])
					else:
						operand_value = int(cmdargs[4])
				else:
					operand_value = cmdargs[4]
				if cmdargs[3] == '加':
					if isinstance(operand_value, (int, float)) and isinstance(current_value, (int, float)):
						result = current_value + operand_value
					else:
						result = str(current_value) + str(operand_value)
				elif cmdargs[3] == '乘':
					if isinstance(operand_value, (int, float)) and isinstance(current_value, (int, float)):
						result = current_value * operand_value
					else:
						if isinstance(operand_value, int) and isinstance(current_value, str):
							result = current_value * operand_value
						elif isinstance(operand_value, str) and isinstance(current_value, int):
							result = operand_value * current_value
						else:
							outputs.append(('§c' if playerId else '')+'对于 %s 存储的变量不支持该乘法' % entityTypeStr)
							continue
				elif var_type in ['int', 'float'] and isinstance(operand_value, (int, float)):
					if cmdargs[3] == '减':
						result = current_value - operand_value
					elif cmdargs[3] == '除':
						if operand_value == 0:
							outputs.append(('§c' if playerId else '')+'除数不能为零')
							continue
						result = current_value / operand_value
					elif cmdargs[3] == '乘方':
						result = current_value ** operand_value
					elif cmdargs[3] == '取余':
						if operand_value == 0:
							outputs.append(('§c' if playerId else '')+'取余操作数不能为零')
							continue
						result = current_value % operand_value
					elif cmdargs[3] == '整除':
						if operand_value == 0:
							outputs.append(('§c' if playerId else '')+'除数不能为零')
							continue
						result = current_value // operand_value
				else:
					outputs.append(('§c' if playerId else '')+'字符串不支持该操作')
					continue
				# 更新结果并转换类型
				if isinstance(result, int):
					var_newtype = 'int'
				elif isinstance(result, float):
					var_newtype = 'float'
				else:
					var_newtype = 'str'
				params[cmdargs[2]]['type'] = var_newtype
				params[cmdargs[2]]['value'] = result
				compExtra.SetExtraData('parameters', params)
				outputs.append('§r对 %s 存储的变量操作完成: 结果 %s' % (entityTypeStr, result))
				faild = False
			print(outputs)
			return faild, '\n'.join(outputs)
		
		elif variant == 4:  # random
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				params = compExtra.GetExtraData('parameters')
				entityTypeStr = CF.CreateEngineType(i).GetEngineTypeStr()
				if not type(params) == dict:
					params = {}
				params[cmdargs[2]] = {
					'type': 'int',
					'value': random.randint(cmdargs[3], cmdargs[4])
				}
				compExtra.SetExtraData('parameters', params)
				outputs.append('已将 %s 存储的变量 %s 设置为随机值 %s' % (entityTypeStr, cmdargs[2], params[cmdargs[2]]['value']))
				faild = False
			return faild, '\n'.join(outputs)
		
		elif variant == 1:  # set 
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				params = compExtra.GetExtraData('parameters')
				entityTypeStr = CF.CreateEngineType(i).GetEngineTypeStr()
				if not type(params) == dict:
					params = {}
				if cmdargs[4] is not None:
					try:
						if cmdargs[3] == 'int':
							value = int(cmdargs[4])
						elif cmdargs[3] == 'float':
							value = float(cmdargs[4])
						else:  # str
							value = str(cmdargs[4])
					except ValueError:
						outputs.append(('§c' if playerId else '')+'%s 无法转换为 %s 类型' % (cmdargs[4], cmdargs[3]))
						continue
				else:
					value = 0 if cmdargs[3] == 'int' else 0.0 if cmdargs[3] == 'float' else ''
				params[cmdargs[2]] = {
					'type': cmdargs[3],
					'value': value
				}
				compExtra.SetExtraData('parameters', params)
				outputs.append('已修改 %s 存储的 %s 类型变量 %s = %s' % (entityTypeStr, cmdargs[3], cmdargs[2], value))
				faild = False
			return faild, '\n'.join(outputs)

	def kickt(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for kickplayer in cmdargs[0]:
			compCmd.SetCommand('/kick "%s" "%s"' % (CF.CreateName(kickplayer).GetName(), cmdargs[1]))
		return False, '已将 %s 踢出游戏: %s' % (create_players_str(cmdargs[0]), cmdargs[1])
			
	def explode(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[4] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[4]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		ExpPlayerId = serverApi.GetPlayerList()
		ExpPlayerId = random.choice(ExpPlayerId)
		for i in cmdargs[0]:
			position = CF.CreatePos(i).GetFootPos()
			CF.CreateExplosion(levelId).CreateExplosion(position, cmdargs[1], cmdargs[3], cmdargs[2], cmdargs[4][0], ExpPlayerId)
		return False, '已引爆 %s 个实体' % len(cmdargs[0])

	def explodebypos(self, cmdargs, playerId, variant, data):
		if cmdargs[4] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[4]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		ExpPlayerId = serverApi.GetPlayerList()
		ExpPlayerId = random.choice(ExpPlayerId)
		if CF.CreateExplosion(levelId).CreateExplosion(cmdargs[0], cmdargs[1], cmdargs[3], cmdargs[2], cmdargs[4][0], ExpPlayerId):
			return False, '爆炸已创建于 Pos%s' % (cmdargs[0],)
		else:
			return True, '爆炸创建失败'

	def console(self, cmdargs, playerId, variant, data):
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		cmd = cmdargs[0]
		if cmd.startswith('/'):
			cmd = cmd[1:]
		params = compExtra.GetExtraData('parameters') or {}
		if '{' in cmd and '}' in cmd:
			words = re.findall(r'\{([^{}]+)\}', cmd)
			processedWords = []
			for word in words:

				if word in processedWords:
					continue

				processedWords.append(word)
				if params.get(word) is None:
					selectors = re.findall(r'\[(.*)\]', word)
					if selectors:
						selector = selectors[0]
						if (cmdargs[1][0] or playerId) is None:
							return True, '未能在处理选择器时找到合适的执行实体'
						compEntity = CF.CreateEntityComponent(cmdargs[1][0] or playerId)
						selectedEntities = compEntity.GetEntitiesBySelector(selector)
						selectedEntitiesNum = len(selectedEntities)
						if selectedEntitiesNum == 0:
							return True, '处理变量 %s 时未选中任何实体' % word
						elif selectedEntitiesNum != 1:
							return True, '处理变量 %s 时选中了多个实体' % word
						elif selectedEntitiesNum == 1:
							compEntityExtra = CF.CreateExtraData(selectedEntities[0])
							entityParams = compEntityExtra.GetExtraData('parameters') or {}
							paramName = word.lstrip('[%s]' % selector)
							if entityParams.get(paramName) is None:
								continue
							else:
								value = entityParams[paramName].get('value', '')
					else:
						continue
				else:
					param = params[word]
					value = param.get('value', '')
				cmd = cmd.replace('{%s}' % word, str(value))
		
		cmd = cmd.replace("'", '"')
		compCmd.SetCommand(cmd, cmdargs[1][0], cmdargs[2])
		return False, '已将指令处理后执行: %s' % cmd
	
	def addaroundentitymotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[1]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				addMotion = CompMotion.AddPlayerAroundEntityMotion
			else:
				addMotion = CompMotion.AddEntityAroundEntityMotion
			Mid = addMotion(cmdargs[1][0],
							cmdargs[2],
							cmdargs[3],
							cmdargs[4],
							cmdargs[5],
							cmdargs[6])
			if Mid != -1:
				tot += 1
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'
	
	def addaroundpointmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				addMotion = CompMotion.AddPlayerAroundPointMotion
			else:
				addMotion = CompMotion.AddEntityAroundPointMotion
			Mid = addMotion(cmdargs[1],
							cmdargs[2],
							cmdargs[3],
							cmdargs[4],
							cmdargs[5])
			if Mid != -1:
				tot += 1
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'

	def addvelocitymotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				addMotion = CompMotion.AddPlayerVelocityMotion
			else:
				addMotion = CompMotion.AddEntityVelocityMotion
			Mid = addMotion(cmdargs[1],
							cmdargs[2],
							cmdargs[3])
			if Mid != -1:
				tot += 1
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'
	
	def startmotion(self, cmdargs, playerId, variant, data):

		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			#旧数据处理
			compExtra = CF.CreateExtraData(i)
			compExtra.CleanExtraData('Motions')
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				startMotion = CompMotion.StartPlayerMotion
				Motions = CompMotion.GetPlayerMotions()
			else:
				startMotion = CompMotion.StartEntityMotion
				Motions = CompMotion.GetEntityMotions()
			for k,_ in Motions.items():
				startMotion(k)
			if Motions:
				tot += 1
		if tot:
			return False, '已启用 %s 个实体的运动器' % tot
		else:
			return True, '实体没有绑定运动器'
	
	def stopmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				stopMotion = CompMotion.StopPlayerMotion
				Motions = CompMotion.GetPlayerMotions()
			else:
				stopMotion = CompMotion.StopEntityMotion
				Motions = CompMotion.GetEntityMotions()
			for k,_ in Motions.items():
				stopMotion(k)
			if Motions:
				tot += 1
		if tot:
			return False, '已暂停 %s 个实体的运动器' % tot
		else:
			return True, '实体没有绑定运动器'
	
	def removemotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				Motions = CompMotion.GetPlayerMotions()
				removeMotion = CompMotion.RemovePlayerMotion
			else:
				Motions = CompMotion.GetEntityMotions()
				removeMotion = CompMotion.RemoveEntityMotion
			for k,_ in Motions.items():
				removeMotion(k)
			if Motions:
				tot += 1
		if tot:
			return False, '已移除 %s 个实体的运动器' % tot
		else:
			return True, '实体没有绑定运动器'

	def addenchant(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if isinstance(cmdargs[3], int):
			slotType = 0
			slot = cmdargs[3]
		else:
			slotType = 2
			slot = 0
		for i in cmdargs[0]:
			itemdict = CF.CreateItem(i).GetPlayerItem(slotType, slot, True)
			if itemdict:
				if itemdict['userData'] is None:
					itemdict['userData'] = {}
				if itemdict['userData'].get('ench', None) is None:
					itemdict['userData']['ench'] = []
				
				itemdict['userData']['ench'].insert(0, {
					'lvl': {'__type__': 2, '__value__': cmdargs[2]},
					'id':  {'__type__': 2, '__value__': cmdargs[1]['type']},
					'modEnchant': {'__type__': 8, '__value__': ''}
				})
				itemdict['enchantData'] = []
				
				if slotType == 0:
					CF.CreateItem(i).SpawnItemToPlayerInv(itemdict, i, slot)
				else:
					CF.CreateItem(i).SpawnItemToPlayerCarried(itemdict, i)
		return False, '已为 %s 的%s物品添加附魔 %s' % (create_players_str(cmdargs[0]), '手持' if slotType == 2 else '背包', cmdargs[1]['identifier'])

	def addtrackmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		tot = 0
		for i in cmdargs[0]:
			CompMotion = CF.CreateActorMotion(i)
			CompType = CF.CreateEngineType(i)
			EntityType = CompType.GetEngineTypeStr()
			if EntityType == 'minecraft:player':
				addMotion = CompMotion.AddPlayerTrackMotion
			else:
				addMotion = CompMotion.AddEntityTrackMotion
			Mid = addMotion(cmdargs[1],
							cmdargs[2],
							None,
							False,
							cmdargs[3],
							None,
							None,
							cmdargs[4])
			if Mid != -1:
				tot += 1
			#Motions = compExtra.GetExtraData('Motions')
			#if not Motions:
			#	Motions = []
			#Motions.append(Mid)
			#compExtra.SetExtraData('Motions', Motions)
		if tot:
			return False, '已设置 %s 个实体的运动器' % tot
		else:
			return True, '设置失败'

	def setactorcanburnbylightning(self, cmdargs, playerId, variant, data):
		compGame.SetCanActorSetOnFireByLightning(cmdargs[0])
		return False, '已 %s 实体被闪电点燃' % ('允许' if cmdargs[0] else '禁止')

	def setblockcanburnbylightning(self, cmdargs, playerId, variant, data):
		compGame.SetCanBlockSetOnFireByLightning(cmdargs[0])
		return False, '已 %s 方块被闪电点燃' % ('允许' if cmdargs[0] else '禁止')

	def cancelshearsdestoryblockspeedall(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			compItem.CancelShearsDestoryBlockSpeedAll()
		return False, '已取消 %s 个实体剪刀破坏方块速度的所有设置' % (len(cmdargs[0]))

	def cancelshearsdestoryblockspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			compItem.CancelShearsDestoryBlockSpeed(cmdargs[1])
			#	return True, '无效的命名空间id'
		return False, '已取消 %s 个实体剪刀破坏 %s 速度的设置' % (len(cmdargs[0]), cmdargs[1])

	def setshearsdestoryblockspeed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[2] < 1:
			return True, '速度必须大于1'
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			compItem.SetShearsDestoryBlockSpeed(cmdargs[1], cmdargs[2])
			#	return True, '无效的命名空间id'
		return False, '已设置 %s 个实体剪刀破坏 %s 速度为 %s' % (len(cmdargs[0]), cmdargs[1], cmdargs[2])

	def changeselectslot(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CompPlayer = CF.CreatePlayer(i)
			CompPlayer.ChangeSelectSlot(cmdargs[1])
		return False, '将 %s 的选择槽位设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def forbidliquidflow(self, cmdargs, playerId, variant, data):
		compGame.ForbidLiquidFlow(cmdargs[0])
		return False, '已 %s 液体流动' % ('禁止' if cmdargs[0] else '允许')

	def getuid(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		uid_dict = {}
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			playername = CF.CreateName(i).GetName()
			uid_dict[playername] = CF.CreateHttp(levelId).GetPlayerUid(i)
		return False, '获取到的UID为%s' % (uid_dict)
		# self.NotifyToMultiClients(list(cmdargs[0]), 'CustomCommandClient', {'cmd':'getuid', 'origin': playerId})

	def givewithnbt(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[1])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			for i in ['isDiggerItem', 'enchantData', 'itemId', 'modEnchantData', 'modId', 'modItemId', 'itemName', 'auxValue']:
				itemDict.pop(i, False) #删去多余键值对(这些已被弃用)
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			for i in cmdargs[0]:
				if not CF.CreateItem(i).SpawnItemToPlayerInv(itemDict, i):
					return True, '此JSON生成物品失败'
			return False, '成功给予 %s 物品 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'
		
	def spawnitemtocontainer(self, cmdargs, playerId, variant, data):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		x = intg(cmdargs[2][0])
		y = int(cmdargs[2][1])
		z = intg(cmdargs[2][2])
		itemDict = compItemWorld.GetContainerItem((x, y, z), cmdargs[1], cmdargs[3]['id'], True)
		result = checkjson(cmdargs[0])
		if result[1] == True:
			return True, result[0]
		itemDict2 = result[0]
		if isinstance(itemDict2, dict):
			for k,v in [('durability', 0), ('customTips', ''), ('extraId', ''), ('newAuxValue', 0), ('userData', None), ('showInHand', True)]:
				itemDict2.setdefault(k, v)
			if itemDict is not None:
				for i in ['isDiggerItem', 'enchantData', 'itemId', 'modEnchantData', 'modId', 'modItemId', 'itemName', 'auxValue']:
					itemDict.pop(i) #删去多余键值对(这些已被弃用)
					itemDict2.pop(i, False)
				countOrign = itemDict.pop('count')
			else: countOrign = 0
			countAdd = itemDict2.pop('count', 1)
			if itemDict2.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if ((itemDict is None) or itemDict == itemDict2) and countOrign+countAdd <= 64:
				itemDict2.update({'count': countOrign+countAdd})
				if compItemWorld.SpawnItemToContainer(itemDict2, cmdargs[1], (x, y, z), cmdargs[3]['id']):
					return False, '向槽位 %s 添加 %s * %s' % (cmdargs[1], itemDict2.get('newItemName'), countAdd)
				else:
					return True, '位于 Pos(%s,%s,%s) 的方块不是容器' % (x,y,z)
			else:
				return True, '槽位已满'
		else:
			return True, '无效的nbt'

	def spawnitemtoenderchest(self, cmdargs, playerId, variant, data):
		# args['return_msg_key'] = '给予失败'
		# args['return_failed'] = True
		if not check_entities_type('minecraft:player', cmdargs[2]):
			return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[0])
		if result[1] == True:
			return True, result[0]
		itemDict2 = result[0]
		if isinstance(itemDict2, dict):
			for k,v in [('durability', 0), ('customTips', ''), ('extraId', ''), ('newAuxValue', 0), ('userData', None), ('showInHand', True)]:
				itemDict2.setdefault(k, v)
			countAdd = itemDict2.pop('count', 1)
			for player in cmdargs[2]:
				compItem = CF.CreateItem(player)
				itemDict = compItem.GetEnderChestItem(player, cmdargs[1], True)
				if itemDict:
					for i in ['isDiggerItem', 'enchantData', 'itemId', 'modEnchantData', 'modId', 'modItemId', 'itemName', 'auxValue']:
						itemDict.pop(i) #删去多余键值对(这些已被弃用)
						itemDict2.pop(i, False)
					countOrign = itemDict.pop('count')
				else: countOrign = 0
				if itemDict2.get('newItemName') is None:
					return True, '物品数据中缺少 newItemName 键'
				if ((not itemDict) or itemDict == itemDict2) and countOrign+countAdd <= 64:
					itemDict2.update({'count': countOrign+countAdd})
					if compItem.SpawnItemToEnderChest(itemDict2, cmdargs[1]):
						return False, '向 %s 的末影箱中的槽位 %s 添加 %s * %s' % (create_players_str(cmdargs[2]), cmdargs[1], itemDict2.get('newItemName'), countAdd)
				else:
					return True, '槽位已满'
		else:
			return True, '无效的nbt'

	def replaceitemtocarried(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[1])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			for i in cmdargs[0]:
				CF.CreateItem(i).SpawnItemToPlayerCarried(itemDict, i)
			return False, '将 %s 的主手物品替换为 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'

	def removeenchant(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[2] is None:
			posType = 2
			pos = 0
		else:
			posType = 0
			pos = cmdargs[2]
		for i in cmdargs[0]:
			compItem = CF.CreateItem(i)
			itemDict = compItem.GetPlayerItem(posType, pos, True)
			if itemDict:
				if itemDict.get('userData') is not None:
					if itemDict['userData'].get('ench') is not None:
						for ii in itemDict['userData']['ench']:
							if ii['id']['__value__'] == cmdargs[1]['type']:
								itemDict['userData']['ench'].remove(ii)
						if itemDict['userData']['ench'] == []:
							del itemDict['userData']['ench']
				del itemDict['enchantData']
				if posType == 0:
					compItem.SpawnItemToPlayerInv(itemDict, i, pos)
				else:
					compItem.SpawnItemToPlayerCarried(itemDict, i)
		return False, '将 %s 背包物品中的 %s 附魔移除' % (create_players_str(cmdargs[0]), cmdargs[1]['identifier'])

	def resetmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CF.CreateEngineType(i)
			CompMotion = CF.CreateActorMotion(i)
			if CompType.GetEngineTypeStr() == 'minecraft:player':
				CompMotion.SetPlayerMotion((0, 0, 0))
			else:
				CompMotion.ResetMotion()
		return False, '已重置 %s 个实体的运动状态' % len(cmdargs[0])

	def setleashholder(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[0]) == 1:
			for i in cmdargs[1]:
				compEntityD = CF.CreateEntityDefinitions(i)
				compEntityD.SetLeashHolder(cmdargs[0])
			return False, '已尝试拴住实体'
		else:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'

	def setlootdropped(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compEntityD = CF.CreateEntityDefinitions(i)
			compEntityD.SetLootDropped(cmdargs[1])
		return False, '将 %s 个实体的掉落概率设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def setmaxairsupply(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compBrea = CF.CreateBreath(i)
			compBrea.SetMaxAirSupply(cmdargs[1])
		return False, '将 %s 个实体的最大氧气量设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def knockback(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CF.CreateAction(i).SetMobKnockback(cmdargs[1], cmdargs[2], cmdargs[3], cmdargs[4], cmdargs[5])
		return False, '已击飞 %s 个实体' % (len(cmdargs[0]))

	def setmotion(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			CompType = CF.CreateEngineType(i)
			CompMotion = CF.CreateActorMotion(i)
			if CompType.GetEngineTypeStr() == 'minecraft:player':
				CompMotion.SetPlayerMotion(cmdargs[1])
			else:
				CompMotion.SetMotion(cmdargs[1])
		return False, '将 %s 个实体的动量设置为 %s' % (len(cmdargs[0]), str(cmdargs[1]))

	def setopencontainersability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetOpenContainersAbility(cmdargs[1])
		return False, '将 %s 的开箱权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def setoperatedoorability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetOperateDoorsAndSwitchesAbility(cmdargs[1])
		return False, '将 %s 的开门权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setorbexperience(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:xp_orb', cmdargs[0]):
			return True, '选择器必须为经验球类型'
		for i in cmdargs[0]:
			compAttr = CF.CreateExp(i)
			compAttr.SetOrbExperience(cmdargs[1])
		return False, '将 %s 个经验球的经验值设置为 %s' % (len(cmdargs[0]), cmdargs[1])

	def setpersistent(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		for i in cmdargs[0]:
			compAttr = CF.CreateAttr(i)
			compAttr.SetPersistent(cmdargs[1])
		return False, '将 %s 个实体的自动清除设置为 %s' % (len(cmdargs[0]), '允许' if cmdargs[1] else '禁止')

	def setpistonmaxinteractioncount(self, cmdargs, playerId, variant, data):
		if compGame.SetPistonMaxInteractionCount(cmdargs[0]):
			return False, '将活塞最大推动数设置为 %s' % cmdargs[0]
		else:
			return True, '无效的数值'

	def setplayeruiitem(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		result = checkjson(cmdargs[2])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			enum = {
					"cursorselected" : 0,
					"anvilinput" : 1,
					"anvilmaterial" : 2,
					"stonecutterinput" : 3,
					"trade2ingredient1" : 4,
					"trade2ingredient2" : 5,
					"loominput" : 9,
					"loomdye" : 10,
					"loommaterial" : 11,
					"cartographyinput" : 12,
					"cartographyadditional" : 13,
					"enchantinginput" : 14,
					"enchantingmaterial" : 15,
					"grindstoneinput" : 16,
					"grindstoneadditional" : 17,
					"beaconpayment" : 27,
					"crafting2x2input1" : 28,
					"crafting2x2input2" : 29,
					"crafting2x2input3" : 30,
					"crafting2x2input4" : 31,
					"crafting3x3input1" : 32,
					"crafting3x3input2" : 33,
					"crafting3x3input3" : 34,
					"crafting3x3input4" : 35,
					"crafting3x3input5" : 36,
					"crafting3x3input6" : 37,
					"crafting3x3input7" : 38,
					"crafting3x3input8" : 39,
					"crafting3x3input9" : 40,
					"createditemoutput" : 50,
					"smithingtableinput" : 51,
					"smithingtablematerial" : 52,
					"smithingtabletemplate" : 53 
			}
			for i in cmdargs[0]:
				CF.CreateItem(i).SetPlayerUIItem(i, enum.get(cmdargs[1]), itemDict, cmdargs[3])
			return False, '将 %s 的UI物品设置为 %s * %s' % (create_players_str(cmdargs[0]), itemDict.get('newItemName'), itemDict.get('count'))
		else:
			return True, '无效的nbt'

	def _if(self, cmdargs, playerId, variant, data):
		if variant == 0:  # cmd模式不变
			if cmdargs[3] is None:
				result = [compCmd.SetCommand(cmdargs[1].replace("'", '"'), playerId), False]
			else:
				result = [compCmd.SetCommand(cmdargs[1].replace("'", '"'), playerId), compCmd.SetCommand(cmdargs[3].replace("'", '"'), playerId)]
			if cmdargs[2] == 'not':
				if result[0]:
					return True, '运算符成立(%s)' % (result[1])
				else:
					return False, '运算符不成立(%s)' % (result[1])
			elif cmdargs[2] == 'and':
				if result[0] and result[1]:
					return False, '运算符成立(%s, %s)' % (result[0], result[1])
				else:
					return True, '运算符不成立(%s, %s)' % (result[0], result[1])
			elif cmdargs[2] == 'or':
				if result[0] or result[1]:
					return False, '运算符成立(%s, %s)' % (result[0], result[1])
				else:
					return True, '运算符不成立(%s, %s)' % (result[0], result[1])
			elif cmdargs[2] == 'xor':
				if result[0] != result[1]:
					return False, '运算符成立(%s, %s)' % (result[0], result[1])
				else:
					return True, '运算符不成立(%s, %s)' % (result[0], result[1])
			else:
				return True, '未知的逻辑运算符'
		
		else:  # param模式 (variant1)
			params = compExtra.GetExtraData('parameters')
			
			# 检查变量是否存在
			if not (type(params) == dict and cmdargs[1] in params):
				return True, '未知的变量\'%s\'' % cmdargs[1]
			
			var_info = params[cmdargs[1]]
			var_value = var_info['value']
			var_type = var_info['type']
			
			# 尝试将输入值转换为变量相应类型
			try:
				if var_type == 'int':
					input_value = int(cmdargs[3])
				elif var_type == 'float':
					input_value = float(cmdargs[3])
				else:  # str
					input_value = str(cmdargs[3])
			except ValueError:
				return True, '无法将 %s 转换为%s类型进行比较' % (cmdargs[3], var_type)
			
			# 执行比较操作
			if cmdargs[2] == 'equals':
				result = var_value == input_value
				symbol = '=='
			elif cmdargs[2] == 'not_equals':
				result = var_value != input_value
				symbol = '!='
			else:
				# 检查类型是否支持比较
				if var_type == 'str':
					return True, '字符串变量只支持等于(equals)和不等于(not_equals)比较'
				
				# 执行数值比较
				if cmdargs[2] == 'greater_than':
					result = var_value > input_value
					symbol = '>'
				elif cmdargs[2] == 'less_than':
					result = var_value < input_value
					symbol = '<'
				elif cmdargs[2] == 'not_less':
					result = var_value >= input_value
					symbol = '>='
				elif cmdargs[2] == 'not_greater':
					result = var_value <= input_value
					symbol = '<='
				else:
					return True, '未知的比较操作符'
			
			# 格式化显示值（避免浮点数精度问题）
			if var_type == 'float':
				display_value = round(var_value, 6)
				display_input = round(input_value, 6)
			else:
				display_value = var_value
				display_input = input_value
			
			return not result, '表达式%s成立(%s %s %s)' % ('' if result else '不', display_value, symbol, display_input)
	
	def setteleportability(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetTeleportAbility(cmdargs[1])
		return False, '将 %s 的传送权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')
	
	def settradelevel(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateEntityDefinitions(i).SetTradeLevel(cmdargs[1])
		return False, '已设置 %s 个村民的交易等级为 %s' % (len(cmdargs[0]), cmdargs[1])
	
	def setvignette(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[1]):
			return True, '选择器必须为玩家类型'
		if variant == 0:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettecenter', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角中心设置为 %s, %s' % (create_players_str(cmdargs[1]), cmdargs[2], cmdargs[3])
		elif variant == 1:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignetteradius', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角半径设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 2:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettecolor', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角颜色设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 3:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignettesmooth', 'cmdargs': cmdargs})
			return False, '已将 %s 的屏幕暗角平滑度设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		elif variant == 4:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setvignette', 'cmdargs': cmdargs})
			return False, '已%s %s 的屏幕暗角' % ('启用' if cmdargs[2] else '禁用', create_players_str(cmdargs[1]))
		
	def setbrewingstandslotitem(self, cmdargs, playerId, variant, data):
		if cmdargs[1] not in range(5):
			return True, '无效的槽位'
		x, y, z = cmdargs[2]
		xyz = (intg(x), int(y), intg(z))
		result = checkjson(cmdargs[0])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if itemDict.get('count') is None:
				return True, '物品数据中缺少 count 键'
			if compItemWorld.SetBrewingStandSlotItem(itemDict, cmdargs[1], xyz, cmdargs[3]['id']):
				return False, '将槽位 %s 的物品设置为 %s' % (cmdargs[1], itemDict.get('itemName'))
			else:
				return True, '设置 Pos%s 的方块时失败' % (xyz,)
		else:
			return True, '无效的nbt'

	def setdisablecontainers(self, cmdargs, playerId, variant, data):
		compGame.SetDisableContainers(cmdargs[0])
		return False, '将世界的容器权限设置为 %s' % ('禁止' if cmdargs[0] else '允许')
		
	def setdisabledropitem(self, cmdargs, playerId, variant, data):
		compGame.SetDisableDropItem(cmdargs[0])
		return False, '将世界的丢弃物品权限设置为 %s' % ('禁止' if cmdargs[0] else '允许')
		
	def setdisablehunger(self, cmdargs, playerId, variant, data):
		compGame.SetDisableHunger(cmdargs[0])
		return False, '将世界的饱食度设置为 %s' % ('屏蔽' if cmdargs[0] else '生效')

	def setenchantmentseed(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreatePlayer(i).SetEnchantmentSeed(cmdargs[1])
		return False, '将 %s 的附魔种子设置为 %s' % (create_players_str(cmdargs[0]), cmdargs[1])

	def setentityitem(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		result = checkjson(cmdargs[2])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if not isinstance(itemDict, dict):
			return True, '无效的nbt'
		for i in cmdargs[0]:
			if CF.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:player':
				return True, '选择器必须为非玩家类型'
		if itemDict.get('newItemName') is None:
			return True, '物品数据中缺少 newItemName 键'
		if itemDict.get('count') is None:
			return True, '物品数据中缺少 count 键'
		for i in cmdargs[0]:
			CF.CreateItem(i).SetEntityItem(cmdargs[1], itemDict, cmdargs[3])
		return False, '已设置 %s 个实体的物品' % (len(cmdargs[0]))
		
	def setentityowner(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if cmdargs[1] is None:
			ownerid = None
		else:
			if len(cmdargs[1]) != 1:
				return True, '只允许一个实体, 但提供的选择器允许多个实体'
			ownerid = cmdargs[1][0]

		failed_entities = []
		
		for i in cmdargs[0]:
			if not CF.CreateActorOwner(i).SetEntityOwner(ownerid):
				failed_entities.append(CF.CreateEngineType(i).GetEngineTypeStr())
		
		if failed_entities:
			return True, '部分实体执行过程中出现错误: %s' % failed_entities
		else:
			return False, '已设置 %s 个实体的属主' % (len(cmdargs[0]))
		
	def setentityride(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None or cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if len(cmdargs[0]) != 1:
			return True, '只允许一个实体, 但提供的选择器允许多个实体'
		failed_entities = []
		
		for i in cmdargs[1]:
			if not CF.CreateRide(i).SetEntityRide(cmdargs[0][0], i):
				failed_entities.append(CF.CreateEngineType(i).GetEngineTypeStr())
		
		if failed_entities:
			return True, '部分实体执行过程中出现错误: %s' % failed_entities,
		else:
			return False, '已驯服 %s 个生物' % (len(cmdargs[1]))
		
	def setframeitemdropchange(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if compBlockEntity.SetFrameItemDropChange(xyz, cmdargs[1]['id'], cmdargs[2]):
			return False, '已设置 Pos%s 的展示框掉落几率为 %s' % (xyz, cmdargs[2]*100)
		else:
			return True, '位于 Pos%s 的方块不是展示框' % (xyz,)
		
	def setframerotation(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if compBlockEntity.SetFrameRotation(xyz, cmdargs[1]['id'], cmdargs[2]):
			return False, '已设置 Pos%s 的展示框旋转角度为 %s 度' % (xyz, cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是展示框' % (xyz,)
		
	def sethopperspeed(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if compBlockEntity.SetHopperSpeed(xyz, cmdargs[1]['id'], cmdargs[2]):
			return False, '已设置 %s 的漏斗运输用时为 %s 红石刻' % (xyz, cmdargs[2])
		else:
			return True, '位于 Pos%s 的方块不是漏斗' % (xyz,)
		
	def sethudchatstackposition(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'sethudchatstackposition', 'cmdargs': cmdargs})
		return False, '将 %s 的聊天UI位置设置为 %s, %s' % (create_players_str(cmdargs[0]), cmdargs[1], cmdargs[2])
	
	def sethudchatstackvisible(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'sethudchatstackvisible', 'cmdargs': cmdargs})
		return False, '已%s %s 的聊天UI' % ('启用' if cmdargs[1] else '禁用', create_players_str(cmdargs[0]))
	
	def setshowrideui(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateRide(i).SetShowRideUI(i, cmdargs[1])
		return False, '已%s %s 的骑乘UI' % ('启用' if cmdargs[1] else '禁用', create_players_str(cmdargs[0]))
	
	def setgaussian(self, cmdargs, playerId, variant, data):
		if cmdargs[1] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[1]):
			return True, '选择器必须为玩家类型'
		if variant == 0:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setgaussian', 'cmdargs': cmdargs})
			return False, '已 %s %s 的高斯模糊' % ('启用' if cmdargs[2] else '禁用', create_players_str(cmdargs[1]))
		elif variant == 1:
			self.NotifyToMultiClients(cmdargs[1], 'CustomCommandClient', {'cmd':'setgaussianradius', 'cmdargs': cmdargs})
			return False, '已将 %s 的高斯模糊半径设置为 %s' % (create_players_str(cmdargs[1]), cmdargs[2])
		
	def scoreparam(self, cmdargs, playerId, variant, data):
		if cmdargs[0] == 'toscore':
			objects = compGame.GetAllScoreboardObjects()
			for obj in objects:
				if obj['name'] == cmdargs[2]:
					break
			else:
				return True, '没有找到名称为“%s”的计分项' % (cmdargs[2])
			param_name = cmdargs[1]
			params = compExtra.GetExtraData('parameters')
			if not (isinstance(params, dict) and params.get(param_name)):
				return True, '未知的变量 %s' % param_name
			var_value = params[param_name].get('value')
			try:
				score = int(var_value)
			except (TypeError, ValueError):
				return True, '无法将变量值转换为整数: %s' % param_name
			command = '/scoreboard players set "%s" "%s" %s' % (cmdargs[3] if cmdargs[3] else param_name, cmdargs[2], score)
			if not compCmd.SetCommand(command):
				return True, '设置计分板失败'
			return False, '将变量 %s 的值(%s)设置到计分板 %s %s中' % (param_name, score, cmdargs[2], ('的 %s ' % cmdargs[3]) if cmdargs[3] else '')
	
		if cmdargs[0] == 'toparam':
			objects = compGame.GetAllScoreboardObjects()
			for obj in objects:
				if obj['name'] == cmdargs[2]:
					break
			else:
				return True, '没有找到名称为“%s”的计分项' % cmdargs[2]
			if not compCmd.SetCommand('/scoreboard players test "%s" "%s" * *' % (cmdargs[3], cmdargs[2])):
				return True, '玩家%s没有分数记录' % cmdargs[3]
			low = -2**31
			high = 2**31 - 1
			while low < high:
				mid = (low + high) // 2
				if compCmd.SetCommand('/scoreboard players test "%s" "%s" %s %s' % (cmdargs[3], cmdargs[2], low, mid)):
					high = mid
				else:
					low = mid + 1
			params = compExtra.GetExtraData('parameters')
			if isinstance(params, dict):
				params.update({cmdargs[1]:{'type':'int','value':int(low)}})
			else:
				params = {cmdargs[1]:{'type':'int','value':int(low)}}
			compExtra.SetExtraData('parameters', params)
			return False, '将 %s 中 %s 的值(%s)写入变量 %s' % (cmdargs[2], cmdargs[3], low, cmdargs[1])

	def setblocknbt(self, cmdargs, playerId, variant, data):
		x, y, z = cmdargs[0]
		xyz = (intg(x), int(y), intg(z))
		if cmdargs[2] is None:
			return False, 'Pos%s 处的方块NBT为\n%s' % (xyz, CF.CreateBlockInfo(levelId).GetBlockEntityData(cmdargs[1]['id'], xyz))
		else:
			result = checkjson(cmdargs[2])
			if result[1] == True:
				return True, result[0]
			blockDict = result[0]
			CF.CreateBlockInfo(levelId).SetBlockEntityData(cmdargs[1]['id'], xyz, blockDict)
			return False, '已设置 Pos%s 的方块nbt' % (xyz,)

	def summonitem(self, cmdargs, playerId, variant, data):
		result = checkjson(cmdargs[1])
		if result[1] == True:
			return True, result[0]
		itemDict = result[0]
		if isinstance(itemDict, dict):
			x, y, z = cmdargs[0]
			xyz = (intg(x), int(y), intg(z))
			itemDict.setdefault('count', 1)
			if itemDict.get('newItemName') is None:
				return True, '物品数据中缺少 newItemName 键'
			if not self.CreateEngineItemEntity(itemDict, data['origin']['dimension'], xyz):
				return True, '生成失败'
			return False, '已在 Pos%s 处生成 %s * %s' % (xyz, itemDict.get('newItemName'), itemDict.get('count'))
		return True, '无效的nbt'
	
	def mute(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateExtraData(i).SetExtraData('mute', cmdargs[1])
		return False, '将 %s 的禁言状态设置为 %s' % (create_players_str(cmdargs[0]), '启用' if cmdargs[1] else '停用')
	
	def chatclear(self, cmdargs, playerId, variant, data):
		if playerId is None:
			return True, '该命令无法在命令方块或控制台执行'	
		self.NotifyToClient(playerId, 'CustomCommandClient', {'cmd': 'chatclear'})
		return False, ''
	
	def openui(self, cmdargs, playerId, variant, data):
		if playerId:
			self.NotifyToClient(playerId, 'CustomCommandClient', {'cmd': 'openui', 'cmdargs': cmdargs})
			return False, ''
		else:
			return True, '执行者必须为玩家'
	
	def gettps(self, cmdargs, playerId, variant, data):
		tick_time = serverApi.GetServerTickTime()
		TPS = "20.0*" if tick_time <= 50 else "%.1f" % (1000 / tick_time)
		if playerId:
			CF.CreateMsg(playerId).NotifyOneMessage(playerId, '§r§eTPS:%s mspt:%.2fms' % (TPS, tick_time))
		return False,''
	
	def copyright(self, cmdargs, playerId, variant, data):
		if playerId:
			CF.CreateMsg(playerId).NotifyOneMessage(playerId,copyRightInfo)
		return False, ''
	
	def chatlimit(self, cmdargs, playerId, variant, data):
		if variant == 0:
			if cmdargs[1] < 0:
				return True, '发言间隔不能小于0'
			if compExtra.SetExtraData('limitFrequency', cmdargs[1]):
				return False, '已将发言间隔限制设置为 %.1f 秒' % cmdargs[1]
			else:
				return True, '设置失败'
		elif variant == 1:
			if cmdargs[1] < 0:
				return True, '消息长度不能小于0'
			if compExtra.SetExtraData('limitLength', cmdargs[1]):
				return False, '已将消息长度限制设置为 %d 个字符' % cmdargs[1]
			else:
				return True, '设置失败'
		
	def allowmsg(self, cmdargs, playerId, variant, data):
		if cmdargs[0]:
			compExtra.SetExtraData('allow_msg', True)
			return False, '已允许玩家间私聊'
		else:
			compExtra.SetExtraData('allow_msg', False)
			return False, '已禁止玩家间私聊'

	def summonnbt(self, cmdargs, playerId, variant, data):
		#result = checkjson(cmdargs[2])
		#if result[1] == True:
		#	return True, result[0]
		#entityDict = result[0]
		#entityDict['identifier'] = {'__type__': 8,'__value__': cmdargs[0]['entityType']}
		#if entityDict.get('Rotation') is None:
		#	rot = (0, 0)
		#else:
		#	rot = None
		#print(entityDict, cmdargs[1], rot, cmdargs[3]['id'], cmdargs[4])
		#self.CreateEngineEntityByNBT(entityDict, cmdargs[1], rot, cmdargs[3]['id'], cmdargs[4])
		#return False, '已生成实体'
		pass

	def hidenametag(self, cmdargs, playerId, variant, data):
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		self.NotifyToMultiClients(cmdargs[0], 'CustomCommandClient', {'cmd':'hidenametag', 'cmdargs': cmdargs})
		return False, '已%s %s 的可见悬浮字' % ('隐藏' if cmdargs[1] else '显示', create_players_str(cmdargs[0]))

	def Cancel_Structure_Loading(self, cmdargs, playerId, variant, data):
		packet = {
			"playerId": playerId
		}
		self.BroadcastEvent('cancel_structure_loading', packet)
		return False, ''
	
	def setoplevel(self, cmdargs, playerId, variant, data):
		oplevel = cmdargs[0]
		if oplevel not in [2, 3, 4]:
			return True, '无效的命令权限等级'
		compCmd.SetCommandPermissionLevel(oplevel)
		compExtra.SetExtraData("gtmb-op-level", oplevel)
		oplevels = {2: '可以使用所有单人游戏作弊命令', 3: '可以使用大多数多人游戏中独有的命令', 4: '可以使用所有命令'}
		return False, '已将命令权限等级设置为 %s 级（%s）。请重新获取命令权限以应用更改。' % (oplevel, oplevels[oplevel])
	
	def opset(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		if cmdargs[1] == 'visitor': # 访客
			for i in cmdargs[0]:
				compPlayer = CF.CreatePlayer(i)
				compPlayer.SetPermissionLevel(0)
			return False, '已将 %s 的权限设置为 访客' % create_players_str(cmdargs[0])
		elif cmdargs[1] == 'member': # 成员
			for i in cmdargs[0]:
				compPlayer = CF.CreatePlayer(i)
				compPlayer.SetPermissionLevel(1)
			return False, '已将 %s 的权限设置为 成员' % create_players_str(cmdargs[0])
		elif cmdargs[1] == 'operator': # 管理员
			for i in cmdargs[0]:
				compPlayer = CF.CreatePlayer(i)
				compPlayer.SetPermissionLevel(2)
			return False, '已将 %s 的权限设置为 管理员' % create_players_str(cmdargs[0])
		else:
			return True, '未知错误'
		
	def setlobbymod(self, cmdargs, playerId, variant, data):
		if variant == 0: # 我的伙伴-全局
			is_enabled = cmdargs[1]
			compExtra.SetExtraData('lobby-enable-pet', is_enabled)
			if is_enabled:
				CF.CreatePet(levelId).Enable()
			else:
				CF.CreatePet(levelId).Disable()
			return False, '已全局 %s 我的伙伴，请重载存档。' % ('启用' if is_enabled else '禁用')
		elif variant == 1: # 我的好友
			if cmdargs[1] is None:
				return True, '没有与选择器匹配的目标'
			if not check_entities_type('minecraft:player', cmdargs[1]):
				return True, '选择器必须为玩家类型'
			is_enabled = cmdargs[2]
			if is_enabled:
				for i in cmdargs[1]:
					CF.CreateExtraData(i).SetExtraData('lobby-chat-extension', True)
					CF.CreateChatExtension(i).Enable()
			else:
				for i in cmdargs[1]:
					CF.CreateExtraData(i).SetExtraData('lobby-chat-extension', False)
					CF.CreateChatExtension(i).Disable()
			return False, '已 %s %s 的我的好友聊天扩展' % ('启用' if is_enabled else '禁用', create_players_str(cmdargs[1]))
		elif variant == 2: # 魔法指令
			if cmdargs[1] is None:
				return True, '没有与选择器匹配的目标'
			if not check_entities_type('minecraft:player', cmdargs[1]):
				return True, '选择器必须为玩家类型'
			is_enabled = cmdargs[2]
			if is_enabled:
				for i in cmdargs[1]:
					CF.CreateExtraData(i).SetExtraData('lobby-ai-command', True)
					CF.CreateAiCommand(i).Enable()
			else:
				for i in cmdargs[1]:
					CF.CreateExtraData(i).SetExtraData('lobby-ai-command', False)
					CF.CreateAiCommand(i).Disable()
			return False, '已 %s %s 的魔法指令' % ('启用' if is_enabled else '禁用', create_players_str(cmdargs[1]))
		elif variant == 3: # 我的好友-全局
			is_enabled = cmdargs[1]
			compExtra.SetExtraData('lobby-enable-chat-extension', is_enabled)
			for i in serverApi.GetPlayerList():
				if is_enabled:
					CF.CreateChatExtension(i).Enable()
				else:
					CF.CreateChatExtension(i).Disable()
			return False, '已全局 %s 我的好友聊天扩展，请重载存档。' % ('启用' if is_enabled else '禁用')
		elif variant == 4: # 魔法指令-全局
			is_enabled = cmdargs[1]
			compExtra.SetExtraData('lobby-enable-ai-command', is_enabled)
			for i in serverApi.GetPlayerList():
				if is_enabled:
					CF.CreateAiCommand(i).Enable()
				else:
					CF.CreateAiCommand(i).Disable()
			return False, '已全局 %s 魔法指令，请重载存档。' % ('启用' if is_enabled else '禁用')
	
	def eula(self, cmdargs, playerId, variant, data):
		if playerId is None:
			return True, '该命令无法在命令方块或控制台执行'	
		self.NotifyToClient(playerId, 'CustomCommandClient', {'cmd': 'eula'})
		return False, ''
	
	def hub(self, cmdargs, playerId, variant, data):
		if playerId is None:
			return True, '该命令无法在命令方块或控制台执行。'	
		if variant == 0:  # hub主城
			LobbyXYZ = compExtra.GetExtraData('lobby-xyz')
			# HubXYZ格式: (dimension, (x, y, z))
			if LobbyXYZ is None:
				return True, '管理员未配置主城坐标。'
			dimension = LobbyXYZ[0]
			coordinates = LobbyXYZ[1]
			CF.CreateDimension(playerId).ChangePlayerDimension(dimension, coordinates)
			return False, ''
		elif variant == 1:  # hub set
			if not CF.CreatePlayer(playerId).GetPlayerOperation() == 2:
				return True, '你没有权限执行该命令。'
			xyz = cmdargs[1]
			dimension = cmdargs[2]["id"]
			dimName = cmdargs[2]["name"]
			compExtra.SetExtraData('lobby-xyz', (dimension, xyz))
			return False, '已将主城坐标设置为 %s, 维度: %s' % (xyz, dimName)
		elif variant == 2:  # hub clear
			if not CF.CreatePlayer(playerId).GetPlayerOperation() == 2:
				return True, '你没有权限执行该命令'
			compExtra.SetExtraData('lobby-xyz', None)
			return False, '已清除主城坐标设置。'

	def lobby(self, cmdargs, playerId, variant, data):
		if playerId is None:
			return True, '该命令无法在命令方块或控制台执行'	
		if variant == 0:  # 和hub基本一致
			LobbyXYZ = compExtra.GetExtraData('lobby-xyz')
			# LobbyXYZ格式: (dimension, (x, y, z))
			if LobbyXYZ is None:
				return True, '管理员未配置主城坐标。'
			dimension = LobbyXYZ[0]
			coordinates = LobbyXYZ[1]
			CF.CreateDimension(playerId).ChangePlayerDimension(dimension, coordinates)
			return False, ''
		elif variant == 1:  # lobby set
			if not CF.CreatePlayer(playerId).GetPlayerOperation() == 2:
				return True, '你没有权限执行该命令。'
			xyz = cmdargs[1]
			dimension = cmdargs[2]["id"]
			dimName = cmdargs[2]["name"]
			compExtra.SetExtraData('lobby-xyz', (dimension, xyz))
			return False, '已将主城坐标设置为 %s, 维度: %s' % (xyz, dimName)
		elif variant == 2:  # lobby clear
			if not CF.CreatePlayer(playerId).GetPlayerOperation() == 2:
				return True, '你没有权限执行该命令'
			compExtra.SetExtraData('lobby-xyz', None)
			return False, '已清除主城坐标设置。'
		
	def setplayercanfly(self, cmdargs, playerId, variant, data):
		if cmdargs[0] is None:
			return True, '没有与选择器匹配的目标'
		if not check_entities_type('minecraft:player', cmdargs[0]):
			return True, '选择器必须为玩家类型'
		for i in cmdargs[0]:
			CF.CreateFly(i).ChangePlayerFlyState(cmdargs[1],False)
		return False, '将 %s 的飞行权限设置为 %s' % (create_players_str(cmdargs[0]), '允许' if cmdargs[1] else '禁止')	


	#服务端函数部分到此结束


	# 调试用，正式版请删除
	# commit: 多好的东西
	def debug(self, cmdargs, playerId, variant, data):
		if CF.CreateEngineType(playerId).GetEngineTypeStr() != 'minecraft:player' or CF.CreateName(playerId).GetName() not in ['ffdgd', 'EGGYLAN_', 'EGGYLAN', '王培衡很丁丁']:
			return True, '未知的命令:gtmbdebug。请检查命令是否存在，以及你对它是否拥有使用权限'
		if cmdargs[0] == 'throw':
			raise Exception('This is a debug exception!')
		elif cmdargs[0] == 'getextra':
			return False, str(compExtra.GetWholeExtraData())
		elif cmdargs[0] == 'showfile':
			try:
				with open(cmdargs[1]) as f:
					lines = f.readlines()
					return False, '文件 %s\n的第%s行如下\n%s' % (cmdargs[1], cmdargs[2], lines[int(cmdargs[2])-1])
			except IOError as e:
				return True, '读取文件 %s 时发生错误: %s' % (cmdargs[1], str(e))
		elif cmdargs[0] == 'writefile':
			try:
				with open(cmdargs[1], 'r+') as f:
					file = f.readlines()
					file[int(cmdargs[2])-1] = cmdargs[3] + '\n'
					f.seek(0)
					f.writelines(file)
				return False, '已修改文件 %s\n的第%s行内容为\n%s' % (cmdargs[1], cmdargs[2], cmdargs[3])
			except IOError as e:
				return True, '修改文件 %s 时发生错误: %s' % (cmdargs[1], str(e))	
	
