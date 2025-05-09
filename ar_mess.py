import os
import c_db
import pathlib
from pathlib import Path
import threading
import time

class ar_directory:
    def __init__(self, directory_path=None):
        self.directory_path = directory_path or os.getcwd()
        #self.file_data = self.directory()
        self.file_data = self.directory()
        #self.return_paths()

        #print(self.file_data)
        #self.fix_path()

    def fix_path(self): 
        self.directory_path = self.directory_path.replace("\\", "/")

    def return_paths(self):
        return self.file_data

    def directory(self):
        # Get the current directory
        current_directory = self.directory_path or os.getcwd()
        
        # List all files in the directory
        files = os.listdir(current_directory)
        
        # Collect file details
        self.file_data = []
        for file in files:
            file_path = os.path.join(current_directory, file)
            if os.path.isfile(file_path):
                file_info = {
                    "name": file,
                    "size": os.path.getsize(file_path),
                    "last_update": pathlib.Path(file_path).stat().st_mtime,
                    "path": file_path
                }
                if file_info["name"] != self.file_data:
                    self.file_data.append(file_info)
        return self.file_data
        
        # Print the collected data
        for data in self.file_data:
            print(f"Name: {data['name']}, Size: {data['size']} bytes, Last Update: {data['last_update']}, Path: {data['path']}")
        #return self.file_data

    def filter_files(self):
        d1 = c_db.data("files_data.db")
        new_files = []
        for data in self.file_data:
            if not d1.is_file_record_exists(data["name"]):
                new_files.append(data)
            elif d1.is_file_record_exists(data["name"] and d1.get_file_record()[3] != data["update_date"]):
                new_files.append(data)
        self.file_data = new_files
        print("Filtered files len:", len(self.file_data))
        

    def add_to_database(self):
        d1 = c_db.data("files_data.db")
        for data in self.file_data:
            d1.add_file_record(data["name"], data["size"], data["last_update"])
    
    def run(self):
        self.directory()
        self.filter_files()
        self.add_to_database()
        d1 = c_db.data("files_data.db")
        d1.print_all_records()
        

def get_messge():
    #files = directory()
    #add_to_database(files)
    pass


def main():
    # Example usage
    #directory_path = input("Enter the directory path (or press Enter for current directory): ").strip()
    #directory_path =  "C:\\Data\\roy\\school\\סייבר\\cloud\\copy"
    directory_path =  Path(r"C:\Data\roy\school\cyber\cloud\copy") 
    #directory_path =  "C:/Data/roy/school/cyber/cloud/copy"
    #ar_dir = ar_directory(directory_path)
    x = ar_directory(directory_path)
    y = x.return_paths()
    for data in y:
        print(f"Name: {data['name']}, Size: {data['size']} bytes, Last Update: {data['last_update']}, Path: {data['path']}")
    #ar_dir.directory()
    #add_to_database(ar_dir.file_data)

if __name__ == "__main__":
    main()