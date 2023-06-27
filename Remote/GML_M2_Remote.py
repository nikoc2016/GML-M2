import socket
import sys

HOST, PORT = "localhost", 3721

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)

print("GML M2 Remote V1")

while True:
    user_input = input("$ ")
    try:
        sock.sendto(bytes(user_input, "utf-8"), (HOST, PORT))
        received = str(sock.recv(1024), "utf-8")
        print(received)
    except Exception as e:
        print(repr(e))
