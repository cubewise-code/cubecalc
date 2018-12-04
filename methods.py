import numpy as np


def irr(tm1_services, tm1_source, tm1_target, cube_source, cube_target, view_source, view_target):
    values = tm1_services[tm1_source].cubes.cells.execute_view_values(
        cube_name=cube_source,
        view_name=view_source,
        private=False)
    result = np.irr(values=list(values))
    mdx = tm1_services[tm1_target].cubes.views.get_native_view(
        cube_name=cube_target,
        view_name=view_target,
        private=False).MDX
    tm1_services[tm1_target].cubes.cells.write_values_through_cellset(
        mdx=mdx,
        values=(result,))


def npv(tm1_services, tm1_source, tm1_target, cube_source, cube_target, view_source, view_target, discount_rate):
    values = tm1_services[tm1_source].cubes.cells.execute_view_values(
        cube_name=cube_source,
        view_name=view_source,
        private=False)
    result = np.npv(rate=float(discount_rate), values=list(values))
    mdx = tm1_services[tm1_target].cubes.views.get_native_view(
        cube_name=cube_target,
        view_name=view_target,
        private=False).MDX
    tm1_services[tm1_target].cubes.cells.write_values_through_cellset(
        mdx=mdx,
        values=(result,))


def stdev(tm1_services, tm1_source, tm1_target, cube_source, cube_target, view_source, view_target, *args):
    print(args)
