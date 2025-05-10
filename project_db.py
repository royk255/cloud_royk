import json
import os

# Path to the JSON file
JSON_FILE = "project_men.json"


def create_json_file():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w") as file:
            json.dump({}, file, indent=4)
        #print(f"Created JSON file: {JSON_FILE}")
    else:
        #print(f"JSON file already exists: {JSON_FILE}")
        pass

# Load JSON data from file
def load_data():
    if not os.path.exists(JSON_FILE):
        return {}
    with open(JSON_FILE, "r") as file:
        return json.load(file) 

# Save JSON data to file
def save_data(data):
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Check if a project exists
def project_exists(project_name):
    data = load_data()
    return any(project_name == os.path.basename(path) for path in data)

# Get project path by name
def get_project_path(project_name):
    data = load_data()
    for path, project_type in data.items():
        if os.path.basename(path) == project_name:
            return path
    return None

# Get project type by name
def get_project_type(project_name):
    data = load_data()
    for path, project_type in data.items():
        if os.path.basename(path) == project_name:
            return project_type
    return None

# Add a new project
def add_project(project_path, project_type):
    data = load_data()
    if project_path in data:
        print("Project already exists.")
        return
    data[project_path] = project_type
    save_data(data)
    print("Project added successfully.")

# Remove a project
def remove_project(project_name):
    data = load_data()
    for path in list(data.keys()):
        if os.path.basename(path) == project_name:
            del data[path]
            save_data(data)
            print("Project removed successfully.")
            return
    print("Project not found.")

def list_projects():
    data = load_data()
    if not data:
        print("No projects found.")
        return
    for path, project_type in data.items():
        print(f"Project Name: {os.path.basename(path)}, Path: {path}, Type: {project_type}")


create_json_file()


def main():
    list_projects()

# Example usage
if __name__ == "__main__":
    #main()
    pass
    """
    # Add projects
    add_project("/path/to/project1", 1)
    add_project("/path/to/project2", 2)

    # Check if a project exists
    print(project_exists("project1"))  # True

    # Get project path
    print(get_project_path("project1"))  # /path/to/project1

    # Get project type
    print(get_project_type("project1"))  # 1

    # Remove a project
    remove_project("project1")
    print(project_exists("project1"))  # False
    """