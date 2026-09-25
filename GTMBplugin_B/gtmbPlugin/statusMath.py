# -*- coding: utf-8 -*-
"""get_status / set_status 的数学表达式求值（服务端与客户端共用）。

只做 AST 白名单遍历，不使用 eval / exec；变量与状态路径由调用方通过 resolve 回调解析，
因此服务端查服务端状态、客户端查客户端状态，而求值语义（常量、缓存、路径校验、错误文案）
两端完全一致 —— 这两份实现原本各写一份，已经出现过「客户端不支持元组字面量」这类漂移。
"""
import ast
import math
# 必须用白名单里的 mod.builtin_modules._operator：裸 `operator` 不在 456 项模块白名单内（引擎 2.9+ 会拦）。
import mod.builtin_modules._operator as operator
import re

from consts import STATUS_MATH_BINOPS
from consts import STATUS_MATH_CMPOPS
from consts import STATUS_MATH_FUNCTIONS

# 状态路径的每一段都必须是常规标识符，避免 __class__ / __dict__ 这类 Python 属性越权访问。
PATH_PART_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# 表达式内置常量；变量按需解析并缓存，同一个变量在一条表达式里只读一次。
CONSTANTS = {'pi': math.pi, 'e': math.e}

UNARY_OPS = {
	ast.USub: operator.neg, ast.UAdd: operator.pos,
	ast.Invert: operator.invert, ast.Not: operator.not_,
}

# Python 2 语义；bool 是 int 子类，按数值参与运算。
NUMBER_TYPES = (int, long, float) #type: ignore


def evaluate_status_math(expression, resolve):
	#type: (str, object) -> tuple[bool, float | int | tuple | None, str | None]
	"""求值数学表达式，返回 (ok, value, error)。

	resolve(name) 必须返回 (found, value, error)，与两端的状态读取契约一致。
	"""
	try:
		parsed = ast.parse(expression, mode='eval')
	except (SyntaxError, ValueError):
		return False, None, '数学表达式语法错误'

	values = dict(CONSTANTS)

	def resolve_number(name):
		if name in values:
			return values[name]
		found, value, error = resolve(name)
		if not found:
			raise ValueError('数学变量 %s 无法读取: %s' % (name, error))
		if not isinstance(value, NUMBER_TYPES):
			raise TypeError('数学变量 %s 不是数值' % name)
		values[name] = value
		return value

	def walk(node):
		if isinstance(node, ast.Expression):
			return walk(node.body)
		if isinstance(node, ast.Num):
			return node.n
		if hasattr(ast, 'Constant') and isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
			return node.value
		if isinstance(node, ast.Name):
			return resolve_number(node.id)
		if isinstance(node, ast.Attribute):
			# 只允许读取状态路径（velocity.x、rotation.yaw…），不允许 Python 对象属性。
			path_parts = []
			current = node
			while isinstance(current, ast.Attribute):
				if not PATH_PART_RE.match(current.attr):
					raise ValueError('非法状态路径')
				path_parts.insert(0, current.attr)
				current = current.value
			if not isinstance(current, ast.Name) or not PATH_PART_RE.match(current.id):
				raise ValueError('非法状态路径')
			path_parts.insert(0, current.id)
			return resolve_number('.'.join(path_parts))
		if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Invert, ast.Not)):
			return UNARY_OPS[type(node.op)](walk(node.operand))
		if isinstance(node, ast.BinOp) and type(node.op) in STATUS_MATH_BINOPS:
			return STATUS_MATH_BINOPS[type(node.op)](walk(node.left), walk(node.right))
		if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
			# 短路计算，避免 `0 and sqrt(-1)` 这类无意义的异常。
			if isinstance(node.op, ast.And):
				result = True
				for item in node.values:
					result = walk(item)
					if not result:
						return False
				return result
			result = False
			for item in node.values:
				result = walk(item)
				if result:
					return True
			return result
		if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators):
			left = walk(node.left)
			for index, comparator in enumerate(node.comparators):
				right = walk(comparator)
				if not STATUS_MATH_CMPOPS[type(node.ops[index])](left, right):
					return False
				left = right
			return True
		if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in STATUS_MATH_FUNCTIONS:
			return STATUS_MATH_FUNCTIONS[node.func.id](*[walk(arg) for arg in node.args])
		if isinstance(node, (ast.Tuple, ast.List)):
			return tuple(walk(item) for item in node.elts)
		raise ValueError('数学表达式包含不支持的语法')

	try:
		return True, walk(parsed), None
	except (ArithmeticError, TypeError, ValueError, OverflowError, KeyError):
		return False, None, '数学表达式计算失败'
