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
    graph_size = int(data[0])
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
    color = ID if parent else '0'
    color = color.zfill(ceil(log2(graph_size)) + 1)

    socket_list = []

    # Listens to parent
    if parent:
        parent_socket = socket(AF_INET, SOCK_STREAM)  # TCP socket
        socket_list.append(parent_socket)
        parent_socket.bind(('', tcp_port))
        parent_connection = [None]
        parent_connection_lock = Lock()

    # Sends my color to children
    children_sockets = [socket(AF_INET, SOCK_STREAM) for child in children]
    socket_list += children_sockets

    # Listens to master for round
    master_listen_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket
    master_listen_socket.bind(('', udp_port))
    socket_list.append(master_listen_socket)

    # Sends round end to master
    master_send_socket = socket(AF_INET, SOCK_DGRAM)  # UDP socket
    socket_list.append(master_send_socket)

    shift_down = True
    done_flag = False
    x = 8  # From the algorithm
    output_file_lock = Lock()
    while not done_flag:
        data, _ = master_listen_socket.recvfrom(4096)
        if data.decode() == '1':
            if parent:
                parent_socket.listen(1)
            master_send_socket.sendto(next_msg, master)

        elif data.decode() == '2':
            if parent:
                # Accept connection from parent
                parent_connect_thread = Thread(target=accept_connection,
                                               args=(parent_socket, parent_connection))
                parent_connect_thread.start()
            # Connect to children
            for child, child_socket in zip(children, children_sockets):
                child_socket.connect(child)
            if parent:
                parent_connect_thread.join()
                socket_list += parent_connection
            master_send_socket.sendto(next_msg, master)

        else:
            # Send color to children
            send_color_threads = [Thread(target=send_color,
                                         args=(child_socket, color, child[1], ID, OUTPUT_DIR, output_file_lock))
                                  for child, child_socket in zip(children, children_sockets)]
            for thread in send_color_threads:
                thread.start()

            # Get color from parent
            parent_color = None
            if parent:
                # TODO message len
                parent_color = parent_socket.recv(4096).decode()

            if len(color) > 3:
                # TreeColoring 8
                color = recolor(color, parent_color)
                master_send_socket.sendto(next_msg, master)
            else:
                # TreeColoring 3
                if shift_down:
                    children_color = color
                    color = parent_color if parent else (color + 1) % 3
                    shift_down = False
                else:
                    x -= 1
                    if color == x:
                        color = min_non_conflicting_color(children_color, parent_color)
                    if x == 3:
                        done_flag = True
                    shift_down = True

                if done_flag:
                    master_send_socket.sendto(done_msg, master)
                else:
                    master_send_socket.sendto(next_msg, master)

    # TODO check correction of coloring
    write_color(ID, color)

    for close_socket in socket_list:
        close_socket.close()


def send_color(tcp_socket: socket, color: str, port: int, ID: str, output_dir: str, file_lock: Lock):
    tcp_socket.send(color.encode())
    file_lock.acquire()
    with open(output_dir + 'output_vertex_' + ID + '.txt', 'a') as output_file:
        output_file.write(f'{color}_{port}\n')
    file_lock.release()


def write_color(ID: str, color: str):
    with open(f'color_vertex_{ID}.txt', 'w') as color_file:
        color_file.write(str(int(color, 2)))


def recolor(color, parent_color=None):
    """
    :param color: current node's color
    :param parent_color: node's parent's color
    :return: new color computed according to the algorithm
    """
    n = len(color)  # perhaps n+1
    new_color_len = ceil(log2(n)) + 1
    if parent_color is None:
        return ''.zfill(new_color_len)
    assert len(color) == len(parent_color)
    color = color[::-1]
    parent_color = parent_color[::-1]
    i_v = None
    for i in range(len(color)):
        if color[i] != parent_color[i]:
            i_v = i
            break
    assert i_v is not None
    new_color = bin(i_v)[2:] + str(color[i_v])
    assert len(new_color) <= new_color_len
    return new_color.zfill(new_color_len)


def accept_connection(tcp_socket: socket, socket_list: list):
    connection_socket, _ = tcp_socket.accept()
    socket_list[0] = connection_socket


def min_non_conflicting_color(children_color, parent_color):
    for i in range(3):
        if children_color != i and parent_color != i:
            return i


if __name__ == '__main__':
    vertex('00101')
