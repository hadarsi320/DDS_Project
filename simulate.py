import random
from math import log2, ceil
from itertools import permutations
from vertex import vertex
from threading import Thread


def build_graph(graph_size, pick_edge_prob, udp_port, tcp_port):
    graph = {}
    vertices = []
    for i in range(1, graph_size + 1):
        udp_port += 1
        tcp_port += 1
        ID = bin(i)[2:].zfill(ceil(log2(graph_size)) + 1)
        graph[ID] = {'in_neighbor': '', 'out_neighbors': [], 'UDP_port': udp_port, 'TCP_port': tcp_port}
        vertices.append(ID)
    edges = list(permutations(vertices, 2))
    random.shuffle(edges)

    for edge in edges:
        out_vertex = edge[0]
        in_vertex = edge[1]
        if not(graph[in_vertex]['in_neighbor']):
            prob = random.random()
            if prob < pick_edge_prob:
                graph[out_vertex]['out_neighbors'].append(in_vertex)
                graph[in_vertex]['in_neighbor'] = out_vertex

    return graph


def vertices_input(graph, udp_port_master):
    for v in graph:
        udp_port = graph[v]['UDP_port']
        tcp_port = graph[v]['TCP_port']
        in_neighbor = graph[v]['in_neighbor']
        out_neighbors = graph[v]['out_neighbors']

        input_file_name = 'input_vertex_' + str(v)+'.txt'
        input_file = open(input_file_name, 'w')

        input_file.write(str(len(graph)) + '\n')
        input_file.write(str(udp_port_master) + '\n')
        input_file.write('127.0.0.1\n')
        input_file.write(str(udp_port) + '\n')
        input_file.write(str(tcp_port) + '\n')

        if in_neighbor:
            input_file.write(str(graph[in_neighbor]['TCP_port']) + '\n')
            input_file.write('127.0.0.1\n')
        else:
            input_file.write('None' + '\n')
            input_file.write('None' + '\n')

        for out_neighbor in out_neighbors:
            input_file.write(str(graph[out_neighbor]['TCP_port']) + '\n')
            input_file.write('127.0.0.1\n')

        input_file.write('*\n')
        input_file.close()


def main():
    # Constructs and simulates a graph.

    try:
        graph_size = int(input('Enter graph size \n'))
    except:
        print('ERROR--graph size')

    random.seed(45970)
    pick_edge_prob = 0.8
    udp_port_start = 31000
    tcp_port_start = 41000

    graph = build_graph(graph_size, pick_edge_prob, udp_port_start, tcp_port_start)
    vertices_input(graph, udp_port_start)

    threads = []
    for ID in graph.keys():
        threads.append(Thread(target=vertex, args=(ID,)))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return graph


if __name__ == '__main__':
    main()
