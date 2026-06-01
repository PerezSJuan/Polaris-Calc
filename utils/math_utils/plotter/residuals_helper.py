"""
math_utils/residuals_helper.py
==============================
Funciones numpy para calcular residuos y estadísticas derivadas
de los distintos tipos de gráfico del módulo plotter.

Categorías
----------
- Regresión lineal / polinómica
- Residuos generales
- Estadísticas de histograma
- Porcentajes de gráficos de sectores (pie)
- Estadísticas de boxplot / violin
- Análisis de heatmap / matriz
- Bondad de ajuste
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Sequence


# ---------------------------------------------------------------------------
# Tipos de retorno
# ---------------------------------------------------------------------------


@dataclass
class LinearRegressionResult:
    slope: float
    intercept: float
    r_squared: float
    pearson_r: float
    residuals: np.ndarray
    y_predicted: np.ndarray
    std_error_slope: float
    std_error_intercept: float
    residual_std_error: float
    ss_res: float  # Suma de cuadrados de residuos
    ss_tot: float  # Suma de cuadrados total
    n: int

    def __str__(self) -> str:
        return (
            f"Regresión lineal  y = {self.slope:.6g}x + {self.intercept:.6g}\n"
            f"  R²              = {self.r_squared:.6f}\n"
            f"  Pearson r       = {self.pearson_r:.6f}\n"
            f"  RSE             = {self.residual_std_error:.6g}\n"
            f"  SE(slope)       = {self.std_error_slope:.6g}\n"
            f"  SE(intercept)   = {self.std_error_intercept:.6g}\n"
            f"  n               = {self.n}"
        )


@dataclass
class PolynomialRegressionResult:
    degree: int
    coefficients: np.ndarray  # índice 0 = mayor grado
    r_squared: float
    residuals: np.ndarray
    y_predicted: np.ndarray
    residual_std_error: float
    ss_res: float
    ss_tot: float
    n: int

    def __str__(self) -> str:
        terms = " + ".join(
            f"{c:.4g}x^{self.degree - i}" if self.degree - i > 0 else f"{c:.4g}"
            for i, c in enumerate(self.coefficients)
        )
        return (
            f"Regresión polinómica grado {self.degree}  y = {terms}\n"
            f"  R²  = {self.r_squared:.6f}\n"
            f"  RSE = {self.residual_std_error:.6g}\n"
            f"  n   = {self.n}"
        )


@dataclass
class PieStats:
    labels: list[str]
    values: np.ndarray
    percentages: np.ndarray  # porcentaje de cada sector
    cumulative_pct: np.ndarray  # porcentaje acumulado
    total: float
    dominant_label: str
    dominant_pct: float

    def __str__(self) -> str:
        rows = "\n".join(
            f"  {lbl:<20s} {val:>12.4g}  {pct:>7.2f}%  (acum {cum:.2f}%)"
            for lbl, val, pct, cum in zip(
                self.labels, self.values, self.percentages, self.cumulative_pct
            )
        )
        return (
            f"Estadísticas de pie chart\n"
            f"  Total: {self.total:.6g}\n"
            f"  Dominante: {self.dominant_label} ({self.dominant_pct:.2f}%)\n"
            f"{rows}"
        )


@dataclass
class HistogramStats:
    counts: np.ndarray
    bin_edges: np.ndarray
    bin_centers: np.ndarray
    bin_widths: np.ndarray
    frequencies: np.ndarray  # densidad relativa (suma = 1)
    cumulative_freq: np.ndarray  # frecuencia acumulada relativa
    mean: float
    median: float
    std: float
    variance: float
    skewness: float
    kurtosis: float
    mode_bin_center: float
    total_count: int

    def __str__(self) -> str:
        return (
            f"Estadísticas de histograma\n"
            f"  n       = {self.total_count}\n"
            f"  Media   = {self.mean:.6g}\n"
            f"  Mediana = {self.median:.6g}\n"
            f"  Std     = {self.std:.6g}\n"
            f"  Var     = {self.variance:.6g}\n"
            f"  Asim.   = {self.skewness:.4f}\n"
            f"  Kurt.   = {self.kurtosis:.4f}\n"
            f"  Moda≈   = {self.mode_bin_center:.6g}"
        )


@dataclass
class BoxplotStats:
    """Estadísticas de cada grupo en un boxplot/violin."""

    group_labels: list[str]
    medians: np.ndarray
    means: np.ndarray
    q1: np.ndarray
    q3: np.ndarray
    iqr: np.ndarray
    whisker_low: np.ndarray
    whisker_high: np.ndarray
    outliers: list[np.ndarray]  # outliers por grupo

    def __str__(self) -> str:
        rows = "\n".join(
            f"  {lbl:<15s}  med={med:.4g}  mean={mn:.4g}"
            f"  Q1={q1:.4g}  Q3={q3:.4g}  IQR={iqr:.4g}"
            f"  n_out={len(out)}"
            for lbl, med, mn, q1, q3, iqr, out in zip(
                self.group_labels,
                self.medians,
                self.means,
                self.q1,
                self.q3,
                self.iqr,
                self.outliers,
            )
        )
        return f"Estadísticas de boxplot\n{rows}"


@dataclass
class ResidualDiagnostics:
    """Diagnóstico completo de un vector de residuos."""

    residuals: np.ndarray
    mean: float
    std: float
    max_abs: float
    rmse: float
    mae: float
    mape: np.ndarray | None  # None si hay ceros en y_true
    ss_res: float
    shapiro_stat: float | None  # None si n > 5000 (demasiado lento)
    shapiro_p: float | None
    durbin_watson: float  # ≈ 2 → sin autocorrelación

    def __str__(self) -> str:
        sw = (
            f"  Shapiro-Wilk    W={self.shapiro_stat:.4f}  p={self.shapiro_p:.4g}"
            if self.shapiro_stat is not None
            else "  Shapiro-Wilk    (omitido, n > 5000)"
        )
        mape_str = (
            f"  MAPE            = {float(np.mean(self.mape)):.4f} %"
            if self.mape is not None
            else "  MAPE            = N/A (hay ceros en y_true)"
        )
        return (
            f"Diagnóstico de residuos\n"
            f"  n               = {len(self.residuals)}\n"
            f"  Media           = {self.mean:.6g}\n"
            f"  Std             = {self.std:.6g}\n"
            f"  RMSE            = {self.rmse:.6g}\n"
            f"  MAE             = {self.mae:.6g}\n"
            f"{mape_str}\n"
            f"  SS_res          = {self.ss_res:.6g}\n"
            f"  Max |residuo|   = {self.max_abs:.6g}\n"
            f"  Durbin-Watson   = {self.durbin_watson:.4f}\n"
            f"{sw}"
        )


# ---------------------------------------------------------------------------
# Regresión lineal
# ---------------------------------------------------------------------------


def linear_regression(
    x: Sequence | np.ndarray,
    y: Sequence | np.ndarray,
) -> LinearRegressionResult:
    """
    Regresión lineal simple por mínimos cuadrados.

    Devuelve pendiente, intercepción, R², residuos, errores estándar y más.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)

    x_mean, y_mean = x.mean(), y.mean()
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_xy = np.sum((x - x_mean) * (y - y_mean))

    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    y_pred = slope * x + intercept

    residuals = y - y_pred
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y - y_mean) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

    rse = np.sqrt(ss_res / (n - 2)) if n > 2 else np.nan
    se_slope = rse / np.sqrt(ss_xx) if ss_xx != 0 else np.nan
    se_intercept = rse * np.sqrt(np.sum(x**2) / (n * ss_xx)) if ss_xx != 0 else np.nan

    pearson_r = float(np.corrcoef(x, y)[0, 1])

    return LinearRegressionResult(
        slope=float(slope),
        intercept=float(intercept),
        r_squared=r_squared,
        pearson_r=pearson_r,
        residuals=residuals,
        y_predicted=y_pred,
        std_error_slope=float(se_slope),
        std_error_intercept=float(se_intercept),
        residual_std_error=float(rse),
        ss_res=ss_res,
        ss_tot=ss_tot,
        n=n,
    )


def polynomial_regression(
    x: Sequence | np.ndarray,
    y: Sequence | np.ndarray,
    degree: int = 2,
) -> PolynomialRegressionResult:
    """
    Regresión polinómica de grado `degree` usando numpy.polyfit.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)

    coeffs = np.polyfit(x, y, degree)
    y_pred = np.polyval(coeffs, x)

    residuals = y - y_pred
    ss_res = float(np.sum(residuals**2))
    y_mean = y.mean()
    ss_tot = float(np.sum((y - y_mean) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

    dof = n - (degree + 1)
    rse = float(np.sqrt(ss_res / dof)) if dof > 0 else np.nan

    return PolynomialRegressionResult(
        degree=degree,
        coefficients=coeffs,
        r_squared=r_squared,
        residuals=residuals,
        y_predicted=y_pred,
        residual_std_error=rse,
        ss_res=ss_res,
        ss_tot=ss_tot,
        n=n,
    )


# ---------------------------------------------------------------------------
# Diagnóstico general de residuos
# ---------------------------------------------------------------------------


def residual_diagnostics(
    residuals: Sequence | np.ndarray,
    y_true: Sequence | np.ndarray | None = None,
) -> ResidualDiagnostics:
    """
    Calcula métricas de diagnóstico sobre un vector de residuos.

    Parámetros
    ----------
    residuals : array-like
        Residuos = y_true - y_pred.
    y_true : array-like, opcional
        Valores reales, necesario para calcular MAPE.
    """
    r = np.asarray(residuals, dtype=float)
    n = len(r)

    rmse = float(np.sqrt(np.mean(r**2)))
    mae = float(np.mean(np.abs(r)))
    ss_res = float(np.sum(r**2))
    max_abs = float(np.max(np.abs(r)))

    mape = None
    if y_true is not None:
        yt = np.asarray(y_true, dtype=float)
        if np.all(yt != 0):
            mape = np.abs(r / yt) * 100

    # Durbin-Watson
    dw = float(np.sum(np.diff(r) ** 2) / ss_res) if ss_res != 0 else np.nan

    # Shapiro-Wilk (solo para n ≤ 5000)
    sw_stat = sw_p = None
    if n <= 5000:
        try:
            from scipy.stats import shapiro  # type: ignore

            sw_stat, sw_p = shapiro(r)
            sw_stat, sw_p = float(sw_stat), float(sw_p)
        except ImportError:
            pass

    return ResidualDiagnostics(
        residuals=r,
        mean=float(r.mean()),
        std=float(r.std()),
        max_abs=max_abs,
        rmse=rmse,
        mae=mae,
        mape=mape,
        ss_res=ss_res,
        shapiro_stat=sw_stat,
        shapiro_p=sw_p,
        durbin_watson=dw,
    )


def standardized_residuals(
    residuals: Sequence | np.ndarray,
) -> np.ndarray:
    """Residuos estandarizados (z-score)."""
    r = np.asarray(residuals, dtype=float)
    return (r - r.mean()) / r.std() if r.std() != 0 else r


def studentized_residuals(
    residuals: Sequence | np.ndarray,
    leverage: Sequence | np.ndarray,
) -> np.ndarray:
    """
    Residuos studentizados externamente (aproximación).

    leverage : array-like
        Valores h_ii de la matriz sombrero (hat matrix).
    """
    r = np.asarray(residuals, dtype=float)
    h = np.asarray(leverage, dtype=float)
    sigma = np.sqrt(np.sum(r**2) / (len(r) - 2))
    return r / (sigma * np.sqrt(1 - h))


def hat_matrix_diagonal(
    x: Sequence | np.ndarray,
    degree: int = 1,
) -> np.ndarray:
    """
    Diagonal de la hat matrix H = X(X'X)^{-1}X' para regresión
    lineal o polinómica.
    """
    x = np.asarray(x, dtype=float)
    X = np.vstack([x**i for i in range(degree + 1)]).T
    H = X @ np.linalg.pinv(X.T @ X) @ X.T
    return np.diag(H)


# ---------------------------------------------------------------------------
# Estadísticas para pie chart
# ---------------------------------------------------------------------------


def pie_stats(
    values: Sequence | np.ndarray,
    labels: Sequence[str] | None = None,
) -> PieStats:
    """
    Calcula porcentajes, porcentajes acumulados y estadísticas
    de un gráfico de sectores.
    """
    v = np.asarray(values, dtype=float)
    total = float(v.sum())
    pcts = v / total * 100
    cum_pcts = np.cumsum(pcts)
    idx_max = int(np.argmax(v))

    lbls = list(labels) if labels is not None else [str(i) for i in range(len(v))]

    return PieStats(
        labels=lbls,
        values=v,
        percentages=pcts,
        cumulative_pct=cum_pcts,
        total=total,
        dominant_label=lbls[idx_max],
        dominant_pct=float(pcts[idx_max]),
    )


# ---------------------------------------------------------------------------
# Estadísticas de histograma
# ---------------------------------------------------------------------------


def histogram_stats(
    data: Sequence | np.ndarray,
    bins: int | str | Sequence = "auto",
) -> HistogramStats:
    """
    Estadísticas completas derivadas de un histograma.
    """
    d = np.asarray(data, dtype=float)
    counts, edges = np.histogram(d, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    total = int(counts.sum())
    freqs = counts / total
    cum_freq = np.cumsum(freqs)

    # Estadísticas sobre los datos originales
    mean = float(d.mean())
    median = float(np.median(d))
    std = float(d.std())
    var = float(d.var())

    # Asimetría y curtosis manuales con numpy
    skewness = float(np.mean(((d - mean) / std) ** 3)) if std != 0 else 0.0
    kurtosis = float(np.mean(((d - mean) / std) ** 4) - 3) if std != 0 else 0.0

    mode_center = float(centers[np.argmax(counts)])

    return HistogramStats(
        counts=counts,
        bin_edges=edges,
        bin_centers=centers,
        bin_widths=widths,
        frequencies=freqs,
        cumulative_freq=cum_freq,
        mean=mean,
        median=median,
        std=std,
        variance=var,
        skewness=skewness,
        kurtosis=kurtosis,
        mode_bin_center=mode_center,
        total_count=total,
    )


# ---------------------------------------------------------------------------
# Estadísticas de boxplot / violin
# ---------------------------------------------------------------------------


def boxplot_stats(
    groups: Sequence[Sequence | np.ndarray],
    labels: Sequence[str] | None = None,
    whis: float = 1.5,
) -> BoxplotStats:
    """
    Calcula las estadísticas de cada grupo para un boxplot.

    Parámetros
    ----------
    groups : lista de arrays
        Cada elemento es un grupo de datos.
    labels : lista de str, opcional
    whis : float
        Multiplicador del IQR para los bigotes (default 1.5).
    """
    groups = [np.asarray(g, dtype=float) for g in groups]
    n_groups = len(groups)
    lbls = list(labels) if labels is not None else [str(i) for i in range(n_groups)]

    medians = np.array([np.median(g) for g in groups])
    means = np.array([g.mean() for g in groups])
    q1 = np.array([np.percentile(g, 25) for g in groups])
    q3 = np.array([np.percentile(g, 75) for g in groups])
    iqr = q3 - q1

    whisker_low = np.array([q1[i] - whis * iqr[i] for i in range(n_groups)])
    whisker_high = np.array([q3[i] + whis * iqr[i] for i in range(n_groups)])

    outliers = [
        g[(g < whisker_low[i]) | (g > whisker_high[i])] for i, g in enumerate(groups)
    ]

    return BoxplotStats(
        group_labels=lbls,
        medians=medians,
        means=means,
        q1=q1,
        q3=q3,
        iqr=iqr,
        whisker_low=whisker_low,
        whisker_high=whisker_high,
        outliers=outliers,
    )


# ---------------------------------------------------------------------------
# Análisis de heatmap / matriz
# ---------------------------------------------------------------------------


def heatmap_stats(
    Z: Sequence | np.ndarray,
) -> dict[str, float | np.ndarray]:
    """
    Estadísticas básicas de una matriz 2D (para heatmap).

    Devuelve un diccionario con: mean, std, min, max, row_means,
    col_means, row_std, col_std, global_sum, frobenius_norm.
    """
    Z = np.asarray(Z, dtype=float)
    return {
        "mean": float(Z.mean()),
        "std": float(Z.std()),
        "min": float(Z.min()),
        "max": float(Z.max()),
        "global_sum": float(Z.sum()),
        "frobenius_norm": float(np.linalg.norm(Z, "fro")),
        "row_means": Z.mean(axis=1),
        "col_means": Z.mean(axis=0),
        "row_std": Z.std(axis=1),
        "col_std": Z.std(axis=0),
    }


# ---------------------------------------------------------------------------
# Bondad de ajuste
# ---------------------------------------------------------------------------


def r_squared(
    y_true: Sequence | np.ndarray,
    y_pred: Sequence | np.ndarray,
) -> float:
    """Coeficiente de determinación R²."""
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((yt - yp) ** 2)
    ss_tot = np.sum((yt - yt.mean()) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0


def adjusted_r_squared(
    y_true: Sequence | np.ndarray,
    y_pred: Sequence | np.ndarray,
    n_predictors: int,
) -> float:
    """R² ajustado para modelos con múltiples predictores."""
    n = len(y_true)
    r2 = r_squared(y_true, y_pred)
    return 1 - (1 - r2) * (n - 1) / (n - n_predictors - 1)


def chi_squared_goodness_of_fit(
    observed: Sequence | np.ndarray,
    expected: Sequence | np.ndarray,
) -> dict[str, float]:
    """
    Test chi² de bondad de ajuste.

    Devuelve: chi2_stat, df, p_value (requiere scipy, None si no disponible).
    """
    obs = np.asarray(observed, dtype=float)
    exp = np.asarray(expected, dtype=float)
    chi2 = float(np.sum((obs - exp) ** 2 / np.where(exp != 0, exp, np.nan)))
    df = len(obs) - 1
    p_val = None
    try:
        from scipy.stats import chi2 as chi2_dist  # type: ignore

        p_val = float(1 - chi2_dist.cdf(chi2, df))
    except ImportError:
        pass
    return {"chi2_stat": chi2, "df": df, "p_value": p_val}
