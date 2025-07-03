import tkinter as tk
import threading
import socket
import json
import time

chat_windows = {}

def interface(sock):
    root = tk.Tk()
    root.title("Chat App")
    root.geometry("400x500")
    root.tk_setPalette("black")

    tk.Label(root, text="Welcome to Chat App", font=("Helvetica", 16),bg="red").pack(pady=20)
    tk.Button(root, text="Sign In", width=20, command=lambda: signin_gui(root, sock)).pack(pady=10)
    tk.Button(root, text="Sign Up", width=20, command=lambda: signup_gui(root, sock)).pack(pady=10)

    root.mainloop()

def signin_gui(parent, sock):
    sign_in = tk.Toplevel(parent)
    sign_in.title("Login")
    sign_in.geometry("400x300")

    tk.Label(sign_in, text="Username").pack()
    username_entry = tk.Entry(sign_in)
    username_entry.pack()

    tk.Label(sign_in, text="Password").pack()
    password_entry = tk.Entry(sign_in, show="*")
    password_entry.pack()

    def do_signin():
        username = username_entry.get()
        password = password_entry.get()
        res = send(sock, {"action": "signin", "username": username, "password": password})
        if res["status"] != "ok":
            tk.Label(sign_in, text="Login failed!", fg="red").pack()
            return
        sign_in.destroy()
        parent.withdraw()  # Don't destroy the main loop
        chat(username, sock)

    tk.Button(sign_in, text="Login", command=do_signin).pack(pady=10)

def signup_gui(parent, sock):
    sign_up = tk.Toplevel(parent)
    sign_up.title("Registration")
    sign_up.geometry("400x400")

    tk.Label(sign_up, text="First Name").pack()
    nom = tk.Entry(sign_up)
    nom.pack()

    tk.Label(sign_up, text="Last Name").pack()
    prenom = tk.Entry(sign_up)
    prenom.pack()

    tk.Label(sign_up, text="Username").pack()
    username = tk.Entry(sign_up)
    username.pack()

    tk.Label(sign_up, text="Password").pack()
    password = tk.Entry(sign_up, show="*")
    password.pack()

    def do_signup():
        res = send(sock, {"action": "signup", "nom": nom.get(), "prenom": prenom.get(),
                          "username": username.get(), "password": password.get()})
        if res["status"] != "ok":
            tk.Label(sign_up, text="Registration failed. Username exists.", fg="red").pack()
        else:
            tk.Label(sign_up, text="Registered successfully!", fg="green").pack()

    tk.Button(sign_up, text="Register", command=do_signup).pack(pady=10)

def send(sock, data):
    try:
        sock.sendall(json.dumps(data).encode())
        return json.loads(sock.recv(4096).decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}

def chat(username, sock):
    chat_root = tk.Toplevel()
    chat_root.title(f"{username}'s Chat")
    chat_root.geometry("400x500")

    tk.Label(chat_root, text="Your Friends", font=("Helvetica", 14)).pack(pady=10)

    response = send(sock, {"action": "friends", "username": username})
    friends = response.get("friends", [])

    for friend in friends:
        tk.Button(chat_root, text=friend, width=30,
                  command=lambda f=friend: chat_with_friend(username, f, sock)).pack(pady=2)
        
    threading.Thread(target=receive_loop, args=(sock,chat_root), daemon=True).start()
    
        


def chat_with_friend(username, friend, sock):
    global messages
    if friend in chat_windows:
        return  # Already open

    root = tk.Toplevel()
    root.title(f"Chat with {friend}")
    root.geometry("400x500")

    tk.Label(root, text=f"Chat with {friend}", font=("Helvetica", 14)).pack(pady=5)

    messages_frame = tk.Frame(root)
    messages_frame.pack(fill="both", expand=True)

    entry = tk.Entry(root)
    entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

    def send_msg():
        msg = entry.get()
        if msg:
            tk.Label(messages_frame, text=f"{username}: {msg}", anchor="w", justify="left").pack(anchor="w")
            data = {
                "action": "send_message",
                "username": username,
                "friendname": friend,
                "message": msg
            }
            sock.sendall(json.dumps(data).encode())
            entry.delete(0, tk.END)

    tk.Button(root, text="Send", command=send_msg).pack(side="right", padx=5)
    sock.sendall(json.dumps({"action": "messages", "username": username, "friendname": friend}).encode())

    time.sleep(1)
    old_msgs = messages

    for msg in old_msgs:
        tk.Label(messages_frame, text=f"{msg[0]}: {msg[1]}", anchor="w", justify="left").pack(anchor="w")

    chat_windows[friend] = messages_frame
    

    def on_close():
        del chat_windows[friend]
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

def receive_loop(sock,chat_root):
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                break
            msg = json.loads(data)
            if msg.get("type") == "incoming_message":
                sender = msg["from"]
                text = msg["message"]
                if sender in chat_windows:
                    frame = chat_windows[sender]
                    frame.after(0, lambda: tk.Label(frame, text=f"{sender}: {text}", anchor="w", justify="left").pack(anchor="w"))
                else:
                    chat_root.after(0,lambda: tk.Label(chat_root,text=f"Message from {sender}").pack(side="top"))
            elif msg.get("type") == "messages":
                global messages
                messages = msg.get("messages")


                    
        except Exception as e:
            print(f"Receive error: {e}")
            break

if __name__ == "__main__":
    messages = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 80))
    interface(sock)     
    

    
