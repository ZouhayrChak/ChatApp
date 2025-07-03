import sqlite3
import bcrypt

DB_NAME = "ChatApp.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL       
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chat (
            username TEXT NOT NULL,
            friendname TEXT NOT NULL,
            message TEXT NOT NULL       
        )
    ''')

    
    conn.commit()
    conn.close()

def register_user(nom,prenom,username,password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor.execute("INSERT INTO Users (nom,prenom,username,password) VALUES (?, ?, ?, ?)", (nom ,prenom, username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM Users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False




def sendMessage(username,friendname,message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Chat (username,friendname,message) VALUES (?, ?, ?)", (username,friendname,message))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    

def getMessages(username,friendname):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM Chat WHERE username=? AND friendname=?", (username,friendname))
    result = cursor.fetchall()
    conn.close()
    if result:
        return result
    return []


def getFriends(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM Users WHERE username != ?", (username,))
    result = cursor.fetchall()
    conn.close()
    if result:
        return result
    return []

