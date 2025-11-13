# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
CF = clientApi.GetEngineCompFactory()
localPlayerId = clientApi.GetLocalPlayerId()
levelId = clientApi.GetLevelId()
compPostProcess = CF.CreatePostProcess(levelId)
compDrawing = CF.CreateDrawing(levelId)
uiNames = {'enchant': ('enchantUI', 'enchant.main_closable'),
  		'getitem': ('getitemUI', 'getitem.main_closable'),
		'itemTips': ('itemTips', 'customtips.main_closable'),
		'nbteditor': ('nbteditor', 'nbteditor.main_closable'),
		'cmdbatch': ('cmdbatch', 'cmdbatch.main_closable'),
		'struimport': ('importstrulogic', 'structureimport.main'),
		'functionBlockScreen': ('functionBlockScreen', 'function_block_screen.node_screen'),
		'listenBlockScreen': ('listenBlockScreen', 'function_block_screen.listen_screen'),
		'EULA': ('EULA', 'GTMB_EULA.main')}

PLATFORM_WINDOWS = 0
PLATFORM_IOS = 1
PLATFORM_ANDROID = 2

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
		if self.is_UI_First_Init:
			self.is_UI_First_Init = False
			for i in uiNames:
				uiClsName = uiNames[i][0]
				clientApi.RegisterUI('gtmbPlugin', i, 'gtmbPlugin.uiScript.%s.%s' % (uiClsName, uiClsName), uiNames[i][1])
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
			"hidenametag": self.client_hidenametag
		}
		compPostProcess.SetEnableColorAdjustment(True)

	def OnCustomCommandClient(self, args):
		# 从dict中选取处理函数
		handler = self.clientCustomCmd.get(args['cmd'])
		if handler:
			handler(args)

	# 客户端函数部分由此开始
	def client_setplayerinteracterange(self, args):
		CF.CreatePlayer(localPlayerId).SetPickRange(args['cmdargs'][1])
	def client_openfoldgui(self, args):
		clientApi.OpenFoldGui()
	def client_setcanpausescreen(self, args):
		CF.CreateOperation(levelId).SetCanPauseScreen(args['cmdargs'][1])
	def client_setcolorbrightness(self, args):
		compPostProcess.SetColorAdjustmentBrightness(args['cmdargs'][2])
	def client_setcolorcontrast(self, args):
		compPostProcess.SetColorAdjustmentContrast(args['cmdargs'][2])
	def client_setcolorsaturation(self, args):
		compPostProcess.SetColorAdjustmentSaturation(args['cmdargs'][2])
	def client_setcolortint(self, args):
		compPostProcess.SetColorAdjustmentTint(args['cmdargs'][2], (args['cmdargs'][3], args['cmdargs'][4], args['cmdargs'][5]))
	def client_setcompassentity(self, args):
		CF.CreateItem(localPlayerId).SetCompassEntity(args['cmdargs'][1][0])
	def client_setcompasstarget(self, args):
		CF.CreateItem(localPlayerId).SetCompassTarget(args['cmdargs'][0], args['cmdargs'][1], args['cmdargs'][2])
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
	# 客户端函数部分到此结束

class functionBlockClientSystem(clientApi.GetClientSystemCls()):
	def __init__(self, modName, systemName):
		super(functionBlockClientSystem, self).__init__(modName, systemName)
		self.ListenForEvent('gtmbPlugin', 'functionBlockServerSystem', 'rendersFromServer', self, self.LoadRenders)

		self.currentRenders = []

	def LoadRenders(self, args):
		renderCreator = {'arrow': compDrawing.AddArrowShape,
						 'circle': compDrawing.AddCircleShape,
						 'line': compDrawing.AddLineShape,
						 'text': compDrawing.AddTextShape,
						 'box': compDrawing.AddBoxShape,
						 'sphere': compDrawing.AddSphereShape}
		for i in args['renders']:
			renderCreator[i['type']](**i['data'])