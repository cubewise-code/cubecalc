# CubeCalc

python command line tool to perform typical financial calculations, such as IRR, NPV in TM1

# Usage
execute the main.py with 7 + x arguments:
- method (IRR, NPV)
- name of source instance in config.ini file
- name of target instance in config.ini file
- name of source cube 
- name of target cube 
- name of source view (view must be defined as a N : 1 or 1 : N matrix) 
- name of target view (view must be defined as a 1 : 1 matrix) 
- ...


> C:/Anaconda3/python main.py "IRR" "tm1srv01" "tm1srv01" "project planning" "project summary" "project1" "project1 IRR"

or

> C:/Anaconda3/python main.py "NPV" "tm1srv01" "tm1srv01" "project planning" "project summary" "project2" "project2 NPV" 0.02

# Installation

Just download the repository

# Samples
- Adjust the config.ini file to match your setup
- Execute the "setup sample.py" file 
- Run main.py with appropriate arguments from the commandline or from TI


# Tests
No tests yet

