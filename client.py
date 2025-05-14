import socket
import base64
import os
from ar_mess import ar_directory
import threading
from pathlib import Path
import project_db
import time

SERVER_HOST = 'localhost'
SERVER_PORT = 5002
BUFFER_SIZE = 4096

class CloudClient:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self.username = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_and_receive(self, message):
        self.sock.send(message.encode())
        return self.sock.recv(BUFFER_SIZE).decode()

    def login(self):
        self.connect()
        username = input("Username: ")
        password = input("Password: ")
        response = self.send_and_receive(f"LOGIN|{username}|{password}")
        print("Server:", response)
        if response == "LOGIN_SUCCESS":
            self.username = username
            self.password = password
            return True
        self.disconnect()
        return False

    def check_text(self, text):
        alowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
        if len(text) == 0:
            return False
        for char in text:
            if char not in alowed_chars:
                return False
        return True
        

    def signup(self):
        self.connect()
        username = input("Choose username: ")
        password = input("Choose password: ")
        if self.check_text(username) == False or self.check_text(password) == False:
            print("Username or password cant be use, pls try again.")
            self.signup()
        response = self.send_and_receive(f"SIGNUP|{username}|{password}")
        print("Server:", response)
        if response == "SIGNUP_SUCCESS":
            self.username = username
            return True
        self.disconnect()
        return False

    def project_directory(self):
        #project_db.create_json_file()
        p1 = project_db.TextFileManager()
        response = self.send_and_receive("PROJECT_LIST")
        print("Server:", response)
        self.project_name = input("Enter project name or type New to create a new project: ").strip()
        if self.project_name.lower() == "new":
            self.project_name = input("Enter project name: ").strip()
            self.project_type = 1
            response = self.send_and_receive(f"CREATE_PROJECT|{self.project_type}|{self.project_name}")
            print("Server:", response)
            if response == "PROJECT_CREATED":
                self.project_directory = input("Enter project directory path: ").strip()
                if not os.path.exists(self.project_directory):
                    print("Directory not found.")
                    while True:
                        self.project_directory = Path(input("Enter project directory path: ").strip())
                        if os.path.exists(self.project_directory):
                            break
                p1.add_project(self.project_name, self.project_directory, self.project_type)
                x = ar_directory(Path(self.project_directory))
                files_data = x.return_paths()
                lis = [data["path"] for data in files_data]
                self.upload_all_files(lis)
                print(f"Project '{self.project_name}' created successfully.")
            else:
                print("Failed to create project.")

        else:
            response = self.send_and_receive(f"OPEN_PROJECT|{self.project_name}")
            print("Server:", response)
            if response == "PROJECT_NOT_FOUND":
                print("Project not found.")
                self.project_directory()
            else:
                print(f"entring '{self.project_name}'.")
                self.project_directory = p1.get_project_path(self.project_name)

    def upload_file(self, path=None):
        try:
            filename = os.path.basename(path)
            with open(path, "rb") as f:
                file_bytes = f.read()
            b64 = base64.b64encode(file_bytes).decode()

            # Create a new socket for each upload to avoid threading conflicts
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as upload_sock:
                upload_sock.connect((self.host, self.port))

                # First login again to establish identity
                upload_sock.send(f"LOGIN|{self.username}|{self.password}".encode())
                response = upload_sock.recv(BUFFER_SIZE).decode().strip()
                if response != "LOGIN_SUCCESS":
                    raise Exception(f"Authentication failed: {response}")

                # Send project context
                current_project = os.path.basename(self.project_directory)
                upload_sock.send(f"OPEN_PROJECT|{self.project_name}".encode())
                response = upload_sock.recv(BUFFER_SIZE).decode().strip()
                if response != "PROJECT_OPENED":
                    raise Exception(f"Failed to open project context: {response}")

                # Now send upload command with correct format matching server expectations
                header = f"UPLOAD|{filename}|{len(b64)}"
                upload_sock.sendall((header).encode())

                ack = upload_sock.recv(BUFFER_SIZE).decode().strip()
                if ack != "READY_TO_RECEIVE":
                    raise Exception(f"Server did not accept file: {ack}")

                upload_sock.sendall(b64.encode())

                response = upload_sock.recv(BUFFER_SIZE).decode().strip()
                if response != "UPLOAD_SUCCESS":
                    raise Exception(f"Upload failed: {response}")

            print(f"[{threading.current_thread().name}] Uploaded: {filename}")

        except Exception as e:
            print(f"[ERROR] Failed to upload {path}: {e}")

    def upload_all_files(self, file_paths, max_threads=5):
        semaphore = threading.Semaphore(max_threads)
        threads = []

        def thread_upload(path):
            with semaphore:
                try:
                    self.upload_file(path)
                except Exception as e:
                    print(f"[ERROR] Failed to upload {path}: {e}")

        for path in file_paths:
            t = threading.Thread(target=thread_upload, args=(path,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print("✅ All uploads finished.")

    def run(self):
        while True:
            action = input("Login or Signup? ").lower()
            if action == "login" and self.login():
                break
            elif action == "signup" and self.signup():
                break
            else:
                print("Try again.")

        print(f"Welcome, {self.username}!")
        self.project_directory()

        while True:
            cmd = input("Type 'upload' to send a file, 'upload all', or 'quit': ").lower()
            if cmd == "upload":
                path = input("Enter full path to file: ")
                self.upload_file(path)
            elif cmd == "upload all":
                d1 = ar_directory(Path(self.project_directory))
                files = d1.run()
                file_paths = [file['path'] for file in files]
                self.upload_all_files(file_paths)
            elif cmd == "quit":
                break
            else:
                print("Unknown command.")

            self.disconnect()

if __name__ == "__main__":
    client = CloudClient()
    client.run()