import json
import os

class TextFileManager:
    def __init__(self, filename="project_men.json"):
        self.filename = filename
        self.data = {}
        self._ensure_file_exists()
        

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump(self.data, f, indent=4)
        self.data = self.load_data()

    def load_data(self):
        with open(self.filename, "r") as f:
            return json.load(f)

    def save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_project(self, project_name, project_path, project_type):
        if project_path in self.data:
            print("Project already exists.")
        else:
            self.data[project_name] = {"path" : project_path ,"type" : project_type}
            self.save_data()
            print("Project added.")

    def get_project_path(self, project_name):
        data = self.load_data()
        return self.data[project_name]["path"]


# path: type
