import socket
from threading import Thread
from math import log2, ceil

INPUT_DIR = 'input/'


def vertex(ID):

    input_file_name = 'input_vertex_' + str(ID) + '.txt'
    input_file = open(INPUT_DIR + input_file_name, 'r')

    graph_size = input_file.readline()
    master_port = input_file.readline()
    master_ip = input_file.readline()
    udp_listen_port = input_file.readline()
    tcp_listen_port = input_file.readline()

    master_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_address = (master_port)


    pass


def main():

    vertex('0001')
    pass


if __name__ == '__main__':
    main()
