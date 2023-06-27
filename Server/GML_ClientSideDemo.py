import errno
import socket
import xmlrpc.client as rpc

rpc_file = rpc.ServerProxy('http://%s:%s' % ("10.10.20.4", 8999))
result = False

try:
    result = rpc_file.hello()
except socket.error as error:
    if error.errno == errno.ECONNREFUSED:
        print("Symlink Server is NOT running.")

tw_username, allow_projects = rpc_file.cgtw_login("luchenglin", "abc")

print(tw_username)
print(allow_projects)
