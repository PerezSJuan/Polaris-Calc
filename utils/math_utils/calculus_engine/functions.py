import numpy as np
from scipy import interpolate


"""── Column generation from functions ────────────────────────────────────────"""


def from_function(func, start: float, end: float, n: int = 100) -> list:
    x = np.linspace(start, end, n)
    return np.vectorize(func)(x).tolist()


def apply_function(func, array: list) -> list:
    arr = np.asarray(array, dtype=float)
    if arr.size == 0:
        return []
    return np.vectorize(func)(arr).tolist()


"""── Sequence generation ──────────────────────────────────────────────────────"""


def linspace(start: float, stop: float, n: int = 50) -> list:
    return np.linspace(start, stop, n).tolist()


def logspace(start: float, stop: float, n: int = 50) -> list:
    return np.logspace(start, stop, n).tolist()


def arange(start: float, stop: float, step: float = 1.0) -> list:
    return np.arange(start, stop, step).tolist()


"""── Interpolation ────────────────────────────────────────────────────────────"""


def interpolate_linear(x: list, y: list, x_new: list) -> list:
    f = interpolate.interp1d(x, y, kind="linear")
    return f(np.asarray(x_new, dtype=float)).tolist()


def interpolate_cubic_spline(x: list, y: list, x_new: list) -> list:
    f = interpolate.CubicSpline(x, y)
    return f(np.asarray(x_new, dtype=float)).tolist()


def interpolate_nearest(x: list, y: list, x_new: list) -> list:
    f = interpolate.interp1d(x, y, kind="nearest")
    return f(np.asarray(x_new, dtype=float)).tolist()


def interpolate_quadratic(x: list, y: list, x_new: list) -> list:
    f = interpolate.interp1d(x, y, kind="quadratic")
    return f(np.asarray(x_new, dtype=float)).tolist()


def interpolate_pchip(x: list, y: list, x_new: list) -> list:
    f = interpolate.PchipInterpolator(x, y)
    return f(np.asarray(x_new, dtype=float)).tolist()


def interpolate_akima(x: list, y: list, x_new: list) -> list:
    f = interpolate.Akima1DInterpolator(x, y)
    return f(np.asarray(x_new, dtype=float)).tolist()
