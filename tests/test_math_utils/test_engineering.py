import sys
import os
import math
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
ops_path = os.path.join(project_root, "utils", "math_utils", "complex_math_operations")

if ops_path not in sys.path:
    sys.path.insert(0, ops_path)

from engineering import (
    bin2dec, bin2hex, bin2oct, dec2bin, dec2hex, dec2oct,
    hex2bin, hex2dec, hex2oct, oct2bin, oct2dec, oct2hex,
    bitand, bitor, bitxor, bitlshift, bitrshift,
    delta, gestep,
    erf, erfc,
    besseli, besselj, besselk, bessely,
    complex_number, imabs, imaginary, imreal, imargument,
    imconjugate, imsum, imsub, improduct, imdiv, impower, imsqrt,
    imexp, imln, imlog10, imlog2,
    imsin, imcos, imtan, imcot, imsec, imcsc,
    imsinh, imcosh, imsech, imcsch
)


class TestBaseConversions:
    def test_bin2dec(self):
        assert bin2dec("1010") == 10
        assert bin2dec("1111") == 15
        assert bin2dec("0") == 0
        assert bin2dec("1") == 1

    def test_bin2hex(self):
        assert bin2hex("1010") == "A"
        assert bin2hex("1111") == "F"
        assert bin2hex("11111111") == "FF"

    def test_bin2oct(self):
        assert bin2oct("1010") == "12"
        assert bin2oct("111111") == "77"

    def test_dec2bin(self):
        assert dec2bin(10) == "1010"
        assert dec2bin(255) == "11111111"
        assert dec2bin(0) == "0"
        with pytest.raises(ValueError):
            dec2bin(-1)

    def test_dec2hex(self):
        assert dec2hex(10) == "A"
        assert dec2hex(255) == "FF"
        assert dec2hex(0) == "0"
        with pytest.raises(ValueError):
            dec2hex(-1)

    def test_dec2oct(self):
        assert dec2oct(8) == "10"
        assert dec2oct(63) == "77"
        assert dec2oct(0) == "0"
        with pytest.raises(ValueError):
            dec2oct(-1)

    def test_hex2bin(self):
        assert hex2bin("A") == "1010"
        assert hex2bin("FF") == "11111111"

    def test_hex2dec(self):
        assert hex2dec("A") == 10
        assert hex2dec("FF") == 255

    def test_hex2oct(self):
        assert hex2oct("A") == "12"
        assert hex2oct("FF") == "377"

    def test_oct2bin(self):
        assert oct2bin("12") == "1010"
        assert oct2bin("77") == "111111"

    def test_oct2dec(self):
        assert oct2dec("12") == 10
        assert oct2dec("77") == 63

    def test_oct2hex(self):
        assert oct2hex("12") == "A"
        assert oct2hex("377") == "FF"


class TestBitwise:
    def test_bitand(self):
        assert bitand(5, 3) == 1
        assert bitand(12, 5) == 4
        assert bitand(0, 255) == 0
        with pytest.raises(ValueError):
            bitand(-1, 5)
        with pytest.raises(ValueError):
            bitand(5, -1)

    def test_bitor(self):
        assert bitor(5, 3) == 7
        assert bitor(12, 5) == 13
        assert bitor(0, 255) == 255

    def test_bitxor(self):
        assert bitxor(5, 3) == 6
        assert bitxor(12, 5) == 9

    def test_bitlshift(self):
        assert bitlshift(1, 3) == 8
        assert bitlshift(5, 2) == 20
        with pytest.raises(ValueError):
            bitlshift(-1, 1)

    def test_bitrshift(self):
        assert bitrshift(8, 3) == 1
        assert bitrshift(20, 2) == 5
        with pytest.raises(ValueError):
            bitrshift(1, -1)


class TestComparison:
    def test_delta(self):
        assert delta(5, 5) == 1
        assert delta(5, 3) == 0
        assert delta(0) == 1
        assert delta(1) == 0

    def test_gestep(self):
        assert gestep(5, 3) == 1
        assert gestep(2, 3) == 0
        assert gestep(0) == 1
        assert gestep(-1) == 0


class TestErrorFunctions:
    def test_erf(self):
        assert abs(erf(0) - 0) < 1e-10
        assert abs(erf(1) - 0.842700792949715) < 1e-10
        assert abs(erf(-1) + 0.842700792949715) < 1e-10

    def test_erf_two_limits(self):
        assert abs(erf(0, 1) - erf(1)) < 1e-10
        assert abs(erf(0.5, 1.5) - (erf(1.5) - erf(0.5))) < 1e-10

    def test_erfc(self):
        assert abs(erfc(0) - 1) < 1e-10
        assert abs(erfc(1) + erf(1) - 1) < 1e-10
        assert abs(erfc(3)) < 1e-4


class TestBessel:
    def test_besseli(self):
        assert abs(besseli(0, 0) - 1) < 1e-10
        assert abs(besseli(1, 1) - 0.565159103992485) < 1e-10
        with pytest.raises(ValueError):
            besseli(1, -1)

    def test_besselj(self):
        assert abs(besselj(0, 0) - 1) < 1e-10
        assert abs(besselj(1, 1) - 0.44005058574493355) < 1e-10
        with pytest.raises(ValueError):
            besselj(1, -1)

    def test_besselk(self):
        assert abs(besselk(1, 0) - 0.421024438240708) < 1e-10
        with pytest.raises(ValueError):
            besselk(-1, 0)
        with pytest.raises(ValueError):
            besselk(1, -1)

    def test_bessely(self):
        assert abs(bessely(1, 0) - 0.088256964215677) < 1e-10
        with pytest.raises(ValueError):
            bessely(-1, 0)
        with pytest.raises(ValueError):
            bessely(1, -1)


class TestComplexInEngineering:
    def test_complex_number(self):
        assert complex_number(3, 4) == complex(3, 4)
        assert complex_number(0, 1) == 1j

    def test_imabs(self):
        assert abs(imabs(3 + 4j) - 5) < 1e-10

    def test_imaginary(self):
        assert imaginary(3 + 4j) == 4

    def test_imreal(self):
        assert imreal(3 + 4j) == 3

    def test_imargument(self):
        assert abs(imargument(1 + 0j)) < 1e-10
        assert abs(imargument(0 + 1j) - math.pi / 2) < 1e-10

    def test_imconjugate(self):
        assert imconjugate(3 + 4j) == 3 - 4j

    def test_imsum(self):
        assert imsum(1 + 2j, 3 + 4j) == 4 + 6j

    def test_imsub(self):
        assert imsub(5 + 5j, 3 + 2j) == 2 + 3j

    def test_improduct(self):
        assert improduct(1 + 2j, 3 + 4j) == (1 + 2j) * (3 + 4j)
        assert improduct(1 + 1j, 2 + 2j, 3 + 3j) == (1 + 1j) * (2 + 2j) * (3 + 3j)

    def test_imdiv(self):
        q = imdiv(3 + 4j, 1 + 2j)
        assert abs(q - (3 + 4j) / (1 + 2j)) < 1e-10
        with pytest.raises(ZeroDivisionError):
            imdiv(1 + 1j, 0 + 0j)

    def test_impower(self):
        assert abs(impower(1 + 1j, 2) - (1 + 1j) ** 2) < 1e-10

    def test_imsqrt(self):
        s = imsqrt(1 + 0j)
        assert abs(s - 1) < 1e-10
        s2 = imsqrt(-1 + 0j)
        assert abs(s2 - 1j) < 1e-10

    def test_imexp(self):
        assert abs(imexp(0 + 0j) - 1) < 1e-10
        assert abs(imexp(1 + 0j) - math.e) < 1e-10

    def test_imln(self):
        assert abs(imln(1 + 0j)) < 1e-10
        assert abs(imln(math.e + 0j) - 1) < 1e-10

    def test_imlog10(self):
        assert abs(imlog10(10 + 0j) - 1) < 1e-10
        assert abs(imlog10(1 + 0j)) < 1e-10

    def test_imlog2(self):
        assert abs(imlog2(8 + 0j) - 3) < 1e-10

    def test_imsin(self):
        assert abs(imsin(0 + 0j)) < 1e-10
        assert abs(imsin(math.pi / 2 + 0j) - 1) < 1e-10

    def test_imcos(self):
        assert abs(imcos(0 + 0j) - 1) < 1e-10
        assert abs(imcos(math.pi / 2 + 0j)) < 1e-10

    def test_imtan(self):
        assert abs(imtan(0 + 0j)) < 1e-10
        assert abs(imtan(math.pi / 4 + 0j) - 1) < 1e-10

    def test_imcot(self):
        assert abs(imcot(math.pi / 4 + 0j) - 1) < 1e-10
        assert abs(imcot(math.pi / 2 + 0j)) < 1e-10

    def test_imsec(self):
        assert abs(imsec(0 + 0j) - 1) < 1e-10
        assert abs(imsec(math.pi / 3 + 0j) - 2) < 1e-10

    def test_imcsc(self):
        assert abs(imcsc(math.pi / 2 + 0j) - 1) < 1e-10

    def test_imsinh(self):
        assert abs(imsinh(0 + 0j)) < 1e-10

    def test_imcosh(self):
        assert abs(imcosh(0 + 0j) - 1) < 1e-10

    def test_imsech(self):
        assert abs(imsech(0 + 0j) - 1) < 1e-10

    def test_imcsch(self):
        assert abs(imcsch(1 + 0j) - 1 / math.sinh(1)) < 1e-10
