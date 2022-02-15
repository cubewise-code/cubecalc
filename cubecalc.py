import configparser
import datetime
import logging
import os
import re
import sys
from typing import Dict

import click
from TM1py import TM1Service, MDXView, AnonymousSubset
from TM1py.Utils.Utils import CaseAndSpaceInsensitiveDict, case_and_space_insensitive_equals

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
    format="%(asctime)s - " + APP_NAME + " - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# also log to stdout
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class CubeCalc:

    def __init__(self):
        self.tm1_services: Dict[str, TM1Service] = dict()
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
            # single mode
            if "dimension" not in parameters:
                logging.info("Running in single mode")
                result = METHODS[method](**parameters, tm1_services=self.tm1_services)
                logging.info(f"Successfully calculated {method} with result: {result} from parameters: {parameters}")
                return True

            # iterative mode
            self.execute_iterative_mode(method, parameters)
            logging.info(f"Successfully calculated {method} in iterative mode with parameters: {parameters}")
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

    def execute_iterative_mode(self, method, parameters):
        dimension = parameters.get("dimension")
        hierarchy = parameters.get("hierarchy", dimension)

        tm1_source_name = parameters['tm1_source']
        tm1_target_name = parameters['tm1_target']

        tm1_source: TM1Service = self.tm1_services[tm1_source_name]
        tm1_target: TM1Service = self.tm1_services[tm1_target_name]

        cube_source = parameters.get("cube_source")
        view_source = parameters.get("view_source")

        cube_target = parameters.get("cube_target")
        view_target = parameters.get("view_target")

        if "subset" in parameters:
            subset = parameters.pop("subset")
            element_names = tm1_source.subsets.get_element_names(
                dimension_name=dimension,
                hierarchy_name=hierarchy,
                subset_name=subset,
                private=False)

        else:
            element_names = tm1_source.elements.get_leaf_element_names(
                dimension_name=dimension,
                hierarchy_name=hierarchy)

        # only pass tidy in run for last element
        if "tidy" in parameters:
            tidy = parameters.pop("tidy")
        else:
            tidy = False

        if not tidy:
            original_view_source = tm1_source.views.get(
                cube_name=cube_source,
                view_name=view_source,
                private=False)
            original_view_target = tm1_target.views.get(
                cube_name=cube_target,
                view_name=view_target,
                private=False)

        for element in element_names:
            self.alter_view(tm1_source=tm1_source_name, tm1_target=tm1_target_name, cube_source=cube_source,
                            view_source=view_source, cube_target=cube_target, view_target=view_target,
                            dimension=dimension, hierarchy=hierarchy, element=element)
            result = METHODS[method](
                **parameters,
                tm1_services=self.tm1_services,
                tidy=tidy if element == element_names[-1] else False)
            logging.info(f"Successfully calculated {method} with result: {result} for title element '{element}'")

        # restore original source_view, target_view
        if not tidy:
            tm1_source.views.update_or_create(original_view_source, False)
            tm1_target.views.update_or_create(original_view_target, False)

    def substitute_mdx_view_title(self, view, dimension, hierarchy, element):
        pattern = re.compile(r"\[" + dimension + r"\].\[" + hierarchy + r"\].\[(.*?)\]", re.IGNORECASE)
        findings = re.findall(pattern, view.mdx)

        if findings:
            view.mdx = re.sub(
                pattern=pattern,
                repl=f"[{dimension}].[{hierarchy}].[{element}]",
                string=view.mdx)
            return

        if hierarchy is None or case_and_space_insensitive_equals(dimension, hierarchy):
            pattern = re.compile(r"\[" + dimension + r"\].\[(.*?)\]", re.IGNORECASE)
            findings = re.findall(pattern, view.mdx)
            if findings:
                view.mdx = re.sub(
                    pattern=pattern,
                    repl=f"[{dimension}].[{element}]",
                    string=view.mdx)
                return

        raise ValueError(f"No selection in title with dimension: '{dimension}' and hierarchy: '{hierarchy}'")

    def substitute_native_view_title(self, view, dimension, element):
        for title in view.titles:
            if case_and_space_insensitive_equals(title.dimension_name, dimension):
                title._subset = AnonymousSubset(dimension, dimension, elements=[element])
                title._selected = element
                return

        raise ValueError(f"Dimension '{dimension}' not found in titles")

    def alter_view(self, tm1_source: str, tm1_target: str, cube_source: str, view_source: str, cube_target: str,
                   view_target: str, dimension: str, hierarchy: str, element: str):

        for tm1_instance_name, cube_name, view_name in zip(
                [tm1_source, tm1_target],
                [cube_source, cube_target],
                [view_source, view_target]):
            tm1 = self.tm1_services[tm1_instance_name]
            view = tm1.views.get(cube_name, view_name, private=False)

            if isinstance(view, MDXView):
                dimension = tm1.dimensions.determine_actual_object_name("Dimension", dimension)
                hierarchy = tm1.hierarchies.determine_actual_object_name("Hierarchy", hierarchy)
                self.substitute_mdx_view_title(view, dimension, hierarchy, element)

            else:
                self.substitute_native_view_title(view, dimension, element)

            tm1.views.update(view, private=False)


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
        main()
    except Exception as exception:
        sys.exit("Aborting {app_name}. Error: {error}".format(app_name=APP_NAME, error=str(exception)))
