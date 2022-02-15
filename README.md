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

cubecalc offers two execution modes:

> 1. Single Mode

If no `dimension`, `hierarchy` and `subset` arguments are passed, cubecalc will execute the calculation for a single
view.

> 2. Batch Mode

If `dimension`, `hierarchy` and `subset` arguments are passed, cubecalc will run the calculation for each element in the
subset. The dynamic dimension (e.g., projects) **must** be placed in the titles! Effectively the source and target view
is updated before every calculation. When no subset is passed, cubecalc will run the calculation for all leaf elements.
When no hierarchy is passed cubecalc assumes the same named hierarchy.

> Examples

Execute the script like this:

`C:\python\python.exe cubecalc.py `

and pass arguments like this:

``` 
--method "IRR" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" 
--cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 IRR" --dimension "Project" 
--hierarchy "Project --subset "All Projects"
```

```
--method "NPV" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" 
--cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 NPV" --dimension "Project" 
--hierarchy "Project --subset "All Projects" --rate 0.1
```

```
--method "STDEV" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" 
--cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 STDEV" --dimension "Project" 
--hierarchy "Project --subset "All Projects"
```

```
--method "FV" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" 
--tm1_target "tm1srv01" --cube_target "Py Project Summary" --view_target "Project1 FV" --dimension "Project" 
--hierarchy "Project --subset "All Projects" --rate 0.1 --nper 3 --pmt 1 --pv -100
```

```
--method "PMT" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" 
--tm1_target "tm1srv01" --cube_target "Py Project Summary" --view_target "Project1 PMT" --dimension "Project" 
--hierarchy "Project --subset "All Projects" --rate 0.1 --nper 3 --pv 1000
```

```
--method "PV" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" 
 --tm1_target "tm1srv01" --cube_target "Py Project Summary" --view_target "Project1 PV" --dimension "Project" 
 --hierarchy "Project --subset "All Projects" --rate 0.1 --nper 3 --pmt 1 --fv -100 --when 0
```

```
--method "MIRR" --tm1_source "tm1srv01" --tm1_target "tm1srv01" --cube_source "Py Project Planning" 
--cube_target "Py Project Summary" --view_source "Project1" --view_target "Project1 MIRR" --dimension "Project" 
--hierarchy "Project --subset "All Projects" --finance_rate 0.12 --reinvest_rate 0.1
```

All arguments have the same names as in the Excel functions (except: `type` is called `when` in CubeCalc since `type` is
a reserved word in python)

The `dimension`, `hierarchy` and `subset` argument are optional (see section on run modes)

# Requirements

- [TM1py](https://github.com/cubewise-code/TM1py)
- [numpy-financial](https://github.com/numpy/numpy-financial)
- [scipy](https://github.com/scipy/scipy)
- [click](https://github.com/pallets/click/)

# Getting Started Guide

For more information about how to use CubeCalc, just follow
the [Getting Started Guide](https://code.cubewise.com/tm1py-help-content/getting-started-with-cubecalc).

# Installation

Just download the repository

# Configuration

Adjust the `config.ini` to match your TM1 environment:

```
[tm1srv01]
base_url=https://localhost:12354
user=admin
password=YXBwbGU=
decode_b64=True
```

# Samples

- Adjust the `config.ini` file to match your setup
- Execute the `setup sample.py` file
- Run `cubecalc.py` with appropriate arguments from the commandline or from TI

# Contribution

CubeCalc is an open source project. It thrives on contribution from the TM1 community. If you find a bug or want to add
more functions to this repository, just:

- Fork the repository
- Add the new function to the methods.py file + Add some tests for your function in the Tests.py file
- Create a MR and we will merge in the changes






