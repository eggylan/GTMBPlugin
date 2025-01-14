# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass


@registerGenericClass("customcmdsPart")
class customcmdsPart(PartBase):
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "自定义指令零件"

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		import mod.client.extraClientApi as clientApi
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		clientsystem.ListenForEvent("Minecraft", "preset", "CustomCommandClient", self, self.OnCustomCommandClient)
		PartBase.InitClient(self)

	def OnCustomCommandClient(self, args):
		import mod.client.extraClientApi as clientApi
		clientsystem = clientApi.GetSystem("Minecraft", "preset")
		CF = clientApi.GetEngineCompFactory()
		if args['cmd'] == 'setplayerinteracterange':
			clientApi.GetEngineCompFactory().CreatePlayer(args['target']).SetPickRange(args['cmdargs'][1])
		
		# clientsystem.NotifyToServer("customCmdReturn", data)

	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		serversystem.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "CustomCommandTriggerServerEvent", self, self.OnCustomCommand)
		serversystem.ListenForEvent("Minecraft", "preset", "customCmdReturn", self, self.OnReturn)
		PartBase.InitServer(self)

	def OnReturn(self, args):
		import mod.server.extraServerApi as serverApi
		CF = serverApi.GetEngineCompFactory()
		compMsg = CF.CreateMsg(args['target'])
		compName = CF.CreateName(args['__id__'])

	def OnCustomCommand(self, args):
		import mod.server.extraServerApi as serverApi
		serversystem = serverApi.GetSystem("Minecraft", "preset")
		CF = serverApi.GetEngineCompFactory()
		levelId = serverApi.GetLevelId()
		compcmd = CF.CreateCommand(levelId)
		compGame = serverApi.GetEngineCompFactory().CreateGame(levelId)
		command = args['command']

		cmdargs = []
		for i in args["args"]:
			cmdargs.append(i["value"])

		try:
			playerId = args['origin']['entityId']
		except:
			playerId = None
		
		if command == 'setinvitemexchange':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				CF.CreateItem(i).SetInvItemExchange(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功交换物品'
			return
		
		
		if command == 'setinvitemnum':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if cmdargs[2] < 0 or cmdargs[2] > 64:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的物品数量'
				return
			for i in cmdargs[0]:
				CF.CreateItem(i).SetInvItemNum(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功设置物品数量'
			return
		
		
		if command == 'setitemdefenceangle':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if cmdargs[1] not in [0,1,2,3]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的位置id'
				return
			if cmdargs[3] < 0 or cmdargs[3] > 180 or cmdargs[4] < 0 or cmdargs[4] > 180:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的角度'
				return
			for i in cmdargs[0]:
				CF.CreateItem(i).SetItemDefenceAngle(cmdargs[1],cmdargs[2],cmdargs[3],cmdargs[4])
			args['return_msg_key'] = '成功设置盾牌抵挡角度'
			return
		
		if command == 'setitemdurability':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if cmdargs[1] < 0 or cmdargs[1] > 32766:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的耐久度'
				return
			for i in cmdargs[0]:
				CF.CreateItem(i).SetItemDurability(2,0,cmdargs[1])
			args['return_msg_key'] = '成功设置物品耐久度'
			return
			
		
		if command == 'setitemmaxdurability':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if cmdargs[1] < 0 or cmdargs[1] > 32766:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的耐久度'
				return
			for i in cmdargs[0]:
				CF.CreateItem(i).SetItemMaxDurability(2,0,cmdargs[1],True)
			args['return_msg_key'] = '成功设置物品最大耐久度'
			return
		
		
		if command == 'setitemtierlevel':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if cmdargs[1] not in [0,1,2,3,4]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的等级'
				return
			for i in cmdargs[0]:
				itemdata = CF.CreateItem(i).GetPlayerItem(2, 0, True)
				CF.CreateItem(i).SetItemTierLevel(itemdata,cmdargs[1])
				CF.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
			args['return_msg_key'] = '成功设置物品等级'
			return
		
		if command == 'setitemtierspeed':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				itemdata = CF.CreateItem(i).GetPlayerItem(2, 0, True)
				CF.CreateItem(i).SetItemTierSpeed(itemdata,cmdargs[1])
				CF.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
			args['return_msg_key'] = '成功设置物品挖掘速度'
			return
		
		if command == 'setmaxstacksize':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if cmdargs[1] < 1 or cmdargs[1] > 64:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的堆叠数量'
				return
			for i in cmdargs[0]:
				itemdata = CF.CreateItem(i).GetPlayerItem(2, 0, True)
				CF.CreateItem(i).SetMaxStackSize(itemdata,cmdargs[1])
				CF.CreateItem(i).SpawnItemToPlayerCarried(itemdata, i)
			args['return_msg_key'] = '成功设置最大堆叠数量'
			return
		
		
		if command == 'playerexhaustionratio':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if cmdargs[1] not in [0, 1, 2, 3, 4, 9]:
				args['return_failed'] = True
				args['return_msg_key'] = '无效的行为id'
				return
			for i in cmdargs[0]:
				CF.CreatePlayer(i).SetPlayerExhaustionRatioByType(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功设置玩家饥饿度消耗倍率'
			return
		
		if command == 'setsigntextstyle':
			x, y, z = cmdargs[0]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			r,g,b = cmdargs[2]
			a = cmdargs[3]
			lighting = cmdargs[4]
			if cmdargs[5] is True:
				side = 1
			else:
				side = 0
			if CF.CreateBlockEntity(levelId).SetSignTextStyle((x,y,z),cmdargs[1],(r,g,b,a),lighting,side):
				args['return_msg_key'] = '设置告示牌文本样式成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
				return
		
		if command == 'setsignblocktext':
			x, y, z = cmdargs[0]
			if x < 0:
				x = int(x) - 1
			else:
				x = int(x)
			y = int(y)
			if z < 0:
				z = int(z) - 1
			else:
				z = int(z)
			if cmdargs[3] is True:
				side = 1
			else:
				side = 0
			if CF.CreateBlockInfo(levelId).SetSignBlockText((x,y,z),cmdargs[1],cmdargs[2],side):
				args['return_msg_key'] = '设置告示牌文本成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '设置失败'
				return

		if command == 'setplayerinteracterange':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				CF.CreatePlayer(i).SetPlayerInteracteRange(cmdargs[1])
				serversystem.NotifyToClient(i, "CustomCommandClient", {'cmd':"setplayerinteracterange", 'target': i, 'cmdargs': cmdargs})
			args['return_msg_key'] = '成功设置触及距离'
			return

		
		if command == 'summonprojectile':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			try:
				targetlen = len(cmdargs[7])
				target = cmdargs[7][0]
			except:
				targetlen = 1
				target = None
			if not targetlen == 1:
				args['return_failed'] = True
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				return
			
			for i in cmdargs[0]:
				param = {
					'position': cmdargs[2],
					'direction': cmdargs[3],
					'power': cmdargs[4],
					'gravity': cmdargs[5],
					'damage': cmdargs[6],
					'targetId': target,
					'isDamageOwner': cmdargs[8],
					'auxValue': cmdargs[9]
				}
				
				CF.CreateProjectile(levelId).CreateProjectileEntity(i, cmdargs[1], param)
			args['return_msg_key'] = '成功生成抛射物'
			return
		
		if command == 'setstepheight':
			if cmdargs[0]:
				for i in cmdargs[0]:
					CF.CreateAttr(i).SetStepHeight(cmdargs[1])
				args['return_msg_key'] = '成功设置能迈过的最大高度'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'

		if command == 'setsize':
			if cmdargs[0]:
				for i in cmdargs[0]:
					CF.CreateCollisionBox(i).SetSize((cmdargs[1],cmdargs[2]))
				args['return_msg_key'] = '成功设置碰撞箱'
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
			
		if command == 'playerchatprefix':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				if CF.CreateEngineType(i).GetEngineTypeStr() == 'minecraft:player':
					CF.CreateExtraData(i).SetExtraData('chatprefix', cmdargs[1])
				else:
					CF.CreateMsg(i).NotifyOneMessage(playerId, '非玩家实体无法设置聊天前缀', "§c")
			args['return_msg_key'] = '成功设置玩家聊天前缀'
			return
		
		if command == 'writehealthtoscoreboard':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CF.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				health = CF.CreateAttr(entity).GetAttrValue(0)
				health = int(round(health))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, health), False)
			args['return_msg_key'] = '成功将生命值写入计分板'
			return
			
		if command == 'writehungertoscoreboard':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CF.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				hunger = CF.CreateAttr(entity).GetAttrValue(4)
				hunger = int(round(hunger))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, hunger), False)
			args['return_msg_key'] = '成功将饥饿值写入计分板'
			return	

		if command == 'writearmortoscoreboard':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CF.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				armor = CF.CreateAttr(entity).GetAttrValue(12)
				armor = int(round(armor))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, armor), False)
			args['return_msg_key'] = '成功将盔甲值写入计分板'
			return
		
		if command == 'writespeedtoscoreboard':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			objects = compGame.GetAllScoreboardObjects()
			scoreboard_name = cmdargs[1]
			if not any(obj['name'] == scoreboard_name for obj in objects):
				args['return_failed'] = True
				args['return_msg_key'] = '未找到该计分板对象'
				return
			for entity in cmdargs[0]:
				name = CF.CreateName(entity).GetName()
				if name is None:
					name = '"' + str(entity) + '"'
				speed = CF.CreateAttr(entity).GetAttrValue(1)
				speed = int(round(speed))
				compcmd.SetCommand('/scoreboard players set %s %s %s' % (name, scoreboard_name, speed), False)
			args['return_msg_key'] = '成功将速度值写入计分板'
			return
		
		if command == 'executecb':
			success = CF.CreateBlockEntity(levelId).ExecuteCommandBlock((cmdargs[0], cmdargs[1], cmdargs[2]), cmdargs[3])
			if success:
				args['return_msg_key'] = '成功执行命令方块'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '执行命令方块失败'
				return
		
		if command == 'setname':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				CF.CreateName(i).SetName(cmdargs[1])
			args['return_msg_key'] = '成功设置名称'
			return
		
		if command == 'aicontrol':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				CF.CreateControlAi(i).SetBlockControlAi(cmdargs[1], cmdargs[2])
			args['return_msg_key'] = '成功设置实体AI'
			return
		
		if command == 'master':
			if cmdargs[0]:
				for i in cmdargs[0]:
					compExtra = CF.CreateExtraData(i)
					compExtra.SetExtraData("isMaster", True)
				args['return_msg_key'] = '锁定玩家权限成功'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return

		if command == 'demaster':
			if cmdargs[0]:
				for i in cmdargs[0]:
					compExtra = CF.CreateExtraData(i)
					compExtra.SetExtraData("isMaster", False)
				args['return_msg_key'] = '解锁玩家权限成功'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return
		
		compExtra = CF.CreateExtraData(serverApi.GetLevelId())
		params = compExtra.GetExtraData('parameters')
		input1 = cmdargs[0]
		if command == 'param':
			if cmdargs[0] is None:
				args['return_msg_key'] = str(params)
				return
			else:
				if type(params) == dict and params.has_key(cmdargs[0]):
					args['return_msg_key'] = "变量\"%s\"为 %s" % (input1, params[input1])
					return
				else:
					args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
					args['return_failed'] = True
					return

		if command == 'paramdel':
			if type(params) == dict and params.has_key(cmdargs[0]):
				args['return_msg_key'] = '删除变量成功'
				del params[input1]
				compExtra.SetExtraData('parameters', params)
				return
			else:
				args['return_msg_key'] = "未知的变量\"%s\"" % (input1)
				args['return_failed'] = True
				return

		if command == 'paramwrite':
			args['return_msg_key'] = '修改变量成功'
			input2 = cmdargs[1]
			if type(params) == dict:
				params[input1] = input2
			else:
				params = {input1: input2}
			compExtra.SetExtraData('parameters', params)
			return

		if command == 'kickt':
			if cmdargs[0]:
				for kickplayer in cmdargs[0]:
					CF.CreateCommand(serverApi.GetLevelId()).SetCommand('/kick ' + CF.CreateName(kickplayer).GetName() + ' ' + cmdargs[1], False)
				args['return_msg_key'] = '已踢出目标玩家'
				return
			else:
				args['return_msg_key'] = '没有与选择器匹配的目标'
				args['return_failed'] = True
				return
				
		if command == 'explode':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				position = CF.CreatePos(i).GetFootPos()
				CF.CreateExplosion(levelId).CreateExplosion(position,cmdargs[1],cmdargs[3],cmdargs[2],i,None)
			args['return_msg_key'] = '爆炸已成功创建'
			return
	
		if command == 'explodebypos':
			if CF.CreateExplosion(levelId).CreateExplosion(cmdargs[0],cmdargs[1],cmdargs[3],cmdargs[2],None,None):
				args['return_msg_key'] = '爆炸已成功创建'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '爆炸创建失败'
				return
	
		if command == "console":
			cmd = cmdargs[0]
			if cmd.startswith("/"):
				cmd = cmd[1:]
			cmd2 = ""
			if compExtra.GetExtraData('parameters'):
				for i in cmd.split(" "):
					for ii in compExtra.GetExtraData('parameters').keys():
						index = i.find("param:%s" % (ii))
						if not index == -1:
							i = compExtra.GetExtraData('parameters')[i[index+6:]]
					cmd2 = "%s %s" % (cmd2, i)
			else:
				cmd2 = cmd
			CF.CreateCommand(serverApi.GetLevelId()).SetCommand("/" + cmd2, False)
			args["return_msg_key"] = "已尝试将指令发送到控制台执行。"
			return
		
		if command == 'addaroundentitymotion' or command == 'addaroundpointmotion':
			if cmdargs[1] is None and command == 'addaroundentitymotion' or cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			if not len(cmdargs[1]) == 1 and command == 'addaroundentitymotion':
				args['return_msg_key'] = '只允许一个实体,但提供的选择器允许多个实体'
				args['return_failed'] = True
				return
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				CompType = CF.CreateEngineType(i)
				EntityType = CompType.GetEngineTypeStr()
				if command == 'addaroundentitymotion':
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
				else:
					if EntityType == 'minecraft:player':
						addMotion = CompMotion.AddPlayerAroundEntityMotion
					else:
						addMotion = CompMotion.AddEntityAroundEntityMotion
					Mid = addMotion(cmdargs[1],
									cmdargs[2],
									cmdargs[3],
									cmdargs[4],
									cmdargs[5])
				if Mid == -1:
					args['return_failed'] = True
					args['return_msg_key'] = '设置失败'
					return
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
			return

		if command == 'addvelocitymotion':
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
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
				if Mid == -1:
					args['return_failed'] = True
					args['return_msg_key'] = '创建失败'
					return
				Motions = compExtra.GetExtraData('Motions')
				if not Motions:
					Motions = []
				Motions.append(Mid)
				compExtra.SetExtraData('Motions', Motions)
			args['return_msg_key'] = '成功设置运动器'
			return
		
		if command == 'startmotion':
			args['return_msg_key'] = ''
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				CompType = CF.CreateEngineType(i)
				CompMsg = CF.CreateMsg(i)
				EntityType = CompType.GetEngineTypeStr()
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					if EntityType == 'minecraft:player':
						startMotion = CompMotion.StartPlayerMotion
					else:
						startMotion = CompMotion.StartEntityMotion
					for ii in Motions:
						startMotion(ii)
					CompMsg.NotifyOneMessage(playerId, '成功启用实体的运动器')
					return
				else :
					args['return_failed'] = True
					CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
					return
		
		if command == 'stopmotion':
			args['return_msg_key'] = ''
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				CompType = CF.CreateEngineType(i)
				CompMsg = CF.CreateMsg(i)
				EntityType = CompType.GetEngineTypeStr()
				Motions = compExtra.GetExtraData('Motions')
				if Motions:
					if EntityType == 'minecraft:player':
						stopMotion = CompMotion.StopPlayerMotion
					else:
						stopMotion = CompMotion.StopEntityMotion
					for ii in Motions:
						stopMotion(ii)
					CompMsg.NotifyOneMessage(playerId, '成功停止实体的运动器')
					return
				else:
					args['return_failed'] = True
					CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
					return
		
		if command == 'removemotion':
			args['return_msg_key'] = ''
			if cmdargs[0] is None:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return
			for i in cmdargs[0]:
				compExtra = CF.CreateExtraData(i)
				CompMotion = CF.CreateActorMotion(i)
				Motions = compExtra.GetExtraData('Motions')
				CompType = CF.CreateEngineType(i)
				CompMsg = CF.CreateMsg(i)
				EntityType = CompType.GetEngineTypeStr()
				if Motions:
					if EntityType == 'minecraft:player':
						removeMotion = CompMotion.RemovePlayerMotion
					else:
						removeMotion = CompMotion.RemoveEntityMotion
					for ii in Motions:
						removeMotion(ii)
						Motions.remove(ii)
					compExtra.SetExtraData('Motions', Motions)
					CompMsg.NotifyOneMessage(playerId, '成功移除实体的运动器')
					return
				else:
					args['return_failed'] = True
					CompMsg.NotifyOneMessage(playerId, '实体没有绑定运动器', "§c")
					return

		if command == 'addenchant':
			if cmdargs[0]:
				for i in cmdargs[0]:
					compItem = CF.CreateItem(i)
					if type(cmdargs[3]) == int:
						slotType = 0
						slot = cmdargs[3]
					else:
						slotType = 2
						slot = 0
					itemDict = compItem.GetPlayerItem(slotType, slot, True)
					if itemDict:
						if itemDict["userData"] is None:
							itemDict["userData"] = {}
						if itemDict["userData"].get('ench', None) is None:
							itemDict["userData"]['ench'] = []
						itemDict["userData"]['ench'].insert(0, {'lvl': {'__type__': 2, '__value__': cmdargs[2]}, 
											  					'id':  {'__type__': 2, '__value__': cmdargs[1]}, 
																'modEnchant': {'__type__': 8, '__value__': ''}})
						itemDict["enchantData"] = []
					else:
						args['return_failed'] = True
						args['return_msg_key'] = '该槽位没有物品或没有该槽位'
						return
					if slotType == 0:
						compItem.SpawnItemToPlayerInv(itemDict, i, slot)
					else:
						compItem.SpawnItemToPlayerCarried(itemDict, i)
					args['return_msg_key'] = '添加附魔成功'
					return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return

		if command == 'addtrackmotion':
			if cmdargs[0]:
				for i in cmdargs[0]:
					compExtra = CF.CreateExtraData(i)
					CompMotion = CF.CreateActorMotion(i)
					CompType = CF.CreateEngineType(i)
					EntityType = CompType.GetEngineType()
					if EntityType == 63:
						addMotion = CompMotion.AddPlayerTrackMotion
					else:
						addMotion = CompMotion.AddEntityTrackMotion
					Mid = addMotion(cmdargs[1],
									cmdargs[2],
									None,
									False,
									cmdargs[3],
									cmdargs[5],
									cmdargs[4],
									cmdargs[6])
					if Mid == -1:
						args['return_failed'] = True
						args['return_msg_key'] = '创建失败'
						return
					Motions = compExtra.GetExtraData('Motions')
					if not Motions:
						Motions = []
					Motions.append(Mid)
					compExtra.SetExtraData('Motions', Motions)
				args['return_msg_key'] = '成功设置运动器'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return

		if command == 'setactorcanburnbylightning':
			compGame.SetCanActorSetOnFireByLightning(cmdargs[0])
			args['return_msg_key'] = '设置成功'
			return

		if command == 'setblockcanburnbylightning':
			compGame.SetCanBlockSetOnFireByLightning(cmdargs[0])
			args['return_msg_key'] = '设置成功'
			return

		if command == 'cancelshearsdestoryblockspeedall':
			if cmdargs[0]:
				for i in cmdargs[0]:
					compItem = CF.CreateItem(i)
					compItem.CancelShearsDestoryBlockSpeedAll()
				args['return_msg_key'] = '取消成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return

		if command == 'cancelshearsdestoryblockspeed':
			if cmdargs[0]:
				for i in cmdargs[0]:
					compItem = CF.CreateItem(i)
					if not compItem.CancelShearsDestoryBlockSpeed(cmdargs[1]):
						args['return_failed'] = True
						args['return_msg_key'] = '无效的命名空间id'
				args['return_msg_key'] = '取消成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return

		if command == 'setshearsdestoryblockspeed':
			if cmdargs[0]:
				if cmdargs[2] < 1:
					args['return_failed'] = True
					args['return_msg_key'] = '速度必须大于1'
					return
				for i in cmdargs[0]:
					compItem = CF.CreateItem(i)
					if not compItem.SetShearsDestoryBlockSpeed(cmdargs[1], cmdargs[2]):
						args['return_failed'] = True
						args['return_msg_key'] = '无效的命名空间id'
				args['return_msg_key'] = '设置成功'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '没有与选择器匹配的目标'
				return

		if command == 'changeselectslot':
			for i in cmdargs[0]:
				CompType = CF.CreateEngineType(i)
				EntityType = CompType.GetEngineTypeStr()
				if EntityType != "minecraft:player":
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法设置选择槽位'
					return
			for i in cmdargs[0]:
				CompPlayer = CF.CreatePlayer(i)
				CompPlayer.ChangeSelectSlot(cmdargs[1])
			args['return_msg_key'] = '设置成功'
			return

		if command == 'forbidliquidflow':
			if compGame.ForbidLiquidFlow(cmdargs[0]):
				args['return_msg_key'] = '已成功修改液体流动性'
				return
			else:
				args['return_failed'] = True
				args['return_msg_key'] = '修改失败'
				return

		if command == 'getuid':
			uid_dict = {}
			for i in cmdargs[0]:
				CompType = CF.CreateEngineType(i)
				if CompType.GetEngineTypeStr() != 'minecraft:player':
					args['return_failed'] = True
					args['return_msg_key'] = '非玩家实体无法获取uid'
					return
				playername = CF.CreateName(i).GetName()
				uid_dict[playername] = CF.CreateHttp(levelId).GetPlayerUid(i)
			args['return_msg_key'] = '获取到的UID为%s' % (uid_dict)
			return
			# serversystem.NotifyToMultiClients(list(cmdargs[0]), "CustomCommandClient", {'cmd':"getuid", 'origin': playerId})
	def TickClient(self):
		"""
		@description 客户端的零件对象逻辑驱动入口
		"""
		PartBase.TickClient(self)

	def TickServer(self):
		"""
		@description 服务端的零件对象逻辑驱动入口
		"""
		PartBase.TickServer(self)

	def DestroyClient(self):
		"""
		@description 客户端的零件对象销毁逻辑入口
		"""
		PartBase.DestroyClient(self)

	def DestroyServer(self):
		"""
		@description 服务端的零件对象销毁逻辑入口
		"""
		PartBase.DestroyServer(self)
