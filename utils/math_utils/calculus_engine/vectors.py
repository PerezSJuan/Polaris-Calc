import numpy as np
import math
from typing import Union


"""── Construction ──────────────────────────────────────────────────────────────"""

def vector(*args: float) -> list:
    """Create a vector from variable number of float arguments. Args: *args (numbers)."""
    return list(args)


def zero_vector(n: int) -> list:
    """Create a zero vector of dimension n. Args: n (dimension)."""
    return [0.0] * n


def unit_basis(dimension: int, index: int) -> list:
    """Create the k-th standard unit basis vector (e_k) of given dimension. Args: dimension, index (0-based)."""
    if index < 0 or index >= dimension:
        raise ValueError("index must be in [0, dimension-1].")
    v = [0.0] * dimension
    v[index] = 1.0
    return v


def from_list(elements: list) -> list:
    """Convert a list of numbers to a float vector. Args: elements."""
    return [float(x) for x in elements]


def uniform_vector(n: int, value: float = 1.0) -> list:
    """Create a vector with all elements set to the same value. Args: n, value (default 1.0)."""
    return [float(value)] * n


def random_vector(n: int, seed: int = None) -> list:
    """Create a random vector of dimension n with values in [-1, 1]. Args: n, seed (optional)."""
    if seed is not None:
        np.random.seed(seed)
    return np.random.uniform(-1, 1, n).tolist()


"""── Properties ────────────────────────────────────────────────────────────────"""

def magnitude(v: list) -> float:
    """Compute the Euclidean norm (L2 magnitude) of a vector. Args: v."""
    return math.sqrt(sum(x * x for x in v))


def magnitude_squared(v: list) -> float:
    """Compute the squared Euclidean norm (|v|^2). Args: v."""
    return sum(x * x for x in v)


def dimension(v: list) -> int:
    """Return the number of elements (dimension) of a vector. Args: v."""
    return len(v)


def normalize(v: list) -> list:
    """Return the unit vector in the same direction. Raises ValueError if zero. Args: v."""
    m = magnitude(v)
    if m == 0:
        raise ValueError("Cannot normalize a zero vector.")
    return [x / m for x in v]


def normalize_safe(v: list, default: list = None) -> list:
    """Normalize safely: returns default or zero vector if magnitude is 0. Args: v, default (optional)."""
    m = magnitude(v)
    if m == 0:
        if default is not None:
            return default
        return [0.0] * len(v)
    return [x / m for x in v]


def normalize_zero(v: list) -> list:
    """Normalize a vector; returns the original vector if magnitude is 0. Args: v."""
    if magnitude(v) == 0:
        return v
    return normalize(v)


def sum_vector(v: list) -> float:
    """Compute the sum of all elements in a vector. Args: v."""
    return sum(v)


"""── Arithmetic ────────────────────────────────────────────────────────────────"""

def add(v1: list, v2: list) -> list:
    """Add two vectors element-wise (same dimension required). Args: v1, v2."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    return [a + b for a, b in zip(v1, v2)]


def sub(v1: list, v2: list) -> list:
    """Subtract v2 from v1 element-wise (same dimension required). Args: v1, v2."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    return [a - b for a, b in zip(v1, v2)]


def scalar_mul(v: list, s: float) -> list:
    """Multiply vector by scalar s. Args: v, s."""
    return [x * s for x in v]


def scalar_div(v: list, s: float) -> list:
    """Divide vector by scalar s. Raises ZeroDivisionError if s=0. Args: v, s."""
    if s == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return [x / s for x in v]


def negate(v: list) -> list:
    """Negate all elements of a vector. Args: v."""
    return [-x for x in v]


def elementwise_mul(v1: list, v2: list) -> list:
    """Multiply two vectors element-wise (Hadamard product). Args: v1, v2 (same dimension)."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    return [a * b for a, b in zip(v1, v2)]


def elementwise_div(v1: list, v2: list) -> list:
    """Divide v1 by v2 element-wise. Inf returned for division by zero. Args: v1, v2 (same dimension)."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    return [a / b if b != 0 else float("inf") for a, b in zip(v1, v2)]


def elementwise_pow(v: list, p: float) -> list:
    """Raise each element of a vector to power p. Args: v, p."""
    return [x ** p for x in v]


"""── Products ──────────────────────────────────────────────────────────────────"""

def dot(v1: list, v2: list) -> float:
    """Compute the dot (inner) product of two vectors. Args: v1, v2 (same dimension)."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    return sum(a * b for a, b in zip(v1, v2))


def cross(v1: list, v2: list) -> list:
    """Compute the cross product of two 3D vectors. Raises ValueError if not 3D. Args: v1, v2."""
    if len(v1) != 3 or len(v2) != 3:
        raise ValueError("Cross product requires 3-dimensional vectors.")
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    ]


def outer_product(v1: list, v2: list) -> list:
    """Compute the outer product v1 ⊗ v2 (matrix of a_i * b_j). Args: v1, v2."""
    return [[a * b for b in v2] for a in v1]


"""── Angles & geometry ─────────────────────────────────────────────────────────"""

def angle_between(v1: list, v2: list) -> float:
    """Compute the angle (in radians) between two vectors. Args: v1, v2."""
    d = dot(v1, v2)
    m1 = magnitude(v1)
    m2 = magnitude(v2)
    if m1 == 0 or m2 == 0:
        raise ValueError("Cannot compute angle with a zero vector.")
    cos_angle = max(-1, min(1, d / (m1 * m2)))
    return math.acos(cos_angle)


def cosine_similarity(v1: list, v2: list) -> float:
    """Compute the cosine similarity (cos(θ)) between two vectors. Args: v1, v2."""
    d = dot(v1, v2)
    m1 = magnitude(v1)
    m2 = magnitude(v2)
    if m1 == 0 or m2 == 0:
        return 0.0
    return max(-1, min(1, d / (m1 * m2)))


def projection(v: list, onto: list) -> list:
    """Compute the projection of v onto the direction of onto. Args: v, onto."""
    d = dot(onto, onto)
    if d == 0:
        raise ValueError("Cannot project onto a zero vector.")
    t = dot(v, onto) / d
    return [t * x for x in onto]


def rejection(v: list, onto: list) -> list:
    """Compute the rejection of v from onto (v minus its projection). Args: v, onto."""
    p = projection(v, onto)
    return [a - b for a, b in zip(v, p)]


def component(v: list, along: list) -> float:
    """Compute the scalar component of v along the direction of along. Args: v, along."""
    m = magnitude(along)
    if m == 0:
        raise ValueError("Cannot compute component along a zero vector.")
    return dot(v, along) / m


"""── Comparisons ───────────────────────────────────────────────────────────────"""

def are_orthogonal(v1: list, v2: list, tol: float = 1e-10) -> bool:
    """Check if two vectors are orthogonal (dot ≈ 0 within tol). Args: v1, v2, tol (default 1e-10)."""
    return abs(dot(v1, v2)) < tol


def are_parallel(v1: list, v2: list, tol: float = 1e-10) -> bool:
    """Check if two vectors are parallel (cross ≈ 0 for 3D, angle ≈ 0 or π for any). Args: v1, v2, tol."""
    m = magnitude(cross(v1, v2)) if len(v1) == 3 else abs(angle_between(v1, v2))
    if len(v1) == 3:
        return m < tol
    return m < tol or abs(m - math.pi) < tol


def are_equal(v1: list, v2: list, tol: float = 1e-10) -> bool:
    """Check if two vectors are element-wise equal within tolerance. Args: v1, v2, tol."""
    if len(v1) != len(v2):
        return False
    return all(abs(a - b) < tol for a, b in zip(v1, v2))


def is_zero_vector(v: list, tol: float = 1e-10) -> bool:
    """Check if all elements of v are approximately zero. Args: v, tol."""
    return all(abs(x) < tol for x in v)


def is_unit_vector(v: list, tol: float = 1e-10) -> bool:
    """Check if the magnitude of v is approximately 1. Args: v, tol."""
    return abs(magnitude(v) - 1) < tol


"""── Distances ─────────────────────────────────────────────────────────────────"""

def euclidean_distance(v1: list, v2: list) -> float:
    """Compute the Euclidean (L2) distance between two vectors. Args: v1, v2."""
    return magnitude(sub(v1, v2))


def manhattan_distance(v1: list, v2: list) -> float:
    """Compute the Manhattan (L1) distance between two vectors. Args: v1, v2."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    return sum(abs(a - b) for a, b in zip(v1, v2))


def chebyshev_distance(v1: list, v2: list) -> float:
    """Compute the Chebyshev (L∞) distance between two vectors. Args: v1, v2."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    return max(abs(a - b) for a, b in zip(v1, v2))


def cosine_distance(v1: list, v2: list) -> float:
    """Compute the cosine distance (1 - cosine_similarity). Args: v1, v2."""
    return 1 - cosine_similarity(v1, v2)


def minkowski_distance(v1: list, v2: list, p: float) -> float:
    """Compute the Minkowski distance of order p. Args: v1, v2, p (positive)."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension.")
    if p <= 0:
        raise ValueError("p must be positive.")
    return sum(abs(a - b) ** p for a, b in zip(v1, v2)) ** (1 / p)


"""── Linear combinations ───────────────────────────────────────────────────────"""

def linear_combination(vectors: list, coefficients: list) -> list:
    """Compute Σ c_i * v_i (linear combination of vectors with coefficients). Args: vectors, coefficients."""
    if not vectors or not coefficients:
        raise ValueError("Vectors and coefficients must not be empty.")
    if len(vectors) != len(coefficients):
        raise ValueError("Must have one coefficient per vector.")
    dim = len(vectors[0])
    result = [0.0] * dim
    for v, c in zip(vectors, coefficients):
        for i in range(dim):
            result[i] += v[i] * c
    return result


def convex_combination(vectors: list, weights: list) -> list:
    """Compute a convex combination (weights normalized to sum 1). Args: vectors, weights."""
    if not vectors or not weights:
        raise ValueError("Vectors and weights must not be empty.")
    if len(vectors) != len(weights):
        raise ValueError("Must have one weight per vector.")
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total weight must not be zero.")
    return linear_combination(vectors, [w / total_weight for w in weights])


"""── Gram-Schmidt orthogonalization ────────────────────────────────────────────"""

def gram_schmidt(vectors: list) -> list:
    """Orthogonalize a set of vectors using the Gram-Schmidt process. Args: vectors."""
    result = []
    for v in vectors:
        w = v[:]
        for u in result:
            proj = projection(v, u)
            w = sub(w, proj)
        if not is_zero_vector(w):
            result.append(w)
    return result


def orthonormalize(vectors: list) -> list:
    """Orthogonalize then normalize (produce orthonormal basis). Args: vectors."""
    orthogonal = gram_schmidt(vectors)
    return [normalize(v) for v in orthogonal]


"""── Statistical ───────────────────────────────────────────────────────────────"""

def mean_vector(vectors: list) -> list:
    """Compute the element-wise mean of a list of vectors. Args: vectors (list of lists)."""
    if not vectors:
        raise ValueError("List of vectors must not be empty.")
    dim = len(vectors[0])
    result = [0.0] * dim
    for v in vectors:
        for i in range(dim):
            result[i] += v[i]
    return [x / len(vectors) for x in result]


def centroid(vectors: list) -> list:
    """Alias for mean_vector: compute the centroid of a set of vectors. Args: vectors."""
    return mean_vector(vectors)


"""── Triple products ───────────────────────────────────────────────────────────"""

def scalar_triple_product(a: list, b: list, c: list) -> float:
    """Compute the scalar triple product a · (b × c). Args: a, b, c (3D vectors)."""
    return dot(a, cross(b, c))


def vector_triple_product(a: list, b: list, c: list) -> list:
    """Compute the vector triple product a × (b × c). Args: a, b, c (3D vectors)."""
    return cross(a, cross(b, c))


"""── Matrix-vector ─────────────────────────────────────────────────────────────"""

def matrix_vector_mul(matrix: list, v: list) -> list:
    """Multiply matrix (list of rows) by vector, yielding a new vector. Args: matrix, v."""
    if not matrix or not v:
        raise ValueError("Matrix and vector must not be empty.")
    if len(matrix[0]) != len(v):
        raise ValueError("Matrix columns must match vector dimension.")
    return [sum(row[i] * v[i] for i in range(len(v))) for row in matrix]


"""── Misc ──────────────────────────────────────────────────────────────────────"""

def midpoint(v1: list, v2: list) -> list:
    """Compute the midpoint (average) of two vectors. Args: v1, v2."""
    return [(a + b) / 2 for a, b in zip(v1, v2)]


def lerp(v1: list, v2: list, t: float) -> list:
    """Linear interpolation between two vectors: (1-t)*v1 + t*v2. Args: v1, v2, t."""
    return [(1 - t) * a + t * b for a, b in zip(v1, v2)]


def pairwise_sum(vectors: list) -> list:
    """Compute the element-wise sum of a list of vectors. Args: vectors."""
    if not vectors:
        raise ValueError("List of vectors must not be empty.")
    dim = len(vectors[0])
    result = [0.0] * dim
    for v in vectors:
        for i in range(dim):
            result[i] += v[i]
    return result


def pairwise_max(vectors: list) -> list:
    """Compute the element-wise maximum of a list of vectors. Args: vectors."""
    if not vectors:
        raise ValueError("List of vectors must not be empty.")
    dim = len(vectors[0])
    result = [-float("inf")] * dim
    for v in vectors:
        for i in range(dim):
            if v[i] > result[i]:
                result[i] = v[i]
    return result


def pairwise_min(vectors: list) -> list:
    """Compute the element-wise minimum of a list of vectors. Args: vectors."""
    if not vectors:
        raise ValueError("List of vectors must not be empty.")
    dim = len(vectors[0])
    result = [float("inf")] * dim
    for v in vectors:
        for i in range(dim):
            if v[i] < result[i]:
                result[i] = v[i]
    return result


"""── Advanced vector operations ────────────────────────────────────────────────"""


def reflect(v: list, normal: list) -> list:
    """Reflect vector v across the given normal. Args: v, normal."""
    n = normalize(normal)
    dot_vn = dot(v, n)
    return [v[i] - 2 * dot_vn * n[i] for i in range(len(v))]


def rotate_around(v: list, axis: list, angle: float) -> list:
    """Rotate vector v around axis by angle radians (Rodrigues). Args: v, axis, angle."""
    k = normalize(axis)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dot_vk = dot(v, k)
    term1 = [cos_a * v[i] for i in range(len(v))]
    term2 = [sin_a * x for x in cross(k, v)]
    term3 = [(1 - cos_a) * dot_vk * k[i] for i in range(len(v))]
    return [term1[i] + (term2[i] if i < len(term2) else 0) + term3[i] for i in range(len(v))]


def slerp(v1: list, v2: list, t: float) -> list:
    """Spherical linear interpolation between v1 and v2. Args: v1, v2, t (0 to 1)."""
    n1 = normalize(v1)
    n2 = normalize(v2)
    omega = math.acos(max(-1, min(1, dot(n1, n2))))
    if abs(omega) < 1e-12:
        return [(1 - t) * v1[i] + t * v2[i] for i in range(len(v1))]
    sin_omega = math.sin(omega)
    s1 = math.sin((1 - t) * omega) / sin_omega
    s2 = math.sin(t * omega) / sin_omega
    r = (1 - t) * magnitude(v1) + t * magnitude(v2)
    return [r * (s1 * n1[i] + s2 * n2[i]) for i in range(len(v1))]


def gram_matrix(vectors: list) -> list:
    """Compute the Gram matrix of inner products. Args: vectors (list of vectors)."""
    n = len(vectors)
    G = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            G[i][j] = dot(vectors[i], vectors[j])
    return G


def distance_matrix(vectors: list) -> list:
    """Compute the pairwise Euclidean distance matrix. Args: vectors (list of vectors)."""
    n = len(vectors)
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            D[i][j] = euclidean_distance(vectors[i], vectors[j])
    return D


def clamp(v: list, min_val: float, max_val: float) -> list:
    """Clamp each component of v to [min_val, max_val]. Args: v, min_val, max_val."""
    return [max(min_val, min(max_val, x)) for x in v]


def random_unit_vector(n: int, seed: int = None) -> list:
    """Generate a random vector uniformly distributed on the unit n-sphere. Args: n (dimension), seed (optional)."""
    import random as _random
    if seed is not None:
        _random.seed(seed)
    v = [_random.gauss(0, 1) for _ in range(n)]
    mag = math.sqrt(sum(x * x for x in v))
    return [x / mag for x in v]


def cumulative_sum(v: list) -> list:
    """Compute the cumulative (running) sum of vector components. Args: v."""
    result = []
    total = 0.0
    for x in v:
        total += x
        result.append(total)
    return result
