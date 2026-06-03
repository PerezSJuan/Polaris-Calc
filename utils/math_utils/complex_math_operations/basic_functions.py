import numpy as np
import math
import random as _random
import builtins


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


"""── List aggregations ─────────────────────────────────────────────────────────"""


def product(elements: list) -> float:
    """Multiply all elements in a list. Args: elements."""
    return float(np.prod(elements))


def cumproduct(elements: list) -> list:
    """Return the cumulative product of elements. Args: elements."""
    return np.cumprod(elements).tolist()


def argmax(elements: list) -> int:
    """Return the index of the maximum value. Args: elements."""
    return int(np.argmax(elements))


def argmin(elements: list) -> int:
    """Return the index of the minimum value. Args: elements."""
    return int(np.argmin(elements))


def count_unique(elements: list) -> int:
    """Return the number of distinct elements. Args: elements."""
    return len(set(elements))


def first(elements: list):
    """Return the first element of a list. Args: elements."""
    if not elements:
        raise ValueError("List is empty.")
    return elements[0]


def last(elements: list):
    """Return the last element of a list. Args: elements."""
    if not elements:
        raise ValueError("List is empty.")
    return elements[-1]


def contains(elements: list, value) -> bool:
    """Check if a value is in the list. Args: elements, value."""
    return value in elements


def index_of(elements: list, value) -> int:
    """Return the first index of value (-1 if not found). Args: elements, value."""
    try:
        return elements.index(value)
    except ValueError:
        return -1


def count_of(elements: list, value) -> int:
    """Count how many times value appears in the list. Args: elements, value."""
    return elements.count(value)


def pairwise_diff(elements: list) -> list:
    """Compute consecutive differences (x[i+1] - x[i]). Args: elements."""
    if len(elements) < 2:
        return []
    return [elements[i + 1] - elements[i] for i in range(len(elements) - 1)]


def min_max_scale(elements: list) -> list:
    """Scale elements to [0, 1] using min-max normalization. Args: elements."""
    arr = np.array(elements, dtype=float)
    mn, mx = np.min(arr), np.max(arr)
    if mx - mn == 0:
        return [0.0] * len(elements)
    return ((arr - mn) / (mx - mn)).tolist()


def delta(elements: list) -> list:
    """Alias for pairwise_diff: first differences. Args: elements."""
    return pairwise_diff(elements)


def running_min(elements: list) -> list:
    """Compute the running minimum over a list. Args: elements."""
    result = []
    cur = float("inf")
    for x in elements:
        cur = builtins.min(cur, x)
        result.append(cur)
    return result


def running_max(elements: list) -> list:
    """Compute the running maximum over a list. Args: elements."""
    result = []
    cur = float("-inf")
    for x in elements:
        cur = builtins.max(cur, x)
        result.append(cur)
    return result


"""── List generation ───────────────────────────────────────────────────────────"""


def range_(start: float, stop: float, step: float = 1.0) -> list:
    """Generate numbers from start to stop (exclusive) by step. Args: start, stop, step."""
    return np.arange(start, stop, step).tolist()


def linspace(start: float, stop: float, n: int = 50) -> list:
    """Generate n evenly spaced numbers from start to stop. Args: start, stop, n."""
    return np.linspace(start, stop, n).tolist()


def logspace(start: float, stop: float, n: int = 50) -> list:
    """Generate n logarithmically spaced numbers from 10^start to 10^stop. Args: start, stop, n."""
    return np.logspace(start, stop, n).tolist()


def fill(value: float, n: int) -> list:
    """Create a list of n copies of value. Args: value, n."""
    return [value] * n


def tabulate(f, n: int) -> list:
    """Apply function f to 0, 1, ..., n-1. Args: f, n."""
    return [f(i) for i in range(n)]


def iterate(f, x0, n: int) -> list:
    """Apply f repeatedly, starting from x0, n times. Args: f, x0, n."""
    result = []
    x = x0
    for _ in range(n):
        result.append(x)
        x = f(x)
    return result


"""── List manipulation ─────────────────────────────────────────────────────────"""


def shuffle(elements: list, seed: int = None) -> list:
    """Return a shuffled copy of the list. Args: elements, seed (optional)."""
    if seed is not None:
        _random.seed(seed)
    lst = list(elements)
    _random.shuffle(lst)
    return lst


def sample(elements: list, n: int, seed: int = None) -> list:
    """Randomly sample n elements without replacement. Args: elements, n, seed (optional)."""
    if seed is not None:
        _random.seed(seed)
    return _random.sample(list(elements), n)


def interleave(*lists) -> list:
    """Interleave multiple lists element by element. Args: *lists."""
    result = []
    for tup in zip(*lists):
        result.extend(tup)
    return result
