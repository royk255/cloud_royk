import os
import c_db
import pathlib
def directory():
    # Get the current directory
    current_directory = os.getcwd()
    
    # List all files in the directory
    files = os.listdir(current_directory)
    
    # Collect file details
    file_data = []
    for file in files:
        file_path = os.path.join(current_directory, file)
        if os.path.isfile(file_path):
            file_info = {
                "name": file,
                "size": os.path.getsize(file_path),
                "last_update": pathlib.Path(file_path).stat().st_mtime,
                "path": file_path
            }
            if file_info["name"] != file_data:
                file_data.append(file_info)
    return file_data
    
    # Print the collected data
    for data in file_data:
        print(f"Name: {data['name']}, Size: {data['size']} bytes, Last Update: {data['last_update']}, Path: {data['path']}")

def add_to_database(file_data):
    d1 = c_db.data("files_data.db")
    for data in file_data:
        if not d1.is_file_record_exists(data["name"]):
            d1.add_file_record(data["name"], data["size"], data["last_update"])
        elif d1.is_file_record_exists(data["name"] and d1.get_file_record() != data["update_date"]):
            d1.delete_file_record(data["name"])
            d1.add_file_record(data["name"], data["size"], data["last_update"])

def get_messge():
    files = directory()
    add_to_database(files)