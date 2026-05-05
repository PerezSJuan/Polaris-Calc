import math
import numpy as np


# ── Basic arithmetic & rounding ───────────────────────────────────────────────

def absolute(number: float) -> float:
    """
    Returns the absolute value of a number.

    Args:
        number: Any real number.

    Returns:
        The non-negative magnitude of number.
    """
    return abs(number)


def ceiling(number: float, significance: float = 1) -> float:
    """
    Rounds a number up to the nearest multiple of significance.

    Equivalent to Excel's CEILING.MATH: always rounds away from zero for
    positive numbers. If significance is negative and number is negative,
    rounding is toward zero.

    Args:
        number:       The value to round.
        significance: The multiple to round up to (default 1).

    Returns:
        The smallest multiple of significance that is ≥ number.

    Raises:
        ValueError: If significance is zero.
    """
    if significance == 0:
        raise ValueError("significance must not be zero.")
    return math.ceil(number / significance) * significance


def floor(number: float, significance: float = 1) -> float:
    """
    Rounds a number down to the nearest multiple of significance.

    Equivalent to Excel's FLOOR.MATH: always rounds toward zero for
    positive numbers.

    Args:
        number:       The value to round.
        significance: The multiple to round down to (default 1).

    Returns:
        The largest multiple of significance that is ≤ number.

    Raises:
        ValueError: If significance is zero.
    """
    if significance == 0:
        raise ValueError("significance must not be zero.")
    return math.floor(number / significance) * significance


def round_number(number: float, num_digits: int = 0) -> float:
    """
    Rounds a number to a specified number of decimal places.

    Uses round-half-to-even (banker's rounding) consistent with Python's
    built-in round(), which matches Excel's ROUND in most cases.

    Args:
        number:     The value to round.
        num_digits: Number of decimal places (default 0). Negative values
                    round to the left of the decimal point.

    Returns:
        The rounded number.
    """
    return round(number, num_digits)


def round_down(number: float, num_digits: int = 0) -> float:
    """
    Rounds a number down (toward zero) to a specified number of digits.

    Args:
        number:     The value to truncate toward zero.
        num_digits: Number of decimal places to keep (default 0).

    Returns:
        The number truncated toward zero to num_digits decimal places.
    """
    factor = 10 ** num_digits
    return math.trunc(number * factor) / factor


def round_up(number: float, num_digits: int = 0) -> float:
    """
    Rounds a number up (away from zero) to a specified number of digits.

    Args:
        number:     The value to round away from zero.
        num_digits: Number of decimal places to keep (default 0).

    Returns:
        The number rounded away from zero to num_digits decimal places.
    """
    factor = 10 ** num_digits
    return math.ceil(abs(number) * factor) / factor * (1 if number >= 0 else -1)


def truncate(number: float, num_digits: int = 0) -> float:
    """
    Truncates a number to an integer by removing the fractional part.

    Args:
        number:     The value to truncate.
        num_digits: Number of decimal places to keep (default 0).
                    Setting num_digits > 0 removes digits beyond that place.

    Returns:
        The truncated number.
    """
    factor = 10 ** num_digits
    return math.trunc(number * factor) / factor


def even(number: float) -> int:
    """
    Rounds a number up to the nearest even integer.

    Positive numbers are rounded toward +∞ and negative numbers toward −∞,
    away from zero, to the next even integer.

    Args:
        number: The value to round.

    Returns:
        The nearest even integer away from zero.
    """
    return math.ceil(number / 2) * 2


def odd(number: float) -> int:
    """
    Rounds a number up to the nearest odd integer.

    Positive numbers are rounded toward +∞ and negative numbers toward −∞,
    away from zero, to the next odd integer.

    Args:
        number: The value to round.

    Returns:
        The nearest odd integer away from zero.
    """
    n = math.ceil(abs(number))
    if n % 2 == 0:
        n += 1
    return n if number >= 0 else -n


def mod(number: float, divisor: float) -> float:
    """
    Returns the remainder of a division, with the sign of the divisor.

    Mirrors Excel's MOD: result has the same sign as divisor, unlike
    Python's % which follows the divisor's sign automatically.

    Args:
        number:  The dividend.
        divisor: The divisor (must not be zero).

    Returns:
        The remainder number − divisor · FLOOR(number/divisor).

    Raises:
        ZeroDivisionError: If divisor is zero.
    """
    if divisor == 0:
        raise ZeroDivisionError("divisor must not be zero.")
    return number % divisor


def quotient(numerator: float, denominator: float) -> int:
    """
    Returns the integer portion of a division (truncates toward zero).

    Args:
        numerator:   The dividend.
        denominator: The divisor (must not be zero).

    Returns:
        The integer part of numerator / denominator.

    Raises:
        ZeroDivisionError: If denominator is zero.
    """
    if denominator == 0:
        raise ZeroDivisionError("denominator must not be zero.")
    return int(numerator / denominator)


def mround(number: float, multiple: float) -> float:
    """
    Returns a number rounded to the nearest specified multiple.

    Args:
        number:   The value to round.
        multiple: The multiple to round to.

    Returns:
        number rounded to the nearest multiple of multiple.

    Raises:
        ValueError: If number and multiple have opposite signs.
    """
    if multiple == 0:
        return 0.0
    if (number > 0 and multiple < 0) or (number < 0 and multiple > 0):
        raise ValueError("number and multiple must have the same sign.")
    return round(number / multiple) * multiple


def sign(number: float) -> int:
    """
    Returns the sign of a number: 1, −1, or 0.

    Args:
        number: The value to evaluate.

    Returns:
        1 if number > 0, −1 if number < 0, 0 if number == 0.
    """
    if number > 0:
        return 1
    elif number < 0:
        return -1
    return 0


# ── Powers, roots & logarithms ────────────────────────────────────────────────

def power(number: float, exponent: float) -> float:
    """
    Returns the result of a number raised to a power.

    Args:
        number:   The base.
        exponent: The exponent.

    Returns:
        number ** exponent.
    """
    return number ** exponent


def sqrt(number: float) -> float:
    """
    Returns the positive square root of a number.

    Args:
        number: A non-negative real number.

    Returns:
        The positive square root √number.

    Raises:
        ValueError: If number is negative.
    """
    if number < 0:
        raise ValueError("number must be non-negative.")
    return math.sqrt(number)


def sqrtpi(number: float) -> float:
    """
    Returns the square root of (number × π).

    Args:
        number: A non-negative real number.

    Returns:
        √(number · π).

    Raises:
        ValueError: If number is negative.
    """
    if number < 0:
        raise ValueError("number must be non-negative.")
    return math.sqrt(number * math.pi)


def exp(number: float) -> float:
    """
    Returns e raised to the power of a number.

    Args:
        number: The exponent.

    Returns:
        e^number.
    """
    return math.exp(number)


def ln(number: float) -> float:
    """
    Returns the natural logarithm (base e) of a number.

    Args:
        number: A positive real number.

    Returns:
        ln(number).

    Raises:
        ValueError: If number is not positive.
    """
    if number <= 0:
        raise ValueError("number must be positive.")
    return math.log(number)


def log(number: float, base: float = 10) -> float:
    """
    Returns the logarithm of a number to a specified base.

    Args:
        number: A positive real number.
        base:   The logarithm base (default 10).

    Returns:
        log_base(number).

    Raises:
        ValueError: If number is not positive or base is not valid.
    """
    if number <= 0:
        raise ValueError("number must be positive.")
    if base <= 0 or base == 1:
        raise ValueError("base must be positive and not equal to 1.")
    return math.log(number, base)


def log10(number: float) -> float:
    """
    Returns the base-10 logarithm of a number.

    Args:
        number: A positive real number.

    Returns:
        log₁₀(number).

    Raises:
        ValueError: If number is not positive.
    """
    if number <= 0:
        raise ValueError("number must be positive.")
    return math.log10(number)


# ── Trigonometric functions ───────────────────────────────────────────────────

def pi() -> float:
    """
    Returns the mathematical constant π ≈ 3.14159265358979.

    Returns:
        The value of π.
    """
    return math.pi


def degrees(angle: float) -> float:
    """
    Converts an angle from radians to degrees.

    Args:
        angle: Angle in radians.

    Returns:
        The equivalent angle in degrees.
    """
    return math.degrees(angle)


def radians(angle: float) -> float:
    """
    Converts an angle from degrees to radians.

    Args:
        angle: Angle in degrees.

    Returns:
        The equivalent angle in radians.
    """
    return math.radians(angle)


def sin(number: float) -> float:
    """
    Returns the sine of an angle given in radians.

    Args:
        number: Angle in radians.

    Returns:
        sin(number), in the range [−1, 1].
    """
    return math.sin(number)


def cos(number: float) -> float:
    """
    Returns the cosine of an angle given in radians.

    Args:
        number: Angle in radians.

    Returns:
        cos(number), in the range [−1, 1].
    """
    return math.cos(number)


def tan(number: float) -> float:
    """
    Returns the tangent of an angle given in radians.

    Args:
        number: Angle in radians.

    Returns:
        tan(number).
    """
    return math.tan(number)


def cot(number: float) -> float:
    """
    Returns the cotangent of an angle given in radians.

    cot(x) = cos(x) / sin(x) = 1 / tan(x)

    Args:
        number: Angle in radians (must not be a multiple of π).

    Returns:
        cot(number).

    Raises:
        ZeroDivisionError: If sin(number) is zero.
    """
    s = math.sin(number)
    if s == 0:
        raise ZeroDivisionError("sin(number) is zero; cotangent is undefined.")
    return math.cos(number) / s


def sec(number: float) -> float:
    """
    Returns the secant of an angle given in radians.

    sec(x) = 1 / cos(x)

    Args:
        number: Angle in radians (must not be π/2 + n·π).

    Returns:
        sec(number).

    Raises:
        ZeroDivisionError: If cos(number) is zero.
    """
    c = math.cos(number)
    if c == 0:
        raise ZeroDivisionError("cos(number) is zero; secant is undefined.")
    return 1 / c


def csc(number: float) -> float:
    """
    Returns the cosecant of an angle given in radians.

    csc(x) = 1 / sin(x)

    Args:
        number: Angle in radians (must not be a multiple of π).

    Returns:
        csc(number).

    Raises:
        ZeroDivisionError: If sin(number) is zero.
    """
    s = math.sin(number)
    if s == 0:
        raise ZeroDivisionError("sin(number) is zero; cosecant is undefined.")
    return 1 / s


def asin(number: float) -> float:
    """
    Returns the arcsine of a number, in radians.

    Args:
        number: A value in [−1, 1].

    Returns:
        The arcsine in [−π/2, π/2] radians.

    Raises:
        ValueError: If number is outside [−1, 1].
    """
    return math.asin(number)


def acos(number: float) -> float:
    """
    Returns the arccosine of a number, in radians.

    Args:
        number: A value in [−1, 1].

    Returns:
        The arccosine in [0, π] radians.

    Raises:
        ValueError: If number is outside [−1, 1].
    """
    return math.acos(number)


def atan(number: float) -> float:
    """
    Returns the arctangent of a number, in radians.

    Args:
        number: Any real number.

    Returns:
        The arctangent in (−π/2, π/2) radians.
    """
    return math.atan(number)


def atan2(x_num: float, y_num: float) -> float:
    """
    Returns the arctangent from x- and y-coordinates, in radians.

    Computes the angle θ between the positive x-axis and the point (x_num, y_num).
    Note: Excel's ATAN2(x, y) takes x first; this matches that convention.

    Args:
        x_num: The x-coordinate.
        y_num: The y-coordinate.

    Returns:
        The angle in (−π, π] radians.
    """
    return math.atan2(y_num, x_num)


def acot(number: float) -> float:
    """
    Returns the arccotangent of a number, in radians.

    acot(x) = π/2 − atan(x)

    Args:
        number: Any real number.

    Returns:
        The arccotangent in (0, π) radians.
    """
    return math.pi / 2 - math.atan(number)


# ── Hyperbolic functions ──────────────────────────────────────────────────────

def sinh(number: float) -> float:
    """
    Returns the hyperbolic sine of a number.

    Args:
        number: Any real number.

    Returns:
        sinh(number).
    """
    return math.sinh(number)


def cosh(number: float) -> float:
    """
    Returns the hyperbolic cosine of a number.

    Args:
        number: Any real number.

    Returns:
        cosh(number) ≥ 1.
    """
    return math.cosh(number)


def tanh(number: float) -> float:
    """
    Returns the hyperbolic tangent of a number.

    Args:
        number: Any real number.

    Returns:
        tanh(number), in (−1, 1).
    """
    return math.tanh(number)


def coth(number: float) -> float:
    """
    Returns the hyperbolic cotangent of a number.

    coth(x) = cosh(x) / sinh(x)

    Args:
        number: Any non-zero real number.

    Returns:
        coth(number).

    Raises:
        ZeroDivisionError: If number is zero.
    """
    if number == 0:
        raise ZeroDivisionError("number must not be zero.")
    return math.cosh(number) / math.sinh(number)


def sech(number: float) -> float:
    """
    Returns the hyperbolic secant of a number.

    sech(x) = 1 / cosh(x)

    Args:
        number: Any real number.

    Returns:
        sech(number), in (0, 1].
    """
    return 1 / math.cosh(number)


def csch(number: float) -> float:
    """
    Returns the hyperbolic cosecant of a number.

    csch(x) = 1 / sinh(x)

    Args:
        number: Any non-zero real number.

    Returns:
        csch(number).

    Raises:
        ZeroDivisionError: If number is zero.
    """
    if number == 0:
        raise ZeroDivisionError("number must not be zero.")
    return 1 / math.sinh(number)


def asinh(number: float) -> float:
    """
    Returns the inverse hyperbolic sine of a number.

    Args:
        number: Any real number.

    Returns:
        asinh(number).
    """
    return math.asinh(number)


def acosh(number: float) -> float:
    """
    Returns the inverse hyperbolic cosine of a number.

    Args:
        number: A real number ≥ 1.

    Returns:
        acosh(number) ≥ 0.

    Raises:
        ValueError: If number < 1.
    """
    return math.acosh(number)


def atanh(number: float) -> float:
    """
    Returns the inverse hyperbolic tangent of a number.

    Args:
        number: A real number in the open interval (−1, 1).

    Returns:
        atanh(number).

    Raises:
        ValueError: If |number| ≥ 1.
    """
    return math.atanh(number)


def acoth(number: float) -> float:
    """
    Returns the inverse hyperbolic cotangent of a number.

    acoth(x) = atanh(1/x) = 0.5 · ln((x+1)/(x−1))

    Args:
        number: A real number with |number| > 1.

    Returns:
        acoth(number).

    Raises:
        ValueError: If |number| ≤ 1.
    """
    if abs(number) <= 1:
        raise ValueError("|number| must be greater than 1.")
    return math.atanh(1 / number)


# ── Combinatorics ─────────────────────────────────────────────────────────────

def factorial(number: int) -> int:
    """
    Returns the factorial of a non-negative integer.

    Args:
        number: A non-negative integer.

    Returns:
        number! = 1 · 2 · … · number (with 0! = 1).

    Raises:
        ValueError: If number is negative.
    """
    if number < 0:
        raise ValueError("number must be a non-negative integer.")
    return math.factorial(int(number))


def double_factorial(number: int) -> int:
    """
    Returns the double factorial of a non-negative integer.

    n!! = n · (n−2) · (n−4) · … down to 1 (odd n) or 2 (even n).

    Args:
        number: A non-negative integer.

    Returns:
        The double factorial number!!

    Raises:
        ValueError: If number is negative.
    """
    if number < 0:
        raise ValueError("number must be a non-negative integer.")
    if number <= 1:
        return 1
    result = 1
    while number > 1:
        result *= number
        number -= 2
    return result


def combin(n: int, k: int) -> int:
    """
    Returns the number of combinations of n objects taken k at a time.

    C(n, k) = n! / (k! · (n−k)!)

    Args:
        n: The total number of objects (non-negative integer).
        k: The number chosen at a time (0 ≤ k ≤ n).

    Returns:
        The binomial coefficient C(n, k).

    Raises:
        ValueError: If k < 0 or k > n.
    """
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 ≤ k ≤ n.")
    return math.comb(int(n), int(k))


def combina(n: int, k: int) -> int:
    """
    Returns the number of combinations with repetition (multiset coefficient).

    Also called "n multichoose k": C(n+k−1, k).

    Args:
        n: The number of types of objects (positive integer).
        k: The number chosen (non-negative integer).

    Returns:
        The multiset coefficient C(n+k−1, k).
    """
    if n < 0 or k < 0:
        raise ValueError("n and k must be non-negative integers.")
    return math.comb(n + k - 1, k)


def multinomial(*numbers: int) -> int:
    """
    Returns the multinomial coefficient of a set of numbers.

    Multinomial(n₁, n₂, …, nₖ) = (n₁+n₂+…+nₖ)! / (n₁! · n₂! · … · nₖ!)

    Args:
        *numbers: Two or more non-negative integers.

    Returns:
        The multinomial coefficient.
    """
    total = sum(numbers)
    result = math.factorial(total)
    for n in numbers:
        result //= math.factorial(n)
    return result


def gcd(*numbers: int) -> int:
    """
    Returns the greatest common divisor of two or more integers.

    Args:
        *numbers: Two or more integers (all must be non-negative).

    Returns:
        The GCD of the supplied integers.
    """
    result = numbers[0]
    for n in numbers[1:]:
        result = math.gcd(int(result), int(n))
    return result


def lcm(*numbers: int) -> int:
    """
    Returns the least common multiple of two or more integers.

    Args:
        *numbers: Two or more positive integers.

    Returns:
        The LCM of the supplied integers.
    """
    result = numbers[0]
    for n in numbers[1:]:
        result = math.lcm(int(result), int(n))
    return result


# ── Summation helpers ─────────────────────────────────────────────────────────

def sum_values(elements: list) -> float:
    """
    Returns the sum of a list of numbers.

    Args:
        elements: List of numeric values.

    Returns:
        The arithmetic sum of all elements.
    """
    return sum(elements)


def sum_if(elements: list, condition: callable) -> float:
    """
    Returns the sum of elements that satisfy a given condition.

    Args:
        elements:  List of numeric values.
        condition: A callable that takes a single element and returns True
                   if it should be included in the sum.

    Returns:
        The sum of filtered elements.
    """
    return sum(x for x in elements if condition(x))


def sum_ifs(elements: list, conditions: list) -> float:
    """
    Returns the sum of elements that satisfy all given conditions simultaneously.

    Args:
        elements:   List of numeric values.
        conditions: List of callables, each returning True for elements to include.

    Returns:
        The sum of elements passing all conditions.
    """
    return sum(x for x in elements if all(c(x) for c in conditions))


def sumproduct(array1: list, array2: list) -> float:
    """
    Returns the sum of the products of corresponding elements in two arrays.

    Args:
        array1: First list of numeric values.
        array2: Second list of numeric values (must have the same length as array1).

    Returns:
        Σ (array1[i] · array2[i]).

    Raises:
        ValueError: If the arrays have different lengths.
    """
    if len(array1) != len(array2):
        raise ValueError("Both arrays must have the same length.")
    return sum(a * b for a, b in zip(array1, array2))


def sumsq(elements: list) -> float:
    """
    Returns the sum of the squares of the elements.

    Args:
        elements: List of numeric values.

    Returns:
        Σ xᵢ².
    """
    return sum(x ** 2 for x in elements)


def sumx2my2(array1: list, array2: list) -> float:
    """
    Returns the sum of the difference of squares of corresponding values.

    Computes Σ (x² − y²) = Σ x² − Σ y².

    Args:
        array1: List of x values.
        array2: List of y values (must have the same length as array1).

    Returns:
        Σ (array1[i]² − array2[i]²).

    Raises:
        ValueError: If the arrays have different lengths.
    """
    if len(array1) != len(array2):
        raise ValueError("Both arrays must have the same length.")
    return sum(x ** 2 - y ** 2 for x, y in zip(array1, array2))


def sumx2py2(array1: list, array2: list) -> float:
    """
    Returns the sum of the sum of squares of corresponding values.

    Computes Σ (x² + y²) = Σ x² + Σ y².

    Args:
        array1: List of x values.
        array2: List of y values (must have the same length as array1).

    Returns:
        Σ (array1[i]² + array2[i]²).

    Raises:
        ValueError: If the arrays have different lengths.
    """
    if len(array1) != len(array2):
        raise ValueError("Both arrays must have the same length.")
    return sum(x ** 2 + y ** 2 for x, y in zip(array1, array2))


def sumxmy2(array1: list, array2: list) -> float:
    """
    Returns the sum of squares of differences of corresponding values.

    Computes Σ (x − y)².

    Args:
        array1: List of x values.
        array2: List of y values (must have the same length as array1).

    Returns:
        Σ (array1[i] − array2[i])².

    Raises:
        ValueError: If the arrays have different lengths.
    """
    if len(array1) != len(array2):
        raise ValueError("Both arrays must have the same length.")
    return sum((x - y) ** 2 for x, y in zip(array1, array2))


def seriessum(x: float, n: float, m: float, coefficients: list) -> float:
    """
    Returns the sum of a power series.

    Computes Σ coefficients[i] · x^(n + i·m) for i = 0, 1, …, len(coefficients)−1.
    This corresponds to Excel's SERIESSUM(x, n, m, coefficients).

    Args:
        x:            The base value of the power series.
        n:            The initial power to which x is raised.
        m:            The step by which to increase the power for each term.
        coefficients: List of coefficients multiplying each power term.

    Returns:
        The sum of the power series.
    """
    return sum(c * x ** (n + i * m) for i, c in enumerate(coefficients))


# ── Matrix functions ──────────────────────────────────────────────────────────

def mdeterm(array: list) -> float:
    """
    Returns the matrix determinant of a square 2-D array.

    Args:
        array: A square list-of-lists (n × n) of numeric values.

    Returns:
        The determinant of the matrix.

    Raises:
        ValueError: If the array is not square.
    """
    matrix = np.array(array, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("array must be a square 2-D matrix.")
    return float(np.linalg.det(matrix))


def minverse(array: list) -> list:
    """
    Returns the inverse of a square matrix.

    Args:
        array: A square list-of-lists (n × n) of numeric values.
               The matrix must be non-singular (determinant ≠ 0).

    Returns:
        The inverse matrix as a list of lists.

    Raises:
        ValueError:       If the array is not square.
        np.linalg.LinAlgError: If the matrix is singular.
    """
    matrix = np.array(array, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("array must be a square 2-D matrix.")
    return np.linalg.inv(matrix).tolist()


def mmult(array1: list, array2: list) -> list:
    """
    Returns the matrix product of two arrays.

    The number of columns in array1 must equal the number of rows in array2.

    Args:
        array1: A 2-D list-of-lists (m × n) of numeric values.
        array2: A 2-D list-of-lists (n × p) of numeric values.

    Returns:
        The (m × p) product matrix as a list of lists.

    Raises:
        ValueError: If inner dimensions do not match.
    """
    a = np.array(array1, dtype=float)
    b = np.array(array2, dtype=float)
    if a.shape[1] != b.shape[0]:
        raise ValueError(
            "Number of columns in array1 must equal number of rows in array2."
        )
    return np.dot(a, b).tolist()


def munit(dimension: int) -> list:
    """
    Returns the identity matrix of the specified dimension.

    Args:
        dimension: The size of the square identity matrix (positive integer).

    Returns:
        A dimension × dimension identity matrix as a list of lists.
    """
    if dimension <= 0:
        raise ValueError("dimension must be a positive integer.")
    return np.eye(int(dimension)).tolist()


# ── Number theory & miscellaneous ─────────────────────────────────────────────

def roman(number: int, form: int = 0) -> str:
    """
    Converts an Arabic numeral to a Roman numeral string.

    Args:
        number: An integer in the range [1, 3999].
        form:   Conciseness level 0 (classic) to 4 (most concise).
                Only form 0 (classic) is supported; other values are accepted
                but treated as classic.

    Returns:
        The Roman numeral representation as a string.

    Raises:
        ValueError: If number is outside [1, 3999].
    """
    if not 1 <= number <= 3999:
        raise ValueError("number must be between 1 and 3999.")
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    result = ""
    for v, s in zip(val, syms):
        while number >= v:
            result += s
            number -= v
    return result


def arabic(text: str) -> int:
    """
    Converts a Roman numeral string to an Arabic integer.

    Args:
        text: A string containing a valid Roman numeral (case-insensitive).

    Returns:
        The decimal integer equivalent.
    """
    text = text.upper()
    roman_values = {"I": 1, "V": 5, "X": 10, "L": 50,
                    "C": 100, "D": 500, "M": 1000}
    result = 0
    prev = 0
    for ch in reversed(text):
        curr = roman_values.get(ch, 0)
        if curr < prev:
            result -= curr
        else:
            result += curr
        prev = curr
    return result


def base(number: int, radix: int, min_length: int = 0) -> str:
    """
    Converts a decimal integer into a text representation with the given radix.

    Args:
        number:     A non-negative decimal integer to convert.
        radix:      The base to convert to (2 ≤ radix ≤ 36).
        min_length: Minimum length of the returned string, left-padded with
                    zeros if necessary (default 0, no padding).

    Returns:
        The uppercase string representation of number in the specified base.

    Raises:
        ValueError: If radix is outside [2, 36] or number is negative.
    """
    if number < 0:
        raise ValueError("number must be a non-negative integer.")
    if not 2 <= radix <= 36:
        raise ValueError("radix must be between 2 and 36.")
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if number == 0:
        return "0".zfill(min_length)
    result = ""
    while number:
        result = digits[number % radix] + result
        number //= radix
    return result.zfill(min_length)


def decimal_from_base(text: str, radix: int) -> int:
    """
    Converts a text representation of a number in a given base to decimal.

    Args:
        text:  A string representing the number in the specified base.
        radix: The base of the input representation (2 ≤ radix ≤ 36).

    Returns:
        The decimal (base-10) integer equivalent.

    Raises:
        ValueError: If radix is outside [2, 36].
    """
    if not 2 <= radix <= 36:
        raise ValueError("radix must be between 2 and 36.")
    return int(text, radix)


def rand() -> float:
    """
    Returns a uniformly distributed random real number in [0, 1).

    Returns:
        A random float in [0, 1).
    """
    return np.random.uniform(0, 1)


def randbetween(bottom: int, top: int) -> int:
    """
    Returns a random integer between bottom and top (inclusive).

    Args:
        bottom: The minimum integer value (inclusive).
        top:    The maximum integer value (inclusive).

    Returns:
        A random integer in [bottom, top].

    Raises:
        ValueError: If bottom > top.
    """
    if bottom > top:
        raise ValueError("bottom must be less than or equal to top.")
    return int(np.random.randint(bottom, top + 1))
