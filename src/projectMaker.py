import importlib
import os
import inspect
import traceback


class Maker():

    def __init__(self, config, path="."):
        self.config = config
        self.path = path
        self.setup()
        self.delegate()

    def setup(self):
        if "path" in self.config:
            self.path = self.config["path"]
            del self.config["path"]

    def delegate(self):
        for key, val in self.config.items():
            try:
                module = importlib.import_module(".." + key, self.__module__)
                module.make(val, self.path)
            except ImportError as error:
                # no module with the name, try to see if a function is defined
                if hasattr(self, key) and callable(getattr(self, key)):
                    getattr(self, key)(val)
                else:
                    print(error)
                    print("{0} couldn't handle '{1}'. Please create a method or module named '{1}'".format(self.__class__, key))

    def load_template(self, template_name, no_context=False, **context):
        with open(inspect.getfile(self.__class__).rpartition("/")[0] + "/templates/" + template_name) as f:
            if len(context) == 0:
                if not no_context:
                    rendered = f.read().format(self)
                else:
                    rendered = f.read()
            else:
                rendered = f.read().format(**context)
        return rendered





make = Maker
