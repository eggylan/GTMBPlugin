# -*- coding: utf-8 -*-
import math
import operator
import ast

STATUS_ATTRS = {
	'health': 0, 'speed': 1, 'damage': 2, 'underwater_speed': 3,
	'hunger': 4, 'saturation': 5, 'absorption': 6, 'lava_speed': 7,
	'luck': 8, 'follow_range': 9, 'knockback_resistance': 10,
	'jump_strength': 11, 'armor': 12, 'attack_knockback': 13,
	'attack_speed': 14, 'explosion_knockback_resistance': 15,
	'flying_speed': 16, 'sneaking_speed': 17, 'movement_efficiency': 18,
	'water_movement_efficiency': 19, 'block_break_speed': 20,
	'mining_efficiency': 21, 'submerged_mining_speed': 22,
}

STATUS_SIMPLE_ENTITY_READERS = {
	'attack_target': ('CreateAction', 'GetAttackTarget'),
	'type_family': ('CreateAttr', 'GetTypeFamily'),
	'air_unit_bubble': ('CreateBreath', 'GetUnitBubbleAirSupply'),
	'consuming_air': ('CreateBreath', 'IsConsumingAirSupply'),
	'collision_size': ('CreateCollisionBox', 'GetSize'),
	'ai_blocked': ('CreateControlAi', 'GetBlockControlAi'),
	'entity_owner': ('CreateActorOwner', 'GetEntityOwner'),
	'aux_value': ('CreateAuxValue', 'GetAuxValue'),
	'bullet_source': ('CreateBulletAttributes', 'GetSourceEntityId'),
	'engine_type_id': ('CreateEngineType', 'GetEngineType'),
	'entity_event_components': ('CreateEntityEvent', 'GetComponents'),
	'death_time': ('CreateEntityDefinitions', 'GetDeathTime'),
	'fall_distance': ('CreateEntityDefinitions', 'GetEntityFallDistance'),
	'entity_definitions': ('CreateEntityDefinitions', 'GetEntityDefinitions'),
	'entity_links': ('CreateEntityDefinitions', 'GetEntityLinksTag'),
	'leash_holder': ('CreateEntityDefinitions', 'GetLeashHolder'),
	'mark_variant': ('CreateEntityDefinitions', 'GetMarkVariant'),
	'mob_color': ('CreateEntityDefinitions', 'GetMobColor'),
	'mob_strength': ('CreateEntityDefinitions', 'GetMobStrength'),
	'max_mob_strength': ('CreateEntityDefinitions', 'GetMobStrengthMax'),
	'trade_level': ('CreateEntityDefinitions', 'GetTradeLevel'),
	'variant': ('CreateEntityDefinitions', 'GetVariant'),
	'has_chest': ('CreateEntityDefinitions', 'HasChest'),
	'has_saddle': ('CreateEntityDefinitions', 'HasSaddle'),
	'angry': ('CreateEntityDefinitions', 'IsAngry'),
	'baby': ('CreateEntityDefinitions', 'IsBaby'),
	'eating': ('CreateEntityDefinitions', 'IsEating'),
	'illager_captain': ('CreateEntityDefinitions', 'IsIllagerCaptain'),
	'loot_dropped': ('CreateEntityDefinitions', 'IsLootDropped'),
	'naturally_spawned': ('CreateEntityDefinitions', 'IsNaturallySpawned'),
	'out_of_control': ('CreateEntityDefinitions', 'IsOutOfControl'),
	'persistent': ('CreateEntityDefinitions', 'IsPersistent'),
	'pregnant': ('CreateEntityDefinitions', 'IsPregnant'),
	'roaring': ('CreateEntityDefinitions', 'IsRoaring'),
	'sheared': ('CreateEntityDefinitions', 'IsSheared'),
	'sitting': ('CreateEntityDefinitions', 'IsSitting'),
	'stunned': ('CreateEntityDefinitions', 'IsStunned'),
	'tamed': ('CreateEntityDefinitions', 'IsTamed'),
	'orb_experience': ('CreateExp', 'GetOrbExperience'),
	'gravity': ('CreateGravity', 'GetGravity'),
	'jump_power': ('CreateGravity', 'GetJumpPower'),
	'all_enchants': ('CreateItem', 'GetAllEnchantsInfo'),
	'selected_slot': ('CreateItem', 'GetSelectSlotId'),
	'fish_hook': ('CreateItem', 'GetPlayerFishHookEntity'),
	'model_name': ('CreateModel', 'GetModelName'),
	'quaternion': ('CreatePhysx', 'GetQuaternion'),
	'entity_scale': ('CreateScale', 'GetEntityScale'),
	'rider': ('CreateRide', 'GetEntityRider'),
	'riders': ('CreateRide', 'GetRiders'),
	'is_riding': ('CreateRide', 'IsEntityRiding'),
	'tame_owner': ('CreateTame', 'GetOwnerId'),
}

# 纯数字字面量（"1"、"-2.5"、"1e3"）也算数学表达式：get_status / set_status 的
# 表达式判定原本只看运算符与 math. 前缀，会把裸数字当成未知状态名。
STATUS_MATH_LITERAL = r'[+\-]?(\d+\.?\d*|\.\d+)([eE][+\-]?\d+)?$'

STATUS_MATH_FUNCTIONS = {
	'abs': abs, 'sqrt': math.sqrt, 'floor': math.floor, 'ceil': math.ceil,
	'round': round, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
	'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
	'atan2': math.atan2, 'log': math.log, 'log10': math.log10,
	'exp': math.exp, 'pow': math.pow, 'min': min, 'max': max,
	'trunc': lambda value: int(value), 'degrees': math.degrees, 'radians': math.radians,
	'hypot': math.hypot, 'sign': lambda value: 1 if value > 0 else (-1 if value < 0 else 0),
	'clamp01': lambda value: max(0, min(1, value)),
	'clamp': lambda value, low, high: max(low, min(high, value)),
	'lerp': lambda start, end, amount: start + (end - start) * amount,
}

STATUS_MATH_BINOPS = {
	ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
	ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
	ast.BitAnd: operator.and_, ast.BitOr: operator.or_, ast.BitXor: operator.xor,
	ast.LShift: operator.lshift, ast.RShift: operator.rshift,
}

STATUS_MATH_CMPOPS = {
	ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
	ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
}

STATUS_VECTOR_ROOTS = {
	'position': ('foot_xyz', {'x': 0, 'y': 1, 'z': 2}),
	'pos': ('foot_xyz', {'x': 0, 'y': 1, 'z': 2}),
	'xyz': ('foot_xyz', {'x': 0, 'y': 1, 'z': 2}),
	'foot_position': ('foot_xyz', {'x': 0, 'y': 1, 'z': 2}),
	'foot_pos': ('foot_xyz', {'x': 0, 'y': 1, 'z': 2}),
	'foot_xyz': ('foot_xyz', {'x': 0, 'y': 1, 'z': 2}),
	'velocity': ('velocity', {'x': 0, 'y': 1, 'z': 2}),
	'motion': ('velocity', {'x': 0, 'y': 1, 'z': 2}),
	'rotation': ('rotxy', {'x': 0, 'pitch': 0, 'y': 1, 'yaw': 1}),
	'rot': ('rotxy', {'x': 0, 'pitch': 0, 'y': 1, 'yaw': 1}),
	'rotxy': ('rotxy', {'x': 0, 'pitch': 0, 'y': 1, 'yaw': 1}),
}

STATUS_PLAYER_SETTERS = {
	'current_exhaustion': ('SetPlayerCurrentExhaustionValue', 'number'),
	'exhaustion': ('SetPlayerCurrentExhaustionValue', 'number'),
	'max_exhaustion': ('SetPlayerMaxExhaustionValue', 'number'),
	'health_level': ('SetPlayerHealthLevel', 'integer'),
	'starve_level': ('SetPlayerStarveLevel', 'integer'),
	'health_tick': ('SetPlayerHealthTick', 'integer'),
	'starve_tick': ('SetPlayerStarveTick', 'integer'),
	'natural_regen': ('SetPlayerNaturalRegen', 'bool'),
	'natural_starve': ('SetPlayerNaturalStarve', 'bool'),
	'jumpable': ('SetPlayerJumpable', 'bool'),
	'movable': ('SetPlayerMovable', 'bool'),
	'attack_mobs': ('SetAttackMobsAbility', 'bool'),
	'attack_players': ('SetAttackPlayersAbility', 'bool'),
	'build_ability': ('SetBuildAbility', 'bool'),
	'mine_ability': ('SetMineAbility', 'bool'),
	'open_containers': ('SetOpenContainersAbility', 'bool'),
	'operate_doors': ('SetOperateDoorsAndSwitchesAbility', 'bool'),
	'operator_commands': ('SetOperatorCommandAbility', 'bool'),
	'teleport_ability': ('SetTeleportAbility', 'bool'),
	'muted': ('SetPlayerMute', 'bool'),
	'permission': ('SetPermissionLevel', 'integer'),
	'game_type': ('SetPlayerGameType', 'integer'),
	'interact_range': ('SetPlayerInteracteRange', 'number'),
	'pickup_area': ('SetPickUpArea', 'number'),
	'attack_speed_amplifier': ('SetPlayerAttackSpeedAmplifier', 'number'),
	'ban_fishing': ('SetBanPlayerFishing', 'bool'),
}

ABILITY_ALIASES = {
	'canfly': 'can_fly', 'can_fly': 'can_fly', 'fly': 'can_fly', 'is_player_can_fly': 'can_fly',
	'isflying': 'is_flying', 'is_flying': 'is_flying', 'flying': 'is_flying', 'jump': 'jumpable',
	'move': 'movable', 'attackmobs': 'attack_mobs', 'attackplayers': 'attack_players',
	'build': 'build_ability', 'mine': 'mine_ability', 'opencontainers': 'open_containers',
	'operatedoors': 'operate_doors', 'operatorcommands': 'operator_commands',
	'teleport': 'teleport_ability',
}

# 可读布尔能力 → GetPlayerAbilities() 字典键。引擎只为这些能力提供了 setter，
# 读取只能靠该字典；movable / jumpable / operator_commands 没有读取来源，只能写。
ABILITY_READ_KEYS = {
	'build_ability': 'build',
	'mine_ability': 'mine',
	'teleport_ability': 'teleport',
	'open_containers': 'opencontainers',
	'operate_doors': 'doorsandswitches',
	'attack_mobs': 'attackmobs',
	'attack_players': 'attackplayers',
}

SIMPLE_ENTITY_BOOL_SETTERS = {
	'persistent': ('CreateAttr', 'SetPersistent'),
	'sitting': ('CreateEntityDefinitions', 'SetSitting'),
	'sheared': ('CreateEntityDefinitions', 'SetSheared'),
	'loot_dropped': ('CreateEntityDefinitions', 'SetLootDropped'),
	'actor_pushable': ('CreateActorPushable', 'SetActorPushable'),
	'actor_collidable': ('CreateActorCollidable', 'SetActorCollidable'),
}

STATUS_EXTERN_NAMES = {
	'forward', 'backward', 'leftward', 'rightward',
	'rising', 'falling', 'downing',
	# climbing 需要客户端 IsOnLadder，服务端 query.is_on_ladder 不受支持，见 client.on_ladder
}

UI_NAMES = {'enchant': ('enchantUI', 'enchant.main_closable'),
  		'getitem': ('getitemUI', 'getitem.main_closable'),
		'itemTips': ('itemTips', 'customtips.main_closable'),
		'nbteditor': ('nbteditor', 'nbteditor.main_closable'),
		'cmdbatch': ('cmdbatch', 'cmdbatch.main_closable'),
		'struimport': ('importstrulogic', 'structureimport.main'),
		'EULA': ('EULA', 'GTMB_EULA.main')}