import socket
import base64
import os

SERVER_HOST = '127.0.0.1'
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
        project_name = input("Enter project name or type New to create a new project: ").strip()
        if project_name.lower() == "new":
            project_name = input("Enter project name: ").strip()
            project_type = input("Enter project type:\n1-backup only\n2-save copy of a dircotory").strip()
            response = self.send_and_receive(f"CREATE_PROJECT|{project_type}|{project_name}")
            print("Server:", response)
            if response == "PROJECT_CREATED":
                print(f"Project '{project_name}' created successfully.")
            else:
                print("Failed to create project.")
        else:
            response = self.send_and_receive(f"LIST_PROJECTS|{self.username}")
            print("Server:", response)
            if response == "PROJECT_NOT_FOUND":
                print("Project not found.")
                self.project_directory()
            else:
                print(f"entring '{project_name}'.")



    def upload_file(self):
        filepath = input("Enter path to file: ").strip()
        if not os.path.exists(filepath):
            print("File not found.")
            return

        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            data = f.read()

        b64_data = base64.b64encode(data)
        size = len(b64_data)

        # Send header
        header = f"UPLOAD|{filename}|{size}\n"
        self.sock.send(header.encode())

        # Wait for server's go-ahead
        if self.sock.recv(BUFFER_SIZE).decode() != "READY_TO_RECEIVE":
            print("Server rejected file upload.")
            return

        self.sock.sendall(b64_data)
        result = self.sock.recv(BUFFER_SIZE).decode()
        if result == "UPLOAD_SUCCESS":
            print("Upload complete.")
        else:
            print("Upload failed:", result)

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
            elif cmd == "quit":
                break
            else:
                print("Unknown command.")

        self.disconnect()

if __name__ == "__main__":
    client = CloudClient()
    client.run()
