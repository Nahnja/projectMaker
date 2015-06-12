#!/usr/bin/python

import importlib
import os.path
from shell import shell
import sys
import yaml
from src.projectMaker import make



argv = sys.argv
argc = len(argv)

# parse command line arguments
if argc <= 1:
    filename = "project.yml"
else:
    filename = argv[1]

if argc <= 2:
    out_dir = "."
else:
    out_dir = argv[2]




def shell_p(command):
    print(command)
    return shell(command)


# check for both .yaml and .yml version of filename (in case of typo)
if not os.path.isfile(filename):
    filename = filename.replace(".yml", ".yaml")

    if not os.path.isfile(filename):
        print("No yaml file found (looked for '" + filename + "')! Exiting...")
        sys.exit(1)



config_file = open(filename, "r")
config_raw = config_file.read()
config_file.close()

config = yaml.load(config_raw)

make(config)
