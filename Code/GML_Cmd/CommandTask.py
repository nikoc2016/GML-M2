class CommandTask:
    def __init__(self,
                 command_id,
                 command_line,
                 receive_datetime,
                 client_socket,
                 client_address,
                 result=None,
                 send_datetime=None):
        self.command_id = command_id
        self.command_line = command_line
        self.receive_datetime = receive_datetime
        self.client_socket = client_socket
        self.client_address = client_address
        self.result = result
        self.send_datetime = send_datetime

    def __str__(self):
        return ("<CommandTask id=%i cmd=%s sock=%s addr=%s result=%s recv=%s send=%s>" %
                (self.command_id,
                 self.command_line,
                 self.client_socket,
                 self.client_address,
                 self.result,
                 self.receive_datetime,
                 self.send_datetime,)
                )
