# encoding=utf-8

"""
Version History

V1.0.0 - Hello(), cgtw_login
"""

import subprocess
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
import time

from GML_CGT import cgtw_func

VERSION = "1.0.0"


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def main():
    # Create server
    server = SimpleXMLRPCServer(("0.0.0.0", 8999), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()
    server.register_function(hello, 'hello')
    server.register_function(cgtw_login, "cgtw_login")

    print(hello())

    # Run the server's main loop
    server.serve_forever()


# Primary Functions
def hello():
    result = "Hello, GML-M2 SERVER V" + VERSION + ": " + exec_os_command("uname")
    return result


def sync():
    time_out = 5
    while time_out > 0:
        time_out -= 1
        print(time_out)
        time.sleep(1)


def cgtw_login(username, password):
    try:
        tw = cgtw_func.login_in_cgtw(user=username, password=password)
        project_data = cgtw_func.get_allowed_projects(tw)
        allow_projects = [project.get('project.code')
                          for project in project_data
                          if project.get('project.code') and project.get('project.database')
                          ]
        tw_username = cgtw_func.get_account_name(tw)
        return tw_username, allow_projects
    except Exception as e:
        print("GML_Core::cgtw_login()::Login failed.")
        return None, None


def exec_os_command(cmd):
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()

    if not stderr:
        result = str(stdout)
        return result
    else:
        error_msg = str(stderr)
        return error_msg


if __name__ == "__main__":
    main()
