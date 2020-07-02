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
    udp_port = int(data[3])
    tcp_port = int(data[4])
    parent = None
    if data[5] != 'None' and data[6] != 'None':
        parent = (int(data[5]), data[6])
    elif data[5] != 'None' or data[6] != 'None':
        raise Exception('Input file is inconsistent')
    children = []
    for i in range(7, len(data) - 2, 2):
        children.append((data[i + 1], int(data[i])))
    color = ID if parent else 0

    # Listens to parent
    parent_socket = socket(AF_INET, SOCK_STREAM)  # TCP socket
    parent_socket.bind(('', tcp_port))
    parent_connection = [None]
    parent_connection_lock = Lock()

    # Sends my color to children
    children_sockets = [socket(AF_INET, SOCK_STREAM) for child in children]

    # tcp_socket = socket(AF_INET, SOCK_STREAM)  # TCP socket
    # send_socket_list = []
    # send_socket_lock = Lock()

    # Listens to master for round
    master_listen_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket
    master_listen_socket.bind(('', udp_port))

    # Sends round end to master
    master_send_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket

    current_round = None
    while True:
        data, addr = master_listen_socket.recvfrom(4096)
        # assert addr[0] == master[0]
        if data.decode() == 'DIE':
            break
        current_round = int(data.decode())
        print(f'Round {current_round}')

        if data.decode() == '1':
            parent_socket.listen(1)
            # TODO what if is root
            master_send_socket.sendto(next_msg, master)

        elif data.decode() == '2':
            # TODO what if vertex has no parent?
            parent_connect_thread = Thread(target=accept_connection,
                                           args=(parent_socket, parent_connection, parent_connection_lock))
            parent_connect_thread.start()
            for child, child_socket in zip(children, children_sockets):
                child_socket.connect(child)
            parent_connect_thread.join()
            master_send_socket.sendto(next_msg, master)

        elif len(color) > 3:
            master_send_socket.sendto(done_msg, master)

        else:
            master_send_socket.sendto(done_msg, master)
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


def accept_connection(tcp_socket: socket, socket_list: list, socket_list_lock: Lock):
    connection_socket, _ = tcp_socket.accept()
    socket_list_lock.acquire()
    socket_list[0] = connection_socket
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
