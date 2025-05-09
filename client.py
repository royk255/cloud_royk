import socket
import base64
import os
from ar_mess import ar_directory
import threading
from pathlib import Path
from project_db import TextFileManager
import time
#SERVER_HOST = '127.0.0.1'
#SERVER_PORT = 5002
SERVER_HOST = 'localhost'  # or your server IP
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
            return True
        self.disconnect()
        return False

    def signup(self):
        self.connect()
        username = input("Choose username: ")
        password = input("Choose password: ")
        response = self.send_and_receive(f"SIGNUP|{username}|{password}")
        print("Server:", response)
        if response == "SIGNUP_SUCCESS":
            self.username = username
            return True
        self.disconnect()
        return False

    def project_directory(self):
        response = self.send_and_receive("PROJECT_LIST")
        print("Server:", response)
        p1 = TextFileManager()
        project_name = input("Enter project name or type New to create a new project: ").strip()
        if project_name.lower() == "new":
            project_name = input("Enter project name: ").strip()
            project_type = input("Enter project type:\n1-backup only\n2-save copy of a dircotory").strip()
            response = self.send_and_receive(f"CREATE_PROJECT|{project_type}|{project_name}")
            print("Server:", response)
            if response == "PROJECT_CREATED":
                self.project_directory = input("Enter project directory path: ").strip()
                if not os.path.exists(self.project_directory):
                    print("Directory not found.")
                    while True:
                        self.project_directory = input("Enter project directory path: ").strip()
                        if os.path.exists(self.project_directory):
                            p1.add_line(self.project_directory)
                            break
                x = ar_directory(Path(self.project_directory))
                files_data = x.return_paths()
                lis = [data["path"] for data in files_data]
                self.upload_all_files(lis)
                print(f"Project '{project_name}' created successfully.")
            else:
                print("Failed to create project.")
                
        else:
            response = self.send_and_receive(f"OPEN_PROJECTS|{project_name}")
            print("Server:", response)
            if response == "PROJECT_NOT_FOUND":
                print("Project not found.")
                self.project_directory()
            else:
                print(f"entring '{project_name}'.")
                self.project_directory = p1.get_line_by_last_part(project_name)
                



    def upload_file(self, path=None):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_HOST, SERVER_PORT))

                filename = os.path.basename(path)
                filesize = os.path.getsize(path)

                # Send upload header (simple protocol: UPLOAD|filename|filesize\n)
                header = f"UPLOAD|{filename}|{filesize}\n"
                s.sendall(header.encode())

                # Wait for server "OK"
                ack = s.recv(1024).decode().strip()
                if ack != "OK":
                    raise Exception(f"Server did not accept file: {ack}")

                # Send file contents as base64
                with open(path, "rb") as f:
                    while chunk := f.read(4096):
                        encoded = base64.b64encode(chunk)
                        s.sendall(encoded + b"\n")

                # Optionally wait for a final confirmation
                result = s.recv(1024).decode().strip()
                if result != "DONE":
                    raise Exception(f"Upload failed: {result}")

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
            cmd = input("Type 'upload' to send a file or 'quit': ").lower()
            if cmd == "upload":
                self.upload_file()
            elif cmd == "upload all":
                d1 = ar_directory(Path(self.project_directory))
                d1.run()
            elif cmd == "quit":
                break
            else:
                print("Unknown command.")

        self.disconnect()

if __name__ == "__main__":
    client = CloudClient()
    client.run()




"""
x = ar_directory(Path(self.project_directory))
                files_data = x.return_paths()
                lis = [data["path"] for data in files_data]
                self.upload_all_files(lis)"""