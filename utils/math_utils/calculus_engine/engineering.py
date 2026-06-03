import numpy as np
import scipy as sp
from scipy import special


# ── Number-base conversions ───────────────────────────────────────────────────

def bin2dec(number: str) -> int:
    """
    Converts a binary number (given as a string) to decimal.

    Args:
        number: A string representing a binary integer (e.g. '1010').

    Returns:
        The decimal (base-10) integer equivalent.
    """
    return int(number, 2)


def bin2hex(number: str) -> str:
    """
    Converts a binary number (given as a string) to hexadecimal.

    Args:
        number: A string representing a binary integer (e.g. '1010').

    Returns:
        The uppercase hexadecimal string equivalent (e.g. 'A').
    """
    return hex(int(number, 2))[2:].upper()


def bin2oct(number: str) -> str:
    """
    Converts a binary number (given as a string) to octal.

    Args:
        number: A string representing a binary integer (e.g. '1010').

    Returns:
        The octal string equivalent (e.g. '12').
    """
    return oct(int(number, 2))[2:]


def dec2bin(number: int) -> str:
    """
    Converts a decimal integer to a binary string.

    Args:
        number: A non-negative decimal integer.

    Returns:
        The binary string representation (without the '0b' prefix).
    """
    if number < 0:
        raise ValueError("number must be a non-negative integer.")
    return bin(number)[2:]


def dec2hex(number: int) -> str:
    """
    Converts a decimal integer to a hexadecimal string.

    Args:
        number: A non-negative decimal integer.

    Returns:
        The uppercase hexadecimal string (without the '0x' prefix).
    """
    if number < 0:
        raise ValueError("number must be a non-negative integer.")
    return hex(number)[2:].upper()


def dec2oct(number: int) -> str:
    """
    Converts a decimal integer to an octal string.

    Args:
        number: A non-negative decimal integer.

    Returns:
        The octal string representation (without the '0o' prefix).
    """
    if number < 0:
        raise ValueError("number must be a non-negative integer.")
    return oct(number)[2:]


def hex2bin(number: str) -> str:
    """
    Converts a hexadecimal string to binary.

    Args:
        number: A string representing a hexadecimal integer (e.g. 'FF').

    Returns:
        The binary string equivalent.
    """
    return bin(int(number, 16))[2:]


def hex2dec(number: str) -> int:
    """
    Converts a hexadecimal string to a decimal integer.

    Args:
        number: A string representing a hexadecimal integer (e.g. 'FF').

    Returns:
        The decimal (base-10) integer equivalent.
    """
    return int(number, 16)


def hex2oct(number: str) -> str:
    """
    Converts a hexadecimal string to an octal string.

    Args:
        number: A string representing a hexadecimal integer (e.g. 'FF').

    Returns:
        The octal string equivalent.
    """
    return oct(int(number, 16))[2:]


def oct2bin(number: str) -> str:
    """
    Converts an octal string to binary.

    Args:
        number: A string representing an octal integer (e.g. '17').

    Returns:
        The binary string equivalent.
    """
    return bin(int(number, 8))[2:]


def oct2dec(number: str) -> int:
    """
    Converts an octal string to a decimal integer.

    Args:
        number: A string representing an octal integer (e.g. '17').

    Returns:
        The decimal (base-10) integer equivalent.
    """
    return int(number, 8)


def oct2hex(number: str) -> str:
    """
    Converts an octal string to a hexadecimal string.

    Args:
        number: A string representing an octal integer (e.g. '17').

    Returns:
        The uppercase hexadecimal string equivalent.
    """
    return hex(int(number, 8))[2:].upper()


# ── Bitwise operations ────────────────────────────────────────────────────────

def bitand(number1: int, number2: int) -> int:
    """
    Returns the bitwise AND of two non-negative integers.

    Args:
        number1: First non-negative integer operand.
        number2: Second non-negative integer operand.

    Returns:
        The result of number1 AND number2, bit by bit.
    """
    if number1 < 0 or number2 < 0:
        raise ValueError("Both numbers must be non-negative integers.")
    return number1 & number2


def bitor(number1: int, number2: int) -> int:
    """
    Returns the bitwise OR of two non-negative integers.

    Args:
        number1: First non-negative integer operand.
        number2: Second non-negative integer operand.

    Returns:
        The result of number1 OR number2, bit by bit.
    """
    if number1 < 0 or number2 < 0:
        raise ValueError("Both numbers must be non-negative integers.")
    return number1 | number2


def bitxor(number1: int, number2: int) -> int:
    """
    Returns the bitwise exclusive OR (XOR) of two non-negative integers.

    Args:
        number1: First non-negative integer operand.
        number2: Second non-negative integer operand.

    Returns:
        The result of number1 XOR number2, bit by bit.
    """
    if number1 < 0 or number2 < 0:
        raise ValueError("Both numbers must be non-negative integers.")
    return number1 ^ number2


def bitlshift(number: int, shift_amount: int) -> int:
    """
    Returns the value of a number shifted left by a given number of bits.

    Equivalent to multiplying by 2**shift_amount.

    Args:
        number:       The non-negative integer to shift.
        shift_amount: Number of bit positions to shift left (must be ≥ 0).

    Returns:
        The result of number << shift_amount.
    """
    if number < 0 or shift_amount < 0:
        raise ValueError("Both number and shift_amount must be non-negative.")
    return number << shift_amount


def bitrshift(number: int, shift_amount: int) -> int:
    """
    Returns the value of a number shifted right by a given number of bits.

    Equivalent to integer division by 2**shift_amount.

    Args:
        number:       The non-negative integer to shift.
        shift_amount: Number of bit positions to shift right (must be ≥ 0).

    Returns:
        The result of number >> shift_amount.
    """
    if number < 0 or shift_amount < 0:
        raise ValueError("Both number and shift_amount must be non-negative.")
    return number >> shift_amount


# ── Comparison / threshold functions ─────────────────────────────────────────

def delta(number1: float, number2: float = 0) -> int:
    """
    Tests whether two values are equal (Kronecker delta).

    Returns 1 if number1 == number2, otherwise 0. Mirrors Excel's DELTA,
    which is used to filter sets of values where two numbers are equal.

    Args:
        number1: The first value to compare.
        number2: The second value to compare (default 0).

    Returns:
        1 if the values are equal, 0 otherwise.
    """
    return int(number1 == number2)


def gestep(number: float, step: float = 0) -> int:
    """
    Tests whether a number is greater than or equal to a threshold (step).

    Returns 1 if number ≥ step, otherwise 0. Useful for counting values
    that exceed a threshold.

    Args:
        number: The value to test.
        step:   The threshold to compare against (default 0).

    Returns:
        1 if number ≥ step, 0 otherwise.
    """
    return int(number >= step)


# ── Error functions ───────────────────────────────────────────────────────────

def erf(lower_limit: float, upper_limit: float = None) -> float:
    """
    Returns the error function integrated between two limits.

    The error function erf(x) = (2/√π) ∫₀ˣ e^(−t²) dt is used in
    probability, statistics, and partial differential equations.
    When only lower_limit is supplied the result is erf(lower_limit);
    when both limits are given the result is erf(upper_limit) − erf(lower_limit).

    Args:
        lower_limit: Lower bound of integration (or the sole argument when
                     upper_limit is omitted).
        upper_limit: Upper bound of integration. If None, evaluates erf
                     from 0 to lower_limit (default None).

    Returns:
        The value of the error function over the specified interval.
    """
    if upper_limit is None:
        return special.erf(lower_limit)
    return special.erf(upper_limit) - special.erf(lower_limit)


def erfc(x: float) -> float:
    """
    Returns the complementary error function integrated between x and infinity.

    Defined as erfc(x) = 1 − erf(x) = (2/√π) ∫ₓ^∞ e^(−t²) dt.
    Numerically more stable than computing 1 − erf(x) for large x.

    Args:
        x: The lower bound of integration.

    Returns:
        The value of the complementary error function at x.
    """
    return special.erfc(x)


# ── Complex numbers ───────────────────────────────────────────────────────────

def complex_number(real: float, imaginary: float) -> complex:
    """
    Converts real and imaginary coefficients into a Python complex number.

    Mirrors Excel's COMPLEX function, which builds a complex number from
    separate real and imaginary parts.

    Args:
        real:      The real part of the complex number.
        imaginary: The imaginary part of the complex number.

    Returns:
        A Python complex number real + imaginary*j.
    """
    return complex(real, imaginary)


def imabs(inumber: complex) -> float:
    """
    Returns the absolute value (modulus) of a complex number.

    |z| = √(Re(z)² + Im(z)²)

    Args:
        inumber: A Python complex number.

    Returns:
        The modulus of the complex number.
    """
    return abs(inumber)


def imaginary(inumber: complex) -> float:
    """
    Returns the imaginary coefficient of a complex number.

    Args:
        inumber: A Python complex number.

    Returns:
        The imaginary part Im(z).
    """
    return inumber.imag


def imreal(inumber: complex) -> float:
    """
    Returns the real coefficient of a complex number.

    Args:
        inumber: A Python complex number.

    Returns:
        The real part Re(z).
    """
    return inumber.real


def imargument(inumber: complex) -> float:
    """
    Returns the argument (phase angle θ) of a complex number, in radians.

    θ = atan2(Im(z), Re(z)), measured counter-clockwise from the positive
    real axis. The result lies in (−π, π].

    Args:
        inumber: A Python complex number.

    Returns:
        The phase angle in radians.
    """
    return np.angle(inumber)


def imconjugate(inumber: complex) -> complex:
    """
    Returns the complex conjugate of a complex number.

    The conjugate of a + bi is a − bi.

    Args:
        inumber: A Python complex number.

    Returns:
        The complex conjugate.
    """
    return inumber.conjugate()


def imsum(*inumbers: complex) -> complex:
    """
    Returns the sum of two or more complex numbers.

    Args:
        *inumbers: Two or more Python complex numbers.

    Returns:
        The sum of all supplied complex numbers.
    """
    return sum(inumbers)


def imsub(inumber1: complex, inumber2: complex) -> complex:
    """
    Returns the difference between two complex numbers.

    Args:
        inumber1: The minuend (complex number to subtract from).
        inumber2: The subtrahend (complex number to subtract).

    Returns:
        inumber1 − inumber2.
    """
    return inumber1 - inumber2


def improduct(*inumbers: complex) -> complex:
    """
    Returns the product of two or more complex numbers.

    Args:
        *inumbers: Two or more Python complex numbers.

    Returns:
        The product of all supplied complex numbers.
    """
    result = complex(1, 0)
    for z in inumbers:
        result *= z
    return result


def imdiv(inumber1: complex, inumber2: complex) -> complex:
    """
    Returns the quotient of two complex numbers.

    Args:
        inumber1: The dividend.
        inumber2: The divisor (must be non-zero).

    Returns:
        inumber1 / inumber2.
    """
    if inumber2 == 0:
        raise ZeroDivisionError("inumber2 must not be zero.")
    return inumber1 / inumber2


def impower(inumber: complex, number: float) -> complex:
    """
    Returns a complex number raised to a real or integer power.

    Args:
        inumber: The base complex number.
        number:  The exponent.

    Returns:
        inumber ** number.
    """
    return inumber ** number


def imsqrt(inumber: complex) -> complex:
    """
    Returns the square root of a complex number.

    The principal square root is returned (non-negative real part).

    Args:
        inumber: A Python complex number.

    Returns:
        The principal square root of inumber.
    """
    return np.sqrt(inumber)


def imexp(inumber: complex) -> complex:
    """
    Returns e raised to the power of a complex number.

    e^(a+bi) = e^a · (cos b + i sin b)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex exponential e^inumber.
    """
    return np.exp(inumber)


def imln(inumber: complex) -> complex:
    """
    Returns the natural logarithm of a complex number.

    ln(z) = ln|z| + i·arg(z)

    Args:
        inumber: A Python complex number (must be non-zero).

    Returns:
        The principal value of the natural logarithm.
    """
    return np.log(inumber)


def imlog10(inumber: complex) -> complex:
    """
    Returns the base-10 logarithm of a complex number.

    log₁₀(z) = ln(z) / ln(10)

    Args:
        inumber: A Python complex number (must be non-zero).

    Returns:
        The base-10 logarithm of inumber.
    """
    return np.log10(inumber)


def imlog2(inumber: complex) -> complex:
    """
    Returns the base-2 logarithm of a complex number.

    log₂(z) = ln(z) / ln(2)

    Args:
        inumber: A Python complex number (must be non-zero).

    Returns:
        The base-2 logarithm of inumber.
    """
    return np.log2(inumber)


def imsin(inumber: complex) -> complex:
    """
    Returns the sine of a complex number.

    sin(a+bi) = sin(a)cosh(b) + i·cos(a)sinh(b)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex sine of inumber.
    """
    return np.sin(inumber)


def imcos(inumber: complex) -> complex:
    """
    Returns the cosine of a complex number.

    cos(a+bi) = cos(a)cosh(b) − i·sin(a)sinh(b)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex cosine of inumber.
    """
    return np.cos(inumber)


def imtan(inumber: complex) -> complex:
    """
    Returns the tangent of a complex number.

    tan(z) = sin(z) / cos(z)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex tangent of inumber.
    """
    return np.tan(inumber)


def imcot(inumber: complex) -> complex:
    """
    Returns the cotangent of a complex number.

    cot(z) = cos(z) / sin(z)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex cotangent of inumber.
    """
    return np.cos(inumber) / np.sin(inumber)


def imsec(inumber: complex) -> complex:
    """
    Returns the secant of a complex number.

    sec(z) = 1 / cos(z)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex secant of inumber.
    """
    return 1 / np.cos(inumber)


def imcsc(inumber: complex) -> complex:
    """
    Returns the cosecant of a complex number.

    csc(z) = 1 / sin(z)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex cosecant of inumber.
    """
    return 1 / np.sin(inumber)


def imsinh(inumber: complex) -> complex:
    """
    Returns the hyperbolic sine of a complex number.

    sinh(z) = (e^z − e^(−z)) / 2

    Args:
        inumber: A Python complex number.

    Returns:
        The complex hyperbolic sine of inumber.
    """
    return np.sinh(inumber)


def imcosh(inumber: complex) -> complex:
    """
    Returns the hyperbolic cosine of a complex number.

    cosh(z) = (e^z + e^(−z)) / 2

    Args:
        inumber: A Python complex number.

    Returns:
        The complex hyperbolic cosine of inumber.
    """
    return np.cosh(inumber)


def imsech(inumber: complex) -> complex:
    """
    Returns the hyperbolic secant of a complex number.

    sech(z) = 1 / cosh(z)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex hyperbolic secant of inumber.
    """
    return 1 / np.cosh(inumber)


def imcsch(inumber: complex) -> complex:
    """
    Returns the hyperbolic cosecant of a complex number.

    csch(z) = 1 / sinh(z)

    Args:
        inumber: A Python complex number.

    Returns:
        The complex hyperbolic cosecant of inumber.
    """
    return 1 / np.sinh(inumber)


# ── Bessel functions ──────────────────────────────────────────────────────────

def besseli(x: float, n: int) -> float:
    """
    Returns the modified Bessel function of the first kind, Iₙ(x).

    The modified Bessel functions arise in problems with cylindrical symmetry
    involving a parameter that changes exponentially (e.g. heat conduction,
    wave equations). Iₙ(x) is the solution that remains finite at x = 0.

    Args:
        x: The value at which to evaluate the function.
        n: The order of the Bessel function (non-negative integer).

    Returns:
        The value of Iₙ(x).
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    return special.iv(n, x)


def besselj(x: float, n: int) -> float:
    """
    Returns the Bessel function of the first kind, Jₙ(x).

    Jₙ(x) is the standard Bessel function solution that is finite at x = 0.
    It describes oscillatory phenomena such as vibrations of a circular membrane
    or electromagnetic waves in cylindrical waveguides.

    Args:
        x: The value at which to evaluate the function.
        n: The order of the Bessel function (non-negative integer).

    Returns:
        The value of Jₙ(x).
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    return special.jv(n, x)


def besselk(x: float, n: int) -> float:
    """
    Returns the modified Bessel function of the second kind, Kₙ(x).

    Kₙ(x) decays exponentially for large x and is singular at x = 0.
    It appears in problems on unbounded domains, such as diffusion outside
    a cylinder.

    Args:
        x: The value at which to evaluate the function (must be > 0).
        n: The order of the Bessel function (non-negative integer).

    Returns:
        The value of Kₙ(x).
    """
    if x <= 0:
        raise ValueError("x must be positive.")
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    return special.kv(n, x)


def bessely(x: float, n: int) -> float:
    """
    Returns the Bessel function of the second kind, Yₙ(x).

    Yₙ(x) is the Bessel function solution that is singular at x = 0.
    Also called the Neumann function, it appears alongside Jₙ(x) in
    problems where the domain excludes the origin.

    Args:
        x: The value at which to evaluate the function (must be > 0).
        n: The order of the Bessel function (non-negative integer).

    Returns:
        The value of Yₙ(x).
    """
    if x <= 0:
        raise ValueError("x must be positive.")
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    return special.yv(n, x)
