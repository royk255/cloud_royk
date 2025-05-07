import socket
import base64
import os

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5001
BUFFER_SIZE = 4096  # 4 KB chunks

def handle_client(conn):
    try:
        header = conn.recv(BUFFER_SIZE).decode()
        if not header.startswith("UPLOAD"):
            print("Unknown command")
            return

        _, filename, filesize = header.split("|")
        filesize = int(filesize)
        print(f"Receiving file: {filename} ({filesize} bytes)")

        conn.send(b"READY")  # Acknowledge the upload

        received_bytes = 0
        b64_data = b""
        while received_bytes < filesize:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk:
                break
            b64_data += chunk
            received_bytes += len(chunk)

        file_data = base64.b64decode(b64_data)
        with open(f"received_{filename}", "wb") as f:
            f.write(file_data)

        print(f"File {filename} received and saved.")
        conn.send(b"SUCCESS")
    except Exception as e:
        print("Error:", e)
        conn.send(b"ERROR")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            handle_client(conn)
            conn.close()

if __name__ == "__main__":
    start_server()
