import tkinter as tk
import threading
import socket
import json


def interface(sock):
    root = tk.Tk()
    root.title("Chat App")
    root.geometry("400x500")
    button_in = tk.Button(root,text="sign in",command=lambda: signin_gui(root,sock))
    button_in.pack()
    button_up = tk.Button(root,text="sign up",command=lambda: signup_gui(root,sock))
    button_up.pack()

    root.mainloop()



def signin_gui(root,sock):
    sign_in = tk.Toplevel(root)
    sign_in.title("Login")
    sign_in.geometry("400x500")
    username = tk.Entry(sign_in)
    username.pack()

    password = tk.Entry(sign_in)
    password.pack()
    
    button = tk.Button(sign_in,command=lambda: signin(username.get(),password.get(),sign_in,root,sock))
    button.pack()

    sign_in.mainloop()

def signup_gui(root,sock):
    sign_up = tk.Toplevel(root)
    sign_up.title("Registration")
    sign_up.geometry("400x500")
    
    nom = tk.Entry(sign_up)
    nom.pack()

    prenom = tk.Entry(sign_up)
    prenom.pack()

    username = tk.Entry(sign_up)
    username.pack()

    password = tk.Entry(sign_up)
    password.pack()
    
    button = tk.Button(sign_up,command=lambda: signup(nom.get(),prenom.get(),username.get(),password.get(),sign_up,sock))
    button.pack()
  




def signin(username,password,sign_in,root,sock):
    res = send(sock, {"action": "signin", "username": username, "password": password})
    if res["status"] != "ok":
            label = tk.Label(sign_in,text="username failed!")
            label.pack()
            return
    sign_in.destroy()
    root.destroy()
    chat(username,sock)
    
    


def send(sock, data):
    try:
        sock.sendall(json.dumps(data).encode())
        response = json.loads(sock.recv(4096).decode())
        return response
    except Exception as e:
        return {"status":"error", "message":str(e)}



def signup(nom,prenom,username,password,root,sock):
    res = send(sock, {"action": "signup", "nom": nom, "prenom": prenom, "username": username, "password": password})

    if res['status'] != "ok":
        label = tk.Label(root,text="registration failed; The username is already there!")
        label.pack()
        return

    root.destroy()
    


def chat(username,sock):
    root = tk.Tk()
    root.title(f"{username}'s Chat")
    root.geometry("400x500")

    response = send(sock, {"action": "friends", "username": username})
    friends = response.get("friends", [])
    
    for friend in friends:
        button = tk.Button(root,text=friend,command=lambda f=friend: chat_with_friend(username,f,sock))
        button.pack(side="top")

    root.mainloop()
   




def chat_with_friend(username,friend,sock):
    newroot = tk.Toplevel()
    newroot.title("Chatting")
    newroot.geometry("400x500")

    label = tk.Label(newroot,text=f" Chat with {friend}")
    label.pack(side="top")

    out = tk.Button(newroot,text="out",command=newroot.destroy)
    out.pack()

    msgs = send(sock,{"action": "messages","username": username ,"friendname": friend})
    
    entry = tk.Entry(newroot)
    entry.pack()
    button = tk.Button(newroot,text="send",command=lambda: write(username,friend,entry.get(),newroot))
    button.pack() 
    
    msgs = msgs.get("messages", [])
    for msg in msgs:
        tk.Label(newroot,text=f"{msg[0]}: {msg[1]}").pack()
    
    
    
    th = threading.Thread(target=receive,args=(friend,newroot,sock))
    th.start()
    
    

    

def write(username,friend,msg,root):
    tk.Label(root,text=f"{username} : {msg}").pack()
    data = {
            "action": "send_message",
            "username": username,
            "friendname": friend,
            "message": msg
    }
    sock.sendall(json.dumps(data).encode())



    


def receive(friend,root,sock):
        while True:
            try:
                data = sock.recv(4096).decode()
                if not data:
                    break
                msg = json.loads(data)
                if msg.get("type") == "incoming_message":
                    if msg['from'] == friend: 
                        root.after(0,lambda: tk.Label(root,text=(f"{msg['from']}: {msg['message']}")).pack())
                    else:
                        print(f"notification from {msg['from']}")
            except Exception as e:
                print(f"Receive error: {e}")
                break


    


    
    
    




    
    







if __name__ == "__main__":
    active_user = None


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("127.0.0.1", 80))
        
        th = threading.Thread(target=interface,args=(sock,))
        th.start()
        th.join()

    
