import numpy as np
import numpy_financial as npf
from datetime import date, timedelta
import math


# ── Time-value-of-money (annuity) functions ───────────────────────────────────

def pv(rate: float, nper: float, pmt: float, fv: float = 0,
       payment_at_beginning: bool = False) -> float:
    """
    Returns the present value of an investment.

    Computes the current lump-sum equivalent of a series of future cash flows
    discounted at a constant interest rate. Mirrors Excel's PV function.

    Args:
        rate:                  Interest rate per period.
        nper:                  Total number of payment periods.
        pmt:                   Payment made each period (negative for outflows).
        fv:                    Future value remaining after the last payment
                               (default 0).
        payment_at_beginning:  True if payments are made at the beginning of
                               each period (annuity-due), False for end of
                               period (ordinary annuity, default False).

    Returns:
        The present value (positive means money received, negative means paid).
    """
    when = 1 if payment_at_beginning else 0
    return float(npf.pv(rate, nper, pmt, fv=fv, when=when))


def fv(rate: float, nper: float, pmt: float, pv: float = 0,
       payment_at_beginning: bool = False) -> float:
    """
    Returns the future value of an investment.

    Calculates the value of an investment at the end of the payment schedule
    given a constant interest rate and fixed periodic payments.

    Args:
        rate:                  Interest rate per period.
        nper:                  Total number of payment periods.
        pmt:                   Payment made each period (negative for outflows).
        pv:                    Present value (initial lump sum, default 0).
        payment_at_beginning:  True if payments are at the beginning of each
                               period (default False).

    Returns:
        The future value of the investment.
    """
    when = 1 if payment_at_beginning else 0
    return float(npf.fv(rate, nper, pmt, pv=pv, when=when))


def pmt(rate: float, nper: float, pv: float, fv: float = 0,
        payment_at_beginning: bool = False) -> float:
    """
    Returns the fixed periodic payment for an annuity.

    Given a present value, interest rate, and number of periods, computes
    the constant payment required to fully amortise the loan or reach the
    target future value.

    Args:
        rate:                  Interest rate per period.
        nper:                  Total number of payment periods.
        pv:                    Present value (loan principal, positive).
        fv:                    Future value after all payments (default 0).
        payment_at_beginning:  True for beginning-of-period payments
                               (default False).

    Returns:
        The periodic payment amount (negative for outflows).
    """
    when = 1 if payment_at_beginning else 0
    return float(npf.pmt(rate, nper, pv, fv=fv, when=when))


def ipmt(rate: float, per: int, nper: float, pv: float, fv: float = 0,
         payment_at_beginning: bool = False) -> float:
    """
    Returns the interest portion of a loan payment for a given period.

    Decomposes a fixed periodic payment into its interest and principal
    components. IPMT gives the interest part for period `per`.

    Args:
        rate:                  Interest rate per period.
        per:                   The period number (1-based) for which to compute
                               the interest payment.
        nper:                  Total number of payment periods.
        pv:                    Present value of the loan.
        fv:                    Future value after all payments (default 0).
        payment_at_beginning:  True for beginning-of-period payments
                               (default False).

    Returns:
        The interest payment for period `per` (negative for outflows).
    """
    when = 1 if payment_at_beginning else 0
    return float(npf.ipmt(rate, per, nper, pv, fv=fv, when=when))


def ppmt(rate: float, per: int, nper: float, pv: float, fv: float = 0,
         payment_at_beginning: bool = False) -> float:
    """
    Returns the principal portion of a loan payment for a given period.

    Decomposes a fixed periodic payment into interest and principal. PPMT
    gives the principal repayment for period `per`.

    Args:
        rate:                  Interest rate per period.
        per:                   The period number (1-based) for which to compute
                               the principal payment.
        nper:                  Total number of payment periods.
        pv:                    Present value of the loan.
        fv:                    Future value after all payments (default 0).
        payment_at_beginning:  True for beginning-of-period payments
                               (default False).

    Returns:
        The principal payment for period `per` (negative for outflows).
    """
    when = 1 if payment_at_beginning else 0
    return float(npf.ppmt(rate, per, nper, pv, fv=fv, when=when))


def nper(rate: float, pmt: float, pv: float, fv: float = 0,
         payment_at_beginning: bool = False) -> float:
    """
    Returns the number of periods required for an investment.

    Calculates how many payment periods are needed to reach a target future
    value (or fully repay a loan) at a given interest rate and payment amount.

    Args:
        rate:                  Interest rate per period.
        pmt:                   Fixed payment per period (negative for outflows).
        pv:                    Present value.
        fv:                    Target future value (default 0).
        payment_at_beginning:  True for beginning-of-period payments
                               (default False).

    Returns:
        The number of periods.
    """
    when = 1 if payment_at_beginning else 0
    return float(npf.nper(rate, pmt, pv, fv=fv, when=when))


def rate(nper: float, pmt: float, pv: float, fv: float = 0,
         payment_at_beginning: bool = False, guess: float = 0.1) -> float:
    """
    Returns the interest rate per period of an annuity.

    Finds the interest rate that equates present value, payments, and future
    value. Solved iteratively; `guess` provides the initial estimate.

    Args:
        nper:                  Total number of payment periods.
        pmt:                   Fixed payment per period (negative for outflows).
        pv:                    Present value of the annuity.
        fv:                    Future value after all payments (default 0).
        payment_at_beginning:  True for beginning-of-period payments
                               (default False).
        guess:                 Initial guess for the rate (default 0.1 = 10%).

    Returns:
        The periodic interest rate.
    """
    when = 1 if payment_at_beginning else 0
    return float(npf.rate(nper, pmt, pv, fv=fv, when=when, guess=guess))


def cumipmt(rate: float, nper: float, pv: float, start_period: int,
            end_period: int, payment_at_beginning: bool = False) -> float:
    """
    Returns the cumulative interest paid on a loan between two periods.

    Sums the interest component of each payment from start_period to
    end_period (both inclusive, 1-based).

    Args:
        rate:                  Interest rate per period.
        nper:                  Total number of payment periods.
        pv:                    Present value of the loan.
        start_period:          First period to include (1-based).
        end_period:            Last period to include (1-based).
        payment_at_beginning:  True for beginning-of-period payments
                               (default False).

    Returns:
        The total interest paid between start_period and end_period (negative).

    Raises:
        ValueError: If start_period or end_period are out of range.
    """
    if start_period < 1 or end_period > nper or start_period > end_period:
        raise ValueError(
            "start_period and end_period must satisfy 1 ≤ start ≤ end ≤ nper."
        )
    when = 1 if payment_at_beginning else 0
    return float(npf.cumipmt(rate, nper, pv, start_period, end_period, when=when))


def cumprinc(rate: float, nper: float, pv: float, start_period: int,
             end_period: int, payment_at_beginning: bool = False) -> float:
    """
    Returns the cumulative principal paid on a loan between two periods.

    Sums the principal repayment component of each payment from start_period
    to end_period (both inclusive, 1-based).

    Args:
        rate:                  Interest rate per period.
        nper:                  Total number of payment periods.
        pv:                    Present value of the loan.
        start_period:          First period to include (1-based).
        end_period:            Last period to include (1-based).
        payment_at_beginning:  True for beginning-of-period payments
                               (default False).

    Returns:
        The total principal repaid between start_period and end_period (negative).

    Raises:
        ValueError: If start_period or end_period are out of range.
    """
    if start_period < 1 or end_period > nper or start_period > end_period:
        raise ValueError(
            "start_period and end_period must satisfy 1 ≤ start ≤ end ≤ nper."
        )
    when = 1 if payment_at_beginning else 0
    return float(npf.cumprinc(rate, nper, pv, start_period, end_period, when=when))


def ispmt(rate: float, per: int, nper: float, pv: float) -> float:
    """
    Returns the interest paid during a specific period of a straight-line loan.

    Unlike IPMT (which works with equal total payments), ISPMT assumes equal
    principal payments each period, so the total payment decreases over time.

    Args:
        rate: Interest rate per period.
        per:  The period number (1-based) for which to compute the interest.
        nper: Total number of payment periods.
        pv:   Present value of the loan (positive).

    Returns:
        The interest payment for period `per` (negative, as it is an outflow).
    """
    return pv * rate * (per / nper - 1)


# ── Rate-of-return & net-present-value functions ─────────────────────────────

def npv(rate: float, values: list) -> float:
    """
    Returns the net present value of an investment based on periodic cash flows.

    Discounts each cash flow at the given rate assuming flows occur at the
    end of each period. The first value corresponds to period 1 (not period 0).
    To include an initial outlay at period 0, add it manually: npv(r, cf) + cf0.

    Args:
        rate:   The discount rate per period.
        values: List of cash flows occurring at the end of each period.
                Positive values are inflows; negative values are outflows.

    Returns:
        The net present value.
    """
    return float(npf.npv(rate, values))


def irr(values: list, guess: float = 0.1) -> float:
    """
    Returns the internal rate of return for a series of periodic cash flows.

    The IRR is the discount rate that makes NPV = 0. The series must contain
    at least one positive and one negative value. Solved iteratively.

    Args:
        values: List of cash flows (first value is typically a negative outlay).
        guess:  Initial estimate for the rate (default 0.1 = 10%).

    Returns:
        The internal rate of return as a decimal (e.g. 0.12 for 12%).
    """
    return float(npf.irr(values))


def mirr(values: list, finance_rate: float, reinvest_rate: float) -> float:
    """
    Returns the modified internal rate of return.

    Unlike IRR, MIRR accounts for the cost of capital for negative cash flows
    (finance_rate) and the return on reinvested positive cash flows
    (reinvest_rate), giving a more realistic measure of profitability.

    Args:
        values:         List of cash flows (must include at least one positive
                        and one negative value).
        finance_rate:   Interest rate paid on negative cash flows (cost of funds).
        reinvest_rate:  Interest rate earned on positive cash flows when reinvested.

    Returns:
        The modified internal rate of return as a decimal.
    """
    return float(npf.mirr(values, finance_rate, reinvest_rate))


def xnpv(rate: float, values: list, dates: list) -> float:
    """
    Returns the net present value for a schedule of non-periodic cash flows.

    Unlike NPV, XNPV allows irregular intervals between cash flows. Dates are
    measured in days from the first date, consistent with Excel's XNPV.

    Args:
        rate:   The annual discount rate.
        values: List of cash flows.
        dates:  List of datetime.date objects corresponding to each cash flow.
                Must be the same length as values and in chronological order.

    Returns:
        The net present value of the irregular cash flow schedule.

    Raises:
        ValueError: If values and dates have different lengths.
    """
    if len(values) != len(dates):
        raise ValueError("values and dates must have the same length.")
    d0 = dates[0]
    return sum(v / (1 + rate) ** ((d - d0).days / 365)
               for v, d in zip(values, dates))


def xirr(values: list, dates: list, guess: float = 0.1) -> float:
    """
    Returns the internal rate of return for non-periodic cash flows.

    Solves for the rate r such that XNPV(r, values, dates) = 0 using
    Newton–Raphson iteration.

    Args:
        values: List of cash flows (must include at least one positive and
                one negative value).
        dates:  List of datetime.date objects for each cash flow.
        guess:  Initial estimate for the rate (default 0.1).

    Returns:
        The internal rate of return as a decimal.

    Raises:
        ValueError: If values and dates have different lengths or convergence fails.
    """
    if len(values) != len(dates):
        raise ValueError("values and dates must have the same length.")
    d0 = dates[0]
    days = [(d - d0).days / 365 for d in dates]

    r = guess
    for _ in range(1000):
        f = sum(v / (1 + r) ** t for v, t in zip(values, days))
        df = sum(-t * v / (1 + r) ** (t + 1) for v, t in zip(values, days))
        if df == 0:
            break
        r_new = r - f / df
        if abs(r_new - r) < 1e-10:
            return r_new
        r = r_new
    raise ValueError("XIRR did not converge. Try a different guess.")


def pduration(rate: float, pv: float, fv: float) -> float:
    """
    Returns the number of periods required for an investment to reach a target value.

    Solves for n in FV = PV · (1 + rate)^n.

    Args:
        rate: The interest rate per period (must be > 0).
        pv:   The present value of the investment (must be > 0).
        fv:   The desired future value (must be > 0 and > pv for positive rate).

    Returns:
        The number of periods required.

    Raises:
        ValueError: If rate ≤ 0, pv ≤ 0, or fv ≤ 0.
    """
    if rate <= 0 or pv <= 0 or fv <= 0:
        raise ValueError("rate, pv, and fv must all be positive.")
    return math.log(fv / pv) / math.log(1 + rate)


def rri(nper: float, pv: float, fv: float) -> float:
    """
    Returns the equivalent interest rate for an investment to grow from PV to FV.

    Solves for r in FV = PV · (1 + r)^nper.

    Args:
        nper: The number of periods.
        pv:   The present value (must be > 0).
        fv:   The future value (must be > 0).

    Returns:
        The equivalent interest rate per period.

    Raises:
        ValueError: If nper ≤ 0, pv ≤ 0, or fv ≤ 0.
    """
    if nper <= 0 or pv <= 0 or fv <= 0:
        raise ValueError("nper, pv, and fv must all be positive.")
    return (fv / pv) ** (1 / nper) - 1


def fvschedule(principal: float, schedule: list) -> float:
    """
    Returns the future value of an initial principal after a series of
    compound interest rates applied sequentially.

    Args:
        principal: The initial lump-sum investment.
        schedule:  List of interest rates for each period (as decimals).

    Returns:
        The future value after applying each rate in schedule sequentially.
    """
    result = principal
    for r in schedule:
        result *= (1 + r)
    return result


# ── Interest-rate functions ───────────────────────────────────────────────────

def effect(nominal_rate: float, npery: int) -> float:
    """
    Returns the effective annual interest rate.

    Converts a nominal annual rate compounded npery times per year into the
    equivalent annually compounded rate.

    effective = (1 + nominal_rate/npery)^npery − 1

    Args:
        nominal_rate: The nominal annual interest rate (as a decimal).
        npery:        The number of compounding periods per year.

    Returns:
        The effective annual interest rate.

    Raises:
        ValueError: If npery < 1 or nominal_rate ≤ 0.
    """
    if npery < 1:
        raise ValueError("npery must be at least 1.")
    if nominal_rate <= 0:
        raise ValueError("nominal_rate must be positive.")
    return (1 + nominal_rate / npery) ** npery - 1


def nominal(effect_rate: float, npery: int) -> float:
    """
    Returns the annual nominal interest rate given the effective rate.

    Inverts the EFFECT formula:
    nominal = npery · ((1 + effect_rate)^(1/npery) − 1)

    Args:
        effect_rate: The effective annual interest rate (as a decimal).
        npery:       The number of compounding periods per year.

    Returns:
        The nominal annual interest rate.

    Raises:
        ValueError: If npery < 1 or effect_rate ≤ 0.
    """
    if npery < 1:
        raise ValueError("npery must be at least 1.")
    if effect_rate <= 0:
        raise ValueError("effect_rate must be positive.")
    return npery * ((1 + effect_rate) ** (1 / npery) - 1)


def intrate(settlement: date, maturity: date, investment: float,
            redemption: float, basis: int = 0) -> float:
    """
    Returns the interest rate for a fully invested (discount) security.

    intrate = (redemption − investment) / investment / (days / year_basis)

    Args:
        settlement:  The security's settlement date.
        maturity:    The security's maturity date.
        investment:  The amount invested.
        redemption:  The amount to be received at maturity.
        basis:       Day-count convention (0 = US 30/360, 1 = actual/actual,
                     2 = actual/360, 3 = actual/365, 4 = European 30/360).
                     Default 0.

    Returns:
        The annualised interest rate.
    """
    days, year = _day_count(settlement, maturity, basis)
    return (redemption - investment) / investment / (days / year)


def received(settlement: date, maturity: date, investment: float,
             discount: float, basis: int = 0) -> float:
    """
    Returns the amount received at maturity for a fully invested security.

    received = investment / (1 − discount · days/year)

    Args:
        settlement: The security's settlement date.
        maturity:   The security's maturity date.
        investment: The amount invested.
        discount:   The security's discount rate.
        basis:      Day-count convention (default 0).

    Returns:
        The amount received at maturity.
    """
    days, year = _day_count(settlement, maturity, basis)
    return investment / (1 - discount * days / year)


# ── Depreciation functions ────────────────────────────────────────────────────

def sln(cost: float, salvage: float, life: float) -> float:
    """
    Returns the straight-line depreciation of an asset for one period.

    Spreads the depreciable cost evenly across all periods.
    SLN = (cost − salvage) / life

    Args:
        cost:    The initial cost of the asset.
        salvage: The residual value at the end of useful life.
        life:    The number of periods over which the asset is depreciated.

    Returns:
        The depreciation charge per period.

    Raises:
        ValueError: If life is zero.
    """
    if life == 0:
        raise ValueError("life must not be zero.")
    return (cost - salvage) / life


def syd(cost: float, salvage: float, life: float, per: float) -> float:
    """
    Returns the sum-of-years'-digits depreciation for a specified period.

    SYD = (cost − salvage) · (life − per + 1) / (life · (life + 1) / 2)

    Args:
        cost:    The initial cost of the asset.
        salvage: The residual value at the end of useful life.
        life:    The total useful life in periods.
        per:     The period for which to calculate depreciation (1-based).

    Returns:
        The depreciation charge for period `per`.

    Raises:
        ValueError: If per > life.
    """
    if per > life:
        raise ValueError("per must not exceed life.")
    return (cost - salvage) * (life - per + 1) / (life * (life + 1) / 2)


def db(cost: float, salvage: float, life: int, period: int,
       month: int = 12) -> float:
    """
    Returns the depreciation for a specified period using the fixed-declining
    balance method.

    The rate is calculated as 1 − (salvage/cost)^(1/life), rounded to three
    decimal places. The first and last periods are prorated by `month`.

    Args:
        cost:    The initial cost of the asset.
        salvage: The residual value at end of useful life (may be 0).
        life:    Total useful life in periods.
        period:  The period for which to calculate depreciation (1-based).
        month:   Number of months in the first year (default 12).

    Returns:
        The fixed-declining balance depreciation for the given period.
    """
    if cost == 0:
        return 0.0
    r = round(1 - (salvage / cost) ** (1 / life), 3)
    book = cost
    dep = 0.0
    for p in range(1, period + 1):
        if p == 1:
            dep = cost * r * month / 12
        elif p == life + 1:
            dep = (book - dep) * r * (12 - month) / 12
        else:
            dep = book * r
        if p < period:
            book -= dep
    return dep


def ddb(cost: float, salvage: float, life: float, period: float,
        factor: float = 2) -> float:
    """
    Returns the depreciation for a specified period using the double-declining
    balance method (or any other user-specified declining-balance factor).

    DDB = min(book_value × factor/life, book_value − salvage)

    Args:
        cost:    The initial cost of the asset.
        salvage: The residual value at end of useful life.
        life:    Total useful life in periods.
        period:  The period for which to calculate depreciation (1-based).
        factor:  The rate at which the balance declines (default 2 = double).

    Returns:
        The double-declining balance depreciation for the given period.
    """
    book = cost
    dep = 0.0
    for p in range(1, int(period) + 1):
        dep = min(book * factor / life, book - salvage)
        if dep < 0:
            dep = 0
        if p < period:
            book -= dep
    return dep


def vdb(cost: float, salvage: float, life: float, start_period: float,
        end_period: float, factor: float = 2,
        no_switch: bool = False) -> float:
    """
    Returns the depreciation of an asset for any partial or full period using
    a declining balance method, with optional switch to straight-line.

    Mirrors Excel's VDB (Variable Declining Balance).

    Args:
        cost:         The initial cost of the asset.
        salvage:      The residual value at end of useful life.
        life:         Total useful life in periods.
        start_period: The starting period (0-based, can be fractional).
        end_period:   The ending period (0-based, can be fractional).
        factor:       The rate of balance decline (default 2 = double).
        no_switch:    If True, never switch to straight-line (default False).

    Returns:
        The total depreciation between start_period and end_period.
    """
    def _ddb_period(cost, salvage, life, per, factor, no_switch):
        """Depreciation for a single period using DDB with optional SL switch."""
        book = cost
        for p in range(1, int(per) + 1):
            ddb_dep = book * factor / life
            sl_dep = (book - salvage) / (life - p + 1) if life > p - 1 else 0
            if not no_switch and sl_dep > ddb_dep:
                dep = sl_dep
            else:
                dep = min(ddb_dep, book - salvage)
            dep = max(dep, 0)
            if p < per:
                book -= dep
        return dep, book

    # Accumulate over all integer sub-periods between start and end.
    total = 0.0
    book = cost
    start = start_period
    end = end_period

    # Fractional first period
    if start % 1 != 0:
        frac = 1 - (start % 1)
        dep, book = _ddb_period(book, salvage, life, 1, factor, no_switch)
        total += dep * frac
        book -= dep * frac
        start = math.ceil(start)

    # Full integer periods
    for p in range(int(start) + 1, int(end) + 1):
        dep, book = _ddb_period(book, salvage, life, 1, factor, no_switch)
        total += dep
        book -= dep

    # Fractional last period
    if end % 1 != 0:
        frac = end % 1
        dep, book = _ddb_period(book, salvage, life, 1, factor, no_switch)
        total += dep * frac

    return total


# ── Bond / security price & yield functions ───────────────────────────────────

def disc(settlement: date, maturity: date, pr: float, redemption: float,
         basis: int = 0) -> float:
    """
    Returns the discount rate for a security.

    disc = (redemption − pr) / redemption / (days/year)

    Args:
        settlement:  The security's settlement date.
        maturity:    The security's maturity date.
        pr:          The security's price per 100 face value.
        redemption:  The security's redemption value per 100 face value.
        basis:       Day-count convention (default 0).

    Returns:
        The annualised discount rate.
    """
    days, year = _day_count(settlement, maturity, basis)
    return (redemption - pr) / redemption / (days / year)


def pricedisc(settlement: date, maturity: date, discount: float,
              redemption: float, basis: int = 0) -> float:
    """
    Returns the price per $100 face value of a discounted security.

    pricedisc = redemption − discount · redemption · days/year

    Args:
        settlement:  The security's settlement date.
        maturity:    The security's maturity date.
        discount:    The security's discount rate.
        redemption:  The redemption value per $100 face value.
        basis:       Day-count convention (default 0).

    Returns:
        The price per $100 face value.
    """
    days, year = _day_count(settlement, maturity, basis)
    return redemption - discount * redemption * days / year


def yielddisc(settlement: date, maturity: date, pr: float,
              redemption: float, basis: int = 0) -> float:
    """
    Returns the annual yield of a discounted security (e.g. a Treasury bill).

    yielddisc = (redemption/pr − 1) · year/days

    Args:
        settlement:  The security's settlement date.
        maturity:    The security's maturity date.
        pr:          The security's price per $100 face value.
        redemption:  The redemption value per $100 face value.
        basis:       Day-count convention (default 0).

    Returns:
        The annualised yield.
    """
    days, year = _day_count(settlement, maturity, basis)
    return (redemption / pr - 1) * year / days


def tbilleq(settlement: date, maturity: date, discount: float) -> float:
    """
    Returns the bond-equivalent yield for a Treasury bill.

    Converts the bank-discount rate to a bond-equivalent yield based on a
    360-day and 365-day year respectively.

    Args:
        settlement: The T-bill's settlement date.
        maturity:   The T-bill's maturity date (≤ 1 year from settlement).
        discount:   The T-bill's discount rate (as a decimal).

    Returns:
        The bond-equivalent yield.
    """
    days = (maturity - settlement).days
    return 365 * discount / (360 - discount * days)


def tbillprice(settlement: date, maturity: date, discount: float) -> float:
    """
    Returns the price per $100 face value of a Treasury bill.

    price = 100 · (1 − discount · days/360)

    Args:
        settlement: The T-bill's settlement date.
        maturity:   The T-bill's maturity date.
        discount:   The T-bill's discount rate (as a decimal).

    Returns:
        The price per $100 face value.
    """
    days = (maturity - settlement).days
    return 100 * (1 - discount * days / 360)


def tbillyield(settlement: date, maturity: date, pr: float) -> float:
    """
    Returns the yield for a Treasury bill.

    yield = (100/pr − 1) · 360/days

    Args:
        settlement: The T-bill's settlement date.
        maturity:   The T-bill's maturity date.
        pr:         The T-bill's price per $100 face value.

    Returns:
        The annualised yield.
    """
    days = (maturity - settlement).days
    return (100 / pr - 1) * 360 / days


def duration(settlement: date, maturity: date, coupon: float, yld: float,
             frequency: int, basis: int = 0) -> float:
    """
    Returns the Macaulay duration of a bond with periodic coupon payments.

    Duration is the weighted average time to receive cash flows, measured in
    years. It indicates the sensitivity of the bond's price to changes in yield.

    Args:
        settlement: The bond's settlement date.
        maturity:   The bond's maturity date.
        coupon:     The bond's annual coupon rate (as a decimal).
        yld:        The bond's annual yield (as a decimal).
        frequency:  The number of coupon payments per year (1, 2, or 4).
        basis:      Day-count convention (default 0).

    Returns:
        The Macaulay duration in years.
    """
    periods = _coupon_periods(settlement, maturity, frequency)
    c = coupon / frequency
    y = yld / frequency
    total_pv = 0.0
    weighted_pv = 0.0
    for i, t in enumerate(periods, start=1):
        cash = c if i < len(periods) else c + 1
        pv_cash = cash / (1 + y) ** i
        total_pv += pv_cash
        weighted_pv += i / frequency * pv_cash
    return weighted_pv / total_pv


def mduration(settlement: date, maturity: date, coupon: float, yld: float,
              frequency: int, basis: int = 0) -> float:
    """
    Returns the modified Macaulay duration of a bond.

    Modified duration = Macaulay duration / (1 + yld/frequency).
    It directly approximates the percentage price change for a 1% yield change.

    Args:
        settlement: The bond's settlement date.
        maturity:   The bond's maturity date.
        coupon:     The bond's annual coupon rate (as a decimal).
        yld:        The bond's annual yield (as a decimal).
        frequency:  The number of coupon payments per year (1, 2, or 4).
        basis:      Day-count convention (default 0).

    Returns:
        The modified duration.
    """
    mac = duration(settlement, maturity, coupon, yld, frequency, basis)
    return mac / (1 + yld / frequency)


# ── Dollar price helpers ──────────────────────────────────────────────────────

def dollarde(fractional_dollar: float, fraction: int) -> float:
    """
    Converts a dollar price expressed as an integer fraction into a decimal.

    For example, 1.02 expressed in eighths (fraction=8) = 1 + 2/8 = 1.25.

    Args:
        fractional_dollar: A price where the digits after the decimal represent
                           the numerator of a fraction.
        fraction:          The denominator of the fraction (e.g. 2, 4, 8, 16, 32).

    Returns:
        The decimal dollar price.

    Raises:
        ValueError: If fraction is not a positive integer.
    """
    if fraction <= 0:
        raise ValueError("fraction must be a positive integer.")
    integer_part = int(fractional_dollar)
    fractional_part = fractional_dollar - integer_part
    return integer_part + fractional_part / fraction * 10 ** len(
        str(int(round(fractional_part * 10 ** 10))).lstrip("0") or "1"
    ) / 10 ** len(
        str(int(round(fractional_part * 10 ** 10))).lstrip("0") or "1"
    ) * fraction / fraction


def dollarfr(decimal_dollar: float, fraction: int) -> float:
    """
    Converts a dollar price expressed as a decimal into a fractional notation.

    For example, 1.25 in eighths (fraction=8) = 1.02 (meaning 1 + 2/8).

    Args:
        decimal_dollar: The price as a decimal number.
        fraction:       The denominator of the fraction (e.g. 2, 4, 8, 16, 32).

    Returns:
        The price in fractional notation.

    Raises:
        ValueError: If fraction is not a positive integer.
    """
    if fraction <= 0:
        raise ValueError("fraction must be a positive integer.")
    integer_part = int(decimal_dollar)
    decimal_part = decimal_dollar - integer_part
    return integer_part + decimal_part * fraction / 10 ** len(str(fraction))


# ── Accrued-interest & coupon helpers ─────────────────────────────────────────

def accrint(issue: date, first_interest: date, settlement: date,
            rate: float, par: float, frequency: int,
            basis: int = 0) -> float:
    """
    Returns the accrued interest for a security that pays periodic interest.

    accrint = par · rate/frequency · (days_accrued / days_in_period) · periods

    Args:
        issue:           The security's issue date.
        first_interest:  The first interest payment date.
        settlement:      The security's settlement date.
        rate:            The security's annual coupon rate.
        par:             The security's par (face) value.
        frequency:       The number of coupon payments per year (1, 2, or 4).
        basis:           Day-count convention (default 0).

    Returns:
        The accrued interest from issue to settlement.
    """
    days, year = _day_count(issue, settlement, basis)
    return par * rate * days / year


def accrintm(issue: date, settlement: date, rate: float, par: float,
             basis: int = 0) -> float:
    """
    Returns the accrued interest for a security that pays interest at maturity.

    accrintm = par · rate · days/year

    Args:
        issue:      The security's issue date.
        settlement: The security's settlement date (= maturity for this function).
        rate:       The security's annual interest rate.
        par:        The security's par (face) value.
        basis:      Day-count convention (default 0).

    Returns:
        The accrued interest from issue to settlement.
    """
    days, year = _day_count(issue, settlement, basis)
    return par * rate * days / year


def coupdaybs(settlement: date, maturity: date, frequency: int,
              basis: int = 0) -> float:
    """
    Returns the number of days from the beginning of the coupon period to
    the settlement date.

    Args:
        settlement: The security's settlement date.
        maturity:   The security's maturity date.
        frequency:  The number of coupon payments per year.
        basis:      Day-count convention (default 0).

    Returns:
        Days from the beginning of the current coupon period to settlement.
    """
    prev = _prev_coupon_date(settlement, maturity, frequency)
    return (settlement - prev).days


def coupdays(settlement: date, maturity: date, frequency: int,
             basis: int = 0) -> float:
    """
    Returns the number of days in the coupon period containing the settlement date.

    Args:
        settlement: The security's settlement date.
        maturity:   The security's maturity date.
        frequency:  The number of coupon payments per year.
        basis:      Day-count convention (default 0).

    Returns:
        The total number of days in the coupon period.
    """
    prev = _prev_coupon_date(settlement, maturity, frequency)
    nxt = _next_coupon_date(settlement, maturity, frequency)
    return (nxt - prev).days


def coupdaysnc(settlement: date, maturity: date, frequency: int,
               basis: int = 0) -> float:
    """
    Returns the number of days from the settlement date to the next coupon date.

    Args:
        settlement: The security's settlement date.
        maturity:   The security's maturity date.
        frequency:  The number of coupon payments per year.
        basis:      Day-count convention (default 0).

    Returns:
        Days from settlement to the next coupon date.
    """
    nxt = _next_coupon_date(settlement, maturity, frequency)
    return (nxt - settlement).days


def coupncd(settlement: date, maturity: date, frequency: int,
            basis: int = 0) -> date:
    """
    Returns the next coupon date after the settlement date.

    Args:
        settlement: The security's settlement date.
        maturity:   The security's maturity date.
        frequency:  The number of coupon payments per year.
        basis:      Day-count convention (default 0).

    Returns:
        The next coupon payment date as a datetime.date.
    """
    return _next_coupon_date(settlement, maturity, frequency)


def couppcd(settlement: date, maturity: date, frequency: int,
            basis: int = 0) -> date:
    """
    Returns the previous coupon date before the settlement date.

    Args:
        settlement: The security's settlement date.
        maturity:   The security's maturity date.
        frequency:  The number of coupon payments per year.
        basis:      Day-count convention (default 0).

    Returns:
        The previous coupon payment date as a datetime.date.
    """
    return _prev_coupon_date(settlement, maturity, frequency)


def coupnum(settlement: date, maturity: date, frequency: int,
            basis: int = 0) -> int:
    """
    Returns the number of coupon payments between settlement and maturity.

    Args:
        settlement: The security's settlement date.
        maturity:   The security's maturity date.
        frequency:  The number of coupon payments per year.
        basis:      Day-count convention (default 0).

    Returns:
        The number of remaining coupon periods.
    """
    return len(_coupon_periods(settlement, maturity, frequency))


# ── Private helpers ───────────────────────────────────────────────────────────

def _day_count(start: date, end: date, basis: int) -> tuple[float, float]:
    """
    Returns (days, year_basis) for the given day-count convention.

    basis 0: US 30/360
    basis 1: Actual/Actual
    basis 2: Actual/360
    basis 3: Actual/365
    basis 4: European 30/360
    """
    actual_days = (end - start).days

    if basis == 0:
        # US 30/360
        d1, m1, y1 = start.day, start.month, start.year
        d2, m2, y2 = end.day, end.month, end.year
        if d1 == 31:
            d1 = 30
        if d2 == 31 and d1 == 30:
            d2 = 30
        days = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
        return float(days), 360.0

    elif basis == 1:
        # Actual/Actual
        # Use average days in year over the period.
        year_days = 365.0
        if start.year != end.year:
            total_years = end.year - start.year
            total_days = (date(end.year, 1, 1) - date(start.year, 1, 1)).days
            year_days = total_days / total_years
        return float(actual_days), year_days

    elif basis == 2:
        return float(actual_days), 360.0

    elif basis == 3:
        return float(actual_days), 365.0

    elif basis == 4:
        # European 30/360
        d1, m1, y1 = start.day, start.month, start.year
        d2, m2, y2 = end.day, end.month, end.year
        d1 = min(d1, 30)
        d2 = min(d2, 30)
        days = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
        return float(days), 360.0

    else:
        raise ValueError(f"Unsupported basis: {basis}. Must be 0–4.")


def _months_offset(d: date, months: int) -> date:
    """Returns d shifted by a given number of months, clamping to month end."""
    m = d.month - 1 + months
    year = d.year + m // 12
    month = m % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
                       else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def _coupon_periods(settlement: date, maturity: date, frequency: int) -> list:
    """Returns a list of coupon dates from settlement to maturity."""
    months_per_period = 12 // frequency
    periods = []
    d = maturity
    while d > settlement:
        periods.append(d)
        d = _months_offset(d, -months_per_period)
    periods.reverse()
    return periods


def _next_coupon_date(settlement: date, maturity: date, frequency: int) -> date:
    """Returns the first coupon date strictly after settlement."""
    for d in _coupon_periods(settlement, maturity, frequency):
        if d > settlement:
            return d
    return maturity


def _prev_coupon_date(settlement: date, maturity: date, frequency: int) -> date:
    """Returns the last coupon date on or before settlement."""
    prev = None
    for d in _coupon_periods(settlement, maturity, frequency):
        if d <= settlement:
            prev = d
        else:
            break
    return prev if prev else settlement
