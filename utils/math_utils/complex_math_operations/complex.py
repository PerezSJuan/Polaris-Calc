import numpy as np
import math
from typing import Union


"""── Construction & conversion ────────────────────────────────────────────────"""

def complex_num(real: float, imag: float = 0) -> complex:
    """Build a complex number from real and imaginary parts. Args: real, imag (default 0)."""
    return complex(real, imag)


def from_polar(modulus: float, argument: float) -> complex:
    """Build a complex number from polar coordinates (modulus, argument in radians). Args: modulus, argument."""
    return modulus * (math.cos(argument) + 1j * math.sin(argument))


def to_polar(z: complex) -> tuple:
    """Convert a complex number to (modulus, argument_radians). Args: z."""
    return abs(z), math.atan2(z.imag, z.real)


def to_string(z: complex, precision: int = 4) -> str:
    """Format complex number as "a+bi" string with given precision. Args: z, precision (default 4)."""
    fmt = f".{precision}f"
    real = format(z.real, fmt)
    imag = format(abs(z.imag), fmt)
    if z.imag >= 0:
        return f"{real}+{imag}i"
    return f"{real}-{imag}i"


def to_exponential(z: complex, precision: int = 4) -> str:
    """Format complex number as "re^(theta)i" exponential form. Args: z, precision (default 4)."""
    r, theta = to_polar(z)
    fmt = f".{precision}f"
    return f"{format(r, fmt)}e^{format(theta, fmt)}i"


"""── Properties ───────────────────────────────────────────────────────────────"""

def real_part(z: complex) -> float:
    """Extract the real part of a complex number. Args: z."""
    return z.real


def imag_part(z: complex) -> float:
    """Extract the imaginary part of a complex number. Args: z."""
    return z.imag


def modulus(z: complex) -> float:
    """Compute the modulus (absolute value) of a complex number. Args: z."""
    return abs(z)


def argument(z: complex) -> float:
    """Compute the argument (phase angle) in radians. Args: z."""
    return math.atan2(z.imag, z.real)


def argument_degrees(z: complex) -> float:
    """Compute the argument (phase angle) in degrees. Args: z."""
    return math.degrees(math.atan2(z.imag, z.real))


def conjugate(z: complex) -> complex:
    """Return the complex conjugate of z. Args: z."""
    return z.conjugate()


def sign(z: complex) -> complex:
    """Return the unit complex number in the same direction (zero returns 0). Args: z."""
    m = abs(z)
    if m == 0:
        return 0j
    return z / m


def squared_modulus(z: complex) -> float:
    """Compute |z|^2 = real^2 + imag^2. Args: z."""
    return z.real ** 2 + z.imag ** 2


"""── Arithmetic ────────────────────────────────────────────────────────────────"""

def add(z1: complex, z2: complex) -> complex:
    """Add two complex numbers. Args: z1, z2."""
    return z1 + z2


def sub(z1: complex, z2: complex) -> complex:
    """Subtract two complex numbers (z1 - z2). Args: z1, z2."""
    return z1 - z2


def mul(z1: complex, z2: complex) -> complex:
    """Multiply two complex numbers. Args: z1, z2."""
    return z1 * z2


def div(z1: complex, z2: complex) -> complex:
    """Divide two complex numbers (z1 / z2). Raises ZeroDivisionError if z2=0. Args: z1, z2."""
    if z2 == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return z1 / z2


def pow_(z: complex, n: float) -> complex:
    """Raise complex z to power n (float exponent). Args: z, n."""
    return z ** n


def sqrt(z: complex) -> complex:
    """Compute the principal square root of a complex number. Args: z."""
    return z ** 0.5


def reciprocal(z: complex) -> complex:
    """Compute 1/z. Raises ZeroDivisionError if z=0. Args: z."""
    if z == 0:
        raise ZeroDivisionError("Cannot compute reciprocal of zero.")
    return 1 / z


def negate(z: complex) -> complex:
    """Negate a complex number (-z). Args: z."""
    return -z


"""── Exponential & logarithms ──────────────────────────────────────────────────"""

def exp(z: complex) -> complex:
    """Compute e^z for complex z. Args: z."""
    return math.e ** z


def ln(z: complex) -> complex:
    """Compute the natural logarithm ln(z) (principal branch). Raises ValueError if z=0. Args: z."""
    if z == 0:
        raise ValueError("Cannot compute logarithm of zero.")
    return math.log(abs(z)) + 1j * math.atan2(z.imag, z.real)


def log(z: complex, base: float = 10) -> complex:
    """Compute log_base(z). Raises ValueError if z=0. Args: z, base (default 10)."""
    if z == 0:
        raise ValueError("Cannot compute logarithm of zero.")
    return ln(z) / math.log(base)


def log10(z: complex) -> complex:
    """Compute base-10 logarithm of complex z. Args: z."""
    return log(z, 10)


def log2(z: complex) -> complex:
    """Compute base-2 logarithm of complex z. Args: z."""
    return log(z, 2)


"""── Trigonometric ─────────────────────────────────────────────────────────────"""

def sin(z: complex) -> complex:
    """Compute the sine of a complex number. Args: z."""
    return math.sin(z.real) * math.cosh(z.imag) + 1j * math.cos(z.real) * math.sinh(z.imag)


def cos(z: complex) -> complex:
    """Compute the cosine of a complex number. Args: z."""
    return math.cos(z.real) * math.cosh(z.imag) - 1j * math.sin(z.real) * math.sinh(z.imag)


def tan(z: complex) -> complex:
    """Compute the tangent of a complex number. Args: z."""
    return sin(z) / cos(z)


def cot(z: complex) -> complex:
    """Compute the cotangent of a complex number (cos/sin). Args: z."""
    return cos(z) / sin(z)


def sec(z: complex) -> complex:
    """Compute the secant of a complex number (1/cos). Args: z."""
    return 1 / cos(z)


def csc(z: complex) -> complex:
    """Compute the cosecant of a complex number (1/sin). Args: z."""
    return 1 / sin(z)


"""── Inverse trigonometric ─────────────────────────────────────────────────────"""

def asin(z: complex) -> complex:
    """Compute the complex arcsin (inverse sine). Args: z."""
    return -1j * ln(1j * z + sqrt(1 - z * z))


def acos(z: complex) -> complex:
    """Compute the complex arccos (inverse cosine). Args: z."""
    return math.pi / 2 - asin(z)


def atan(z: complex) -> complex:
    """Compute the complex arctan (inverse tangent). Args: z."""
    return 1j / 2 * ln((1j - z) / (1j + z))


def acot(z: complex) -> complex:
    """Compute the complex arccot (inverse cotangent). Args: z."""
    return math.pi / 2 - atan(z)


"""── Hyperbolic ────────────────────────────────────────────────────────────────"""

def sinh(z: complex) -> complex:
    """Compute the hyperbolic sine of a complex number. Args: z."""
    return math.sinh(z.real) * math.cos(z.imag) + 1j * math.cosh(z.real) * math.sin(z.imag)


def cosh(z: complex) -> complex:
    """Compute the hyperbolic cosine of a complex number. Args: z."""
    return math.cosh(z.real) * math.cos(z.imag) + 1j * math.sinh(z.real) * math.sin(z.imag)


def tanh(z: complex) -> complex:
    """Compute the hyperbolic tangent of a complex number. Args: z."""
    return sinh(z) / cosh(z)


def coth(z: complex) -> complex:
    """Compute the hyperbolic cotangent of a complex number. Args: z."""
    return cosh(z) / sinh(z)


def sech(z: complex) -> complex:
    """Compute the hyperbolic secant of a complex number (1/cosh). Args: z."""
    return 1 / cosh(z)


def csch(z: complex) -> complex:
    """Compute the hyperbolic cosecant of a complex number (1/sinh). Args: z."""
    return 1 / sinh(z)


"""── Inverse hyperbolic ────────────────────────────────────────────────────────"""

def asinh(z: complex) -> complex:
    """Compute the inverse hyperbolic sine (arsinh) of a complex number. Args: z."""
    return ln(z + sqrt(z * z + 1))


def acosh(z: complex) -> complex:
    """Compute the inverse hyperbolic cosine (arcosh) of a complex number. Args: z."""
    return ln(z + sqrt(z * z - 1))


def atanh(z: complex) -> complex:
    """Compute the inverse hyperbolic tangent (artanh) of a complex number. Args: z."""
    return 1 / 2 * ln((1 + z) / (1 - z))


def acoth(z: complex) -> complex:
    """Compute the inverse hyperbolic cotangent (arcoth) of a complex number. Args: z."""
    return 1 / 2 * ln((z + 1) / (z - 1))


"""── Array / list operations ───────────────────────────────────────────────────"""

def sum_(*z: complex) -> complex:
    """Sum of variable number of complex numbers. Args: *z (one or more)."""
    return sum(z)


def product(*z: complex) -> complex:
    """Product of variable number of complex numbers. Args: *z (one or more)."""
    result = 1 + 0j
    for val in z:
        result *= val
    return result


def mean(z_list: list) -> complex:
    """Mean (average) of a list of complex numbers. Raises ValueError if empty. Args: z_list."""
    if not z_list:
        raise ValueError("List must not be empty.")
    return sum(z_list) / len(z_list)


def dot_product(z1: list, z2: list) -> complex:
    """Hermitian dot product sum(a * b.conjugate()) for two complex lists. Args: z1, z2 (same length)."""
    if len(z1) != len(z2):
        raise ValueError("Lists must have the same length.")
    return sum(a * b.conjugate() for a, b in zip(z1, z2))


def distance(z1: complex, z2: complex) -> float:
    """Euclidean distance |z1 - z2| between two complex numbers. Args: z1, z2."""
    return abs(z1 - z2)


"""── Roots of unity & nth roots ────────────────────────────────────────────────"""

def roots_of_unity(n: int) -> list:
    """Return the n complex roots of unity (e^(2πik/n)). Args: n (positive integer)."""
    if n <= 0:
        raise ValueError("n must be a positive integer.")
    return [from_polar(1, 2 * math.pi * k / n) for k in range(n)]


def nth_roots(z: complex, n: int) -> list:
    """Return the n complex nth roots of z. Args: z, n (positive integer)."""
    if n <= 0:
        raise ValueError("n must be a positive integer.")
    r, theta = to_polar(z)
    r_n = r ** (1 / n)
    return [from_polar(r_n, (theta + 2 * math.pi * k) / n) for k in range(n)]


"""── Phasor / electrical engineering ───────────────────────────────────────────"""

def phasor(magnitude: float, phase_degrees: float) -> complex:
    """Create a phasor from magnitude and phase in degrees. Args: magnitude, phase_degrees."""
    return magnitude * (math.cos(math.radians(phase_degrees)) + 1j * math.sin(math.radians(phase_degrees)))


def phasor_rad(magnitude: float, phase_rad: float) -> complex:
    """Create a phasor from magnitude and phase in radians. Args: magnitude, phase_rad."""
    return magnitude * (math.cos(phase_rad) + 1j * math.sin(phase_rad))


def phase_shift(z: complex, shift_rad: float) -> complex:
    """Rotate complex number by a phase shift (z * e^(i*shift)). Args: z, shift_rad (radians)."""
    return z * from_polar(1, shift_rad)


def impedance(resistance: float, reactance: float) -> complex:
    """Create an impedance complex number R + jX. Args: resistance, reactance."""
    return complex(resistance, reactance)


"""── Polynomial operations ─────────────────────────────────────────────────────"""

def polyval(coefficients: list, z: complex) -> complex:
    """Evaluate a polynomial (Horner's method) at point z. Args: coefficients [a0..an], z."""
    result = 0 + 0j
    for c in coefficients:
        result = result * z + c
    return result


def polyroots(coefficients: list) -> list:
    """Find all roots of a polynomial (uses np.roots). Args: coefficients [a0..an]."""
    return np.roots(coefficients).tolist()


"""── Comparison helpers ────────────────────────────────────────────────────────"""

def approx_equal(z1: complex, z2: complex, tol: float = 1e-10) -> bool:
    """Check if two complex numbers are approximately equal (within tol). Args: z1, z2, tol (default 1e-10)."""
    return abs(z1 - z2) < tol


def is_zero(z: complex, tol: float = 1e-10) -> bool:
    """Check if a complex number is approximately zero. Args: z, tol (default 1e-10)."""
    return abs(z) < tol


def is_real(z: complex, tol: float = 1e-10) -> bool:
    """Check if imaginary part is negligible (z is effectively real). Args: z, tol (default 1e-10)."""
    return abs(z.imag) < tol


def is_imaginary(z: complex, tol: float = 1e-10) -> bool:
    """Check if real part is negligible (z is effectively imaginary). Args: z, tol (default 1e-10)."""
    return abs(z.real) < tol


def is_unit_modulus(z: complex, tol: float = 1e-10) -> bool:
    """Check if |z| is approximately 1. Args: z, tol (default 1e-10)."""
    return abs(abs(z) - 1) < tol


"""── Rotation & interpolation ──────────────────────────────────────────────────"""

def rotate(z: complex, angle_rad: float) -> complex:
    """Rotate z by angle_rad radians (multiply by e^(i*angle)). Args: z, angle_rad."""
    return z * from_polar(1, angle_rad)


def lerp(z1: complex, z2: complex, t: float) -> complex:
    """Linear interpolation between z1 and z2: (1-t)*z1 + t*z2. Args: z1, z2, t (0 to 1)."""
    return (1 - t) * z1 + t * z2


"""── Special complex matrices ──────────────────────────────────────────────────"""

def complex_identity(n: int) -> list:
    """Return an n×n complex identity matrix. Args: n (size)."""
    return [[1 + 0j if i == j else 0 + 0j for j in range(n)] for i in range(n)]


def complex_zeros(rows: int, cols: int) -> list:
    """Return an rows×cols complex zero matrix. Args: rows, cols."""
    return [[0 + 0j for _ in range(cols)] for _ in range(rows)]


"""── Advanced complex functions ─────────────────────────────────────────────────"""


def mobius(z: complex, a: complex, b: complex, c: complex, d: complex) -> complex:
    """Apply Möbius transformation (a*z+b)/(c*z+d). Args: z, a, b, c, d."""
    denom = c * z + d
    if denom == 0:
        raise ZeroDivisionError("Möbius transformation denominator is zero.")
    return (a * z + b) / denom


def slerp(z1: complex, z2: complex, t: float) -> complex:
    """Spherical linear interpolation between z1 and z2. Args: z1, z2, t (0 to 1)."""
    r1, theta1 = to_polar(z1)
    r2, theta2 = to_polar(z2)
    r = (1 - t) * r1 + t * r2
    theta = theta1 + t * (theta2 - theta1)
    return from_polar(r, theta)


def newton(f, fprime, z0: complex, max_iter: int = 100, tol: float = 1e-10) -> complex:
    """Find a root of f using Newton's method starting from z0. Args: f, fprime, z0, max_iter, tol."""
    z = z0
    for _ in range(max_iter):
        fz = f(z)
        if abs(fz) < tol:
            return z
        fpz = fprime(z)
        if fpz == 0:
            raise ZeroDivisionError("Newton iteration: derivative is zero.")
        z = z - fz / fpz
    return z


def mandelbrot(c: complex, max_iter: int = 100) -> int:
    """Return iteration count for Mandelbrot set at c. Args: c, max_iter."""
    z = 0 + 0j
    for i in range(max_iter):
        if abs(z) > 2:
            return i
        z = z * z + c
    return max_iter


def random_complex(seed: int = None) -> complex:
    """Return a random complex number in [-1,1]×[-1,1]. Args: seed (optional)."""
    import random as _random
    if seed is not None:
        _random.seed(seed)
    return complex(_random.uniform(-1, 1), _random.uniform(-1, 1))
