from socket import socket, error
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR, SHUT_WR
from threading import Thread

if __name__ == '__main__':
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    MESSAGE = b"Hello, World!"

    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE)

    sock = socket(AF_INET,  # Internet
                  SOCK_DGRAM)  # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
