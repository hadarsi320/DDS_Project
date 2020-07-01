from socket import socket, error
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR, SHUT_WR
from threading import Thread, Lock
from math import log2, ceil

# TODO update this code so it works out of the box
INPUT_DIR = 'input/'
OUTPUT_DIR = 'output/'


def vertex(ID):
    next_msg = f'next_{ID}'
    done_msg = f'done_{ID}'

    input_file_name = 'input_vertex_' + str(ID) + '.txt'
    with open(INPUT_DIR + input_file_name, 'r') as input_file:
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

    # Listens to neighbours
    tcp_socket = socket(AF_INET, SOCK_STREAM)  # TCP socket
    tcp_socket.bind(('', tcp_port))

    # Listens to master for round
    rounds_lock = Lock()
    master_listen_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket
    master_listen_socket.bind(('', udp_port))

    # Sends round end to master
    master_send_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket

    current_round = None
    while True:
        data, addr = master_listen_socket.recvfrom(4096)
        assert addr == master[1]
        if data.decode() == 'DIE':
            break
        elif data.decode() == '0':
            current_round = int(data.decode())
            tcp_socket.listen(len(neighbors))
            master_send_socket.send(('next'+str(id)))
        elif len(color) > 3:
            pass
        else:
            pass
    master_listen_socket.close()


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
