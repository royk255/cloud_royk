import socket
import base64
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001
BUFFER_SIZE = 4096  # 4 KB

def upload_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_data = f.read()

    b64_data = base64.b64encode(file_data)
    filesize = len(b64_data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))

        # Send header
        header = f"UPLOAD|{filename}|{filesize}"
        s.send(header.encode())

        # Wait for READY
        response = s.recv(BUFFER_SIZE).decode()
        if response != "READY": 
            print("Server did not acknowledge.")
            return

        # Send the file in base64-encoded form
        s.sendall(b64_data)

        # Get final response
        final = s.recv(BUFFER_SIZE).decode()
        print("Server response:", final)

if __name__ == "__main__":
    upload_file("example.txt")  # Replace with your file path
