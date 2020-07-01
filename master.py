from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread, Lock
from math import log2, ceil


def synchronizer(graph_size, udp_port):
    # Create round dict {node id: node round}
    rounds = {}
    for i in range(1, graph_size + 1):
        ID = bin(i)[2:].zfill(ceil(log2(graph_size)) + 1)
        rounds[ID] = 0
    shut_down_flag = [False]  # algorithm end flag
    r = [1]  # algorithm round

    # Start listening
    Thread(target=listen, args=(int(udp_port), rounds, shut_down_flag, graph_size, r)).start()

    # Starts the algorithm
    send_round(graph_size, udp_port, r[0])


def listen(udp_port, rounds, shut_down_flag, graph_size, r):
    # Listens to udp port until the algorithm terminates
    rounds_lock = Lock()  # Lock on rounds dict
    sock_udp = socket(AF_INET, SOCK_DGRAM)  # UDP socket
    sock_udp.bind(('', udp_port))

    while True:
        if not shut_down_flag[0]:  # While algorithm is running
            data, addr = sock_udp.recvfrom(4096)
            Thread(target=update, args=(data, rounds, rounds_lock, graph_size, r, udp_port, shut_down_flag,)).start()
        else:
            break
    sock_udp.close()


def update(data, rounds, rounds_lock, graph_size, r, udp_port, shut_down_flag):
    message = data.decode().split('_')
    sender = message[1]
    if message[0] == 'next':
        if sender in rounds:
            rounds_lock.acquire()
            rounds[sender] += 1
            rounds_lock.release()
        else:
            # TODO figure out how can this happen
            rounds_lock.acquire()
            rounds[sender] = 1
            rounds_lock.release()
    else:
        rounds_lock.acquire()
        rounds[sender] = 'done'
        rounds_lock.release()
    status(rounds, graph_size, r, udp_port, shut_down_flag)
    return


def status(rounds, graph_size, r, udp_port, shut_down_flag):
    if len(rounds) == graph_size:
        s = next_round(rounds)
        if s == -1:
            pass

        elif s == 'done':
            # Algorithm terminated
            shut_down_flag[0] = True
            sock_udp = socket(AF_INET, SOCK_DGRAM)
            sock_udp.sendto('DIE'.encode(), ('127.0.0.1', udp_port))
            sock_udp.close()

        else:
            # Round finished
            r[0] += 1
            send_round(graph_size, udp_port, r[0])


def next_round(rounds):
    # Checks if all vertices have reached the next round
    if rounds != {}:
        value = list(rounds.values())[0]
        if all(val == value for val in rounds.values()):
            return value
    return -1


def send_round(graph_size, udp_port, r):
    threads = []
    for i in range(1, graph_size + 1):
        threads.append(Thread(target=send, args=('127.0.0.1', udp_port + i, r,)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def send(ip, port, message):
    sock_udp = socket(AF_INET, SOCK_DGRAM)
    sock_udp.sendto(str(message).encode(), (ip, port))
    sock_udp.close()


def main():
    # Generates synchronous rounds.
    try:
        graph_size = int(input('Enter graph size \n'))
    except:
        print('ERROR--graph size')

    udp_port_start = 31000
    synchronizer(graph_size, udp_port_start)


if __name__ == '__main__':
    main()

