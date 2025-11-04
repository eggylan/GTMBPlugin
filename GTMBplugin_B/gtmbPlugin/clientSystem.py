# -*- coding: utf-8 -*-
import client.extraClientApi as clientApi
CF = clientApi.GetEngineCompFactory()

class mainClientSystem(clientApi.GetClientSystemCls()):
	def __init__(self, modName, systemName):
		super(mainClientSystem, self).__init__(modName, systemName)
		listenClientSysEvent = lambda eventId, callback: self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), eventId, self, callback)
		listenClientSysEvent('OnLocalPlayerStopLoading', self.OnFinish)
		listenClientSysEvent('OnKeyPressInGame', self.OnPressKey)
		self.uiNames = {'enchant': ['enchant', 'main_closable'],
				  		'getitem': ['getitem', 'main_closable'],
						'itemTips': ['customtips', 'main_closable'],
						'nbteditor': ['nbteditor', 'main_closable'],
						'cmdbatch': ['cmdbatch', 'main_closable'],
						'EULA': ['GTMB_EULA', 'main'],
						'struimport': ['structureimport', 'main_closable'],
						'functionBlockScreen': ['function_block_screen', 'node_screen'],
						'listenBlockScreen': ['function_block_screen', 'listen_screen']}

	def OnPressKey(self, args):
		if args['key'] == '27':
			if args['isDown']:
				if clientApi.GetTopUI().endswith('closable'): #这里只有插件可关闭的ui的画布叫做xxxx_closable
					clientApi.PopTopUI()

	def OnFinish(self, args):
		self.NotifyToServer('TryOpenEULA', {})