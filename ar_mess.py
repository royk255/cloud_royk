import os
import c_db
import pathlib
from pathlib import Path
import threading
import time
import json
import sqlite3

class ar_directory:
    def __init__(self, project_name, directory_path=None):
        self.project_name = project_name
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
        d1 = c_db.data("files_data.db", self.project_name)
        new_files = []
        for data in self.file_data:
            if not d1.is_file_record_exists(data["name"]):
                new_files.append(data)
            elif d1.is_file_record_exists(data["name"] and d1.get_file_record(data["name"])[3] != data["last_update"]):
                new_files.append(data)
        self.file_data = new_files
        print("Filtered files len:", len(self.file_data))
    
    def print_all_records(self):
        d1 = c_db.data("files_data.db", self.project_name)
        d1.print_all_records()
    
    def add_file_record(self, name_of_file, file_size, update_date):
        d1 = c_db.data("files_data.db", self.project_name)
        d1.add_file_record(name_of_file, file_size, update_date)

    def add_to_database(self):
        d1 = c_db.data("files_data.db", self.project_name)
        for data in self.file_data:
            d1.add_file_record(data["name"], data["size"], data["last_update"])

    def clear_all_records(self):
        """
        Clear all tracked file records in local state and in the files DB.
        """
        self.file_data = []

        db_path = "files_data.db"
        d1 = c_db.data(db_path)

        if hasattr(d1, "clear_file_records"):
            d1.clear_file_records()
        elif hasattr(d1, "delete_all_files"):
            d1.delete_all_files()
        else:
            # fallback: direct sqlite delete (guess table name)
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("DELETE FROM files")
                conn.commit()
            finally:
                conn.close()

        print("ar_directory: all file records cleared")
    
    

    def run(self):
        #self.clear_all_records()
        self.directory()
        self.filter_files()
        #self.add_to_database()
        #d1 = c_db.data("files_data.db")
        #print("Database records:")
        #d1.print_all_records()
        #print("--------------------")
        return self.file_data
        

class DatabaseManager:
    def get_lowest_price_server(self, required_space):
        self.cursor.execute('''
            SELECT * FROM servers WHERE space >= ? ORDER BY price ASC LIMIT 1
        ''', (required_space,))
        return self.cursor.fetchone()
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                need_to_pay INTEGER NOT NULL DEFAULT 0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                project_name TEXT NOT NULL,
                username TEXT NOT NULL,
                ip TEXT NOT NULL,
                price INTEGER NOT NULL,
                curr_space INTEGER NOT NULL,
                max_space INTEGER NOT NULL,
                path TEXT NOT NULL
            )
        ''') #might have probkem with username in both tables
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY,
                user TEXT NOT NULL,
                user_ip TEXT NOT NULL,
                price REAL NOT NULL,
                space INTEGER NOT NULL
            )
        ''') #wrong need to be a diffrent db
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER SECONDARY KEY NOT NULL,
                name_of_file TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                update_date INTEGER NOT NULL
            )
        ''')
        self.connection.commit()

    def add_user(self, username, password, email, need_to_pay=0):
        self.cursor.execute('''
            INSERT INTO user_data (username, password, email, need_to_pay)
            VALUES (?, ?, ?, ?)
        ''', (username, password, email, need_to_pay))
        self.connection.commit()
    
    def add_to_pay(self, username, amount):
        self.cursor.execute('''
            UPDATE user_data SET need_to_pay = need_to_pay + ? WHERE username = ?
        ''', (amount, username))
        self.connection.commit()

    def sub_to_pay(self, username, amount):
        self.cursor.execute('''
            UPDATE user_data SET need_to_pay = need_to_pay - ? WHERE username = ?
        ''', (amount, username))
        self.connection.commit()

    def add_project(self, project_name, username, ip, price, curr_space, max_space, path):
        self.cursor.execute('''
            INSERT INTO projects (project_name, username, ip, price, curr_space, max_space, path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_name, username, ip, price, curr_space, max_space, path))
        self.connection.commit()

    def add_server(self, user, user_ip, price, space):
        self.cursor.execute('''
            INSERT INTO servers (user, user_ip, price, space)
            VALUES (?, ?, ?, ?)
        ''', (user, user_ip, price, space))
        self.connection.commit()

    def add_file(self, project_name, name_of_file, file_size, update_date):
        project_id = self.get_project_id(project_name)
        self.cursor.execute('''
            INSERT INTO files (project_id, name_of_file, file_size, update_date)
            VALUES (?, ?, ?, ?)
        ''', (project_id, name_of_file, file_size, update_date))
        self.connection.commit()

    def get_project_id(self, project_name):
        self.cursor.execute('SELECT id FROM projects WHERE project_name = ?', (project_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def remove_user(self, user_id):
        self.cursor.execute('DELETE FROM user_data WHERE id = ?', (user_id,))
        self.connection.commit()

    def remove_project(self, project_id):
        self.cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        self.connection.commit()

    def remove_server(self, server_id):
        self.cursor.execute('DELETE FROM servers WHERE id = ?', (server_id,))
        self.connection.commit()

    def user_exists(self, username):
        self.cursor.execute('SELECT * FROM user_data WHERE username = ?', (username,))
        return self.cursor.fetchone() is not None
        
        ger

    def get_projects_list(self):
        self.cursor.execute('SELECT project_name FROM projects')
        return [row[0] for row in self.cursor.fetchall()]
    
    def print_all_projects(self):
        self.cursor.execute('SELECT * FROM projects')
        for row in self.cursor.fetchall():
            print(row)
    
    def get_ip_by_project(self, project_name):
        self.cursor.execute('SELECT ip FROM projects WHERE project_name = ?', (project_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_project_path(self, project_name):
        self.cursor.execute('SELECT path FROM projects WHERE project_name = ?', (project_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.connection.close()
    
    def check_login(self, username, password):
        self.cursor.execute('SELECT * FROM user_data WHERE username = ? AND password = ?', (username, password))
        return self.cursor.fetchone() is not None
    
    def clear_data_base(self):
        self.cursor.execute('DELETE FROM user_data')
        self.cursor.execute('DELETE FROM projects')
        self.cursor.execute('DELETE FROM servers')
        self.cursor.execute('DELETE FROM files')
        self.connection.commit()

    def delete_file_record(self, project_name, name_of_file):
        project_id = self.get_project_id(project_name)
        self.cursor.execute('DELETE FROM files WHERE project_id = ? AND name_of_file = ?', (project_id, name_of_file))
        self.connection.commit()
    
    def get_file_record(self, project_name, name_of_file):
        project_id = self.get_project_id(project_name)
        self.cursor.execute('SELECT * FROM files WHERE project_id = ? AND name_of_file = ?', (project_id, name_of_file))
        return self.cursor.fetchone()
    def get_all_file_records(self, project_name):
        project_id = self.get_project_id(project_name)
        self.cursor.execute('SELECT * FROM files WHERE project_id = ?', (project_id,))
        return self.cursor.fetchall()
    def is_file_record_exists(self, project_name, name_of_file):
        project_id = self.get_project_id(project_name)
        self.cursor.execute('SELECT * FROM files WHERE project_id = ? AND name_of_file = ?', (project_id, name_of_file))
        return self.cursor.fetchone() is not None
    def filter_file_records(self, project_name, file_data_list):
        project_id = self.get_project_id(project_name)
        filtered_files = []
        for file_data in file_data_list:
            if not self.is_file_record_exists(project_name, file_data["name"]):       #need to add if date is diffrent
                filtered_files.append(file_data)
            else:
                record = self.get_file_record(project_name, file_data["name"])
                if record[3] != file_data["last_update"]:
                    filtered_files.append(file_data)
        return filtered_files
    def directory(self, project_name):
        """Get all files from project path with size, last change, name and path"""
        project_path = self.get_project_path(project_name)
        if not project_path:
            return []
        
        files = []
        try:
            for file in os.listdir(project_path):
                file_path = os.path.join(project_path, file)
                if os.path.isfile(file_path):
                    files.append({
                        "name": file,
                        "size": os.path.getsize(file_path),
                        "last_update": pathlib.Path(file_path).stat().st_mtime,
                        "path": file_path
                    })
        except Exception as e:
            print(f"Error reading directory: {e}")
        
        return files

    def run(self, project_name):
        file_data = self.directory(project_name)
        filtered_files = self.filter_file_records(project_name, file_data)
        return filtered_files
class JSONConfig:
    def __init__(self, filename):
        self.filename = filename
        self.data = {"max_space": 20, "space_left": 20, "code": ""}
        self.load()
    
    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
    
    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def set_value(self, key, value):
        self.data[key] = value
        self.save()
    
    def get_value(self, key):
        return self.data.get(key)

"""
# Example usage
db_manager = DatabaseManager("user_data.db")
db_manager.add_user("john_doe", "securepassword", "john@example.com", "192.168.1.1")
#db_manager.add_project("Project Alpha", 1, "192.168.1.1")
db_manager.add_server("john_doe", "192.168.1.1", 19.99, 100)
db_manager.close()
"""
def main():
    directory_path =  Path(r"C:\Data\roy\school\cyber\cloud\copy") 
    x = ar_directory(directory_path)
    y = x.return_paths()
    for data in y:
        print(f"Name: {data['name']}, Size: {data['size']} bytes, Last Update: {data['last_update']}, Path: {data['path']}")
"""
if __name__ == "__main__":
    d = DatabaseManager("project_data.db")
    d.clear_data_base()
    d = DatabaseManager("user_data.db")
    d.clear_data_base()
   """
#    main()