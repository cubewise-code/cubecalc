import configparser

from TM1py import TM1Service, Dimension, Hierarchy, Element, Cube, NativeView, AnonymousSubset

CONFIG = "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG)

with TM1Service(**config['tm1srv01']) as tm1:
    # create dimensions

    dimension = Dimension(
        name="Project")
    hierarchy = Hierarchy(
        name="Project",
        dimension_name="Project",
        elements=[
            Element("Project1", "Numeric"),
            Element("Project2", "Numeric"),
            Element("Project3", "Numeric")])
    dimension.add_hierarchy(hierarchy)
    if not tm1.dimensions.exists(dimension.name):
        tm1.dimensions.create(dimension)

    dimension = Dimension(
        name="Quarter")
    hierarchy = Hierarchy(
        name="Quarter",
        dimension_name="Quarter",
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
        name="Project Planning Measure")
    hierarchy = Hierarchy(
        name="Project Planning Measure",
        dimension_name="Project Planning Measure",
        elements=[Element("Cashflow", "Numeric")])
    if not tm1.dimensions.exists(dimension.name):
        tm1.dimensions.create(dimension)

    dimension = Dimension(
        name="Project Summary Measure")
    hierarchy = Hierarchy(
        name="Project Summary Measure",
        dimension_name="Project Planning Measure",
        elements=[Element("IRR", "Numeric"), Element("NPV", "Numeric")])
    dimension.add_hierarchy(hierarchy)
    if not tm1.dimensions.exists(dimension.name):
        tm1.dimensions.create(dimension)

    # create cube 1
    cube = Cube(
        name="Project Planning", dimensions=["Project", "Quarter", "Project Planning Measure"])
    if not tm1.cubes.exists(cube.name):
        tm1.cubes.create(cube)

    # create cube 2
    cube = Cube(
        name="Project Summary", dimensions=["Project", "Project Summary Measure"])
    if not tm1.cubes.exists(cube.name):
        tm1.cubes.create(cube)

    # create views
    for project in ("Project1", "Project2", "Project3"):
        # Project Summary
        cube_name = "Project Summary"
        view = NativeView(
            cube_name=cube_name,
            view_name=project + " NPV",
            format_string="0.#########",
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view.add_row(
            dimension_name="Project Summary Measure",
            subset=AnonymousSubset(
                dimension_name="Project Summary Measure",
                elements=["NPV"]))
        view.add_column(
            dimension_name="Project",
            subset=AnonymousSubset(
                dimension_name="Project",
                elements=[project]))
        if tm1.cubes.views.exists(cube_name=view.cube, view_name=view.name, private=False):
            tm1.cubes.views.delete(cube_name=view.cube, view_name=view.name, private=False)
        tm1.cubes.views.create(view=view, private=False)

        view = NativeView(
            cube_name=cube_name,
            view_name=project + " IRR",
            format_string="0.#########",
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view.add_row(
            dimension_name="Project Summary Measure",
            subset=AnonymousSubset(
                dimension_name="Project Summary Measure",
                elements=["IRR"]))
        view.add_column(
            dimension_name="Project",
            subset=AnonymousSubset(
                dimension_name="Project",
                elements=[project]))
        if tm1.cubes.views.exists(cube_name=view.cube, view_name=view.name, private=False):
            tm1.cubes.views.delete(cube_name=view.cube, view_name=view.name, private=False)
        tm1.cubes.views.create(view=view, private=False)

        # Project Planning
        cube_name = "Project Planning"
        view = NativeView(
            cube_name=cube_name,
            view_name=project,
            format_string="0.#########",
            suppress_empty_columns=False,
            suppress_empty_rows=False)
        view.add_row(
            dimension_name="Quarter",
            subset=AnonymousSubset(
                dimension_name="Quarter",
                expression="{Tm1SubsetAll([Quarter])}"))
        view.add_column(
            dimension_name="Project",
            subset=AnonymousSubset(
                dimension_name="Project",
                elements=[project]))
        view.add_title(
            dimension_name="Project Planning Measure",
            selection="Cashflow",
            subset=AnonymousSubset(
                dimension_name="Project Planning Measure",
                elements=["Cashflow"])
        )
        if tm1.cubes.views.exists(cube_name=view.cube, view_name=view.name, private=False):
            tm1.cubes.views.delete(cube_name=view.cube, view_name=view.name, private=False)
        tm1.cubes.views.create(view=view, private=False)

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
        cube_name="Project Planning",
        cellset_as_dict=cellset
    )
