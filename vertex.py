from socket import socket, error
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR, SHUT_WR
from threading import Thread, Lock
from math import log2, ceil

# TODO update this code so it works out of the box
INPUT_DIR = 'input/'
OUTPUT_DIR = 'output/'


def vertex(ID):
    next_msg = f'next_{ID}'.encode()
    done_msg = f'done_{ID}'.encode()

    input_file_name = 'input_vertex_' + str(ID) + '.txt'
    with open(INPUT_DIR + input_file_name, 'r') as input_file:
        data = input_file.read().split('\n')
    graph_size = data[0]
    master = (data[2], int(data[1]))
    udp_port = data[3]
    tcp_port = data[4]
    is_root = True  # a vertex is a root if it has no parent
    parent = None
    if data[5] != 'None' and data[6] != 'None':
        is_root = False
        parent = (int(data[5]), data[6])
    elif data[5] != 'None' or data[6] != 'None':
        raise Exception('Input file is inconsistent')
    children = []
    for i in range(7, len(data) - 2, 2):
        children.append((data[i + 1], int(data[i])))
    color = 0 if is_root else ID

    # Listens to neighbours
    tcp_socket = socket(AF_INET, SOCK_STREAM)  # TCP socket
    tcp_socket.bind(('', tcp_port))

    # Sends my color to neighbours
    receive_sockets = [socket(AF_INET, SOCK_STREAM) for child in children]

    tcp_socket = socket(AF_INET, SOCK_STREAM)  # TCP socket
    send_socket_list = []
    send_socket_lock = Lock()

    # Listens to master for round
    master_listen_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket
    master_listen_socket.bind(('', udp_port))

    # Sends round end to master
    master_send_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket

    current_round = None
    while True:
        data, addr = master_listen_socket.recvfrom(4096)
        assert addr == master[0]
        if data.decode() == 'DIE':
            break
        current_round = int(data.decode())
        if data.decode() == '0':
            # if not is_root:
            tcp_socket.listen(1)
            master_send_socket.sendto(next_msg, master)

        elif data.decode() == '1':
            threads = [Thread(target=accept_connection,
                              args=(tcp_socket, send_socket_list, send_socket_lock))
                       for child in children]
            for thread in threads:
                thread.start()
            if not is_root:
                receive_socket, _ = tcp_socket.accept()
            # for neighbor, neighbor_socket in zip(neighbors, receive_sockets):
            #     neighbor_socket.connect(neighbor)
            for thread in threads:
                thread.join()

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

# TODO change to connect to child
def accept_connection(tcp_socket: socket, socket_list: list, socket_list_lock: Lock):
    send_socket, _ = tcp_socket.accept()
    socket_list_lock.acquire()
    socket_list.append(send_socket)
    socket_list_lock.release()


def main():
    pass


if __name__ == '__main__':
    s = socket()
    s.bind(('', 5001))
    s.listen(2)

    s1 = socket()
    s1.connect(('127.0.0.1', 5001))
    s2 = socket()
    s2.connect(('127.0.0.1', 5001))

    res1 = s.accept()
    res2 = s.accept()
    pass
    s.close()
    s1.close()
    # vertex('0011')
