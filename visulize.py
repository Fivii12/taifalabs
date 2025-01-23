from graphviz import Digraph
import networkx as nx


def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Удаляем пустые строки и разделяем строки по табуляции
    lines = [line.strip().replace(' ', '').replace('\t', '') for line in lines if line.strip()]
    ygreks = lines[0][1:].split(';')  # Игреки (y)
    header = lines[1][1:].split(';')  # Состояния
    transitions = lines[2:]  # Переходы

    return ygreks, header, transitions


def create_graph(ygreks, header, transitions):
    G = nx.DiGraph()

    # Добавляем узлы с y
    for index, state in enumerate(header):
        y_label = ygreks[index]  # Получаем y для текущего состояния
        node_label = f'{state}/{y_label}'  # Формируем метку узла: состояние/y
        G.add_node(state, label=node_label)  # Добавляем узел с меткой

    # Добавляем ребра
    for row in transitions:
        line = row.split(';')
        symbol = line[0]  # Символ перехода
        parts = line[1:]  # Состояния перехода

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
    dot = Digraph(comment='graph', format='png')

    # Добавляем узлы с y
    for node, data in G.nodes(data=True):
        node_label = data.get('label', node)
        dot.node(node, label=node_label)


    for edge in G.edges(data=True):
        src = edge[0]
        dst = edge[1]
        label = edge[2].get('label', '')
        dot.edge(src, dst, label=label)


    dot.render('graph', cleanup=True)


def main(file_path):
    ygreks, header, transitions = read_file(file_path)
    Graph = create_graph(ygreks, header, transitions)
    visualize_graph(Graph)


if __name__ == "__main__":
    main("output.txt")