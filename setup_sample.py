import configparser

from TM1py import TM1Service, Dimension, Hierarchy, Element, Cube, NativeView, AnonymousSubset

CONFIG = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG)

with TM1Service(**config['tm1srv01']) as tm1:
    # create dimensions

    dimension = Dimension(
        name="Py Project")
    hierarchy = Hierarchy(
        name="Py Project",
        dimension_name="Py Project",
        elements=[
            Element("Project1", "Numeric"),
            Element("Project2", "Numeric"),
            Element("Project3", "Numeric")])
    dimension.add_hierarchy(hierarchy)
    if not tm1.dimensions.exists(dimension.name):
        tm1.dimensions.create(dimension)

    dimension = Dimension(
        name="Py Quarter")
    hierarchy = Hierarchy(
        name="Py Quarter",
        dimension_name="Py Quarter",
        elements=[
            Element("2018-Q1", "Numeric"),
            Element("2018-Q2", "Numeric"),
            Element("2018-Q3", "Numeric"),
            Element("2018-Q4", "Numeric"),
            Element("2019-Q1", "Numeric"),
            Element("2019-Q2", "Numeric"),
            Element("2019-Q3", "Numeric"),
            Element("2019-Q4", "Numeric"),
            Element("2020-Q1", "Numeric"),
            Element("2020-Q2", "Numeric"),
            Element("2020-Q3", "Numeric"),
            Element("2020-Q4", "Numeric")])
    dimension.add_hierarchy(hierarchy)
    if not tm1.dimensions.exists(dimension.name):
        tm1.dimensions.create(dimension)

    dimension = Dimension(
        name="Py Project Planning Measure")
    hierarchy = Hierarchy(
        name="Py Project Planning Measure",
        dimension_name="Py Project Planning Measure",
        elements=[Element("Cashflow", "Numeric")])
    dimension.add_hierarchy(hierarchy)
    tm1.dimensions.update_or_create(dimension)

    dimension = Dimension(
        name="Py Project Summary")
    hierarchy = Hierarchy(
        name="Py Project Summary",
        dimension_name="Py Project Summary",
        elements=[Element("IRR", "Numeric"), Element("NPV", "Numeric")])
    dimension.add_hierarchy(hierarchy)
    tm1.dimensions.update_or_create(dimension)

    dimension = Dimension(
        name="Py Project Summary Measure")
    hierarchy = Hierarchy(
        name="Py Project Summary Measure",
        dimension_name="Py Project Summary Measure",
        elements=[Element("Value", "Numeric")])
    dimension.add_hierarchy(hierarchy)
    tm1.dimensions.update_or_create(dimension)

    # create cube 1
    cube = Cube(
        name="Py Project Planning", dimensions=["Py Project", "Py Quarter", "Py Project Planning Measure"])
    if tm1.cubes.exists(cube.name):
        tm1.cubes.delete(cube.name)
    tm1.cubes.create(cube)

    # create cube 2
    cube = Cube(
        name="Py Project Summary", dimensions=["Py Project", "Py Project Summary", "Py Project Summary Measure"])
    if tm1.cubes.exists(cube.name):
        tm1.cubes.delete(cube.name)
    tm1.cubes.create(cube)

    # create views
    for project in ("Project1", "Project2", "Project3"):
        # Project Summary
        cube_name = "Py Project Summary"
        view = NativeView(
            cube_name=cube_name,
            view_name=project + " NPV",
            format_string="0.#########",
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view.add_row(
            dimension_name="Py Project Summary",
            subset=AnonymousSubset(
                dimension_name="Py Project Summary",
                elements=["NPV"]))
        view.add_title(
            dimension_name="Py Project",
            subset=AnonymousSubset(
                dimension_name="Py Project",
                elements=[project]),
            selection=project)
        view.add_column(
            dimension_name="Py Project Summary Measure",
            subset=AnonymousSubset(
                dimension_name="Py Project Summary Measure",
                elements=["Value"]))
        tm1.views.update_or_create(view)

        view = NativeView(
            cube_name=cube_name,
            view_name=project + " IRR",
            format_string="0.#########",
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view.add_row(
            dimension_name="Py Project Summary",
            subset=AnonymousSubset(
                dimension_name="Py Project Summary",
                elements=["IRR"]))
        view.add_title(
            dimension_name="Py Project",
            subset=AnonymousSubset(
                dimension_name="Py Project",
                elements=[project]),
            selection=project)
        view.add_column(
            dimension_name="Py Project Summary Measure",
            subset=AnonymousSubset(
                dimension_name="Py Project Summary Measure",
                elements=["Value"]))
        tm1.views.update_or_create(view)

        # Project Planning
        cube_name = "Py Project Planning"
        view = NativeView(
            cube_name=cube_name,
            view_name=project,
            format_string="0.#########",
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view.add_row(
            dimension_name="Py Quarter",
            subset=AnonymousSubset(
                dimension_name="Py Quarter",
                expression="{Tm1SubsetAll([Py Quarter])}"))
        view.add_title(
            dimension_name="Py Project",
            selection=project,
            subset=AnonymousSubset(
                dimension_name="Py Project",
                elements=[project]))
        view.add_column(
            dimension_name="Py Project Planning Measure",
            subset=AnonymousSubset(
                dimension_name="Py Project Planning Measure",
                elements=["Cashflow"])
        )
        tm1.views.update_or_create(view)

    # write to cube 1
    cellset = {
        ('Project1', '2018-Q1', 'Cashflow'): -100000,
        ('Project1', '2018-Q2', 'Cashflow'): 10000,
        ('Project1', '2018-Q3', 'Cashflow'): 10000,
        ('Project1', '2018-Q4', 'Cashflow'): 10000,
        ('Project1', '2019-Q1', 'Cashflow'): 10000,
        ('Project1', '2019-Q2', 'Cashflow'): 10000,
        ('Project1', '2019-Q3', 'Cashflow'): 10000,
        ('Project1', '2019-Q4', 'Cashflow'): 10000,
        ('Project1', '2020-Q1', 'Cashflow'): 10000,
        ('Project1', '2020-Q2', 'Cashflow'): 10000,
        ('Project1', '2020-Q3', 'Cashflow'): 10000,
        ('Project1', '2020-Q4', 'Cashflow'): 10000,
        ('Project2', '2018-Q1', 'Cashflow'): -100000,
        ('Project2', '2018-Q2', 'Cashflow'): 8000,
        ('Project2', '2018-Q3', 'Cashflow'): 8000,
        ('Project2', '2018-Q4', 'Cashflow'): 8000,
        ('Project2', '2019-Q1', 'Cashflow'): 8000,
        ('Project2', '2019-Q2', 'Cashflow'): 11000,
        ('Project2', '2019-Q3', 'Cashflow'): 11000,
        ('Project2', '2019-Q4', 'Cashflow'): 11000,
        ('Project2', '2020-Q1', 'Cashflow'): 12000,
        ('Project2', '2020-Q2', 'Cashflow'): 12000,
        ('Project2', '2020-Q3', 'Cashflow'): 13000,
        ('Project2', '2020-Q4', 'Cashflow'): 13000,
        ('Project3', '2018-Q1', 'Cashflow'): -90000,
        ('Project3', '2018-Q2', 'Cashflow'): 8000,
        ('Project3', '2018-Q3', 'Cashflow'): 8000,
        ('Project3', '2018-Q4', 'Cashflow'): 8000,
        ('Project3', '2019-Q1', 'Cashflow'): 8000,
        ('Project3', '2019-Q2', 'Cashflow'): 8000,
        ('Project3', '2019-Q3', 'Cashflow'): 8000,
        ('Project3', '2019-Q4', 'Cashflow'): 8000,
        ('Project3', '2020-Q1', 'Cashflow'): 8000,
        ('Project3', '2020-Q2', 'Cashflow'): 8000,
        ('Project3', '2020-Q3', 'Cashflow'): 8000,
        ('Project3', '2020-Q4', 'Cashflow'): 8000
    }
    tm1.cubes.cells.write_values(
        cube_name="Py Project Planning",
        cellset_as_dict=cellset
    )
