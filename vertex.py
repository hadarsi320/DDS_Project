from socket import socket, error
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR, SHUT_WR
from threading import Thread, Lock
from math import log2, ceil

FILE_DIR = 'input/'


def vertex(ID):
    input_file_name = 'input_vertex_' + str(ID) + '.txt'
    with open(FILE_DIR + input_file_name, 'r') as input_file:
        data = input_file.read().split('\n')
    graph_size = data[0]
    master = (int(data[1]), data[2])
    udp_port = data[3]
    tcp_port = data[4]
    is_root = True  # a vertex is a root if it has no parent
    parent = None
    if data[5] != 'None' and data[6] != 'None':
        is_root = False
        parent = (int(data[5]), data[6])
    elif data[5] != 'None' or data[6] != 'None':
        raise Exception('Input file is inconsistent')
    neighbors = []
    for i in range(7, len(data)-2, 2):
        neighbors.append((int(data[i]), data[i+1]))

    color = 0 if is_root else ID


def recolor(color, parent_color):
    """
    :param color: current node's color
    :param parent_color: node's parent's color
    :return: new color computed according to the algorithm
    """
    assert len(color) == len(parent_color)
    color = color[::-1]
    parent_color = parent_color[::-1]
    n = len(color)  # perhaps n+1
    i_v = None
    for i in range(len(color)):
        if color[i] != parent_color[i]:
            i_v = i
            break
    assert i_v is not None
    new_color = bin(i_v)[2:] + str(color[i_v])
    assert len(new_color) <= ceil(log2(n)) + 1
    return new_color.zfill(ceil(log2(n)) + 1)


def main():
    pass


if __name__ == '__main__':
    res = recolor(bin(15)[2:].zfill(10), bin(17)[2:].zfill(10))
    pass
