from Actions.sql import init_db
from Actions.User import User
import socket
import threading
import json

connected_users = {} 

def handle_signin(conn, username, password):
    user = User("", "", username=username, password=password)
    if user.login_success():
        connected_users[username] = conn 
        conn.send(json.dumps({"status": "ok", "message": "Login successful"}).encode())
    else:
        conn.send(json.dumps({"status": "fail", "message": "Invalid credentials"}).encode())

def handle_signup(conn, nom, prenom, username, password):
    user = User(nom, prenom, username, password)
    if user.register():
        conn.send(json.dumps({"status": "ok", "message": "Registration successful"}).encode())
    else:
        conn.send(json.dumps({"status": "fail", "message": "Username already exists"}).encode())

def handle_client(conn):
    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break

            request = json.loads(data)
            action = request.get("action")

            if action == "signup":
                handle_signup(conn, request["nom"], request["prenom"], request["username"], request["password"])

            elif action == "signin":
                handle_signin(conn, request["username"], request["password"])

            elif action == "friends":
                user = User("", "", username=request["username"], password="")
                friends = [f[0] for f in user.getFriends()]
                conn.send(json.dumps({"type":"friends","friends": friends}).encode())

            elif action == "messages":
                u1 = User("", "", username=request["username"], password="")
                u2 = User("", "", username=request["friendname"], password="")
                msgs1 = [(request["username"], m[0]) for m in u1.getMessages(request["friendname"])]
                msgs2 = [(request["friendname"], m[0]) for m in u2.getMessages(request["username"])]
                all_msgs = sorted(msgs1 + msgs2, key=lambda x: x[1])
                conn.send(json.dumps({"type":"messages", "messages": all_msgs}).encode())

            elif action == "send_message":
                u = User("", "", username=request["username"], password="")
                success = u.chat(request["friendname"], request["message"])
                print(request["friendname"], request["message"])
                receiver_sock = connected_users.get(request["friendname"])
                if receiver_sock:
                    try:
                        receiver_sock.send(json.dumps({
                            "type": "incoming_message",
                            "from": request["username"],
                            "message": request["message"]
                        }).encode())
                    except Exception as e:
                        print(f"Push failed: {e}")

                conn.send(json.dumps({"status": "ok" if success else "fail"}).encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        for uname, sock_obj in list(connected_users.items()):
            if sock_obj == conn:
                del connected_users[uname]
                break
        conn.close()

if __name__ == "__main__":
    init_db()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("", 80))
        server.listen(5)
        print("Server started on port 80")
        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle_client, args=(conn,),daemon=True).start()