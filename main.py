import configparser
import datetime
import logging
import os
from base64 import b64decode

import click
from TM1py import TM1Service
from TM1py.Utils.Utils import CaseAndSpaceInsensitiveDict

import methods

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
    "SLN": methods.sln
})


def set_current_directory():
    abspath = os.path.abspath(__file__)
    directory = os.path.dirname(abspath)
    # set current directory
    os.chdir(directory)
    return directory


APPNAME = "CubeCalc"
CURRENT_DIRECTORY = set_current_directory()
LOGFILE = os.path.join(CURRENT_DIRECTORY, APPNAME + ".log")
CONFIG = os.path.join(CURRENT_DIRECTORY, "config.ini")

logging.basicConfig(
    filename=LOGFILE,
    format='%(asctime)s - ' + APPNAME + ' - %(levelname)s - %(message)s',
    level=logging.INFO)


def setup_tm1_services():
    """ Return Dictionary with TM1ServerName (as in config.ini) : Instantiated TM1Service

    :return: Dictionary server_names and TM1py.TM1Service instances pairs
    """
    if not os.path.isfile(CONFIG):
        raise ValueError("{config} does not exist.".format(config=CONFIG))
    tm1_services = dict()
    # parse .ini
    config = configparser.ConfigParser()
    config.read(CONFIG)
    # build tm1_services dictionary
    for tm1_server_name, params in config.items():
        # handle default values from configparser
        if tm1_server_name != config.default_section:
            try:
                params["password"] = decrypt_password(params["password"])
                tm1_services[tm1_server_name] = TM1Service(**params, session_context=APPNAME)
            # Instance not running, Firewall or wrong connection parameters
            except Exception as e:
                logging.error("TM1 instance {} not accessible. Error: {}".format(tm1_server_name, str(e)))
    return tm1_services


def decrypt_password(encrypted_password):
    """ b64 decoding

    :param encrypted_password: encrypted password with b64
    :return: password in plain text
    """
    return b64decode(encrypted_password).decode("UTF-8")


def logout(tm1_services):
    """ logout from all instances

    :param tm1_services:
    :return:
    """
    for tm1 in tm1_services.values():
        tm1.logout()


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
    ...
    """
    parameters = {click_arguments.args[arg][2:]: click_arguments.args[arg + 1]
                  for arg
                  in range(0, len(click_arguments.args), 2)}
    logging.info("{app_name} starts. Parameters: {parameters}.".format(
        app_name=APPNAME,
        parameters=parameters))
    # start timer
    start = datetime.datetime.now()

    # setup connections
    tm1_services = setup_tm1_services()

    # challenge commandline arguments
    method = parameters.pop('method')

    # execution
    try:
        result = METHODS[method](**parameters, tm1_services=tm1_services)
        logging.info("Successfully calculated {method} with Result: {result} from Parameters: {parameters}".format(
            method=method,
            parameters=parameters,
            result=result))
    except:
        logging.exception("Error happened during Calculation:")
    finally:
        logout(tm1_services=tm1_services)
    # timing
    end = datetime.datetime.now()
    duration = end - start
    logging.info(("{app_name} ends. Duration: " + str(duration)).format(app_name=APPNAME))


if __name__ == "__main__":
    result = main()
