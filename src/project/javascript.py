import os
import requests

from src import projectMaker

class JavascriptMaker(projectMaker.Maker):

    def setup(self):
        self.path = "js"

    def jQuery(self, config):
        yield {
            "jQuery": {
                "jquery-{version}.min.js".format(**config):
                    requests.get(
                        "http://code.jquery.com/jquery-{version}.min.js".format(**config)
                    ).content.decode("utf-8"),
                "jquery-{version}.js".format(**config):
                    requests.get(
                        "http://code.jquery.com/jquery-{version}.js".format(**config)
                    ).content.decode("utf-8"),
            }
        }


make = JavascriptMaker
