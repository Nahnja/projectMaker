import importlib
import os
import inspect
import collections


class Maker(dict):
    """given config-dictionary initialize yourself, s.t. you are a tree of directories and files to write
    """

    def __init__(self, config):
        self.config = config
        self.path = None
        self.setup()

        for dict in self.delegate():
            if self.path is not None:
                self.update({
                    self.path: dict,
                })
            else:
                self.update(dict)

    # meh. turn this into a pure function??
    def update(self, dict):
        """recursively update yourself with the given dict"""
        for key, val in dict.items():
            if isinstance(val, collections.Mapping):
                val = Maker.update(self.get(key, {}), val)
            self[key] = val
        return self

    def setup(self):
        if "path" in self.config:
            self.path = self.config["path"]
            del self.config["path"]

    def delegate(self):
        """For each key in self.config try and find a handler. That handler is given the key's value and should itself return a tree of directories and files it would like to see created.

            Handlers may be modules defined in the calling instance's class'es folder or methods on the instance. Modules override methods.
            If a module with the correct name is found it is expected to define the name `make` which in turn is expected to be the callable handler. It is expected to return a mapping.
            If the handler used is a method of `self` it is expected to ge a generator yielding mappings.
        """
        # this should be extended to look for modules in other places so people can define their handler whereever* they want
        # also expecting methods to be generators, but module.make not might be a bit  weird
        for key, val in self.config.items():
            # maybe wrap the whole thing in a try except. We can be pretty sure every other part is unaffected of errors occuring in one
            try:
                module = importlib.import_module(".." + key, self.__module__)
                yield module.make(val)
            except ImportError as error:
                # no module with the name, try to see if a function is defined
                if hasattr(self, key) and callable(getattr(self, key)):
                    yield from getattr(self, key)(val)
                else:
                    print(error)
                    print("{0} couldn't handle '{1}'. Please create a method or module named '{1}'".format(self.__class__, key))


    def load_template(self, template_name, no_context=False, **context):
        """utility to load a template

            looks for templates in ./templates where . is the folder the calling instance's class is defined in

            if no kwargs are provided uses `self` as the templates' context unless `no_context` is specifically set to True.
        """
        with open(inspect.getfile(self.__class__).rpartition("/")[0] + "/templates/" + template_name) as f:
            if len(context) == 0:
                if not no_context:
                    rendered = f.read().format(context=self)
                else:
                    rendered = f.read()
            else:
                rendered = f.read().format(**context)
        return rendered





make = Maker
