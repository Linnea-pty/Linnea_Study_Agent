"""安全数学计算工具：AST 白名单实现，杜绝 eval 代码注入。"""

from __future__ import annotations

import ast
import operator
from collections.abc import Callable
from typing import Any

from langchain_core.tools import tool

_BIN_OPS: dict[type[ast.operator], Callable[..., Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_UNARY_OPS: dict[type[ast.unaryop], Callable[..., Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_MAX_EXP = 1000


def _safe_eval(node: ast.AST):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type is ast.Pow:
            base, exp = _safe_eval(node.left), _safe_eval(node.right)
            if abs(exp) > _MAX_EXP:
                raise ValueError(f"指数过大：{exp}")
            return base**exp
        fn = _BIN_OPS.get(op_type)
        if fn is None:
            raise ValueError(f"不支持的运算符：{op_type.__name__}")
        return fn(_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        unary_fn = _UNARY_OPS.get(type(node.op))
        if unary_fn is None:
            raise ValueError(f"不支持的一元运算符：{type(node.op).__name__}")
        return unary_fn(_safe_eval(node.operand))
    raise ValueError(f"不支持的表达式节点：{type(node).__name__}")


@tool
def calculator(expression: str) -> str:
    """计算数学表达式，支持 + - * / // % ** 和括号，如：'3*(4+2)'。"""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_safe_eval(tree))
    except Exception as exc:  # noqa: BLE001 - 计算失败统一返回文本
        return f"计算失败：{exc}"
