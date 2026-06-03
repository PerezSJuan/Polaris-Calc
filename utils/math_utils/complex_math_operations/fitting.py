import numpy as np
from scipy import stats


def _check_min_points(x, y, n=2):
    if len(x) < n or len(y) < n:
        raise ValueError(f"Need at least {n} data points, got len(x)={len(x)}, len(y)={len(y)}")


def _to_float_arrays(x, y):
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def _check_positive(arr, label):
    if np.any(arr <= 0):
        raise ValueError(f"{label} must be positive for this fit type")


"""── Linear regression ────────────────────────────────────────────────────────"""


def linest(x: list, y: list) -> list:
    model = stats.linregress(x, y)
    return model.slope, model.intercept, model.rvalue ** 2, model.rvalue, model.stderr


def linest_slope(x: list, y: list) -> float:
    _check_min_points(x, y)
    return float(stats.linregress(x, y).slope)


def linest_intercept(x: list, y: list) -> float:
    _check_min_points(x, y)
    return float(stats.linregress(x, y).intercept)


def linest_r2(x: list, y: list) -> float:
    _check_min_points(x, y)
    model = stats.linregress(x, y)
    return float(model.rvalue ** 2)


def linest_pearson(x: list, y: list) -> float:
    _check_min_points(x, y)
    return float(stats.linregress(x, y).rvalue)


def linest_stderr(x: list, y: list) -> float:
    _check_min_points(x, y)
    return float(stats.linregress(x, y).stderr)


"""── Polynomial regression ────────────────────────────────────────────────────"""


def polyfit(x: list, y: list, degree: int = 2) -> list:
    _check_min_points(x, y, degree + 1)
    xa, ya = _to_float_arrays(x, y)
    coeffs = np.polyfit(xa, ya, degree)
    y_pred = np.polyval(coeffs, xa)
    ss_res = np.sum((ya - y_pred) ** 2)
    ss_tot = np.sum((ya - np.mean(ya)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
    return coeffs.tolist(), r2


def polyfit_coeffs(x: list, y: list, degree: int = 2) -> list:
    _check_min_points(x, y, degree + 1)
    return np.polyfit(x, y, degree).tolist()


def polyfit_r2(x: list, y: list, degree: int = 2) -> float:
    _check_min_points(x, y, degree + 1)
    xa, ya = _to_float_arrays(x, y)
    coeffs = np.polyfit(xa, ya, degree)
    y_pred = np.polyval(coeffs, xa)
    ss_res = np.sum((ya - y_pred) ** 2)
    ss_tot = np.sum((ya - np.mean(ya)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0


def polyval(coeffs: list, x: list) -> list:
    return np.polyval(coeffs, np.asarray(x, dtype=float)).tolist()


"""── Exponential fit y = a * exp(b * x) ────────────────────────────────────────"""


def fit_exponential(x: list, y: list) -> list:
    xa, ya = _to_float_arrays(x, y)
    _check_positive(ya, "y")
    log_y = np.log(ya)
    slope, intercept, _, _, _ = stats.linregress(xa, log_y)
    a, b = np.exp(intercept), slope
    y_pred = a * np.exp(b * xa)
    ss_res = np.sum((ya - y_pred) ** 2)
    ss_tot = np.sum((ya - np.mean(ya)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
    return a, b, r2


def fit_exponential_coeffs(x: list, y: list) -> list:
    xa, ya = _to_float_arrays(x, y)
    _check_positive(ya, "y")
    log_y = np.log(ya)
    slope, intercept, _, _, _ = stats.linregress(xa, log_y)
    return np.exp(intercept), slope


def fit_exponential_r2(x: list, y: list) -> float:
    a, b, r2 = fit_exponential(x, y)
    return float(r2)


"""── Power fit y = a * x^b ────────────────────────────────────────────────────"""


def fit_power(x: list, y: list) -> list:
    xa, ya = _to_float_arrays(x, y)
    _check_positive(xa, "x")
    _check_positive(ya, "y")
    log_x, log_y = np.log(xa), np.log(ya)
    slope, intercept, _, _, _ = stats.linregress(log_x, log_y)
    a, b = np.exp(intercept), slope
    y_pred = a * xa ** b
    ss_res = np.sum((ya - y_pred) ** 2)
    ss_tot = np.sum((ya - np.mean(ya)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
    return a, b, r2


def fit_power_coeffs(x: list, y: list) -> list:
    xa, ya = _to_float_arrays(x, y)
    _check_positive(xa, "x")
    _check_positive(ya, "y")
    log_x, log_y = np.log(xa), np.log(ya)
    slope, intercept, _, _, _ = stats.linregress(log_x, log_y)
    return np.exp(intercept), slope


def fit_power_r2(x: list, y: list) -> float:
    a, b, r2 = fit_power(x, y)
    return float(r2)


"""── Logarithmic fit y = a + b * ln(x) ────────────────────────────────────────"""


def fit_logarithmic(x: list, y: list) -> list:
    xa, ya = _to_float_arrays(x, y)
    _check_positive(xa, "x")
    log_x = np.log(xa)
    slope, intercept, _, _, _ = stats.linregress(log_x, ya)
    a, b = intercept, slope
    y_pred = a + b * np.log(xa)
    ss_res = np.sum((ya - y_pred) ** 2)
    ss_tot = np.sum((ya - np.mean(ya)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
    return a, b, r2


def fit_logarithmic_coeffs(x: list, y: list) -> list:
    xa, ya = _to_float_arrays(x, y)
    _check_positive(xa, "x")
    log_x = np.log(xa)
    slope, intercept, _, _, _ = stats.linregress(log_x, ya)
    return intercept, slope


def fit_logarithmic_r2(x: list, y: list) -> float:
    a, b, r2 = fit_logarithmic(x, y)
    return float(r2)


"""── Goodness of fit ───────────────────────────────────────────────────────────"""


def r_squared(y_true: list, y_pred: list) -> float:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((yt - yp) ** 2)
    ss_tot = np.sum((yt - np.mean(yt)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0


def rmse(y_true: list, y_pred: list) -> float:
    return float(np.sqrt(np.mean((np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)) ** 2)))


def mae(y_true: list, y_pred: list) -> float:
    return float(np.mean(np.abs(np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float))))
