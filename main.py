import pandas as pd
from graphviz import Digraph


def load_data(file_path):
    """Загрузить данные из CSV файла и вернуть DataFrame и NumPy массив."""
    df = pd.read_csv(file_path, delimiter=';')
    np_df = df.to_numpy()
    return df, np_df


def extract_transitions_and_states(df):
    """Извлечь уникальные переходы и состояния из DataFrame."""
    unique_transitions = set()
    unique_states = set()

    for index, row in df.iterrows():
        for state, transition in row.items():
            if state == 'Unnamed: 0':
                continue
            unique_states.add(state)
            next_state, output_symbol = transition.split('/')
            unique_transitions.add((next_state, output_symbol))

    return sorted(unique_transitions), sorted(unique_states)


def create_new_state_dict(unique_transitions, unique_states):
    """Создать новый словарь состояний на основе уникальных переходов и состояний."""
    state_counter = 0
    new_states = {}

    for next_state, output_symbol in unique_transitions:
        new_state = f'q{state_counter}'
        new_states[new_state] = (next_state, output_symbol)
        state_counter += 1

    for state in unique_states:
        found = any(state == transition_state for transition_state, _ in unique_transitions)
        if not found:
            new_state = f'q{state_counter}'
            new_states[new_state] = (state, '-')

    return new_states


def order_states(new_states):
    """Упорядочить состояния и создать словарь переходов."""
    ordered_states = {}
    state_count = {}
    all_states = [new_states[key][0] for key in new_states]

    # Считаем количество состояний
    for state in sorted(all_states):
        state_count[state] = state_count.get(state, 0) + 1

    first_key = sorted(state_count.keys())[0]
    step = -state_count[first_key]
    added_states_without_transitions = []

    for key in new_states:
        state_name = new_states[key][0]
        counter = 0
        step = state_count[state_name]

        for i in range(len(all_states)):
            if state_name == all_states[i]:
                if counter < step:
                    for added_state in added_states_without_transitions:
                        if state_name == added_state:
                            counter += 1
                    ordered_new_state = f'q{i + counter}'
                    ordered_states[ordered_new_state] = new_states[key]
                    added_states_without_transitions.append(state_name)
                    break

    return ordered_states


def build_moore_machine(transitions_dict, ordered_states):
    """Построить автомат Мура на основе переходов и упорядоченных состояний."""
    moore = {}
    keys = list(transitions_dict.keys())
    moore_step = 0
    moore_with_symbols = {}
    past_states = []
    prev_state = ''

    for state, (next_state, output_symbol) in ordered_states.items():
        moore[state] = []
        moore_with_symbols[state] = []
        moore_counter = 0

        if next_state == prev_state:
            moore_step -= 1

        for i in range(moore_step, len(keys)):
            key = keys[i]
            value = transitions_dict[key]

            for qkey, qvalue in ordered_states.items():
                for j in range(len(value)):
                    if qvalue == value[j]:
                        moore_counter += 1
                        moore[state].append(qkey)
                        moore_with_symbols[state].append((qkey, j))

            if moore_counter == len(transitions_dict):
                prev_state = key
                moore_step = i + 1
                break

    return moore, moore_with_symbols


def save_moore_machine_to_csv(moore, moore_with_symbols, count_x, output_file='moore_machine_output.csv'):
    """Сохранить автомат Мура в CSV файл."""
    headers = [''] + [f"x{i + 1}" for i in range(count_x)]
    states_row = [''] + [state for state in moore.keys()]

    moore_output = []
    for i in range(count_x):
        row = [f'x{i + 1}']
        for state in moore:
            found_transition = False
            for next_state, x_index in moore_with_symbols[state]:
                if x_index == i:
                    row.append(next_state)
                    found_transition = True
                    break
            if not found_transition:
                row.append('-')
        moore_output.append(row)

    data = [headers] + [states_row] + moore_output
    moore_df = pd.DataFrame(data)
    moore_df.to_csv(output_file, sep=';', header=False, index=False)
    print(f"Автомат Мура сохранен в файл {output_file}")


def generate_state_machine_graph(moore, moore_with_symbols, output_file='state_machine_graph_with_labels'):
    """Сгенерировать граф состояний и сохранить в файл."""
    dot = Digraph(comment='State Machine')

    for state, next_states in moore.items():
        dot.node(state[0:2])
        for i, next_state in enumerate(next_states):
            x = moore_with_symbols[state][i][1]
            dot.edge(state[0:2], next_state[0:2], label=f'x{x + 1}')

    dot.render(output_file, format='png', cleanup=True)


def main(file_path):
    df, np_df = load_data(file_path)
    unique_transitions, unique_states = extract_transitions_and_states(df)
    new_states = create_new_state_dict(unique_transitions, unique_states)
    ordered_states = order_states(new_states)

    # Подготовка переходов
    transitions_dict = {col: [] for col in df.columns[1:]}
    for col in df.columns[1:]:
        for value in df[col]:
            if value:
                next_state, output_symbol = value.split('/')
                transitions_dict[col].append((next_state, output_symbol))

    moore, moore_with_symbols = build_moore_machine(transitions_dict, ordered_states)
    save_moore_machine_to_csv(moore, moore_with_symbols, df.shape[0])
    generate_state_machine_graph(moore, moore_with_symbols)


if __name__ == "__main__":
    main('data.csv')
