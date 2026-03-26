import socket
import base64



SERVER_HOST = 'localhost' # Change to your server's IP if not running locally
SERVER_PORT = 5002
BUFFER_SIZE = 4096

class mange:
    def __init__(self):
        pass
    def choose(self):
        c = input("do you want to rent or buy a server? (rent/buy) ")
        if c.lower() == "rent":
            self.rent()
        elif c.lower() == "buy":
            self.buy()
    
    def rent(self):
        sure = input("do you want to rent a server? (y/n) ")
        if sure.lower() == "y":
            space_gb = int(input("how many space in GB do you want to rent? "))
            price = int(input("enter the amount of money you want to charge for 1 GB per month: "))
            ip = input("enter the IP address of the server you want to rent: ")
            self.send_command(f"RENT|{space_gb}|{price}|{ip}")   #You are renting a server with {space_gb} GB for {price} per month from [response username]
            

    def buy(self):
        sure = input("do you want to buy a server? (y/n) ")
        if sure.lower() == "y":
            space_gb = int(input("how many space in GB do you want to buy? "))
            price = int(input("enter the amount of money you want for 1 GB: "))
            self.send_command(f"BUY|{space_gb}|{price}")   #You are buying a server with {space_gb} GB for {price} per month from [response username] 

    def send_command(self, cmd):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.send(cmd.encode())
            response = s.recv(BUFFER_SIZE).decode()
            print(f"Server response: {response}")
        

        def run(self):
            pass