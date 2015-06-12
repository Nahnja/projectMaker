import os
import requests

from src import projectMaker

class JavascriptMaker(projectMaker.Maker):

    def setup(self):
        self.path = self.path + "/js"
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def jQuery(self, config):
        jquery_name = "jquery-" + config["version"]

        jquery_path = self.path + "/jQuery"
        if not os.path.exists(jquery_path):
            os.makedirs(jquery_path)

        with open(jquery_path + "/" + jquery_name + ".min.js", "w") as f:
            data = requests.get(
                "http://code.jquery.com/" + jquery_name + ".min.js").content
            f.write(data.decode("utf-8"))

        with open(jquery_path + "/" + jquery_name + ".js", "w") as f:
            data = requests.get(
                "http://code.jquery.com/" + jquery_name + ".js").content
            f.write(data.decode("utf-8"))



make = JavascriptMaker
