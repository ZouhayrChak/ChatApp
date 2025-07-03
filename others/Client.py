import socket
import threading
import json

def send(sock, data):
    sock.sendall(json.dumps(data).encode())
    response = json.loads(sock.recv(4096).decode())
    return response

def sign_up(sock):
    nom = input("Nom: ")
    prenom = input("Prenom: ")
    username = input("Username: ")
    password = input("Password: ")
    return send(sock, {"action": "signup", "nom": nom, "prenom": prenom, "username": username, "password": password})

def sign_in(sock):
    username = input("Username: ")
    password = input("Password: ")
    response = send(sock, {"action": "signin", "username": username, "password": password})
    return response, username

def chat_interface(sock, username, friend):
    msgs = send(sock,{"action": "messages","username": username ,"friendname": friend})

    msgs = msgs.get("messages", [])
    for msg in msgs:
        print(f"{msg[0]}: {msg[1]}")

    def receive():
        
        while True:
            try:
                data = sock.recv(4096).decode()
                if not data:
                    break
                msg = json.loads(data)
                if msg.get("type") == "incoming_message":
                    if msg['from'] == friend: 
                        print(f"\n{msg['from']}: {msg['message']}")
                    else:
                        print(f"notification from {msg['from']}")
            except Exception as e:
                print(f"Receive error: {e}")
                break

    def write():
        while True:
            msg = input("")
            data = {
                "action": "send_message",
                "username": username,
                "friendname": friend,
                "message": msg
            }
            sock.sendall(json.dumps(data).encode())

    th1 = threading.Thread(target=receive,daemon=True)
    th2 = threading.Thread(target=write,daemon=True)

    th1.start()
    th2.start()

    while True:
        pass

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("127.0.0.1", 80))

        choice = input("Do you want to signup or signin? ").strip().lower()
        if choice == "signup":
            print(sign_up(sock))
            return

        auth_response, username = sign_in(sock)
        if auth_response["status"] != "ok":
            print("Login failed.")
            return

        response = send(sock, {"action": "friends", "username": username})
        friends = response.get("friends", [])
        print("Your friends:", ", ".join(friends))

        active_user = input("Enter a friend's name to chat with: ")
        chat_interface(sock, username, active_user)

if __name__ == "__main__":
    main()
