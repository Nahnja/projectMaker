import os
from src import projectMaker

class ProjectBaseMaker(projectMaker.Maker):

    def setup(self):
        super().setup()

        self.path = (self.path + "/" if self.path else "") + self.config["title"]
        del self.config["title"]
