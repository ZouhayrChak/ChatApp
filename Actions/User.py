from Actions.sql import *

class User:
    def __init__(self,nom,prenom,username,password):
            self.nom=nom or ""
            self.prenom=prenom or ""
            self.username=username or ""
            self.password=password or ""
             
            
    def register(self):
            if self.nom and self.prenom and self.username and self.password:
                return register_user(self.nom,self.prenom,self.username,self.password)
            return False
        
    def login_success(self):
        return check_user(self.username,self.password)   
    

    def chat(self,friendname,message):
        return sendMessage(self.username,friendname,message)
    
    def getMessages(self,friendname):
        return getMessages(self.username,friendname)

    def getFriends(self):
        return getFriends(self.username)         

    def __repr__(self):
        if self.nom and self.prenom and self.username:
            return f"name: {self.nom}, prenom: {self.prenom}, username : {self.username}"
        return "not a valid user"




