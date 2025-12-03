import functools
import re
import statistics
from datetime import date, datetime

import numpy_financial as npf
import numpy as np
from dateutil import parser
from scipy import optimize, stats
import calendar



from datetime import date
from datetime import datetime
from dateutil import parser
import calendar


def generate_dates_from_rows(rows):
    """
    Converts row elements into datetime.date objects.

    Supports:
      - Standard date strings (for example '2024-03-31')
      - Quarter formats (for example '2024-Q1' or '2024Q1')
        -> mapped to the last day of the quarter:
           Q1 -> 31 Mar, Q2 -> 30 Jun, Q3 -> 30 Sep, Q4 -> 31 Dec
      - YearMonth formats (for example '2024-01' or '202401')
        -> mapped to the last day of that month
    """
    dates = []

    for row in rows:
        # Support both raw strings and rows with the date in the last column
        if isinstance(row, (list, tuple)):
            raw_value = row[-1]
        else:
            raw_value = row

        element = str(raw_value).strip()

        if not element:
            raise ValueError(f"Empty date value in row: {row!r}")

        upper = element.upper()

        # --- Handle Quarter formats first: 'YYYY-Q1', 'YYYYQ1' ---
        if "Q" in upper:
            try:
                cleaned = upper.replace("-", "").replace(" ", "")
                # Expect something like '2025Q1'
                if len(cleaned) >= 6 and cleaned[4] == "Q":
                    year = int(cleaned[:4])
                    q = int(cleaned[5:])  # supports 'Q1' (and weird 'Q01', but fine)
                    if 1 <= q <= 4:
                        # End of quarter: Q1 -> Mar, Q2 -> Jun, Q3 -> Sep, Q4 -> Dec
                        month = q * 3
                        last_day = calendar.monthrange(year, month)[1]
                        dates.append(date(year, month, last_day))
                        continue
            except ValueError:
                # Fall through to other handlers
                pass

        # --- Handle YearMonth formats: 'YYYYMM' or 'YYYY-MM' ---
        # Only 6 digits -> year-month, not a full date
        digits = "".join(ch for ch in element if ch.isdigit())
        if len(digits) == 6:
            try:
                year = int(digits[:4])
                month = int(digits[4:6])
                if 1 <= month <= 12:
                    last_day = calendar.monthrange(year, month)[1]
                    dates.append(date(year, month, last_day))
                    continue
            except ValueError:
                # Fall through to generic parsing
                pass

        # --- Fallback: full date parsing ---
        try:
            dt = parser.parse(element, fuzzy=False)
            dates.append(dt.date())
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Unrecognized date format: {element!r}") from exc

    return dates


def tm1_io(func):
    """Higher Order Function to read values from source and write result to target view"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # read values from view
        if (
            "tm1_services" in kwargs
            and "tm1_source" in kwargs
            and "cube_source" in kwargs
            and "view_source" in kwargs
        ):
            tm1 = kwargs["tm1_services"][kwargs["tm1_source"]]
            if "values" not in kwargs:
                rows_and_values = tm1.cubes.cells.execute_view_rows_and_values(
                    cube_name=kwargs["cube_source"],
                    view_name=kwargs["view_source"],
                    private=False,
                    element_unique_names=False,
                )
                kwargs["values"] = [
                    values_by_row[0] for values_by_row in rows_and_values.values()
                ]
                kwargs["dates"] = generate_dates_from_rows(rows_and_values.keys())
        result = func(*args, **kwargs)
        # write result to source view
        if (
            "tm1_services" in kwargs
            and "tm1_target" in kwargs
            and "cube_target" in kwargs
            and "view_target" in kwargs
        ):
            tm1 = kwargs["tm1_services"][kwargs["tm1_target"]]
            mdx = tm1.cubes.views.get(
                cube_name=kwargs["cube_target"],
                view_name=kwargs["view_target"],
                private=False,
            ).MDX
            tm1.cubes.cells.write_values_through_cellset(mdx=mdx, values=(result,))
        return result

    return wrapper


def tm1_tidy(func):
    """Higher Order Function to delete source view and target view (if param tidy is set to true)"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            if "tm1_services" in kwargs and kwargs.get("tidy", False) in (
                "True",
                "true",
                "TRUE",
                "1",
                1,
            ):
                # delete source view
                if (
                    "tm1_source" in kwargs
                    and "cube_source" in kwargs
                    and "view_source" in kwargs
                ):
                    tm1 = kwargs["tm1_services"][kwargs["tm1_source"]]
                    tm1.cubes.views.delete(
                        cube_name=kwargs["cube_source"],
                        view_name=kwargs["view_source"],
                        private=False,
                    )
                # delete target view
                if (
                    kwargs
                    and "tm1_target" in kwargs
                    and "cube_target" in kwargs
                    and "view_target" in kwargs
                ):
                    tm1 = kwargs["tm1_services"][kwargs["tm1_target"]]
                    tm1.cubes.views.delete(
                        cube_name=kwargs["cube_target"],
                        view_name=kwargs["view_target"],
                        private=False,
                    )

    return wrapper


def _nroot(value, n):
    """
    Returns the nth root of the given value.
    """
    return value ** (1.0 / n)


@tm1_tidy
@tm1_io
def irr(values, *args, **kwargs):
    return npf.irr(values=values)


@tm1_tidy
@tm1_io
def npv(rate, values, *args, **kwargs):
    return npf.npv(rate=float(rate), values=list(values))


@tm1_tidy
@tm1_io
def stdev(values, *args, **kwargs):
    return np.std(values)


@tm1_tidy
@tm1_io
def stdev_p(values, *args, **kwargs):
    return np.std(values, ddof=1)


@tm1_tidy
@tm1_io
def fv(rate, nper, pmt, pv, when=0, *args, **kwargs):
    """Calculates the future value

    :param rate: Rate of interest as decimal (not per cent) per period
    :param nper: Number of compounding periods
    :param pmt: Payment
    :param pv: Present Value
    :param when: 0 or 1. When the payment is made (Default: the payment is made at the end of the period)
    :param args:
    :param kwargs:
    :return:
    """
    return npf.fv(
        rate=float(rate), nper=float(nper), pmt=float(pmt), pv=float(pv), when=int(when)
    )


@tm1_tidy
@tm1_io
def fv_schedule(principal, values, *args, **kwargs):
    """The future value with the variable interest rate

    :param principal: Principal is the present value of a particular investment
    :param values: A series of interest rate
    :return:
    """
    return functools.reduce(lambda x, y: x + (x * y), values, float(principal))


@tm1_tidy
@tm1_io
def pv(rate, nper, pmt, fv, when=0, *args, **kwargs):
    """Calculate the Present Value

    :param rate: It is the interest rate/period
    :param nper: Number of periods
    :param pmt: Payment/period
    :param fv: Future Value
    :param when: 0 or 1. When the payment is made (Default: the payment is made at the end of the period)
    :return:
    """
    return npf.pv(
        rate=float(rate), nper=float(nper), pmt=float(pmt), fv=float(fv), when=int(when)
    )


@tm1_tidy
@tm1_io
def xnpv(rate, values, dates, *args, **kwargs):
    """Calculates the Net Present Value for a schedule of cash flows that is not necessarily periodic

    :param rate: Discount rate for a period
    :param values: Positive or negative cash flows
    :param dates: Specific dates
    :return:
    """
    rate = float(rate)
    if len(values) != len(dates):
        raise ValueError("values and dates must be the same length")
    if sorted(dates) != dates:
        raise ValueError("dates must be in chronological order")
    first_date = dates[0]
    return sum(
        [
            value / ((1 + rate) ** ((date - first_date).days / 365.0))
            for (value, date) in zip(values, dates)
        ]
    )


@tm1_tidy
@tm1_io
def pmt(rate, nper, pv, fv=0, when=0, *args, **kwargs):
    """PMT denotes the periodical payment required to pay off for a particular period of time with a constant interest rate

    :param rate: Interest rate/period
    :param nper: Number of periods
    :param pv: Present Value
    :param fv: Future Value, if not assigned 0 is assumed
    :param when: 0 or 1. When the payment is made (Default: the payment is made at the end of the period)
    :return:
    """
    return npf.pmt(
        rate=float(rate), nper=float(nper), pv=float(pv), fv=float(fv), when=int(when)
    )


@tm1_tidy
@tm1_io
def ppmt(rate, per, nper, pv, fv=0, when=0, *args, **kwargs):
    """calculates payment on principal with a constant interest rate and constant periodic payments

    :param rate: Interest rate/period
    :param per: The period for which the principal is to be calculated
    :param nper: Number of periods
    :param pv: Present Value
    :param fv: Future Value, if not assigned 0 is assumed
    :param when: 0 or 1. When the payment is made (Default: the payment is made at the end of the period)
    :return:
    """
    return npf.ppmt(
        rate=float(rate),
        per=float(per),
        nper=float(nper),
        pv=float(pv),
        fv=float(fv),
        when=int(when),
    )


@tm1_tidy
@tm1_io
def mirr(values, finance_rate, reinvest_rate, *args, **kwargs):
    """MIRR is calculated by assuming NPV as zero

    :param values: Positive or negative cash flows
    :param finance_rate: Interest rate paid for the money used in cash flows
    :param reinvest_rate: Interest rate paid for reinvestment of cash flows
    :return:
    """
    return npf.mirr(
        values=values,
        finance_rate=float(finance_rate),
        reinvest_rate=float(reinvest_rate),
    )


@tm1_tidy
@tm1_io
def xirr(values, dates, guess=0.1, *args, **kwargs):
    """Returns the internal rate of return for a schedule of cash flows that is not necessarily periodic.

    :param values: Positive or negative cash flows
    :param dates: Specific dates
    :param guess: An assumption of what you think IRR should be
    :return:
    """
    return optimize.newton(lambda r: xnpv(r, values, dates), float(guess))


@tm1_tidy
@tm1_io
def nper(rate, pmt, pv, fv=0, when=0, *args, **kwargs):
    """Number of periods one requires to pay off the loan

    :param rate: Interest rate/period
    :param pmt: Amount paid per period
    :param pv: Present Value
    :param fv: Future Value, if not assigned 0 is assumed
    :param when: 0 or 1. When the payment is made (Default: the payment is made at the end of the period)
    :return:
    """
    return npf.nper(
        rate=float(rate), pmt=float(pmt), pv=float(pv), fv=float(fv), when=int(when)
    ).item(0)


@tm1_tidy
@tm1_io
def rate(nper, pmt, pv, fv=0, when=0, guess=0.1, maxiter=100, *args, **kwargs):
    """The interest rate needed to pay off the loan in full for a given period of time

    :param nper: Number of periods
    :param pmt: Amount paid per period
    :param pv: Present Value
    :param fv: Future Value, if not assigned 0 is assumed
    :param when: 0 or 1. When the payment is made (Default: the payment is made at the end of the period)
    :param guess: An assumption of what you think the rate should be
    :param maxiter: maximum number of iterations
    :return:
    """
    return npf.rate(
        nper=float(nper),
        pmt=float(pmt),
        pv=float(pv),
        fv=float(fv),
        when=int(when),
        guess=float(guess),
        maxiter=int(maxiter),
    )


@tm1_tidy
@tm1_io
def effect(nominal_rate, npery, *args, **kwargs):
    """Returns the effective annual interest rate, given the nominal annual interest rate
    and the number of compounding periods per year.

    :param nominal_rate: Nominal Interest Rate
    :param npery: Number of compounding per year
    :return:
    """
    nominal_rate, npery = float(nominal_rate), float(npery)
    return ((1 + (nominal_rate / npery)) ** npery) - 1


@tm1_tidy
@tm1_io
def nominal(effect_rate, npery, *args, **kwargs):
    """Returns the nominal annual interest rate, given the effective rate and the number of compounding periods per year.

    :param effect_rate: Effective annual interest rate
    :param npery: Number of compounding per year
    :return:
    """
    effect_rate, npery = float(effect_rate), float(npery)
    return (_nroot(effect_rate + 1, npery) - 1) * npery


@tm1_tidy
@tm1_io
def sln(cost, salvage, life, *args, **kwargs):
    """Returns the straight-line depreciation of an asset for one period.

    :param cost: Cost of asset when bought (initial amount)
    :param salvage: Value of asset after depreciation
    :param life: Number of periods over which the asset is being depreciated
    :return:
    """
    return (float(cost) - float(salvage)) / float(life)


@tm1_tidy
@tm1_io
def mean(values, *args, **kwargs):
    return statistics.mean(values)


@tm1_tidy
@tm1_io
def sem(values, *args, **kwargs):
    """
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.sem.html
    :return:
    """
    return stats.sem(values)


@tm1_tidy
@tm1_io
def median(values, *args, **kwargs):
    return statistics.median(values)


@tm1_tidy
@tm1_io
def mode(values, *args, **kwargs):
    """
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mode.html
    :param values:
    :return:
    """
    return stats.mode(values)[0][0]


@tm1_tidy
@tm1_io
def var(values, *args, **kwargs):
    return np.var(values)


@tm1_tidy
@tm1_io
def var_p(values, *args, **kwargs):
    return np.var(values, ddof=1)


@tm1_tidy
@tm1_io
def kurt(values, *args, **kwargs):
    """
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html
    :param values:
    :return:
    """
    return stats.kurtosis(values)


@tm1_tidy
@tm1_io
def skew(values, *args, **kwargs):
    """
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html
    :param values:
    :return:
    """
    return stats.skew(values)


@tm1_tidy
@tm1_io
def rng(values, *args, **kwargs):
    return max(values) - min(values)


@tm1_tidy
@tm1_io
def min_(values, *args, **kwargs):
    return min(values)


@tm1_tidy
@tm1_io
def max_(values, *args, **kwargs):
    return max(values)


@tm1_tidy
@tm1_io
def sum_(values, *args, **kwargs):
    return sum(values)


@tm1_tidy
@tm1_io
def count(values, *args, **kwargs):
    return len(set(values))
