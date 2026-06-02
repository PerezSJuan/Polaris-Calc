import numpy as np
import math


"""── Constants ─────────────────────────────────────────────────────────────────"""

def true() -> bool:
    """Return the boolean constant True. Args: none."""
    return True


def false() -> bool:
    """Return the boolean constant False. Args: none."""
    return False


"""── Basic logical operations ──────────────────────────────────────────────────"""

def not_(value: bool) -> bool:
    """Logical NOT (negation) of a boolean value. Args: value."""
    return not value


def and_(value1: bool, value2: bool) -> bool:
    """Logical AND of two boolean values. Args: value1, value2."""
    return value1 and value2


def or_(value1: bool, value2: bool) -> bool:
    """Logical OR of two boolean values. Args: value1, value2."""
    return value1 or value2


def xor_(value1: bool, value2: bool) -> bool:
    """Logical XOR (exclusive OR) of two boolean values. Args: value1, value2."""
    return value1 != value2


def nand_(value1: bool, value2: bool) -> bool:
    """Logical NAND (NOT AND) of two boolean values. Args: value1, value2."""
    return not (value1 and value2)


def nor_(value1: bool, value2: bool) -> bool:
    """Logical NOR (NOT OR) of two boolean values. Args: value1, value2."""
    return not (value1 or value2)


def xnor_(value1: bool, value2: bool) -> bool:
    """Logical XNOR (equivalence) of two boolean values. Args: value1, value2."""
    return value1 == value2


def implies_(antecedent: bool, consequent: bool) -> bool:
    """Logical implication: antecedent → consequent. Args: antecedent, consequent."""
    return not antecedent or consequent


def iff_(value1: bool, value2: bool) -> bool:
    """Logical biconditional (if and only if): value1 ↔ value2. Args: value1, value2."""
    return value1 == value2


"""── Conditional functions ─────────────────────────────────────────────────────"""

def if_(condition: bool, true_value, false_value):
    """If condition is True return true_value, else false_value. Args: condition, true_value, false_value."""
    return true_value if condition else false_value


def if_error(value, default):
    """Return value if no exception occurs, otherwise return default. Args: value, default."""
    try:
        return value
    except Exception:
        return default


def if_na(value, default):
    """Return value if not None, otherwise return default. Args: value, default."""
    if value is None:
        return default
    return value


def switch(expression: object, *cases) -> object:
    """Match expression against case-value pairs; return matching result or default. Args: expression, *cases."""
    for i in range(0, len(cases) - 1, 2):
        if cases[i] == expression:
            return cases[i + 1]
    if len(cases) % 2 == 1:
        return cases[-1]
    return None


def choose(index: int, *options) -> object:
    """Choose the index-th option (1-based). Returns None if out of range. Args: index, *options."""
    if index < 1 or index > len(options):
        return None
    return options[index - 1]


"""── Comparison operators ──────────────────────────────────────────────────────"""

def equal(value1, value2) -> bool:
    """Check if value1 == value2. Args: value1, value2."""
    return value1 == value2


def not_equal(value1, value2) -> bool:
    """Check if value1 != value2. Args: value1, value2."""
    return value1 != value2


def greater_than(value1, value2) -> bool:
    """Check if value1 > value2. Args: value1, value2."""
    return value1 > value2


def less_than(value1, value2) -> bool:
    """Check if value1 < value2. Args: value1, value2."""
    return value1 < value2


def greater_equal(value1, value2) -> bool:
    """Check if value1 >= value2. Args: value1, value2."""
    return value1 >= value2


def less_equal(value1, value2) -> bool:
    """Check if value1 <= value2. Args: value1, value2."""
    return value1 <= value2


"""── Array / list logical operations ──────────────────────────────────────────"""

def and_all(values: list) -> bool:
    """Check if all values in the list are truthy (logical AND over list). Args: values."""
    return all(bool(v) for v in values)


def or_any(values: list) -> bool:
    """Check if any value in the list is truthy (logical OR over list). Args: values."""
    return any(bool(v) for v in values)


def xor_all(values: list) -> bool:
    """Check if an odd number of values are truthy (logical XOR over list). Args: values."""
    return sum(bool(v) for v in values) % 2 == 1


def not_all(values: list) -> list:
    """Apply logical NOT to each element in the list. Args: values."""
    return [not bool(v) for v in values]


def elementwise_and(list1: list, list2: list) -> list:
    """Element-wise logical AND of two lists. Args: list1, list2 (same length)."""
    if len(list1) != len(list2):
        raise ValueError("Lists must have the same length.")
    return [a and b for a, b in zip(list1, list2)]


def elementwise_or(list1: list, list2: list) -> list:
    """Element-wise logical OR of two lists. Args: list1, list2 (same length)."""
    if len(list1) != len(list2):
        raise ValueError("Lists must have the same length.")
    return [a or b for a, b in zip(list1, list2)]


def elementwise_xor(list1: list, list2: list) -> list:
    """Element-wise logical XOR of two lists. Args: list1, list2 (same length)."""
    if len(list1) != len(list2):
        raise ValueError("Lists must have the same length.")
    return [bool(a) != bool(b) for a, b in zip(list1, list2)]


"""── Logical tests ─────────────────────────────────────────────────────────────"""

def is_true(value) -> bool:
    """Check if value is truthy (bool conversion). Args: value."""
    return bool(value)


def is_false(value) -> bool:
    """Check if value is falsy. Args: value."""
    return not bool(value)


def is_number(value) -> bool:
    """Check if value is a number (int, float, complex, but not bool). Args: value."""
    return isinstance(value, (int, float, complex)) and not isinstance(value, bool)


def is_text(value) -> bool:
    """Check if value is a string. Args: value."""
    return isinstance(value, str)


def is_non_text(value) -> bool:
    """Check if value is not a string. Args: value."""
    return not isinstance(value, str)


def is_even(number: int) -> bool:
    """Check if an integer is even. Args: number."""
    return isinstance(number, int) and number % 2 == 0


def is_odd(number: int) -> bool:
    """Check if an integer is odd. Args: number."""
    return isinstance(number, int) and number % 2 != 0


def is_blank(value) -> bool:
    """Check if value is None or an empty string. Args: value."""
    return value is None or (isinstance(value, str) and value.strip() == "")


def is_logical(value) -> bool:
    """Check if value is a boolean. Args: value."""
    return isinstance(value, bool)


"""── Conditional counting ──────────────────────────────────────────────────────"""

def count_true(values: list) -> int:
    """Count the number of truthy values in a list. Args: values."""
    return sum(1 for v in values if bool(v))


def count_false(values: list) -> int:
    """Count the number of falsy values in a list. Args: values."""
    return sum(1 for v in values if not bool(v))


"""── Error handling ────────────────────────────────────────────────────────────"""

def is_error(value) -> bool:
    """Check if value is an exception/error instance. Args: value."""
    return isinstance(value, BaseException)


"""── Multiple condition evaluation ─────────────────────────────────────────────"""

def and_ifs(*conditions: bool) -> bool:
    """Check if all provided conditions are True. Args: *conditions."""
    return all(conditions)


def or_ifs(*conditions: bool) -> bool:
    """Check if any of the provided conditions is True. Args: *conditions."""
    return any(conditions)


"""── Numeric-to-logical ────────────────────────────────────────────────────────"""

def logical_value(value, threshold: float = 0.5) -> bool:
    """Convert a value to boolean; for numbers, check if > threshold. Args: value, threshold (default 0.5)."""
    return bool(value) if isinstance(value, bool) else value > threshold


def to_bool(value) -> bool:
    """Convert any value to its boolean equivalent. Args: value."""
    return bool(value)


def to_number(value: bool) -> int:
    """Convert a boolean to an integer (1 for True, 0 for False). Args: value."""
    return 1 if value else 0


"""── Integer bitwise operations ────────────────────────────────────────────────"""


def bitwise_and(a: int, b: int) -> int:
    """Bitwise AND of two integers. Args: a, b."""
    return a & b


def bitwise_or(a: int, b: int) -> int:
    """Bitwise OR of two integers. Args: a, b."""
    return a | b


def bitwise_xor(a: int, b: int) -> int:
    """Bitwise XOR of two integers. Args: a, b."""
    return a ^ b


"""── Aggregate logical operations ────────────────────────────────────────────────"""


def majority(*values: bool) -> bool:
    """Return True if more than half of the values are truthy. Args: *values."""
    return sum(bool(v) for v in values) > len(values) / 2


def exactly_one(*values: bool) -> bool:
    """Return True if exactly one value is truthy. Args: *values."""
    return sum(bool(v) for v in values) == 1


def at_least_n(values: list, n: int) -> bool:
    """Return True if at least n values are truthy. Args: values, n."""
    return sum(bool(v) for v in values) >= n


def at_most_n(values: list, n: int) -> bool:
    """Return True if at most n values are truthy. Args: values, n."""
    return sum(bool(v) for v in values) <= n


def all_same(*values) -> bool:
    """Return True if all values are equal. Args: *values."""
    if not values:
        return True
    first = values[0]
    return all(v == first for v in values)


def all_different(*values) -> bool:
    """Return True if all values are distinct. Args: *values."""
    return len(values) == len(set(values))
