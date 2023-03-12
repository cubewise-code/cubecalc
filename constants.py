from pathlib import Path

from TM1py.Utils import CaseAndSpaceInsensitiveDict

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
LOGFILE = Path(__file__).parent.joinpath(APP_NAME + ".log")
CONFIG = Path(__file__).parent.joinpath("config.ini")