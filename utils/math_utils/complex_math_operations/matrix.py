import numpy as np
import math
from typing import Union


"""── Construction ──────────────────────────────────────────────────────────────"""

def matrix(data: list) -> list:
    """Create a matrix (list of lists) from nested data. Args: data (2D list)."""
    return [list(row) for row in data]


def zeros(rows: int, cols: int) -> list:
    """Create an rows×cols zero matrix. Args: rows, cols."""
    return [[0.0] * cols for _ in range(rows)]


def ones(rows: int, cols: int) -> list:
    """Create an rows×cols matrix of ones. Args: rows, cols."""
    return [[1.0] * cols for _ in range(rows)]


def identity(n: int) -> list:
    """Create an n×n identity matrix. Args: n (size)."""
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def diag(elements: list) -> list:
    """Create a diagonal matrix from a list of elements. Args: elements."""
    n = len(elements)
    return [[elements[i] if i == j else 0.0 for j in range(n)] for i in range(n)]


def random(rows: int, cols: int, seed: int = None) -> list:
    """Create an rows×cols matrix with random values in [-1, 1]. Args: rows, cols, seed (optional)."""
    if seed is not None:
        np.random.seed(seed)
    return np.random.uniform(-1, 1, (rows, cols)).tolist()


def from_rows(rows: list) -> list:
    """Build a matrix from a list of rows. Args: rows (list of lists)."""
    return [list(r) for r in rows]


def from_columns(columns: list) -> list:
    """Build a matrix from a list of columns. Args: columns (list of lists)."""
    nrows = len(columns[0])
    ncols = len(columns)
    return [[columns[j][i] for j in range(ncols)] for i in range(nrows)]


def from_function(f, rows: int, cols: int) -> list:
    """Build a matrix by applying f(i, j) for each cell. Args: f (callable), rows, cols."""
    return [[f(i, j) for j in range(cols)] for i in range(rows)]


def vandermonde(x: list, n: int = None) -> list:
    """Create a Vandermonde matrix [[xi^j]]. Args: x (list), n (number of columns, default len(x))."""
    if n is None:
        n = len(x)
    return [[xi ** i for i in range(n)] for xi in x]


def hilbert(n: int) -> list:
    """Create an n×n Hilbert matrix H[i][j] = 1/(i+j+1). Args: n (size)."""
    return [[1.0 / (i + j + 1) for j in range(n)] for i in range(n)]


"""── Properties ────────────────────────────────────────────────────────────────"""

def shape(matrix_: list) -> tuple:
    """Return the (rows, cols) shape of a matrix. Args: matrix_."""
    if not matrix_:
        return (0, 0)
    return (len(matrix_), len(matrix_[0]))


def size(matrix_: list) -> int:
    """Return the total number of elements (rows * cols). Args: matrix_."""
    r, c = shape(matrix_)
    return r * c


def rank(matrix_: list) -> int:
    """Compute the matrix rank (number of linearly independent rows/cols). Args: matrix_."""
    return int(np.linalg.matrix_rank(np.array(matrix_, dtype=float)))


def trace(matrix_: list) -> float:
    """Compute the trace (sum of diagonal elements). Raises ValueError if not square. Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("Matrix must be square.")
    return float(np.trace(a))


def determinant(matrix_: list) -> float:
    """Compute the determinant of a square matrix. Args: matrix_."""
    return float(np.linalg.det(np.array(matrix_, dtype=float)))


def condition_number(matrix_: list) -> float:
    """Compute the condition number of a matrix (measures sensitivity). Args: matrix_."""
    return float(np.linalg.cond(np.array(matrix_, dtype=float)))


def norm(matrix_: list, ord: str = "fro") -> float:
    """Compute the norm of a matrix (default Frobenius). Args: matrix_, ord (default "fro")."""
    return float(np.linalg.norm(np.array(matrix_, dtype=float), ord=ord))


"""── Boolean properties ────────────────────────────────────────────────────────"""

def is_square(matrix_: list) -> bool:
    """Check if the matrix is square (rows == cols). Args: matrix_."""
    r, c = shape(matrix_)
    return r == c


def is_symmetric(matrix_: list) -> bool:
    """Check if the matrix is symmetric (A == A^T). Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        return False
    return np.allclose(a, a.T)


def is_skew_symmetric(matrix_: list) -> bool:
    """Check if the matrix is skew-symmetric (A == -A^T). Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        return False
    return np.allclose(a, -a.T)


def is_positive_definite(matrix_: list) -> bool:
    """Check if matrix is positive definite (Cholesky succeeds). Args: matrix_."""
    try:
        np.linalg.cholesky(np.array(matrix_, dtype=float))
        return True
    except np.linalg.LinAlgError:
        return False


def is_diagonal(matrix_: list) -> bool:
    """Check if only diagonal elements are non-zero. Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2:
        return False
    i, j = np.nonzero(a)
    return np.all(i == j) or len(i) == 0


def is_identity(matrix_: list) -> bool:
    """Check if the matrix is the identity matrix. Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        return False
    return np.allclose(a, np.eye(a.shape[0]))


def is_orthogonal(matrix_: list) -> bool:
    """Check if the matrix is orthogonal (A @ A^T == I). Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        return False
    return np.allclose(a @ a.T, np.eye(a.shape[0]))


def is_singular(matrix_: list) -> bool:
    """Check if the square matrix is singular (det ≈ 0). Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("Matrix must be square.")
    return abs(np.linalg.det(a)) < 1e-12


def is_involutory(matrix_: list) -> bool:
    """Check if matrix is involutory (A @ A == I). Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        return False
    return np.allclose(a @ a, np.eye(a.shape[0]))


def is_nilpotent(matrix_: list, max_power: int = 10) -> bool:
    """Check if matrix is nilpotent (A^k == 0 for some k ≤ max_power). Args: matrix_, max_power (default 10)."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        return False
    p = a.copy()
    for _ in range(1, max_power + 1):
        if np.allclose(p, np.zeros_like(p)):
            return True
        p = p @ a
    return False


def is_upper_triangular(matrix_: list) -> bool:
    """Check if the matrix is upper triangular (zeros below diagonal). Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2:
        return False
    return np.allclose(a, np.triu(a))


def is_lower_triangular(matrix_: list) -> bool:
    """Check if the matrix is lower triangular (zeros above diagonal). Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2:
        return False
    return np.allclose(a, np.tril(a))


"""── Arithmetic ────────────────────────────────────────────────────────────────"""

def add(m1: list, m2: list) -> list:
    """Add two matrices element-wise. Args: m1, m2."""
    return np.add(np.array(m1, dtype=float), np.array(m2, dtype=float)).tolist()


def sub(m1: list, m2: list) -> list:
    """Subtract m2 from m1 element-wise. Args: m1, m2."""
    return np.subtract(np.array(m1, dtype=float), np.array(m2, dtype=float)).tolist()


def mul(m1: list, m2: list) -> list:
    """Multiply two matrices (matrix product). Args: m1, m2."""
    return (np.array(m1, dtype=float) @ np.array(m2, dtype=float)).tolist()


def scalar_mul(matrix_: list, s: float) -> list:
    """Multiply a matrix by a scalar. Args: matrix_, s (scalar)."""
    return (np.array(matrix_, dtype=float) * s).tolist()


def elementwise_mul(m1: list, m2: list) -> list:
    """Multiply two matrices element-wise (Hadamard product). Args: m1, m2."""
    return np.multiply(np.array(m1, dtype=float), np.array(m2, dtype=float)).tolist()


def elementwise_div(m1: list, m2: list) -> list:
    """Divide matrix m1 by m2 element-wise. Args: m1, m2."""
    return np.divide(np.array(m1, dtype=float), np.array(m2, dtype=float)).tolist()


def elementwise_pow(matrix_: list, p: float) -> list:
    """Raise each element of a matrix to power p. Args: matrix_, p."""
    return (np.array(matrix_, dtype=float) ** p).tolist()


"""── Transforms ────────────────────────────────────────────────────────────────"""

def transpose(matrix_: list) -> list:
    """Transpose a matrix (swap rows and columns). Args: matrix_."""
    return np.array(matrix_, dtype=float).T.tolist()


def inverse(matrix_: list) -> list:
    """Compute the inverse of a square matrix. Raises ValueError if not square. Args: matrix_."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("Matrix must be square.")
    return np.linalg.inv(a).tolist()


def power(matrix_: list, n: int) -> list:
    """Raise a square matrix to integer power n (negative n uses inverse). Args: matrix_, n."""
    a = np.array(matrix_, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("Matrix must be square.")
    if n < 0:
        a = np.linalg.inv(a)
        n = -n
    return np.linalg.matrix_power(a, n).tolist()


def flatten(matrix_: list) -> list:
    """Flatten a matrix into a 1D list (row-major). Args: matrix_."""
    return np.array(matrix_, dtype=float).flatten().tolist()


def reshape(matrix_: list, new_rows: int, new_cols: int) -> list:
    """Reshape a matrix to new dimensions (product must match). Args: matrix_, new_rows, new_cols."""
    return np.array(matrix_, dtype=float).reshape(new_rows, new_cols).tolist()


def diagonal(matrix_: list) -> list:
    """Extract the diagonal entries of a matrix as a list. Args: matrix_."""
    return np.diag(np.array(matrix_, dtype=float)).tolist()


"""── Decompositions ────────────────────────────────────────────────────────────"""

def lu(matrix_: list) -> tuple:
    """LU decomposition with partial pivoting: (P, L, U). Args: matrix_."""
    from scipy.linalg import lu as sp_lu
    p, l, u = sp_lu(np.array(matrix_, dtype=float))
    return p.tolist(), l.tolist(), u.tolist()


def qr(matrix_: list) -> tuple:
    """QR decomposition: (Q, R) where Q is orthogonal, R is upper triangular. Args: matrix_."""
    q, r = np.linalg.qr(np.array(matrix_, dtype=float))
    return q.tolist(), r.tolist()


def svd(matrix_: list, full_matrices: bool = True) -> tuple:
    """Singular value decomposition: (U, S, V^T). Args: matrix_, full_matrices (default True)."""
    u, s, vt = np.linalg.svd(np.array(matrix_, dtype=float), full_matrices=full_matrices)
    return u.tolist(), s.tolist(), vt.tolist()


def cholesky(matrix_: list) -> list:
    """Cholesky decomposition (L where A = L L^T). Args: matrix_ (positive definite)."""
    return np.linalg.cholesky(np.array(matrix_, dtype=float)).tolist()


def eigen(matrix_: list) -> tuple:
    """Compute eigenvalues and eigenvectors: (eigvals, eigvecs). Args: matrix_."""
    eigvals, eigvecs = np.linalg.eig(np.array(matrix_, dtype=float))
    return eigvals.tolist(), eigvecs.tolist()


def eigvals(matrix_: list) -> list:
    """Compute eigenvalues only (general matrix). Args: matrix_."""
    return np.linalg.eigvals(np.array(matrix_, dtype=float)).tolist()


def eigvalsh(matrix_: list) -> list:
    """Compute eigenvalues of a symmetric/Hermitian matrix (real). Args: matrix_."""
    return np.linalg.eigvalsh(np.array(matrix_, dtype=float)).tolist()


def eigh(matrix_: list) -> tuple:
    """Compute eigenvalues and eigenvectors for symmetric/Hermitian: (vals, vecs). Args: matrix_."""
    eigvals, eigvecs = np.linalg.eigh(np.array(matrix_, dtype=float))
    return eigvals.tolist(), eigvecs.tolist()


"""── Solving ───────────────────────────────────────────────────────────────────"""

def solve_linear(A: list, b: list) -> list:
    """Solve the linear system Ax = b (A must be square and invertible). Args: A, b."""
    return np.linalg.solve(np.array(A, dtype=float), np.array(b, dtype=float)).tolist()


def lstsq(A: list, b: list) -> list:
    """Solve Ax = b in the least-squares sense (minimizes ||Ax - b||). Args: A, b."""
    return np.linalg.lstsq(np.array(A, dtype=float), np.array(b, dtype=float), rcond=None)[0].tolist()


"""── Augmented & block operations ──────────────────────────────────────────────"""

def hstack(matrices: list) -> list:
    """Horizontally stack matrices (same number of rows). Args: matrices (list of 2D lists)."""
    return np.hstack([np.array(m, dtype=float) for m in matrices]).tolist()


def vstack(matrices: list) -> list:
    """Vertically stack matrices (same number of columns). Args: matrices (list of 2D lists)."""
    return np.vstack([np.array(m, dtype=float) for m in matrices]).tolist()


def block_diag(matrices: list) -> list:
    """Create a block diagonal matrix from a list of matrices. Args: matrices."""
    from scipy.linalg import block_diag as sp_block_diag
    return sp_block_diag(*[np.array(m, dtype=float) for m in matrices]).tolist()


"""── Row operations ────────────────────────────────────────────────────────────"""

def swap_rows(matrix_: list, i: int, j: int) -> list:
    """Swap rows i and j of a matrix (returns a new matrix). Args: matrix_, i, j."""
    result = [list(row) for row in matrix_]
    result[i], result[j] = result[j], result[i]
    return result


def scale_row(matrix_: list, i: int, factor: float) -> list:
    """Multiply row i by a non-zero factor (returns a new matrix). Args: matrix_, i, factor."""
    if factor == 0:
        raise ValueError("Scale factor must not be zero.")
    result = [list(row) for row in matrix_]
    for j in range(len(result[i])):
        result[i][j] *= factor
    return result


def add_row_multiple(matrix_: list, source: int, target: int, factor: float) -> list:
    """Add factor * row[source] to row[target] (returns a new matrix). Args: matrix_, source, target, factor."""
    result = [list(row) for row in matrix_]
    for j in range(len(result[target])):
        result[target][j] += factor * result[source][j]
    return result


def row_echelon(matrix_: list) -> list:
    """Convert to row echelon form via Gaussian elimination (forward elimination only). Args: matrix_."""
    a = np.array(matrix_, dtype=float, ndmin=2)
    m, n = a.shape
    r = 0
    for c in range(n):
        pivot = None
        for i in range(r, m):
            if abs(a[i, c]) > 1e-12:
                pivot = i
                break
        if pivot is None:
            continue
        if pivot != r:
            a[[r, pivot]] = a[[pivot, r]]
        a[r] = a[r] / a[r, c]
        for i in range(r + 1, m):
            a[i] = a[i] - a[i, c] * a[r]
        r += 1
        if r == m:
            break
    return a.tolist()


def rref(matrix_: list) -> list:
    """Convert to reduced row echelon form (Gauss-Jordan elimination). Args: matrix_."""
    a = np.array(matrix_, dtype=float, ndmin=2)
    m, n = a.shape
    r = 0
    for c in range(n):
        pivot = None
        for i in range(r, m):
            if abs(a[i, c]) > 1e-12:
                pivot = i
                break
        if pivot is None:
            continue
        if pivot != r:
            a[[r, pivot]] = a[[pivot, r]]
        a[r] = a[r] / a[r, c]
        for i in range(m):
            if i != r:
                a[i] = a[i] - a[i, c] * a[r]
        r += 1
        if r == m:
            break
    return a.tolist()


"""── Special matrices ──────────────────────────────────────────────────────────"""

def companion(poly: list) -> list:
    """Build the companion matrix of a polynomial (last row has negated coefficients). Args: poly [a0..an]."""
    n = len(poly) - 1
    if n <= 0:
        raise ValueError("Polynomial must have at least degree 1.")
    c = zeros(n, n)
    for i in range(n - 1):
        c[i + 1][i] = 1.0
    for i in range(n):
        c[i][n - 1] = -poly[n - 1 - i] / poly[n]
    return c


def cauchy(x: list, y: list) -> list:
    """Build a Cauchy matrix C[i][j] = 1/(x_i + y_j). Args: x, y (lists)."""
    return [[1.0 / (xi + yj) for yj in y] for xi in x]


"""── Kronecker ─────────────────────────────────────────────────────────────────"""

def kronecker_product(m1: list, m2: list) -> list:
    """Compute the Kronecker product A ⊗ B. Args: m1, m2."""
    return np.kron(np.array(m1, dtype=float), np.array(m2, dtype=float)).tolist()


def kronecker_sum(m1: list, m2: list) -> list:
    """Compute the Kronecker sum A ⊕ B = A⊗I + I⊗B. Args: m1, m2 (square)."""
    a = np.array(m1, dtype=float)
    b = np.array(m2, dtype=float)
    return (np.kron(a, np.eye(b.shape[0])) + np.kron(np.eye(a.shape[0]), b)).tolist()


"""── Misc ──────────────────────────────────────────────────────────────────────"""

def matrix_power_series(A: list, coefficients: list) -> list:
    """Evaluate Σ c_i * A^i (matrix power series). Args: A (square), coefficients."""
    a = np.array(A, dtype=float)
    result = np.zeros_like(a)
    for i, c in enumerate(coefficients):
        result = result + c * np.linalg.matrix_power(a, i)
    return result.tolist()


def matrix_exp(A: list) -> list:
    """Compute the matrix exponential e^A (uses scipy). Args: A (square)."""
    from scipy.linalg import expm
    return expm(np.array(A, dtype=float)).tolist()


def matrix_log(A: list) -> list:
    """Compute the matrix logarithm log(A) (uses scipy). Args: A (square)."""
    from scipy.linalg import logm
    return logm(np.array(A, dtype=float)).tolist()


def matrix_sqrt(A: list) -> list:
    """Compute the matrix square root sqrtm(A) (uses scipy). Args: A (square)."""
    from scipy.linalg import sqrtm
    return sqrtm(np.array(A, dtype=float)).tolist()


def matrix_sin(A: list) -> list:
    """Compute the matrix sine sin(A) (uses scipy). Args: A (square)."""
    from scipy.linalg import sinm
    return sinm(np.array(A, dtype=float)).tolist()


def matrix_cos(A: list) -> list:
    """Compute the matrix cosine cos(A) (uses scipy). Args: A (square)."""
    from scipy.linalg import cosm
    return cosm(np.array(A, dtype=float)).tolist()


"""── Advanced matrix functions ─────────────────────────────────────────────────"""


def adjugate(A: list) -> list:
    """Compute the adjugate (classical adjoint) of a square matrix. Args: A."""
    A_np = np.array(A, dtype=float)
    n = A_np.shape[0]
    if n == 1:
        return [[1.0]]
    minors = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            minor = np.delete(np.delete(A_np, i, axis=0), j, axis=1)
            minors[i, j] = ((-1) ** (i + j)) * np.linalg.det(minor)
    return minors.T.tolist()


def characteristic_poly(A: list) -> list:
    """Return the coefficients of the characteristic polynomial det(xI - A). Args: A (square)."""
    A_np = np.array(A, dtype=float)
    return np.poly(A_np).tolist()


def pascal(n: int, kind: str = "symmetric") -> list:
    """Generate a Pascal matrix of size n. Args: n, kind ('symmetric', 'lower', 'upper')."""
    P = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            from math import comb as _comb
            val = _comb(i + j, i)
            if kind == "lower":
                val = _comb(i, j) if i >= j else 0
            elif kind == "upper":
                val = _comb(j, i) if j >= i else 0
            P[i][j] = float(val)
    return P


def frobenius_inner(A: list, B: list) -> float:
    """Compute the Frobenius inner product trace(A^T B). Args: A, B."""
    A_np = np.array(A, dtype=float)
    B_np = np.array(B, dtype=float)
    return float(np.trace(A_np.T @ B_np))
