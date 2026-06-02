import sys
import os
import math
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
ops_path = os.path.join(project_root, "utils", "math_utils", "complex_math_operations")

if ops_path not in sys.path:
    sys.path.append(ops_path)

from complex import (
    complex_num, from_polar, to_polar, modulus, argument, argument_degrees,
    conjugate, sign, squared_modulus,
    add, sub, mul, div, pow_, sqrt, reciprocal, negate,
    exp, ln, log, log10, log2,
    sin, cos, tan, cot, sec, csc,
    asin, acos, atan, acot,
    sinh, cosh, tanh, coth, sech, csch,
    asinh, acosh, atanh, acoth,
    sum_, product, mean, dot_product, distance,
    roots_of_unity, nth_roots,
    phasor, phasor_rad, phase_shift, impedance,
    polyval, polyroots,
    approx_equal, is_zero, is_real, is_imaginary, is_unit_modulus,
    rotate, lerp,
    complex_identity, complex_zeros,
    mobius, slerp, newton, mandelbrot, random_complex
)
from vectors import (
    vector, zero_vector, unit_basis, from_list, uniform_vector, random_vector,
    magnitude, magnitude_squared, dimension, normalize, normalize_safe, normalize_zero, sum_vector,
    add as v_add, sub as v_sub, scalar_mul, scalar_div, negate as v_negate,
    elementwise_mul, elementwise_div, elementwise_pow,
    dot, cross, outer_product,
    angle_between, cosine_similarity, projection, rejection, component,
    are_orthogonal, are_parallel, are_equal, is_zero_vector, is_unit_vector,
    euclidean_distance, manhattan_distance, chebyshev_distance, cosine_distance, minkowski_distance,
    linear_combination, convex_combination,
    gram_schmidt, orthonormalize,
    mean_vector, centroid,
    scalar_triple_product, vector_triple_product,
    matrix_vector_mul,
    midpoint, lerp as v_lerp, pairwise_sum, pairwise_max, pairwise_min,
    reflect, rotate_around, slerp as v_slerp, gram_matrix, distance_matrix,
    clamp, random_unit_vector, cumulative_sum
)
from matrix import (
    matrix, zeros, ones, identity, diag, random, from_rows, from_columns, from_function,
    vandermonde, hilbert,
    shape, size, rank, trace, determinant, condition_number, norm,
    is_square, is_symmetric, is_skew_symmetric, is_positive_definite,
    is_diagonal, is_identity, is_orthogonal, is_singular, is_involutory, is_nilpotent,
    is_upper_triangular, is_lower_triangular,
    add as m_add, sub as m_sub, mul as m_mul, scalar_mul as m_scalar_mul,
    elementwise_mul as m_elem_mul, elementwise_div as m_elem_div, elementwise_pow as m_elem_pow,
    transpose, inverse, power, flatten, reshape, diagonal,
    lu, qr, svd, cholesky, eigen, eigvals, eigvalsh, eigh,
    solve_linear, lstsq,
    hstack, vstack, block_diag,
    swap_rows, scale_row, add_row_multiple, row_echelon, rref,
    companion, cauchy,
    kronecker_product, kronecker_sum,
    matrix_power_series, matrix_exp, matrix_log, matrix_sqrt, matrix_sin, matrix_cos,
    adjugate, characteristic_poly, pascal, frobenius_inner
)
from bools import (
    true, false,
    not_, and_, or_, xor_, nand_, nor_, xnor_, implies_, iff_,
    if_, if_error, if_na, switch, choose,
    equal, not_equal, greater_than, less_than, greater_equal, less_equal,
    and_all, or_any, xor_all, not_all,
    elementwise_and, elementwise_or, elementwise_xor,
    is_true, is_false, is_number, is_text, is_non_text,
    is_even, is_odd, is_blank, is_logical,
    count_true, count_false, is_error,
    and_ifs, or_ifs,
    logical_value, to_bool, to_number,
    bitwise_and, bitwise_or, bitwise_xor,
    majority, exactly_one,
    at_least_n, at_most_n,
    all_same, all_different
)


# ── Complex number tests ─────────────────────────────────────────────────────

class TestComplexConstruction:
    def test_complex_num(self):
        z = complex_num(3, 4)
        assert z == 3 + 4j

    def test_from_polar(self):
        z = from_polar(1, math.pi)
        assert abs(z.real + 1) < 1e-10
        assert abs(z.imag) < 1e-10

    def test_to_polar(self):
        r, theta = to_polar(1 + 1j)
        assert abs(r - math.sqrt(2)) < 1e-10
        assert abs(theta - math.pi / 4) < 1e-10

    def test_modulus(self):
        assert modulus(3 + 4j) == 5.0

    def test_argument_zero(self):
        assert argument(1 + 0j) == 0.0

    def test_conjugate(self):
        assert conjugate(3 + 4j) == 3 - 4j


class TestComplexArithmetic:
    def test_add(self):
        assert add(1 + 2j, 3 + 4j) == 4 + 6j

    def test_sub(self):
        assert sub(5 + 5j, 3 + 2j) == 2 + 3j

    def test_mul(self):
        assert mul(1 + 2j, 3 + 4j) == (1+2j)*(3+4j)

    def test_div(self):
        assert div(1 + 2j, 1 + 1j) == (1+2j)/(1+1j)

    def test_div_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            div(1 + 0j, 0 + 0j)

    def test_sqrt(self):
        s = sqrt(-1 + 0j)
        assert abs(s - 1j) < 1e-10

    def test_sqrt_negative_real(self):
        s = sqrt(4 + 0j)
        assert abs(s - 2) < 1e-10


class TestComplexFunctions:
    def test_ln(self):
        l = ln(1 + 0j)
        assert abs(l) < 1e-10

    def test_sin(self):
        z = sin(math.pi / 2 + 0j)
        assert abs(z - 1) < 1e-10

    def test_cos_zero(self):
        z = cos(0 + 0j)
        assert abs(z - 1) < 1e-10

    def test_roots_of_unity(self):
        r = roots_of_unity(4)
        assert len(r) == 4
        assert abs(abs(r[0]) - 1) < 1e-10
        assert abs(r[1] - 1j) < 1e-10

    def test_nth_roots(self):
        r = nth_roots(8 + 0j, 3)
        assert len(r) == 3
        assert any(abs(x - 2) < 1e-10 for x in r)

    def test_polyval(self):
        v = polyval([1, 0, -1], 2)  # x^2 - 1 at x=2
        assert abs(v - 3) < 1e-10

    def test_polyroots(self):
        r = polyroots([1, 0, -1])  # x^2 - 1 = 0
        assert len(r) == 2
        assert -1 in [round(x, 10) for x in r]
        assert 1 in [round(x, 10) for x in r]

    def test_exp(self):
        z = exp(0 + 0j)
        assert abs(z - 1) < 1e-10

    def test_tan(self):
        z = tan(0 + 0j)
        assert abs(z) < 1e-10

    def test_sinh(self):
        z = sinh(0 + 0j)
        assert abs(z) < 1e-10

    def test_cosh(self):
        z = cosh(0 + 0j)
        assert abs(z - 1) < 1e-10

    def test_asin(self):
        z = asin(0 + 0j)
        assert abs(z) < 1e-10

    def test_acos(self):
        z = acos(1 + 0j)
        assert abs(z) < 1e-10

    def test_sign(self):
        s = sign(3 + 4j)
        assert abs(s - (3+4j)/5) < 1e-10

    def test_argument_degrees(self):
        a = argument_degrees(1 + 1j)
        assert abs(a - 45) < 1e-10

    def test_squared_modulus(self):
        assert squared_modulus(3 + 4j) == 25.0

    def test_reciprocal(self):
        r = reciprocal(2 + 0j)
        assert abs(r - 0.5) < 1e-10

    def test_sum_(self):
        assert sum_(1 + 0j, 2 + 0j, 3 + 0j) == 6 + 0j

    def test_product(self):
        assert product(1 + 0j, 2 + 0j, 3 + 0j) == 6 + 0j

    def test_rotate(self):
        z = rotate(1 + 0j, math.pi / 2)
        assert abs(z - 1j) < 1e-10

    def test_lerp(self):
        z = lerp(0 + 0j, 2 + 2j, 0.5)
        assert abs(z - (1 + 1j)) < 1e-10


class TestComplexComparison:
    def test_approx_equal(self):
        assert approx_equal(1 + 1j, 1 + 1.000000000001j)
        assert not approx_equal(1 + 1j, 2 + 1j)

    def test_is_real(self):
        assert is_real(3 + 0j)
        assert not is_real(3 + 1j)

    def test_is_imaginary(self):
        assert is_imaginary(0 + 4j)
        assert not is_imaginary(1 + 4j)

    def test_is_zero(self):
        assert is_zero(0 + 0j)
        assert not is_zero(1 + 0j)


# ── Vector tests ──────────────────────────────────────────────────────────────

class TestVectorConstruction:
    def test_vector(self):
        v = vector(1, 2, 3)
        assert v == [1, 2, 3]

    def test_magnitude(self):
        assert abs(magnitude([3, 4]) - 5) < 1e-10

    def test_normalize(self):
        v = normalize([3, 0])
        assert v == [1, 0]

    def test_normalize_zero_raises(self):
        with pytest.raises(ValueError):
            normalize([0, 0])


class TestVectorOperations:
    def test_dot(self):
        assert dot([1, 2, 3], [4, 5, 6]) == 32

    def test_cross(self):
        c = cross([1, 0, 0], [0, 1, 0])
        assert c == [0, 0, 1]

    def test_cross_non_3d_raises(self):
        with pytest.raises(ValueError):
            cross([1, 2], [3, 4])

    def test_angle_between(self):
        a = angle_between([1, 0], [0, 1])
        assert abs(a - math.pi / 2) < 1e-10

    def test_angle_parallel(self):
        a = angle_between([1, 0], [2, 0])
        assert abs(a) < 1e-10

    def test_projection(self):
        p = projection([1, 2, 3], [1, 0, 0])
        assert p == [1, 0, 0]

    def test_euclidean_distance(self):
        d = euclidean_distance([0, 0], [3, 4])
        assert abs(d - 5) < 1e-10

    def test_are_orthogonal(self):
        assert are_orthogonal([1, 0], [0, 1])
        assert not are_orthogonal([1, 0], [1, 0])

    def test_gram_schmidt(self):
        gs = gram_schmidt([[1, 1, 0], [1, 0, 1]])
        assert len(gs) == 2
        assert abs(dot(gs[0], gs[1])) < 1e-10

    def test_linear_combination(self):
        lc = linear_combination([[1, 0], [0, 1]], [3, 4])
        assert lc == [3, 4]

    def test_scalar_triple_product(self):
        stp = scalar_triple_product([1, 0, 0], [0, 1, 0], [0, 0, 1])
        assert abs(stp - 1) < 1e-10


# ── Matrix tests ──────────────────────────────────────────────────────────────

class TestMatrixConstruction:
    def test_zeros(self):
        m = zeros(2, 3)
        assert m == [[0, 0, 0], [0, 0, 0]]

    def test_ones(self):
        m = ones(2, 2)
        assert m == [[1, 1], [1, 1]]

    def test_identity(self):
        m = identity(3)
        assert m == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    def test_diag(self):
        m = diag([1, 2, 3])
        assert m == [[1, 0, 0], [0, 2, 0], [0, 0, 3]]


class TestMatrixProperties:
    def test_shape(self):
        assert shape([[1, 2], [3, 4], [5, 6]]) == (3, 2)

    def test_trace(self):
        assert trace([[1, 2], [3, 4]]) == 5

    def test_trace_non_square_raises(self):
        with pytest.raises(ValueError):
            trace([[1, 2], [3, 4], [5, 6]])

    def test_determinant_2x2(self):
        d = determinant([[1, 2], [3, 4]])
        assert abs(d - (-2)) < 1e-10

    def test_determinant_identity(self):
        d = determinant(identity(5))
        assert abs(d - 1) < 1e-10


class TestMatrixTransforms:
    def test_transpose(self):
        t = transpose([[1, 2, 3], [4, 5, 6]])
        assert t == [[1, 4], [2, 5], [3, 6]]

    def test_inverse(self):
        inv = inverse([[1, 2], [3, 4]])
        assert abs(determinant(inv) - (-0.5)) < 1e-10

    def test_inverse_non_square_raises(self):
        with pytest.raises(ValueError):
            inverse([[1, 2], [3, 4], [5, 6]])

    def test_flatten(self):
        f = flatten([[1, 2], [3, 4]])
        assert f == [1, 2, 3, 4]


class TestMatrixPropertiesBool:
    def test_is_square(self):
        assert is_square([[1, 2], [3, 4]])
        assert not is_square([[1, 2, 3]])

    def test_is_symmetric(self):
        assert is_symmetric([[1, 2], [2, 1]])
        assert not is_symmetric([[1, 2], [3, 4]])

    def test_is_positive_definite(self):
        assert is_positive_definite([[2, 0], [0, 2]])
        assert not is_positive_definite([[-1, 0], [0, -1]])


class TestMatrixDecompositions:
    def test_lu(self):
        p, l, u = lu([[1, 2], [3, 4]])
        assert p is not None
        assert l is not None
        assert u is not None

    def test_qr(self):
        q, r = qr([[1, 2], [3, 4]])
        assert len(q) == 2
        assert len(r) == 2

    def test_svd(self):
        u, s, vt = svd([[1, 2], [3, 4]])
        assert len(u) > 0
        assert len(s) == 2
        assert len(vt) > 0

    def test_eigen(self):
        vals, vecs = eigen(identity(3))
        assert all(abs(v - 1) < 1e-10 for v in vals)


class TestMatrixSolving:
    def test_solve_linear(self):
        x = solve_linear([[2, 0], [0, 2]], [4, 6])
        assert abs(x[0] - 2) < 1e-10
        assert abs(x[1] - 3) < 1e-10

    def test_rref(self):
        r = rref([[1, 2, 3], [4, 5, 6]])
        assert abs(r[0][0] - 1) < 1e-10
        assert abs(r[1][1] - 1) < 1e-10


class TestVectorExtended:
    def test_magnitude_squared(self):
        assert magnitude_squared([3, 4]) == 25.0

    def test_dimension(self):
        assert dimension([1, 2, 3]) == 3

    def test_normalize_safe(self):
        v = normalize_safe([0, 0], [0, 0])
        assert v == [0, 0]

    def test_sum_vector(self):
        assert sum_vector([1, 2, 3]) == 6

    def test_outer_product(self):
        op = outer_product([1, 2], [3, 4])
        assert op == [[3, 4], [6, 8]]

    def test_cosine_similarity(self):
        cs = cosine_similarity([1, 0], [0, 1])
        assert abs(cs) < 1e-10

    def test_rejection(self):
        r = rejection([1, 2, 3], [1, 0, 0])
        assert r == [0, 2, 3]

    def test_is_zero_vector(self):
        assert is_zero_vector([0, 0])
        assert not is_zero_vector([1, 0])

    def test_is_unit_vector(self):
        assert is_unit_vector([1, 0])
        assert not is_unit_vector([2, 0])

    def test_manhattan_distance(self):
        d = manhattan_distance([0, 0], [3, 4])
        assert d == 7


class TestMatrixExtended:
    def test_size(self):
        assert size([[1, 2], [3, 4]]) == 4

    def test_rank(self):
        r = rank([[1, 2], [2, 4]])
        assert r == 1

    def test_is_identity(self):
        assert is_identity([[1, 0], [0, 1]])
        assert not is_identity([[1, 2], [3, 4]])

    def test_is_diagonal(self):
        assert is_diagonal([[1, 0], [0, 2]])
        assert not is_diagonal([[1, 2], [3, 4]])

    def test_reshape(self):
        r = reshape([[1, 2, 3, 4]], 2, 2)
        assert r == [[1, 2], [3, 4]]

    def test_diagonal(self):
        d = diagonal([[1, 2], [3, 4]])
        assert d == [1, 4]

    def test_cholesky(self):
        L = cholesky([[4, 0], [0, 9]])
        assert abs(L[0][0] - 2) < 1e-10

    def test_eigvals(self):
        vals = eigvals([[2, 0], [0, 3]])
        assert sorted([round(float(v), 10) for v in vals]) == [2, 3]

    def test_hstack(self):
        h = hstack([[[1, 2]], [[3, 4]]])
        assert h == [[1, 2, 3, 4]]


class TestBoolExtended:
    def test_equal(self):
        assert equal(3, 3)
        assert not equal(3, 4)

    def test_not_equal(self):
        assert not_equal(3, 4)
        assert not not_equal(3, 3)

    def test_greater_than(self):
        assert greater_than(5, 3)
        assert not greater_than(3, 5)

    def test_less_than(self):
        assert less_than(3, 5)
        assert not less_than(5, 3)

    def test_is_text(self):
        assert is_text("hello")
        assert not is_text(42)

    def test_is_error(self):
        assert is_error(ValueError("test"))
        assert not is_error(42)

    def test_not_all(self):
        assert not_all([True, True, False]) == [False, False, True]
        assert not_all([True, True, True]) == [False, False, False]

    def test_xor_all(self):
        assert xor_all([True, False])
        assert not xor_all([True, True])

    def test_implies_(self):
        assert implies_(False, False)
        assert implies_(False, True)
        assert implies_(True, True)
        assert not implies_(True, False)

    def test_iff_(self):
        assert iff_(True, True)
        assert iff_(False, False)
        assert not iff_(True, False)

    def test_elementwise_and(self):
        assert elementwise_and([True, True, False], [True, False, False]) == [True, False, False]


# ── Bool tests ────────────────────────────────────────────────────────────────

class TestBoolConstants:
    def test_true(self):
        assert true() is True

    def test_false(self):
        assert false() is False


class TestBoolOperations:
    def test_and(self):
        assert and_(True, True)
        assert not and_(True, False)

    def test_or(self):
        assert or_(True, False)
        assert not or_(False, False)

    def test_xor(self):
        assert xor_(True, False)
        assert not xor_(True, True)

    def test_not(self):
        assert not_(True) is False
        assert not_(False) is True

    def test_nand(self):
        assert nand_(True, False)
        assert not nand_(True, True)

    def test_nor(self):
        assert nor_(False, False)
        assert not nor_(True, False)

    def test_xnor(self):
        assert xnor_(True, True)
        assert not xnor_(True, False)


class TestBoolConditional:
    def test_if_true(self):
        assert if_(True, "yes", "no") == "yes"

    def test_if_false(self):
        assert if_(False, "yes", "no") == "no"

    def test_if_error_no_error(self):
        assert if_error(42, 0) == 42

    def test_switch(self):
        r = switch(2, 1, "one", 2, "two", 3, "three")
        assert r == "two"

    def test_switch_default(self):
        r = switch(99, 1, "one", 2, "two", "default")
        assert r == "default"

    def test_choose(self):
        assert choose(2, "a", "b", "c") == "b"

    def test_choose_out_of_range(self):
        assert choose(5, "a", "b") is None


class TestBoolArray:
    def test_and_all(self):
        assert and_all([True, True, True])
        assert not and_all([True, False, True])

    def test_or_any(self):
        assert or_any([False, True, False])
        assert not or_any([False, False, False])

    def test_count_true(self):
        assert count_true([True, False, True, False]) == 2

    def test_count_false(self):
        assert count_false([True, False, True]) == 1


class TestBoolPredicates:
    def test_is_even(self):
        assert is_even(4)
        assert not is_even(5)

    def test_is_odd(self):
        assert is_odd(5)
        assert not is_odd(4)

    def test_is_number(self):
        assert is_number(42)
        assert is_number(3.14)
        assert not is_number("hello")
        assert not is_number(True)

    def test_is_blank_none(self):
        assert is_blank(None)

    def test_is_blank_empty_string(self):
        assert is_blank("")

    def test_is_blank_whitespace(self):
        assert is_blank("   ")

    def test_to_number(self):
        assert to_number(True) == 1
        assert to_number(False) == 0

    def test_to_bool(self):
        assert to_bool(1)
        assert not to_bool(0)


class TestComplexAdvanced:
    def test_mobius(self):
        z = mobius(1 + 0j, 1, 0, 0, 1)  # identity
        assert abs(z - 1) < 1e-10

    def test_mobius_denom_zero(self):
        with pytest.raises(ZeroDivisionError):
            mobius(1 + 0j, 1, 0, 1, -1)

    def test_slerp_complex(self):
        z = slerp(1 + 0j, 0 + 1j, 0.5)
        assert abs(abs(z) - 1) < 1e-10
        assert abs(z - (math.cos(math.pi/4) + 1j*math.sin(math.pi/4))) < 1e-10

    def test_newton(self):
        root = newton(lambda z: z*z - 1, lambda z: 2*z, 3 + 0j)
        assert abs(abs(root) - 1) < 1e-10

    def test_newton_deriv_zero(self):
        with pytest.raises(ZeroDivisionError):
            newton(lambda z: z*z, lambda z: 0*z, 1 + 0j)

    def test_mandelbrot_inside(self):
        assert mandelbrot(0 + 0j, 100) == 100

    def test_mandelbrot_outside(self):
        assert mandelbrot(2 + 2j, 100) < 100

    def test_random_complex(self):
        z = random_complex(seed=42)
        assert isinstance(z, complex)
        assert -1 <= z.real <= 1
        assert -1 <= z.imag <= 1


class TestVectorAdvanced:
    def test_reflect(self):
        r = reflect([1, -1, 0], [0, 1, 0])
        assert all(abs(r[i] - [1, 1, 0][i]) < 1e-10 for i in range(3))

    def test_rotate_around(self):
        v = rotate_around([1, 0, 0], [0, 0, 1], math.pi / 2)
        assert abs(v[0] - 0) < 1e-10
        assert abs(v[1] - 1) < 1e-10
        assert abs(v[2] - 0) < 1e-10

    def test_slerp_vectors(self):
        v = v_slerp([1, 0], [0, 1], 0.5)
        assert abs(v[0] - math.cos(math.pi/4)) < 1e-10
        assert abs(v[1] - math.sin(math.pi/4)) < 1e-10

    def test_gram_matrix(self):
        G = gram_matrix([[1, 0], [0, 1]])
        assert abs(G[0][0] - 1) < 1e-10
        assert abs(G[0][1] - 0) < 1e-10
        assert abs(G[1][1] - 1) < 1e-10

    def test_distance_matrix(self):
        D = distance_matrix([[0, 0], [3, 4]])
        assert abs(D[0][1] - 5) < 1e-10
        assert abs(D[0][0]) < 1e-10

    def test_clamp(self):
        c = clamp([-1, 5, 3], 0, 4)
        assert c == [0, 4, 3]

    def test_random_unit_vector(self):
        v = random_unit_vector(3, seed=42)
        assert abs(magnitude(v) - 1) < 1e-10

    def test_cumulative_sum(self):
        cs = cumulative_sum([1, 2, 3, 4])
        assert cs == [1, 3, 6, 10]


class TestMatrixAdvanced:
    def test_adjugate_2x2(self):
        adj = adjugate([[1, 2], [3, 4]])
        assert abs(adj[0][0] - 4) < 1e-10
        assert abs(adj[0][1] + 2) < 1e-10
        assert abs(adj[1][0] + 3) < 1e-10
        assert abs(adj[1][1] - 1) < 1e-10

    def test_characteristic_poly(self):
        poly = characteristic_poly([[1, 0], [0, 2]])
        assert len(poly) == 3
        assert abs(poly[0] - 1) < 1e-10
        assert abs(poly[1] + 3) < 1e-10
        assert abs(poly[2] - 2) < 1e-10

    def test_pascal_symmetric(self):
        P = pascal(3)
        assert P[0] == [1, 1, 1]
        assert P[1] == [1, 2, 3]
        assert P[2] == [1, 3, 6]

    def test_pascal_lower(self):
        P = pascal(3, kind="lower")
        assert P[0] == [1, 0, 0]
        assert P[1] == [1, 1, 0]
        assert P[2] == [1, 2, 1]

    def test_frobenius_inner(self):
        inner = frobenius_inner([[1, 0], [0, 1]], [[2, 0], [0, 3]])
        assert abs(inner - 5) < 1e-10


class TestBoolExtended2:
    def test_bitwise_and(self):
        assert bitwise_and(5, 3) == 1

    def test_bitwise_or(self):
        assert bitwise_or(5, 3) == 7

    def test_bitwise_xor(self):
        assert bitwise_xor(5, 3) == 6

    def test_majority(self):
        assert majority(True, True, False)
        assert not majority(True, False, False)

    def test_exactly_one(self):
        assert exactly_one(False, True, False)
        assert not exactly_one(True, True, False)

    def test_at_least_n(self):
        assert at_least_n([True, True, False], 2)
        assert not at_least_n([True, False, False], 2)

    def test_at_most_n(self):
        assert at_most_n([True, False, False], 2)
        assert not at_most_n([True, True, True], 2)

    def test_all_same(self):
        assert all_same(3, 3, 3)
        assert not all_same(3, 4, 3)

    def test_all_different(self):
        assert all_different(1, 2, 3)
        assert not all_different(1, 2, 1)
