import socketserver
import threading

import GML
from GML_Cmd.CommandHandler import CommandHandler


class CommandServer:
    def __init__(self):
        self.udp_thread = None

    def launch(self):
        self.stop()
        self.udp_thread = self.UDP_Thread()
        self.udp_thread.start()

    def stop(self):
        try:
            self.udp_thread.stop()
            self.udp_thread.join()
        except:
            pass
        self.udp_thread = None

    class UDP_Thread(threading.Thread):
        def __init__(self):
            super(CommandServer.UDP_Thread, self).__init__()
            self.udp_server = None

        def run(self):
            self.udp_server = socketserver.UDPServer((GML.app_command_host,
                                                      GML.app_command_port),
                                                     CommandHandler)
            self.udp_server.serve_forever()

        def stop(self):
            self.udp_server.server_close()
