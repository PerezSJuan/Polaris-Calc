from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    def child_nodes(self) -> list["Node"]:
        return []


@dataclass
class NumberNode(Node):
    value: Any

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class SymbolNode(Node):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass
class AddNode(Node):
    operands: list[Node] = field(default_factory=list)

    def child_nodes(self) -> list[Node]:
        return self.operands

    def __str__(self) -> str:
        return " + ".join(str(node) for node in self.operands)


@dataclass
class MulNode(Node):
    operands: list[Node] = field(default_factory=list)

    def child_nodes(self) -> list[Node]:
        return self.operands

    def __str__(self) -> str:
        return " * ".join(str(node) for node in self.operands)


@dataclass
class PowNode(Node):
    base: Node
    exponent: Node

    def child_nodes(self) -> list[Node]:
        return [self.base, self.exponent]

    def __str__(self) -> str:
        return f"{self.base}^{self.exponent}"


@dataclass
class FuncNode(Node):
    name: str
    args: list[Node] = field(default_factory=list)
    latex_name: str | None = None

    def child_nodes(self) -> list[Node]:
        return self.args

    def __str__(self) -> str:
        fn_name = self.latex_name or self.name
        return f"{fn_name}({', '.join(str(arg) for arg in self.args)})"


@dataclass
class CompareNode(Node):
    operator: str
    left: Node
    right: Node

    def child_nodes(self) -> list[Node]:
        return [self.left, self.right]

    def __str__(self) -> str:
        return f"{self.left} {self.operator} {self.right}"
