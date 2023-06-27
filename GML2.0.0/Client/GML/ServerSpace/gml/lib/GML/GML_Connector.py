import select
import socket


class GMLConnector:
    def __init__(self, host="localhost", port=40000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)

    def get_feedback(self):
        read_ready, _, _ = select.select([self.sock], [], [], 0)
        if len(read_ready):
            try:
                received = str(self.sock.recv(1024), "gbk")
            except WindowsError as e:
                if e.winerror == 10054:
                    received = "FAIL Server Offline"
                else:
                    received = "FAIL " + str(e)
            return received
        return None

    def awake(self, target):
        command = "awake " + target
        self.free_command(command)

    def free_command(self, command):
        self.sock.sendto(bytes(command, "gbk"), (self.host, self.port))
