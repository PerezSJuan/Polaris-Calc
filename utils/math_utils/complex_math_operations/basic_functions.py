import numpy as np


def count(elements: list) -> int:
    """Return the number of elements in a list. Args: elements."""
    return len(elements)


def count_if(elements: list, condition: callable) -> int:
    """Count elements that satisfy a condition. Args: elements, condition."""
    return len([element for element in elements if condition(element)])


def count_ifs(elements: list, conditions: list) -> int:
    """Count elements that satisfy all conditions. Args: elements, conditions."""
    return len([element for element in elements if all(condition(element) for condition in conditions)])


def sum(elements: list) -> float:
    """Sum all elements in a list. Args: elements."""
    return float(np.sum(elements))


def max(elements: list) -> float:
    """Return the maximum value in a list. Args: elements."""
    return float(np.max(elements))


def min(elements: list) -> float:
    """Return the minimum value in a list. Args: elements."""
    return float(np.min(elements))


def product(elements: list) -> float:
    """Multiply all elements in a list. Args: elements."""
    return float(np.prod(elements))
