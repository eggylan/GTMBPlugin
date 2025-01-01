# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
'''
零件简介：
	输入绑定零件提供了通用的系统按键监听广播流程
逻辑简述：
	开发者可以在"按键绑定"属性中定义自定义事件以及唤起该事件所需要按下的系统按键。
	当某个按键被按下或抬起时，对应的自定义事件就会被广播。
	开发者可以在零件代码中调用零件的事件监听函数监听，或在mod代码中调用系统监听函数监听。
使用方法：
	1.通过属性面板设置自定义事件以及绑定的系统按键
	2.在需要的脚本中编写监听函数监听对应的自定义事件
	3.启动运行，查看回调运行情况
'''
@registerGenericClass("InputBindPart")
class InputBindPart(PartBase):
	def __init__(self):
		super(InputBindPart, self).__init__()
		self.name = "输入绑定零件"
		self.description = "输入绑定零件"
		self.inputBindings = [{'customEvent': 'closeui', 'bindings': [27]}]
		self.keyBoard2CustomEventDict = dict()
		self.mPlayerId = None
		self.clientSystem = None

	def InitClient(self):
		import mod.client.extraClientApi as clientApi
		customEventSet = set()
		if self.inputBindings:
			for inputBinding in self.inputBindings:
				customEvent = inputBinding["customEvent"]
				if customEvent:
					customEventSet.add(customEvent)
				bindings = inputBinding["bindings"]
				for binding in bindings:
					if binding in self.keyBoard2CustomEventDict.keys():
						self.keyBoard2CustomEventDict[str(binding)].add(customEvent)
					else:
						self.keyBoard2CustomEventDict[str(binding)] = set([customEvent])
		self.mPlayerId = clientApi.GetLocalPlayerId()
		for customEvent in customEventSet:
			self.GetSystem().DefineEvent(customEvent)
		self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "OnKeyPressInGame", self, self.OnKeyPressInGameCallback)

	def OnKeyPressInGameCallback(self, args):
		screenName = args["screenName"]
		key = str(args["key"])
		isDown = args["isDown"]
		if key in self.keyBoard2CustomEventDict.keys():
			targetCustomEvents = self.keyBoard2CustomEventDict[key]
			for event in targetCustomEvents:
				eventData = self.CreateEventData()
				eventData["id"] = self.mPlayerId
				eventData["screenName"] = screenName
				eventData["key"] = key
				eventData["isDown"] = isDown
				# 发送数据给服务端
				self.GetSystem().NotifyToServer(event, eventData)
				# 广播给客户端
				self.GetSystem().BroadcastEvent(event, eventData)
				# 发送数据给零件服务端
				self.NotifyToServer(event, eventData)
				# 广播给零件客户端
				self.BroadcastEvent(event, eventData)

	def DestroyClient(self):
		import mod.client.extraClientApi as clientApi
		self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "OnKeyPressInGame", self, self.OnKeyPressInGameCallback)
