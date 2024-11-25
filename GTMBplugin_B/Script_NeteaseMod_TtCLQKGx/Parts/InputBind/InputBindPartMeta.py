# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.TypeMeta import PBool, PStr, PInt, PCustom, PVector3, PVector3TF, PEnum, PDict, PFloat, PArray, PVector2
from Preset.Model import PartBaseMeta
from Preset.Parts.PartCommon import KeyBoardType


@sunshine_class_meta
class InputBindPartMeta(PartBaseMeta):
	CLASS_NAME = "InputBindPart"
	PROPERTIES = {
		'inputBindings': PArray(sort=6, text='按键绑定', childAttribute=PDict(
			sort=1, text='绑定事件', children={
				'customEvent': PStr(sort=1, text='自定义事件'),
				'bindings': PArray(sort=2, text='绑定系统按键', childAttribute=PEnum(
					text="系统按键",
					sort=1,
					func=lambda obj: {'enumData': KeyBoardType}
				)),
			}
		))
	}
