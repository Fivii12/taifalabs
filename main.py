import pandas as pd
from graphviz import Digraph

def read_csv(file_path, delimiter=';'):
    """
    Загружает CSV файл и возвращает DataFrame и numpy-массив.
    """
    df = pd.read_csv(file_path, delimiter=delimiter)
    np_df = df.to_numpy()
    return df, np_df

def mili_to_moore(df):
    """
    Преобразует автомат Мили в автомат Мура и сохраняет результат в CSV и графический файл.
    """
    # Разделяем состояния и переходы
    unique_transitions = set()
    unique_states = set()
    for _, row in df.iterrows():
        for state, transition in row.items():
            if state == 'Unnamed: 0':
                continue
            unique_states.add(state)
            next_state, output_symbol = transition.split('/')
            unique_transitions.add((next_state, output_symbol))

    # Сортируем переходы и состояния
    sorted_transitions = sorted(unique_transitions)
    sorted_states = sorted(unique_states)

    # Генерируем новые состояния
    new_states = {}
    state_counter = 0
    for next_state, output_symbol in sorted_transitions:
        new_state = f'q{state_counter}'
        new_states[new_state] = (next_state, output_symbol)
        state_counter += 1

    # Учитываем состояния без переходов
    for state in sorted_states:
        if not any(state == t[0] for t in sorted_transitions):
            new_state = f'q{state_counter}'
            new_states[new_state] = (state, '-')
            state_counter += 1

    # Упорядочиваем состояния
    ordered_states = {}
    added_states = set()
    for new_state, (next_state, output_symbol) in new_states.items():
        if (next_state, output_symbol) not in added_states:
            ordered_states[new_state] = (next_state, output_symbol)
            added_states.add((next_state, output_symbol))

    # Создаем автомат Мура
    moore = {}
    transitions_dict = {col: [] for col in df.columns[1:]}
    for col in df.columns[1:]:
        for value in df[col]:
            if value:
                next_state, output_symbol = value.split('/')
                transitions_dict[col].append((next_state, output_symbol))

    state_names = list(ordered_states.keys())
    qstates = [f"{state}/{ordered_states[state][1]}" for state in state_names]
    moore_with_symbols = {}

    for state in qstates:
        qstate, yout = state.split('/')
        moore[state] = []
        moore_with_symbols[state] = []
        for key, values in transitions_dict.items():
            for value in values:
                if value[0] == ordered_states[qstate][0]:
                    moore[state].append(key)
                    moore_with_symbols[state].append((key, value[1]))

    # Генерация графа
    dot = Digraph(comment='State Machine')
    for state, next_states in moore.items():
        dot.node(state.split('/')[0])
        for i, next_state in enumerate(next_states):
            dot.edge(state.split('/')[0], next_state, label=f'x{i+1}')
    dot.render('state_machine_graph_with_labels', format='png', cleanup=True)

    # Генерация CSV
    count_x = len(df.columns) - 1
    headers = [''] + [f"{ordered_states[state][1]}" for state in ordered_states]
    states_row = [''] + [state.split('/')[0] for state in moore.keys()]
    moore_output = []

    for i in range(count_x):
        row = [f'x{i+1}']
        for state in moore:
            found = False
            for next_state, x_index in moore_with_symbols[state]:
                if x_index == f'x{i+1}':
                    row.append(next_state)
                    found = True
                    break
            if not found:
                row.append('-')
        moore_output.append(row)

    data = [headers] + [states_row] + moore_output
    moore_df = pd.DataFrame(data)
    moore_df.to_csv('moore_machine_output.csv', sep=';', header=False, index=False)

    print("Автомат Мура сохранен в файл moore_machine_output.csv")
    print("Граф автомата сохранен в файл state_machine_graph_with_labels.png")

file_path = 'data.csv'
df, np_df = read_csv(file_path)
mili_to_moore(df)