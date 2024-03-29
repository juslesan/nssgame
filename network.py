import socket

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost" # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
                                    # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
                                    # ipv4 address. This feild will be the same for all your clients.
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id, self.options = self.connect()
    def connect(self):
        self.client.connect(self.addr)
        res = self.client.recv(2048).decode()
        res = res.split(";")
        #print(res[1])
        return res[0], res[1].split(",")

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(8192).decode()
            return reply
        except socket.error as e:
            return str(e)