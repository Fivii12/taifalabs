import networkx as nx
from pyvis.network import Network


def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Удаляем пустые строки и разделяем строки по табуляции
    lines = [line.strip().replace(' ', '').replace('\t', '') for line in lines if line.strip()]
    header = lines[1][1:].split(';')
    transitions = lines[2:]

    return header, transitions


def create_graph(header, transitions):
    G = nx.DiGraph()

    # Добавляем узлы
    for state in header:
        G.add_node(state)

    # Добавляем ребра
    for row in transitions:
        line = row.split(';')
        symbol = line[0]
        parts = line[1:]

        for index, state in enumerate(header):
            transition = parts[index].split(',')
            for childState in transition:
                if childState != '-':
                    if G.has_edge(state, childState):
                        # Если ребро уже существует, обновляем метку
                        current_label = G.edges[state, childState]['label']
                        new_label = current_label + "," + symbol
                        G.edges[state, childState]['label'] = new_label
                    else:
                        # Если ребра нет, добавляем его с меткой
                        G.add_edge(state, childState, label=symbol)

    return G


def visualize_graph(G):
    net = Network(notebook=True, directed=True)

    # Добавляем узлы и ребра в pyvis
    for node in G.nodes():
        net.add_node(node)

    for edge in G.edges(data=True):
        src = edge[0]
        dst = edge[1]
        label = edge[2].get('label', '')
        net.add_edge(src, dst, arrows='to', label=label)

    net.show('graph.html')


def main(file_path):
    header, transitions = read_file(file_path)
    Graph = create_graph(header, transitions)
    visualize_graph(Graph)


if __name__ == "__main__":
    main("output.txt")