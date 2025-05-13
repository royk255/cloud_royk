import sqlite3
from datetime import datetime

class data:
    def __init__(self,db_name,reset=False):
        self.db_name = db_name
        self.reset = reset
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        if self.reset:
            # Drop the table if it exists
            cursor.execute('''DROP TABLE IF EXISTS files''')
        # Create the table again
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_of_file TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                update_date INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    # Function to add a new record to the table
    def add_file_record(self, name_of_file, file_size, update_date):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        #update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO files (name_of_file, file_size, update_date)
            VALUES (?, ?, ?)
        ''', (name_of_file, file_size, update_date))
        conn.commit()
        for row in cursor.execute("SELECT * FROM files").fetchall():
            print(row)
        conn.close()
    
    def get_file_records(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files")
        records = cursor.fetchall()
        conn.close()
        return records
    
    def is_file_record_exists(self, name_of_file):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE name_of_file=?", (name_of_file,))
        record = cursor.fetchone()
        conn.close()
        return record is not None
    
    def get_file_record(self, name_of_file):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE name_of_file=?", (name_of_file,))
        record = cursor.fetchone()
        conn.close()
        return record

    def delete_file_record(self, name_of_file):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE name_of_file=?", (name_of_file,))
        conn.commit()
        conn.close()

    def print_all_records(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files")
        records = cursor.fetchall()
        for record in records:
            print(record)
        conn.close()
    
    def clean_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files")
        conn.commit()
        conn.close()

    def __repr__(self):
        return f"FileRecord(name_of_file={self.name_of_file}, file_size={self.file_size}, update_date={self.update_date})"

    

# Example usage
if __name__ == "__main__":
    #db_name = "files_data.db"
    d1 = data("files_data.db",reset=True)
    d1.print_all_records()
    #d1.add_file_record("example.txt", 1024, 123456789)
    #print(d1.get_file_records())
    #for row in cursor.execute("SELECT * FROM files").fetchall():
    #    print(row)
#(1, 'example.txt', 1024, 123456789)