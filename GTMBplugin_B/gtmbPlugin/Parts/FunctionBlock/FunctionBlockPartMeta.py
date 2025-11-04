# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.EnumMeta import DefEnum
from Meta.TypeMeta import PBool, PStr, PInt, PCustom, PVector3, PVector3TF, PEnum, PDict, PFloat, PArray, PVector2, PColor
from Preset.Model import PartBaseMeta


@sunshine_class_meta
class FunctionBlockPartMeta(PartBaseMeta):
	CLASS_NAME = "FunctionBlockPart"
	PROPERTIES = {
		#   "int1": PInt(text="整数1", sort=1, default=1, tip="这是个整数", group="分组1"),
		#   "float1": PFloat(text="浮点数1", sort=3, default=1.1),
		#   "bool1": PBool(text="Bool1", sort=5, default=False),
		#   "str2": PStr(text="字符串2", sort=8, default="default"),
		#   "enum1": PEnum(text="枚举1", sort=9, enumType="IntOption"),
		#   "vector2": PVector2(text="二维向量", sort=11),
		#   "color2": PColor(text="颜色2", sort=17, format="#RRGGBB"),
		#   "array2": PArray(text="整数数组", sort=19, childAttribute=PInt()),
		#   "dict2": PDict(text="字典2", sort=21, removable=True, addable=True, children={
		#      "key1": PInt(),
		#      "key2": PStr(),
		#   }),
	}
