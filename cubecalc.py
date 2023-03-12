import datetime
import logging
import sys

import click

from constants import APP_NAME
from utils import CubeCalc, exit_cubecalc, configure_logging


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.pass_context
def main(click_arguments):
    """ Needs > 7 arguments arguments:
    method, 
    tm1_source,
    tm1_target,
    cube_source, 
    cube_target, 
    view_source, 
    view_target,
    dimension,
    subset

    """
    parameters = {click_arguments.args[arg][2:]: click_arguments.args[arg + 1]
                  for arg
                  in range(0, len(click_arguments.args), 2)}
    method_name = parameters.pop('method')
    logging.info("{app_name} starts. Parameters: {parameters}.".format(
        app_name=APP_NAME,
        parameters=parameters))
    # start timer
    start = datetime.datetime.now()
    # setup connections
    calculator = CubeCalc()
    # execute method
    success = calculator.execute(method=method_name, parameters=parameters)
    # exit
    exit_cubecalc(success=success, elapsed_time=datetime.datetime.now() - start)


if __name__ == "__main__":
    try:
        configure_logging()
        main()
    except Exception as exception:
        sys.exit("Aborting {app_name}. Error: {error}".format(app_name=APP_NAME, error=str(exception)))
