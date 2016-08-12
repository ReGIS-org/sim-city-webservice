#!/usr/bin/env python

import json
import os
import sys

try:
    with open(os.environ['SIMCITY_PARAMS']) as f:
        obj = json.load(f)

    for k, v in obj.items():
        os.environ[k.upper()] = str(v)
except KeyError:
    print("No input file given")

command = []
for arg in sys.argv[1:]:
    if arg.startswith('$'):
        command.append(os.environ.get(arg[1:].upper(), arg))
    else:
        command.append(arg)

try:
    os.chdir(os.environ['SIMCITY_TMP'])
    print("Executing in temporary directory " + os.environ['SIMCITY_TMP'])
except KeyError:
    print("Not executing in temporary directory")

print('"' + '" "'.join(command) + '"')
os.execvp(command[0], command)
