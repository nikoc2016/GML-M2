import socketserver

import GML


class CommandHandler(socketserver.BaseRequestHandler):
    def handle(self):
        command_line = self.request[0].strip()
        try:
            command_line = command_line.decode()
        except:
            pass

        sock = self.request[1]

        GML.Cmd.execute_command(
            command_line=command_line,
            client_socket=sock,
            client_address=self.client_address
        )
