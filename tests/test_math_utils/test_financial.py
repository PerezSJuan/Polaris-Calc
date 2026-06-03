import sys
import os
import math
import pytest
from datetime import date

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
ops_path = os.path.join(project_root, "utils", "math_utils", "complex_math_operations")

if ops_path not in sys.path:
    sys.path.insert(0, ops_path)

from financial import (
    pv, fv, pmt, ipmt, ppmt, nper, rate, cumipmt, cumprinc, ispmt,
    npv, irr, mirr,
    effect, nominal, intrate, received,
    sln, syd, db, ddb, vdb,
    disc, pricedisc, yielddisc, tbilleq, tbillprice, tbillyield,
    duration, mduration,
    dollarde, dollarfr,
    accrint, accrintm,
    coupdaybs, coupdays, coupdaysnc, coupncd, couppcd, coupnum,
    pduration, rri, fvschedule, xnpv, xirr
)


class TestTimeValueOfMoney:
    def test_pv(self):
        result = pv(0.05, 10, 100, 0)
        assert abs(result - (-772.173492)) < 1e-6

    def test_fv(self):
        result = fv(0.05, 10, 100, 0)
        assert abs(result - (-1257.789)) < 1e-3

    def test_fv_with_pv(self):
        result = fv(0.05, 10, 100, -1000)
        assert abs(result - 371.105373) < 1e-4

    def test_pmt(self):
        result = pmt(0.05, 10, 1000, 0)
        assert abs(result - (-129.504575)) < 1e-6

    def test_pmt_at_beginning(self):
        result = pmt(0.05, 10, 1000, 0, payment_at_beginning=True)
        assert abs(result - (-123.337691)) < 1e-6

    def test_ipmt(self):
        result = ipmt(0.05, 1, 10, 1000, 0)
        assert abs(result - (-50.0)) < 1e-6

    def test_ppmt(self):
        result = ppmt(0.05, 1, 10, 1000, 0)
        assert abs(result - (-79.504575)) < 1e-6

    def test_nper(self):
        result = nper(0.05, -100, 1000, 0)
        assert abs(result - 14.206699) < 1e-4

    def test_rate(self):
        result = rate(10, -129.5, 1000, 0)
        assert abs(result - 0.05) < 1e-3

    def test_cumipmt(self):
        result = cumipmt(0.05, 10, 1000, 1, 3)
        assert abs(result - (-137.875552)) < 1e-6

    def test_cumprinc(self):
        result = cumprinc(0.05, 10, 1000, 1, 3)
        assert abs(result - (-250.638173)) < 1e-6

    def test_cumipmt_out_of_range(self):
        with pytest.raises(ValueError):
            cumipmt(0.05, 10, 1000, 0, 3)

    def test_ispmt(self):
        result = ispmt(0.05, 1, 10, 1000)
        assert abs(result - (-45.0)) < 1e-10

    def test_ispmt_last_period(self):
        result = ispmt(0.05, 10, 10, 1000)
        assert abs(result - 0) < 1e-10

    def test_pduration(self):
        result = pduration(0.05, 1000, 2000)
        assert abs(result - 14.206699) < 1e-4
        with pytest.raises(ValueError):
            pduration(0, 1000, 2000)

    def test_rri(self):
        result = rri(10, 100, 200)
        assert abs(result - 0.071773) < 1e-5
        with pytest.raises(ValueError):
            rri(0, 100, 200)

    def test_fvschedule(self):
        result = fvschedule(100, [0.05, 0.06, 0.07])
        assert abs(result - 119.091) < 1e-3


class TestNpvAndIrr:
    def test_npv(self):
        result = npv(0.1, [-100, 60, 60, 60])
        assert abs(result - 49.211) < 1e-3

    def test_irr(self):
        result = irr([-100, 30, 40, 50, 60])
        assert abs(result - 0.248883) < 1e-5

    def test_mirr(self):
        result = mirr([-100, 30, 40, 50, 60], 0.08, 0.12)
        assert abs(result - 0.201392) < 1e-5

    def test_xnpv(self):
        dates = [
            date(2020, 1, 1),
            date(2020, 7, 1),
            date(2021, 1, 1),
            date(2021, 7, 1),
        ]
        result = xnpv(0.1, [-1000, 300, 400, 500], dates)
        assert abs(result - 83.066221) < 1e-5

    def test_xnpv_length_mismatch(self):
        with pytest.raises(ValueError):
            xnpv(0.1, [1, 2], [date(2020, 1, 1)])

    def test_xirr(self):
        dates = [
            date(2020, 1, 1),
            date(2020, 7, 1),
            date(2021, 1, 1),
            date(2021, 7, 1),
        ]
        result = xirr([-1000, 300, 400, 500], dates)
        assert abs(result - 0.185838) < 1e-5

    def test_xirr_length_mismatch(self):
        with pytest.raises(ValueError):
            xirr([1, 2], [date(2020, 1, 1)])


class TestInterestRates:
    def test_effect(self):
        result = effect(0.05, 4)
        assert abs(result - 0.050945) < 1e-5
        with pytest.raises(ValueError):
            effect(0.05, 0)

    def test_nominal(self):
        result = nominal(0.050945, 4)
        assert abs(result - 0.05) < 1e-4
        with pytest.raises(ValueError):
            nominal(0.05, 0)

    def test_intrate(self):
        result = intrate(date(2020, 1, 1), date(2021, 1, 1), 95, 100, 3)
        assert abs(result - 0.0524877) < 1e-6

    def test_received(self):
        result = received(date(2020, 1, 1), date(2021, 1, 1), 100, 0.05, 3)
        assert abs(result - 105.278338) < 1e-5


class TestDepreciation:
    def test_sln(self):
        result = sln(1000, 100, 5)
        assert abs(result - 180) < 1e-10
        with pytest.raises(ValueError):
            sln(100, 0, 0)

    def test_syd(self):
        result = syd(1000, 100, 5, 1)
        assert abs(result - 300) < 1e-10

    def test_syd_last_period(self):
        result = syd(1000, 100, 5, 5)
        assert abs(result - 60) < 1e-10

    def test_syd_out_of_range(self):
        with pytest.raises(ValueError):
            syd(1000, 100, 5, 6)

    def test_db(self):
        result = db(1000, 100, 5, 1)
        assert result > 0

    def test_db_mid_life(self):
        result = db(1000, 100, 5, 3)
        assert result > 0

    def test_db_zero_cost(self):
        assert db(0, 0, 5, 1) == 0

    def test_ddb(self):
        result = ddb(1000, 100, 5, 1)
        assert abs(result - 400) < 1e-10

    def test_ddb_later_period(self):
        result = ddb(1000, 100, 5, 3)
        assert result > 0

    def test_vdb(self):
        result = vdb(1000, 100, 5, 0, 1)
        assert result > 0

    def test_vdb_full_life(self):
        total = vdb(1000, 100, 5, 0, 5)
        assert abs(total - 900) < 1


class TestBondPrices:
    def test_disc(self):
        result = disc(date(2020, 1, 1), date(2021, 1, 1), 95, 100, 3)
        assert abs(result - 0.0498634) < 1e-6

    def test_pricedisc(self):
        result = pricedisc(date(2020, 1, 1), date(2021, 1, 1), 0.05, 100, 3)
        assert abs(result - 94.9863014) < 1e-6

    def test_yielddisc(self):
        result = yielddisc(date(2020, 1, 1), date(2021, 1, 1), 95, 100, 3)
        assert result > 0

    def test_tbilleq(self):
        result = tbilleq(date(2020, 1, 1), date(2020, 7, 1), 0.05)
        assert abs(result - 0.0515) < 1e-3

    def test_tbillprice(self):
        result = tbillprice(date(2020, 1, 1), date(2020, 7, 1), 0.05)
        assert abs(result - 97.472222) < 1e-5

    def test_tbillyield(self):
        result = tbillyield(date(2020, 1, 1), date(2020, 7, 1), 97.43)
        assert abs(result - 0.053) < 1e-3

    def test_duration(self):
        result = duration(date(2020, 1, 1), date(2025, 1, 1), 0.05, 0.05, 1, 0)
        assert abs(result - 4.545) < 1e-2

    def test_mduration(self):
        mac = duration(date(2020, 1, 1), date(2025, 1, 1), 0.05, 0.05, 1, 0)
        mod = mduration(date(2020, 1, 1), date(2025, 1, 1), 0.05, 0.05, 1, 0)
        assert abs(mod - mac / (1 + 0.05)) < 1e-10


class TestDollarPrice:
    def test_dollarde(self):
        assert abs(dollarde(1.02, 8) - 1.25) < 1e-10
        assert abs(dollarde(1.1, 8) - 1.125) < 1e-10
        with pytest.raises(ValueError):
            dollarde(1.02, 0)

    def test_dollarfr(self):
        assert abs(dollarfr(1.25, 8) - 1.2) < 1e-10
        assert abs(dollarfr(1.5, 2) - 1.1) < 1e-10
        with pytest.raises(ValueError):
            dollarfr(1.25, 0)


class TestAccruedInterest:
    def test_accrint(self):
        result = accrint(
            date(2020, 1, 1), date(2020, 7, 1), date(2020, 4, 1),
            0.05, 100, 2, 3
        )
        assert abs(result - 1.25) < 1e-2

    def test_accrintm(self):
        result = accrintm(
            date(2020, 1, 1), date(2020, 7, 1), 0.05, 100, 3
        )
        assert abs(result - 2.5) < 1e-2

    def test_coupdaybs(self):
        result = coupdaybs(date(2020, 6, 1), date(2025, 1, 1), 2, 0)
        assert result >= 0

    def test_coupdays(self):
        result = coupdays(date(2020, 6, 1), date(2025, 1, 1), 2, 0)
        assert result > 0

    def test_coupdaysnc(self):
        result = coupdaysnc(date(2020, 6, 1), date(2025, 1, 1), 2, 0)
        assert result >= 0

    def test_coupncd(self):
        result = coupncd(date(2020, 6, 1), date(2025, 1, 1), 2, 0)
        assert result > date(2020, 6, 1)

    def test_couppcd(self):
        result = couppcd(date(2020, 6, 1), date(2025, 1, 1), 2, 0)
        assert result <= date(2020, 6, 1)

    def test_coupnum(self):
        result = coupnum(date(2020, 1, 1), date(2025, 1, 1), 2, 0)
        assert result == 10
