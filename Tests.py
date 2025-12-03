import configparser
import os
import unittest
from datetime import date
from dateutil.relativedelta import relativedelta

from TM1py import (
    TM1Service,
    Dimension,
    Hierarchy,
    Element,
    Cube,
    NativeView,
    AnonymousSubset,
    MDXView,
)

from methods import (
    irr,
    npv,
    stdev,
    stdev_p,
    fv,
    fv_schedule,
    pv,
    xnpv,
    pmt,
    ppmt,
    mirr,
    xirr,
    nper,
    rate,
    effect,
    nominal,
    sln,
    mean,
    sem,
    median,
    mode,
    var,
    rng,
    count,
    skew,
    var_p,
    kurt,
    generate_dates_from_rows,
)

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.ini"))

MDX_TEMPLATE = """
SELECT 
{rows} ON ROWS,
{columns} ON COLUMNS
FROM {cube}
WHERE {where}
"""

MDX_TEMPLATE_SHORT = """
SELECT 
{rows} ON ROWS,
{columns} ON COLUMNS
FROM {cube}
"""

PREFIX = "CubeCalc_Tests_"

CUBE_NAME_SOURCE = PREFIX + "Cube_Source"
CUBE_NAME_TARGET = PREFIX + "Cube_Target"
DIMENSION_NAMES = [
    PREFIX + "Dimension1",
    PREFIX + "Dimension2"
]
VIEW_NAME_SOURCE = PREFIX + "View_Source"
VIEW_NAME_TARGET = PREFIX + "View_Target"

IRR_INPUT_VALUES = (-100000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000)
IRR_EXPECTED_RESULT = 0.0162313281744622
IRR_TOLERANCE = 0.00001

NPV_INPUT_RATE = 0.02
NPV_INPUT_VALUES = IRR_INPUT_VALUES
NPV_EXPECTED_RESULT = -2089.72504573015
NPV_TOLERANCE = 50

FV_INPUT_RATE = 0.1
FV_INPUT_NPER = 3
FV_INPUT_PMT = 1
FV_INPUT_PV = -100
FV_INPUT_WHEN = 0
FV_EXPECTED_RESULT = 129.79
FV_TOLERANCE = 0.00001

FV_SCHEDULE_PRINCIPLE = 100
FV_SCHEDULE_SCHEDULE = (0.04, 0.06, 0.05)
FV_SCHEDULE_EXPECTED_RESULT = 115.752

PV_INPUT_RATE = 0.1
PV_INPUT_NPER = 3
PV_INPUT_PMT = 1
PV_INPUT_FV = -100
PV_INPUT_WHEN = 0
PV_EXPECTED_RESULT = 72.6446280991735
PV_TOLERANCE = 0.00001

XNPV_INPUT_RATE = 0.05
XNPV_INPUT_VALUES = [-1000, 300, 400, 400, 300]
XNPV_INPUT_DATES = [date(2011, 12, 1), date(2012, 1, 1), date(2013, 2, 1), date(2014, 3, 1), date(2015, 4, 1)]
XNPV_EXPECTED_RESULT = 289.901722604195
XNPV_TOLERANCE = 0.00001

PMT_INPUT_RATE = 0.1
PMT_INPUT_NPER = 3
PMT_INPUT_PV = 1000
PMT_EXPECTED_RESULT = -402.1148036253
PMT_TOLERANCE = 0.00001

PPMT_INPUT_RATE = 0.1
PPMT_INPUT_PER = 2
PPMT_INPUT_NPER = 3
PPMT_INPUT_PV = 1000
PPMT_EXPECTED_RESULT = -332.32628398791
PPMT_TOLERANCE = 0.00001

MIRR_INPUT_VALUES = [-1000, 300, 400, 400, 300]
MIRR_INPUT_FINANCE_RATE = 0.12
MIRR_INPUT_REINVEST_RATE = 0.1
MIRR_EXPECTED_RESULT = 0.12875502614825
MIRR_TOLERANCE = 0.00001

XIRR_INPUT_VALUES = [-1000, 300, 400, 400, 300]
XIRR_INPUT_DATES = [date(2011, 12, 1), date(2012, 1, 1), date(2013, 2, 1), date(2014, 3, 1), date(2015, 4, 1)]
XIRR_EXPECTED_RESULT = 0.23860325587217
XIRR_TOLERANCE = 0.00001

NPER_INPUT_RATE = 0.1
NPER_INPUT_PMT = -200
NPER_INPUT_PV = 1000
NPER_EXPECTED_RESULT = 7.272540897341
NPER_TOLERANCE = 0.00001

RATE_INPUT_NPER = 6
RATE_INPUT_PMT = -200
RATE_INPUT_PV = 1000
RATE_EXPECTED_RESULT = 0.054717925023
RATE_TOLERANCE = 0.00001

EFFECT_INPUT_NOMINAL_RATE = 0.12
EFFECT_INPUT_NPERY = 12
EFFECT_EXPECTED_RESULT = 0.12682503013196
EFFECT_TOLERANCE = 0.00001

NOMINAL_INPUT_EFFECT_RATE = 0.12
NOMINAL_INPUT_NPERY = 12
NOMINAL_EXPECTED_RESULT = 0.11386551521
NOMINAL_TOLERANCE = 0.00001

SLN_INPUT_COST = 5000
SLN_INPUT_SALVAGE = 300
SLN_INPUT_LIFE = 10
SLN_EXPECTED_RESULT = 470
SLN_TOLERANCE = 0.00001

MEAN_VALUES = [1, 2, 3, 4, 5]
MEAN_EXPECTED_RESULT = 3

SEM_VALUES = [1, 2, 3, 4, 5]
SEM_EXPECTED_RESULT = 0.707106781
SEM_TOLERANCE = 0.00001

MEDIAN_VALUES = [1, 2, 3, 4, 5]
MEDIAN_EXPECTED_RESULT = 3

MODE_VALUES = [1, 1, 2, 3, 4, 5]
MODE_EXPECTED_RESULT = 1

VAR_VALUES = [1, 2, 3, 4, 5]
VAR_EXPECTED_RESULT = 2
VAR_P_EXPECTED_RESULT = 2.5

KURTOSIS_VALUES = [1, 2, 3, 4, 5]
KURTOSIS_EXPECTED_RESULT = -1.3

SKEWNESS_VALUES = [1, 2, 3, 4, 5]
SKEWNESS_EXPECTED_RESULT = 0

RNG_VALUES = [1, 2, 3, 4, 5]
RNG_EXPECTED_RESULT = 4

COUNT_VALUES = [1, 2, 3, 4, 5]
COUNT_EXPECTED_RESULT = 5

STDEV_INPUT_VALUES = (1, 2, 3, 4, 5, 6, 7, 8, 9)
STDEV_EXPECTED_RESULT = 2.58198889747161
STDEV_P_EXPECTED_RESULT = 2.73861278752583
STDEV_TOLERANCE = 0.00001





class TestUtils(unittest.TestCase):

    def test_generate_dates_from_rows_quarters(self):
        dates = generate_dates_from_rows(["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1"])
        expected_dates = [
            date(2025, 3, 31),
            date(2025, 6, 30),
            date(2025, 9, 30),
            date(2025, 12, 31),
            date(2026, 3, 31)
        ]
        self.assertEqual(expected_dates, dates)


    def test_generate_dates_from_rows_moths(self):
        dates = generate_dates_from_rows(["2025-01", "2025-02", "2025-03", "2025-04", "2026-05"])
        expected_dates = [
            date(2025, 1, 31),
            date(2025, 2, 28),
            date(2025, 3, 31),
            date(2025, 4, 30),
            date(2026, 5, 31),
        ]
        self.assertEqual(expected_dates, dates)

    def test_generate_dates_from_rows_dates(self):
        dates = generate_dates_from_rows(
            ["2025-01-31", "2025-02-12", "2025-03-8", "2025-04-15", "2026-05-24"]
        )
        expected_dates = [
            date(2025, 1, 31),
            date(2025, 2, 12),
            date(2025, 3, 8),
            date(2025, 4, 15),
            date(2026, 5, 24),
        ]
        self.assertEqual(expected_dates, dates)

    def test_generate_dates_from_rows_invalid(self):
        with self.assertRaises(ValueError):
            generate_dates_from_rows(
                ["2025-01-31", "2025-02-12", "2025-03-8", "2025-04-15", "2026-05-42"]
            )


class TestMethods(unittest.TestCase):

    def test_irr(self):
        result = irr(values=IRR_INPUT_VALUES)
        self.assertAlmostEqual(result, IRR_EXPECTED_RESULT, delta=IRR_TOLERANCE)

    def test_npv(self):
        result = npv(values=IRR_INPUT_VALUES, rate=NPV_INPUT_RATE)
        self.assertAlmostEqual(result, NPV_EXPECTED_RESULT, delta=NPV_TOLERANCE)

    def test_stdev(self):
        result = stdev(values=STDEV_INPUT_VALUES)
        self.assertAlmostEqual(result, STDEV_EXPECTED_RESULT, delta=STDEV_TOLERANCE)

    def test_stdev_p(self):
        result = stdev_p(values=STDEV_INPUT_VALUES)
        self.assertAlmostEqual(result, STDEV_P_EXPECTED_RESULT, delta=STDEV_TOLERANCE)

    def test_fv(self):
        result = fv(rate=FV_INPUT_RATE, nper=FV_INPUT_NPER, pmt=FV_INPUT_PMT, pv=FV_INPUT_PV, when=FV_INPUT_WHEN)
        self.assertAlmostEqual(result, FV_EXPECTED_RESULT, delta=FV_TOLERANCE)

    def test_fv_schedule(self):
        result = fv_schedule(principal=FV_SCHEDULE_PRINCIPLE, values=FV_SCHEDULE_SCHEDULE)
        self.assertEqual(result, FV_SCHEDULE_EXPECTED_RESULT)

    def test_pv(self):
        result = pv(rate=PV_INPUT_RATE, nper=PV_INPUT_NPER, pmt=PV_INPUT_PMT, fv=PV_INPUT_FV, when=PV_INPUT_WHEN)
        self.assertAlmostEqual(result, PV_EXPECTED_RESULT, delta=PV_TOLERANCE)

    def test_xnpv(self):
        result = xnpv(rate=XNPV_INPUT_RATE, values=XNPV_INPUT_VALUES, dates=XNPV_INPUT_DATES)
        self.assertAlmostEqual(result, XNPV_EXPECTED_RESULT, delta=XNPV_TOLERANCE)

    def test_pmt(self):
        result = pmt(rate=PMT_INPUT_RATE, nper=PMT_INPUT_NPER, pv=PMT_INPUT_PV)
        self.assertAlmostEqual(result, PMT_EXPECTED_RESULT, delta=PMT_TOLERANCE)

    def test_ppmt(self):
        result = ppmt(rate=PPMT_INPUT_RATE, per=PPMT_INPUT_PER, nper=PPMT_INPUT_NPER, pv=PPMT_INPUT_PV)
        self.assertAlmostEqual(result, PPMT_EXPECTED_RESULT, delta=PPMT_TOLERANCE)

    def test_mirr(self):
        result = mirr(
            values=MIRR_INPUT_VALUES,
            finance_rate=MIRR_INPUT_FINANCE_RATE,
            reinvest_rate=MIRR_INPUT_REINVEST_RATE)
        print(result)
        self.assertAlmostEqual(result, MIRR_EXPECTED_RESULT, delta=MIRR_TOLERANCE)

    def test_xirr(self):
        result = xirr(
            values=XIRR_INPUT_VALUES,
            dates=XIRR_INPUT_DATES)
        self.assertAlmostEqual(result, XIRR_EXPECTED_RESULT, delta=XIRR_TOLERANCE)

    def test_nper(self):
        result = nper(
            rate=NPER_INPUT_RATE,
            pmt=NPER_INPUT_PMT,
            pv=NPER_INPUT_PV)
        self.assertAlmostEqual(result, NPER_EXPECTED_RESULT, delta=NPER_TOLERANCE)

    def test_rate(self):
        result = rate(
            nper=RATE_INPUT_NPER,
            pmt=RATE_INPUT_PMT,
            pv=RATE_INPUT_PV)
        self.assertAlmostEqual(result, RATE_EXPECTED_RESULT, delta=RATE_TOLERANCE)

    def test_effect(self):
        result = effect(nominal_rate=EFFECT_INPUT_NOMINAL_RATE, npery=EFFECT_INPUT_NPERY)
        self.assertAlmostEqual(result, EFFECT_EXPECTED_RESULT, delta=EFFECT_TOLERANCE)

    def test_nominal(self):
        result = nominal(effect_rate=NOMINAL_INPUT_EFFECT_RATE, npery=NOMINAL_INPUT_NPERY)
        self.assertAlmostEqual(result, NOMINAL_EXPECTED_RESULT, delta=NOMINAL_TOLERANCE)

    def test_sln(self):
        result = sln(
            cost=SLN_INPUT_COST,
            salvage=SLN_INPUT_SALVAGE,
            life=SLN_INPUT_LIFE)
        self.assertAlmostEqual(result, SLN_EXPECTED_RESULT, delta=SLN_TOLERANCE)

    def test_mean(self):
        result = mean(values=[1, 2, 3, 4, 5])
        self.assertEqual(result, 3)

    def test_sem(self):
        result = sem(SEM_VALUES)
        self.assertAlmostEqual(result, SEM_EXPECTED_RESULT, delta=SEM_TOLERANCE)

    def test_median(self):
        result = median(MEDIAN_VALUES)
        self.assertEqual(result, MEDIAN_EXPECTED_RESULT)

    def test_mode(self):
        result = mode(MODE_VALUES)
        self.assertEqual(result, MODE_EXPECTED_RESULT)

    def test_var(self):
        result = var(VAR_VALUES)
        self.assertEqual(result, VAR_EXPECTED_RESULT)

    def test_var_p(self):
        result = var_p(VAR_VALUES)
        self.assertEqual(result, VAR_P_EXPECTED_RESULT)

    def test_kurt(self):
        result = kurt(KURTOSIS_VALUES)
        self.assertEqual(result, KURTOSIS_EXPECTED_RESULT)

    def test_skew(self):
        result = skew(SKEWNESS_VALUES)
        self.assertEqual(result, SKEWNESS_EXPECTED_RESULT)

    def test_rng(self):
        result = rng(RNG_VALUES)
        self.assertEqual(result, RNG_EXPECTED_RESULT)

    def test_count(self):
        result = count(COUNT_VALUES)
        self.assertEqual(result, COUNT_EXPECTED_RESULT)


class TestDecorators(unittest.TestCase):
    tm1 = TM1Service(**config["tm1srv01"])

    @classmethod
    def setUpClass(cls):
        start_date = date.today().replace(day=1)

        cls.dimension1 = Dimension(
            name=DIMENSION_NAMES[0],
            hierarchies=[
                Hierarchy(
                    name=DIMENSION_NAMES[0],
                    dimension_name=DIMENSION_NAMES[0],
                    elements=[
                        Element((start_date + relativedelta(months=i)).strftime("%Y-%m"), "Numeric")
                        for i
                        in range(100)])])
        cls.dimension2 = Dimension(
            name=DIMENSION_NAMES[1],
            hierarchies=[
                Hierarchy(
                    name=DIMENSION_NAMES[1],
                    dimension_name=DIMENSION_NAMES[1],
                    elements=[Element(name="Element_{}".format(i), element_type="Numeric") for i in range(1, 101)])])
        cls.cube_source = Cube(
            name=CUBE_NAME_SOURCE,
            dimensions=DIMENSION_NAMES)
        cls.cube_target = Cube(
            name=CUBE_NAME_TARGET,
            dimensions=DIMENSION_NAMES)

    @classmethod
    def tearDownClass(cls):
        cls.tm1.logout()

    def setUp(self):
        if not self.tm1.dimensions.exists(dimension_name=self.dimension1.name):
            self.tm1.dimensions.update_or_create(dimension=self.dimension1)
        if not self.tm1.dimensions.exists(dimension_name=self.dimension2.name):
            self.tm1.dimensions.update_or_create(dimension=self.dimension2)
        if not self.tm1.cubes.exists(cube_name=self.cube_source.name):
            self.tm1.cubes.update_or_create(cube=self.cube_source)
        if not self.tm1.cubes.exists(cube_name=self.cube_target.name):
            self.tm1.cubes.update_or_create(cube=self.cube_target)

    def tearDown(self):
        self.tm1.cubes.delete(cube_name=self.cube_source.name)
        self.tm1.cubes.delete(cube_name=self.cube_target.name)
        self.tm1.dimensions.delete(dimension_name=self.dimension1.name)
        self.tm1.dimensions.delete(dimension_name=self.dimension2.name)

    def test_tm1io_input_nativeview_output_nativeview(self):
        # create input view
        view_input = NativeView(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view_input.add_row(
            dimension_name=DIMENSION_NAMES[0],
            subset=AnonymousSubset(
                dimension_name=DIMENSION_NAMES[0],
                expression="{ HEAD ( { [" + DIMENSION_NAMES[0] + "].Members}," + str(len(IRR_INPUT_VALUES)) + ") }"))
        view_input.add_column(
            dimension_name=DIMENSION_NAMES[1],
            subset=AnonymousSubset(
                dimension_name=DIMENSION_NAMES[1],
                expression="{[" + DIMENSION_NAMES[1] + "].[Element_1]}"))
        self.tm1.cubes.views.update_or_create(
            view=view_input,
            private=False)
        # create output view
        view_output = NativeView(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view_output.add_row(
            dimension_name=DIMENSION_NAMES[0],
            subset=AnonymousSubset(
                dimension_name=DIMENSION_NAMES[0],
                expression="{[" + DIMENSION_NAMES[0] + "].DefaultMember}"))
        view_output.add_column(
            dimension_name=DIMENSION_NAMES[1],
            subset=AnonymousSubset(
                dimension_name=DIMENSION_NAMES[1],
                expression="{[" + DIMENSION_NAMES[1] + "].[Element_1]}"))
        self.tm1.cubes.views.update_or_create(
            view=view_output,
            private=False)
        # write values into input view
        mdx = view_input.MDX
        self.tm1.cubes.cells.write_values_through_cellset(mdx, IRR_INPUT_VALUES)
        # execute method
        result = irr(
            tm1_services={"tm1srv01": self.tm1, "tm1srv02": self.tm1},
            tm1_source="tm1srv01",
            tm1_target="tm1srv02",
            cube_source=CUBE_NAME_SOURCE,
            cube_target=CUBE_NAME_TARGET,
            view_source=VIEW_NAME_SOURCE,
            view_target=VIEW_NAME_TARGET)
        self.assertAlmostEqual(IRR_EXPECTED_RESULT, result, delta=IRR_TOLERANCE)
        # check output view
        cell_value = self.tm1.cubes.cells.execute_view_values(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            private=False)[0]
        self.assertAlmostEqual(cell_value, IRR_EXPECTED_RESULT, delta=IRR_TOLERANCE)

    def test_tm1io_input_mdx_view_output_mdx_view(self):
        # create input view
        mdx_input = MDX_TEMPLATE_SHORT.format(
            rows="{ HEAD ( { [" + DIMENSION_NAMES[0] + "].Members}," + str(len(STDEV_INPUT_VALUES)) + ") }",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_SOURCE)
        view_input = MDXView(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            MDX=mdx_input)
        self.tm1.cubes.views.update_or_create(
            view=view_input,
            private=False)
        # create output view
        mdx_output = MDX_TEMPLATE_SHORT.format(
            rows="{[" + DIMENSION_NAMES[0] + "].DefaultMember}",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_TARGET)
        view_output = MDXView(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            MDX=mdx_output)
        self.tm1.cubes.views.update_or_create(
            view=view_output,
            private=False)
        # write values into input view
        mdx = view_input.MDX
        self.tm1.cubes.cells.write_values_through_cellset(mdx, STDEV_INPUT_VALUES)
        # execute method
        result = stdev(
            tm1_services={"tm1srv01": self.tm1, "tm1srv02": self.tm1},
            tm1_source="tm1srv01",
            tm1_target="tm1srv02",
            cube_source=CUBE_NAME_SOURCE,
            cube_target=CUBE_NAME_TARGET,
            view_source=VIEW_NAME_SOURCE,
            view_target=VIEW_NAME_TARGET)
        self.assertAlmostEqual(STDEV_EXPECTED_RESULT, result, delta=STDEV_TOLERANCE)
        # check output view
        cell_value = self.tm1.cubes.cells.execute_view_values(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            private=False)[0]
        self.assertAlmostEqual(cell_value, STDEV_EXPECTED_RESULT, delta=STDEV_TOLERANCE)

    def test_tm1io_input_view(self):
        # define input view and output view
        mdx_input = MDX_TEMPLATE_SHORT.format(
            rows="{ HEAD ( { [" + DIMENSION_NAMES[0] + "].Members}," + str(len(IRR_INPUT_VALUES)) + ") }",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_SOURCE)
        view_input = MDXView(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            MDX=mdx_input)
        self.tm1.cubes.views.update_or_create(
            view=view_input,
            private=False)
        # write values into input view
        mdx = view_input.MDX
        self.tm1.cubes.cells.write_values_through_cellset(mdx, IRR_INPUT_VALUES)
        # execute method
        result = irr(
            tm1_services={"tm1srv01": self.tm1, "tm1srv02": self.tm1},
            tm1_source="tm1srv01",
            cube_source=CUBE_NAME_SOURCE,
            view_source=VIEW_NAME_SOURCE)
        self.assertAlmostEqual(IRR_EXPECTED_RESULT, result, delta=IRR_TOLERANCE)

    def test_tm1io_input_values_output_view(self):
        # define output view
        mdx_output = MDX_TEMPLATE_SHORT.format(
            rows="{[" + DIMENSION_NAMES[0] + "].DefaultMember}",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_TARGET)
        view_output = MDXView(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            MDX=mdx_output)
        self.tm1.cubes.views.update_or_create(
            view=view_output,
            private=False)
        # execute method
        stdev_p(
            tm1_services={"tm1srv01": self.tm1},
            tm1_target="tm1srv01",
            cube_target=CUBE_NAME_TARGET,
            view_target=VIEW_NAME_TARGET,
            values=STDEV_INPUT_VALUES,
            tidy=False)
        # do check
        result = self.tm1.cubes.cells.execute_view_values(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            private=False
        )[0]
        self.assertAlmostEqual(result, STDEV_P_EXPECTED_RESULT, delta=STDEV_TOLERANCE)

    def test_tm1tidy_true_input_view_output_view(self):
        # create source_view
        mdx_input = MDX_TEMPLATE_SHORT.format(
            rows="{ HEAD ( { [" + DIMENSION_NAMES[0] + "].Members}," + str(len(STDEV_INPUT_VALUES)) + ") }",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_SOURCE)
        view_input = MDXView(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            MDX=mdx_input)
        self.tm1.cubes.views.update_or_create(
            view=view_input,
            private=False)
        # create target_view
        mdx_output = MDX_TEMPLATE_SHORT.format(
            rows="{[" + DIMENSION_NAMES[0] + "].DefaultMember}",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_TARGET)
        view_output = MDXView(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            MDX=mdx_output)
        self.tm1.cubes.views.update_or_create(
            view=view_output,
            private=False)
        # write values into input view
        mdx = view_input.MDX
        self.tm1.cubes.cells.write_values_through_cellset(mdx, STDEV_INPUT_VALUES)
        # execute method
        stdev(
            tm1_services={"tm1srv01": self.tm1, "tm1srv02": self.tm1},
            tm1_source="tm1srv01",
            tm1_target="tm1srv02",
            cube_source=CUBE_NAME_SOURCE,
            cube_target=CUBE_NAME_TARGET,
            view_source=VIEW_NAME_SOURCE,
            view_target=VIEW_NAME_TARGET,
            tidy=True)
        # check existence
        self.assertFalse(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            private=False))
        self.assertFalse(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            private=False))

    def test_tm1tidy_false_input_view_output_view(self):
        # define input view
        mdx_input = MDX_TEMPLATE_SHORT.format(
            rows="{ HEAD ( { [" + DIMENSION_NAMES[0] + "].Members}," + str(len(STDEV_INPUT_VALUES)) + ") }",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_SOURCE)
        view_input = MDXView(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            MDX=mdx_input)
        self.tm1.cubes.views.update_or_create(
            view=view_input,
            private=False)
        # define output view
        mdx_output = MDX_TEMPLATE_SHORT.format(
            rows="{[" + DIMENSION_NAMES[0] + "].DefaultMember}",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_TARGET)
        view_output = MDXView(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            MDX=mdx_output)
        self.tm1.cubes.views.update_or_create(
            view=view_output,
            private=False)
        # write values into input view
        mdx = view_input.MDX
        self.tm1.cubes.cells.write_values_through_cellset(mdx, STDEV_INPUT_VALUES)
        # execute method
        stdev(
            tm1_services={"tm1srv01": self.tm1},
            tm1_source="tm1srv01",
            cube_source=CUBE_NAME_SOURCE,
            view_source=VIEW_NAME_SOURCE,
            tidy=False)
        # check existence
        self.assertTrue(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            private=False))
        self.assertTrue(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            private=False))

    def test_tm1tidy_true_input_view(self):
        # define input view and output view
        mdx_input = MDX_TEMPLATE_SHORT.format(
            rows="{ HEAD ( { [" + DIMENSION_NAMES[0] + "].Members}," + str(len(STDEV_INPUT_VALUES)) + ") }",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_SOURCE)
        view_input = MDXView(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            MDX=mdx_input)
        self.tm1.cubes.views.update_or_create(
            view=view_input,
            private=False)
        # write values into input view
        mdx = view_input.MDX
        self.tm1.cubes.cells.write_values_through_cellset(mdx, STDEV_INPUT_VALUES)
        # execute method
        stdev(
            tm1_services={"tm1srv01": self.tm1},
            tm1_source="tm1srv01",
            cube_source=CUBE_NAME_SOURCE,
            view_source=VIEW_NAME_SOURCE,
            tidy=True)
        # check existence
        self.assertFalse(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            private=False))

    def test_tm1tidy_false_input_view(self):
        # define input view and output view
        mdx_input = MDX_TEMPLATE_SHORT.format(
            rows="{ HEAD ( { [" + DIMENSION_NAMES[0] + "].Members}," + str(len(STDEV_INPUT_VALUES)) + ") }",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_SOURCE)
        view_input = MDXView(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            MDX=mdx_input)
        self.tm1.cubes.views.update_or_create(
            view=view_input,
            private=False)
        # write values into input view
        mdx = view_input.MDX
        self.tm1.cubes.cells.write_values_through_cellset(mdx, STDEV_INPUT_VALUES)
        # execute method
        stdev_p(
            tm1_services={"tm1srv01": self.tm1},
            tm1_source="tm1srv01",
            cube_source=CUBE_NAME_SOURCE,
            view_source=VIEW_NAME_SOURCE,
            tidy=False)
        self.assertTrue(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_SOURCE,
            view_name=VIEW_NAME_SOURCE,
            private=False))

    def test_tm1tidy_true_input_values_output_view(self):
        # define output view
        mdx_output = MDX_TEMPLATE_SHORT.format(
            rows="{[" + DIMENSION_NAMES[0] + "].DefaultMember}",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_TARGET)
        view_output = MDXView(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            MDX=mdx_output)
        self.tm1.cubes.views.update_or_create(
            view=view_output,
            private=False)
        # execute method
        stdev(
            tm1_services={"tm1srv01": self.tm1},
            tm1_target="tm1srv01",
            cube_target=CUBE_NAME_TARGET,
            view_target=VIEW_NAME_TARGET,
            values=STDEV_INPUT_VALUES,
            tidy=True)
        # check view existence
        self.assertFalse(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            private=False))

    def test_tm1tidy_false_input_values_output_view(self):
        # define output view
        mdx_output = MDX_TEMPLATE_SHORT.format(
            rows="{[" + DIMENSION_NAMES[0] + "].DefaultMember}",
            columns="{[" + DIMENSION_NAMES[1] + "].[Element_1]}",
            cube=CUBE_NAME_TARGET)
        view_output = MDXView(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            MDX=mdx_output)
        self.tm1.cubes.views.update_or_create(
            view=view_output,
            private=False)
        # execute method
        irr(
            tm1_services={"tm1srv01": self.tm1},
            tm1_target="tm1srv01",
            cube_target=CUBE_NAME_TARGET,
            view_target=VIEW_NAME_TARGET,
            values=IRR_INPUT_VALUES,
            tidy=False)
        # check view existence
        self.assertTrue(self.tm1.cubes.views.exists(
            cube_name=CUBE_NAME_TARGET,
            view_name=VIEW_NAME_TARGET,
            private=False))