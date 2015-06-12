import os
from src import projectMaker

class ProjectBaseMaker(projectMaker.Maker):

    def setup(self):
        super().setup()
        
        self.path = self.path + "/" + self.config["title"]
        del self.config["title"]
        if not os.path.exists(self.path):
            os.makedirs(self.path)
