import configparser
import datetime
import logging
import os
import sys

import click
from TM1py import TM1Service
from TM1py.Utils.Utils import CaseAndSpaceInsensitiveDict

import methods
from utils import set_current_directory

METHODS = CaseAndSpaceInsensitiveDict({
    "IRR": methods.irr,
    "NPV": methods.npv,
    "STDEV": methods.stdev,
    "STDEV_P": methods.stdev_p,
    "FV": methods.fv,
    "FV_SCHEDULE": methods.fv_schedule,
    "PV": methods.pv,
    "XNPV": methods.xnpv,
    "PMT": methods.pmt,
    "PPMT": methods.ppmt,
    "MIRR": methods.mirr,
    "XIRR": methods.xirr,
    "NPER": methods.nper,
    "RATE": methods.rate,
    "EFFECT": methods.effect,
    "NOMINAL": methods.nominal,
    "SLN": methods.sln,
    "MEAN": methods.mean,
    "SEM": methods.sem,
    "MEDIAN": methods.median,
    "MODE": methods.mode,
    "VAR": methods.var,
    "KURT": methods.kurt,
    "SKEW": methods.skew,
    "RNG": methods.rng,
    "MIN": methods.min_,
    "MAX": methods.max_,
    "SUM": methods.sum_,
    "COUNT": methods.count
})

APP_NAME = "CubeCalc"
CURRENT_DIRECTORY = set_current_directory()
LOGFILE = os.path.join(CURRENT_DIRECTORY, APP_NAME + ".log")
CONFIG = os.path.join(CURRENT_DIRECTORY, "config.ini")

logging.basicConfig(
    filename=LOGFILE,
    format='%(asctime)s - ' + APP_NAME + ' - %(levelname)s - %(message)s',
    level=logging.INFO)


class CubeCalc:

    def __init__(self):
        self.tm1_services = dict()
        self.setup()

    def setup(self):
        """ Fill Dictionary with TM1ServerName (as in config.ini) : Instantiated TM1Service

        :return: Dictionary server_names and TM1py.TM1Service instances pairs
        """
        if not os.path.isfile(CONFIG):
            raise ValueError("{config} does not exist.".format(config=CONFIG))
        config = configparser.ConfigParser()
        config.read(CONFIG)
        # build tm1_services dictionary
        for tm1_server_name, params in config.items():
            # handle default values from configparser
            if tm1_server_name != config.default_section:
                try:
                    self.tm1_services[tm1_server_name] = TM1Service(**params, session_context=APP_NAME)
                # Instance not running, Firewall or wrong connection parameters
                except Exception as e:
                    logging.error("TM1 instance {} not accessible. Error: {}".format(tm1_server_name, str(e)))

    def logout(self):
        """ logout from all instances
        :return:
        """
        for tm1 in self.tm1_services.values():
            tm1.logout()

    def execute(self, method, parameters):
        """

        :param method:
        :param parameters:
        :return:
        """
        try:
            result = METHODS[method](**parameters, tm1_services=self.tm1_services)
            logging.info("Successfully calculated {method} with result: {result} from parameters: {parameters}".format(
                method=method,
                parameters=parameters,
                result=result))
            return True
        except Exception as ex:
            message = "Failed calculating {method} with parameters {parameters}. Error: {error}".format(
                method=method,
                parameters=parameters,
                error=str(ex))
            logging.exception(message)
            return False
        finally:
            self.logout()


def exit_cubecalc(success, elapsed_time):
    message = "{app_name} {ends}. Duration: {elapsed_time}.".format(
        app_name=APP_NAME,
        ends="aborted" if not success else "ends",
        elapsed_time=str(elapsed_time))
    if success:
        logging.info(message)
    else:
        logging.error(message)
        sys.exit(message)


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
    view_target
    ...
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
        main()
    except Exception as exception:
        sys.exit("Aborting {app_name}. Error: {error}".format(app_name=APP_NAME, error=str(exception)))
