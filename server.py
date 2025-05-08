import socket
import base64
import os
from user_database import check_login, add_user, user_exists

HOST = '0.0.0.0'
PORT = 5002
BUFFER_SIZE = 4096
USER_ROOT = "user_data"   # top-level directory for all users

# ensure user data root exists
os.makedirs(USER_ROOT, exist_ok=True)

def ensure_user_dir(username):
    path = os.path.join(USER_ROOT, username)
    os.makedirs(path, exist_ok=True)
    return path

def handle_client(conn):
    try:
        # 1) First message must be AUTH: either LOGIN or SIGNUP
        msg = conn.recv(BUFFER_SIZE).decode()
        cmd, *parts = msg.strip().split("|")

        if cmd == "SIGNUP":
            username, password = parts
            if user_exists(username):
                return conn.send(b"USERNAME_EXISTS")
            add_user(username, password)
            ensure_user_dir(username)
            conn.send(b"SIGNUP_SUCCESS")
            return

        if cmd == "LOGIN":
            username, password = parts
            if not check_login(username, password):
                return conn.send(b"LOGIN_FAIL")
            # successful login → let them proceed
            conn.send(b"LOGIN_SUCCESS")
        else:
            return conn.send(b"ERROR: AUTH REQUIRED")

        # 2) After LOGIN_SUCCESS, enter command loop
        user_dir = ensure_user_dir(username)

        msg = conn.recv(BUFFER_SIZE).decode()
        if msg.startswith("PROJECT_LIST"):
            # list all projects for the user
            projects = os.listdir(user_dir)
            if not projects:
                conn.send(b"NO_PROJECTS")
            else:
                conn.send("|".join(projects).encode())
                
        msg = conn.recv(BUFFER_SIZE).decode()
        if msg.startswith("CREATE_PROJECT"):
            _, project_type, project_name = msg.split("|")
            project_path = os.path.join(user_dir, project_name)
            if os.path.exists(project_path):
                conn.send(b"PROJECT_EXISTS")
            else:
                os.makedirs(project_path)
                conn.send(b"PROJECT_CREATED")

        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            header = data.decode(errors="ignore")
            if header.startswith("UPLOAD"):
                # header format: UPLOAD|filename|size\n
                line, rest = header.split("\n", 1)
                _, filename, b64size = line.split("|")
                b64size = int(b64size)

                conn.send(b"READY_TO_RECEIVE")
                # collect exactly b64size bytes from socket
                received = rest.encode()  # any leftover after the newline
                while len(received) < b64size:
                    received += conn.recv(BUFFER_SIZE)

                file_bytes = base64.b64decode(received[:b64size])
                #save_path = os.path.join(user_dir, filename)
                save_path = os.path.join(project_path, filename)
                with open(save_path, "wb") as f:
                    f.write(file_bytes)
                conn.send(b"UPLOAD_SUCCESS")

            elif header.startswith("DOWNLOAD"):
                # header: DOWNLOAD|filename
                _, filename = header.strip().split("|")
                #file_path = os.path.join(user_dir, filename)
                file_path = os.path.join(project_path, filename)
                if not os.path.exists(file_path):
                    conn.send(b"ERROR|FILE_NOT_FOUND")
                    continue

                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read())
                size = len(b64)
                conn.send(f"DOWNLOAD|{size}".encode())
                ack = conn.recv(BUFFER_SIZE)
                if ack == b"READY":
                    conn.sendall(b64)
            else:
                conn.send(b"UNKNOWN_COMMAND")

    except Exception as e:
        print("Server error:", e)
        try: conn.send(b"ERROR")
        except: pass

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            print("→ Connection:", addr)
            handle_client(conn)
            conn.close()

if __name__ == "__main__":
    start_server()
