import configparser
import datetime
import logging
import os
import sys
from base64 import b64decode

from TM1py import TM1Service
from TM1py.Utils.Utils import CaseAndSpaceInsensitiveDict

import methods

METHODS = CaseAndSpaceInsensitiveDict({
    "IRR": methods.irr,
    "NPV": methods.npv,
    "STDEV": methods.stdev
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


def translate_cmd_arguments(tm1_services, method, tm1_source, tm1_target, cube_source, cube_target, view_source,
                            view_target, *args):
    """ Translation and Validity-checks for command line arguments.

    :param view_target:
    :param view_source:
    :param cube_target:
    :param cube_source:
    :param tm1_target:
    :param tm1_source:
    :param tm1_services:
    :param args:
    :return:
    """

    # method not implemented
    if method not in METHODS:
        msg = "method {method} not implemented.".format(method=method)
        logging.error(msg)
        raise ValueError(msg)

    # source instance not in config
    if tm1_source not in tm1_services:
        msg = "TM1 instance {instance} not specified in config.".format(instance=tm1_source)
        logging.error(msg)
        raise ValueError(msg)

    # target instance not in config
    if tm1_target not in tm1_services:
        msg = "TM1 instance {instance} not specified in config.".format(instance=tm1_target)
        logging.error(msg)
        raise ValueError(msg)

    # cube_source doesn't exist
    if not tm1_services[tm1_source].cubes.exists(cube_source):
        msg = "source cube {cube} doesn't exist in instance {instance}.".format(cube=cube_source, instance=tm1_target)
        logging.error(msg)
        raise ValueError(msg)

    # cube_target doesn't exist
    if not tm1_services[tm1_target].cubes.exists(cube_target):
        msg = "target cube {cube} doesn't exist in instance {instance}.".format(cube=cube_target, instance=tm1_target)
        logging.error(msg)
        raise ValueError(msg)

    # view_source doesn't exist
    if not tm1_services[tm1_target].cubes.views.exists(
            cube_name=cube_source,
            view_name=view_source,
            private=False):
        msg = "source view {view} doesn't exist in instance {instance}.".format(view=view_source, instance=tm1_source)
        logging.error(msg)
        raise ValueError(msg)

    # view_target doesn't exist
    if not tm1_services[tm1_source].cubes.views.exists(
            cube_name=cube_target,
            view_name=view_target,
            private=False):
        msg = "target view {view} doesn't exist in instance {instance}.".format(view=view_target, instance=tm1_target)
        logging.error(msg)
        raise ValueError(msg)

    return (method, tm1_source, tm1_target, cube_source, cube_target, view_source, view_target, *args)


if __name__ == "__main__":
    """ Receives > 7 arguments arguments: 
    method, 
    source_instance, 
    target_instance, 
    cube_source, 
    cube_target, 
    view_source, 
    view_target, ...
    """
    logging.info("{app_name} starts. Parameters: {parameters}.".format(
        app_name=APPNAME,
        parameters=sys.argv))
    # start timer
    start = datetime.datetime.now()

    # setup connections
    tm1_services = setup_tm1_services()

    # read commandline arguments
    method, *args = translate_cmd_arguments(tm1_services, *sys.argv[1:])

    # execution
    try:
        METHODS[method](tm1_services, *args)
    finally:
        logout(tm1_services)
    # timing
    end = datetime.datetime.now()
    duration = end - start
    logging.info(("{app_name} ends. Duration: " + str(duration)).format(app_name=APPNAME))
