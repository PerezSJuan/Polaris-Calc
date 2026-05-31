from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import AddNode, CompareNode, FuncNode, MulNode, Node, NumberNode, PowNode, SymbolNode
from .eval_types import UndefinedSymbolError, UnknownOperationError
from .pool_schema import OperationSpec, PoolValue


@dataclass
class ResolvedNode:
    node: Node
    children: list["ResolvedNode"]
    symbol: PoolValue | None = None
    operation: OperationSpec | None = None

    def node_repr(self) -> str:
        return str(self.node)


def resolve_node(
    node: Node,
    variables: dict[str, PoolValue],
    extra_constants: dict[str, PoolValue],
    builtin_constants: dict[str, PoolValue],
    operations: dict[str, OperationSpec],
) -> ResolvedNode:
    if isinstance(node, NumberNode):
        return ResolvedNode(node=node, children=[])
    if isinstance(node, SymbolNode):
        if node.name in variables:
            return ResolvedNode(node=node, children=[], symbol=variables[node.name])
        if node.name in extra_constants:
            return ResolvedNode(node=node, children=[], symbol=extra_constants[node.name])
        if node.name in builtin_constants:
            return ResolvedNode(node=node, children=[], symbol=builtin_constants[node.name])
        raise UndefinedSymbolError(f"Undefined symbol: '{node.name}'", str(node))
    if isinstance(node, FuncNode):
        candidates = []
        for raw in (node.latex_name, node.name):
            if not raw:
                continue
            candidates.append(raw)
            if raw.startswith("\\"):
                candidates.append(raw[1:])
            else:
                candidates.append(f"\\{raw}")
        op = next((operations[name] for name in candidates if name in operations), None)
        if op is None:
            raise UnknownOperationError(f"Unknown operation: '{node.latex_name or node.name}'", str(node))
        return ResolvedNode(
            node=node,
            children=[resolve_node(child, variables, extra_constants, builtin_constants, operations) for child in node.args],
            operation=op,
        )
    if isinstance(node, AddNode):
        return ResolvedNode(node=node, children=[resolve_node(child, variables, extra_constants, builtin_constants, operations) for child in node.operands])
    if isinstance(node, MulNode):
        return ResolvedNode(node=node, children=[resolve_node(child, variables, extra_constants, builtin_constants, operations) for child in node.operands])
    if isinstance(node, PowNode):
        return ResolvedNode(node=node, children=[resolve_node(node.base, variables, extra_constants, builtin_constants, operations), resolve_node(node.exponent, variables, extra_constants, builtin_constants, operations)])
    if isinstance(node, CompareNode):
        return ResolvedNode(node=node, children=[resolve_node(node.left, variables, extra_constants, builtin_constants, operations), resolve_node(node.right, variables, extra_constants, builtin_constants, operations)])
    raise TypeError(f"Unsupported AST node type: {type(node)}")
