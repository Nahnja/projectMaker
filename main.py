#!/usr/bin/python

import importlib
import os.path
import sys
import yaml
import collections

from src.projectMaker import make


def write(dict, path="."):
    """given a tree build a directory structure according to that tree
        assume leaves are files' contents

        dict -> {
            'root': {
                'js': {'functions.js': 'function main() {alert("moooo")}'}
            }
        }
    """
    for key, val in dict.items():
        if isinstance(val, str):
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + "/" + key, "w") as out:
                out.write(val)
        elif isinstance(val, collections.Mapping):
            write(val, path + "/" + key)
        else:
            raise ValueError("values must be mappings or string")


if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc <= 1:
        filename = "project.yml"
    else:
        filename = argv[1]

    # check for both .yaml and .yml version of filename (in case of typo)
    if not os.path.isfile(filename):
        filename = filename.replace(".yml", ".yaml")

        if not os.path.isfile(filename):
            print("No yaml file found (looked for '" + filename + "')! Exiting...")
            sys.exit(1)

    with open(filename) as config_file:
        config = yaml.load(config_file.read())

    #magic
    write(make(config))
