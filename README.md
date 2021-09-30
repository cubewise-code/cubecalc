![](https://github.com/MariusWirtz/CubeCalc/blob/master/Images/logo.svg)

Python command line tool to perform typical financial and statistical calculations in TM1:

- COUNT
- EFFECT
- FV
- FV_SCHEDULE
- IRR
- KURT
- MAX
- MEAN
- MEDIAN
- MIN
- MIRR
- MODE
- NOMINAL
- NPER
- NPV
- PMT
- PPMT
- PV
- RATE
- RNG
- SEM
- SKEW
- SLN
- STDEV
- STDEV_P
- SUM
- VAR
- XIRR
- XNPV


# Usage
execute the CubeCalc.py with arguments. Samples:

> --method "IRR" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" --cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 IRR" --tidy True

> --method "NPV" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" --cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 NPV" --rate 0.1

> --method "STDEV" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" --cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 STDEV"

> --method "FV" --tm1_target "tm1srv01" --cube_target "Py Project Summary" --view_target "Project1 FV" --rate 0.1 --nper 3 --pmt 1 --pv -100

> --method "PMT" --tm1_target "tm1srv01" --cube_target "Py Project Summary" --view_target "Project1 PMT" --rate 0.1 --nper 3 --pv 1000

> --method "PV" --tm1_target "tm1srv01" --cube_target "Py Project Summary" --view_target "Project1 PV" --rate 0.1 --nper 3 --pmt 1 --fv -100 --when 0

> --method "MIRR" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" --cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 MIRR" --finance_rate 0.12 --reinvest_rate 0.1

All arguments have the same names as in the Excel functions (except: `type` is called `when` in CubeCalc since `type` is a reserved word in python) 

# Requirements
- [TM1py](https://github.com/cubewise-code/TM1py)
- [numpy-financial](https://github.com/numpy/numpy-financial)
- [scipy](https://github.com/scipy/scipy)
- [click](https://github.com/pallets/click/)

# Getting Started Guide

For more information about how to use CubeCalc, just follow the [Getting Started Guide](https://code.cubewise.com/tm1py-help-content/getting-started-with-cubecalc).

# Installation

Just download the repository

# Samples
- Adjust the config.ini file to match your setup
- Execute the "setup sample.py" file 
- Run CubeCalc.py with appropriate arguments from the commandline or from TI


# Tests
in Tests.py file


# Contribution
CubeCalc is an open source project. It thrives on contribution from the TM1 community. If you find a bug or want to add more functions to this repository, just:
- Fork the repository
- Add the new function to the methods.py file + Add some tests for your function in the Tests.py file
- Create a MR
and we will merge in the changes






