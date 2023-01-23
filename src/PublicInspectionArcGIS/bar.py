import os 

class Tool() :
    def __init__(self):
        self.username = os.getenv("username")

    def hello(self):
        message = f'Hello {self.username}'
        return message
