import socket
import base64
import os
import threading
#from user_database import check_login, add_user, user_exists
from ar_mess import DatabaseManager as d_manager
from ar_mess import JSONConfig as j_config



HOST = '0.0.0.0'
PORT = 5002
BUFFER_SIZE = 4096
USER_ROOT = "user_data"  # top-level directory for all users

# ensure user data root exists
os.makedirs(USER_ROOT, exist_ok=True)

def ensure_user_dir(username):
    path = os.path.join(USER_ROOT, username)
    os.makedirs(path, exist_ok=True)
    return path

def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    try:
        username = None
        project_path = None
        
        user_dir = None
        msg = conn.recv(BUFFER_SIZE).decode()
        cmd, *parts = msg.strip().split("|")
        db_u = d_manager("user_data.db")

        """"
        if cmd == "SIGNUP":
            username, password, email = parts
            if db_u.user_exists(username):
                return conn.send(b"USERNAME_EXISTS")
            db_u.add_user(username, password, email)
            user_dir = ensure_user_dir(username)
            conn.send(b"SIGNUP_SUCCESS")
        """
        if cmd == "LOGIN":
            username, password = parts
            if not db_u.check_login(username, password):
                return conn.send(b"LOGIN_FAIL")
            conn.send(b"LOGIN_SUCCESS")
            user_dir = ensure_user_dir(username)

        #elif cmd.startswith("CREATE_PROJECT"):
        elif cmd == "CREATE_PROJECT":
                conn.send(b"bla")
                msg_2 = conn.recv(BUFFER_SIZE).decode()
                cmd_2, *parts_2 = msg_2.strip().split("|")
                all_good =True
                if cmd_2 == "SIGNUP":                #realy not sure
                    username, password, email = parts_2
                    if db_u.user_exists(username):
                        conn.send(b"USERNAME_EXISTS")
                        #all_good = False
                    db_u.add_user(username, password, email)
                    user_dir = ensure_user_dir(username)
                    conn.send(b"SIGNUP_SUCCESS")
                else:
                    conn.send(b"ERROR: AUTH REQUIRED")
                    #all_good = False
                #_, project_name, ip, space,price, code = msg.split("|") #why do i send the ip
                _, project_name, space,price, code = msg.split("|") #why do i send the ip
                project_path = os.path.join(user_dir, project_name)
                if os.path.exists(project_path):
                    conn.send(b"PROJECT_EXISTS")
                else:
                    if code == "0":
                        db_u.add_to_pay(username,price)
                        j_config("config.json").set_value("space_left", j_config("config.json").get_value("space_left") - int(space))
                    elif code != j_config("config.json").get_value("code"):
                        conn.send(b"INVALID_CODE")
                        alll_good = False
                    if int(space) > j_config("config.json").get_value("space_left"):
                        conn.send(b"NOT_ENOUGH_SPACE")
                        all_good = False
                    if all_good:
                        os.makedirs(project_path)
                        conn.send(b"PROJECT_CREATED")
                    else:
                        conn.send(b"PROJECT_CREATION_FAILED")

        else:
            return conn.send(b"ERROR: AUTH REQUIRED")

        while True:
            msg = conn.recv(BUFFER_SIZE).decode()
            if not msg:
                break

            if msg.startswith("PROJECT_LIST"):    #dosnt need to happen
                projects = os.listdir(user_dir)
                if not projects:
                    conn.send(b"NO_PROJECTS")
                else:
                    conn.send("|".join(projects).encode())

            #signup was here

            elif msg.startswith("OPEN_PROJECT"):
                _, project_name = msg.split("|")
                project_path = os.path.join(user_dir, project_name)
                if not os.path.exists(project_path):
                    conn.send(b"PROJECT_NOT_FOUND")
                else:
                    conn.send(b"PROJECT_OPENED")
            elif msg.startswith("UPLOAD"):
                try:
                    # Make sure we have an active project
                    if project_path is None:
                        conn.send(b"ERROR|NO_ACTIVE_PROJECT")
                        continue
                        
                    # header: UPLOAD|filename|size
                    header_parts = msg.split("|")
                    if len(header_parts) != 3:
                        conn.send(b"ERROR|INVALID_UPLOAD_HEADER")
                        continue

                    _, filename, b64size = header_parts
                    b64size = int(b64size)
                    if b64size > 0:
                        conn.send(b"READY_TO_RECEIVE")

                    received = b""
                    while len(received) < b64size:
                        chunk = conn.recv(min(BUFFER_SIZE, b64size - len(received)))
                        if not chunk:
                            break
                        received += chunk

                    file_bytes = base64.b64decode(received)
                    save_path = os.path.join(project_path, filename)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    with open(save_path, "wb") as f:
                        f.write(file_bytes)

                    conn.send(b"UPLOAD_SUCCESS")
                    print(f"[+] File '{filename}' uploaded to {project_path}")    #  cmd|par1|par2
                    
                except Exception as e:
                    print(f"[UPLOAD ERROR] {e}")
                    conn.send(f"ERROR|UPLOAD_FAILED: {str(e)}".encode())

            elif msg.startswith("DOWNLOAD"):
                try:
                    _, filename = msg.strip().split("|")
                    if project_path is None:
                        conn.send(b"ERROR|NO_ACTIVE_PROJECT")
                        continue
                        
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
                except Exception as e:
                    print(f"[DOWNLOAD ERROR] {e}")
                    conn.send(b"ERROR|DOWNLOAD_FAILED")

            else:
                conn.send(b"UNKNOWN_COMMAND")

    except Exception as e:
        print(f"[SERVER ERROR] {e}")
        try:
            conn.send(f"ERROR|{str(e)}".encode())
        except:
            pass
    finally:
        conn.close()
        print(f"[-] Disconnected: {addr}")






def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[+] Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
