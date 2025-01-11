import pandas as pd
from graphviz import Digraph

def read_csv(file_path, delimiter=';'):
    """
    Загружает CSV файл и возвращает DataFrame и numpy-массив.
    """
    df = pd.read_csv(file_path, delimiter=delimiter)
    np_df = df.to_numpy()
    return df, np_df

def mili_to_moore(df, np_df):
    """
    Преобразует автомат Мили в автомат Мура и сохраняет результат в CSV и графический файл.
    """
    first_row = df.iloc[0]
    print(np_df.shape)
    count_x = np_df.shape[0]
    state_counter = 0

    unique_transitions = set()
    unique_states = set()
    #разделяем переходы и состояния
    for index, row in df.iterrows():
        for state, transition in row.items():
            if state == 'Unnamed: 0':
                continue
            unique_states.add(state)
            next_state, output_symbol = transition.split('/')
            unique_transitions.add((next_state, output_symbol))
    sorted_transitions = sorted(unique_transitions)
    sorted_states = sorted(unique_states)

    new_states = {}
    output_symbols = {}
    #добавляем их в словарь
    for next_state, output_symbol in sorted_transitions:
        new_state = f'q{state_counter}'
        new_states[new_state] = (next_state, output_symbol)
        state_counter += 1

    #добавляем с минусом если нет в переходах
    for state in sorted_states:
        found = False
        for transition_state, transition in sorted_transitions:
            if state == transition_state:
                found = True
                break
        if not found:
            new_state = f'q{state_counter}'
            new_states[new_state] = (state, '-')

    all_states = []
    #сохраняем все состояния
    for key in new_states:
        print(new_states[key][0])
        all_states.append(new_states[key][0])

    all_states_sorted = sorted(all_states)
    print(all_states_sorted)

    new_key = 0
    ordered_new_state = 0
    #сохраняем сколько раз каждое состяние нужно писать
    state_count = {}
    for state in all_states_sorted:
        if state in state_count:
            state_count[state] += 1
        else:
            state_count[state] = 1
    print(state_count)
    #делаем новый словарь с учетом минуса
    first_key = sorted(state_count.keys())[0]
    step = -state_count[first_key]
    added_states = set()
    added_states_without_transitions = []
    a = 0
    ordered_states = {}
    # added_states_without_transitions - список символов переходных, added_states - переходные состояния и выходные символы
    for key in new_states:
        counter = 0
        step = state_count[new_states[key][0]]
        for i in range(len(all_states_sorted)):
            if new_states[key][0] == all_states_sorted[i]:
                if counter < step:
                    for j in range(len(added_states_without_transitions)):
                        if (new_states[key][0]) == added_states_without_transitions[j]:
                            counter += 1
                    ordered_new_state = f'q{i + counter}'
                    if (new_states[key][0],new_states[key][1]) not in added_states:
                        ordered_states[ordered_new_state] = (new_states[key][0], new_states[key][1])
                        added_states.add(((new_states[key][0], new_states[key][1])))
                        added_states_without_transitions.append((new_states[key][0]))

    ordered_states_sorted = dict(sorted(ordered_states.items()))
    print(new_states)
    print(ordered_states)
    print("ordered_states_sorted", ordered_states_sorted)

    transitions_dict = {}
    np_df = df.to_numpy()
    transitions = {}
    transitions_dict = {}

    for col in df.columns[1:]:  # Пропускаем первую колонку 'Unnamed: 0'
        transitions_dict[col] = []  # Инициализируем список для данной колонки
        for value in df[col]:  # Проходим по всем значениям в колонке
            if value:  # Проверяем, есть ли значение
                next_state, output_symbol = value.split('/')  # Разделяем по '/'
                transitions_dict[col].append((next_state, output_symbol))

    print("переходы", transitions_dict)
    state_names = list(ordered_states_sorted.keys()) # названия состояний
    qstates = [f"{state}/{ordered_states_sorted[state][1]}" for state in state_names] # Создаем список состояний

    # Выводим новый список

    moore = {}
    keys = list(transitions_dict.keys())  # Преобразуем ключи в список для индексации
    print('keys', keys)
    print('qstates', qstates)
    print('transitions_dict', transitions_dict)
    moore_step = 0  # Сдвиг для ключа
    moore_with_symbols = {}
    past_states = []
    prev_state = ''

    for state in qstates:
        qstate, yout = state.split('/')
        moore[state] = []  # инициализируем список переходов для текущего состояния
        moore_with_symbols[state] = []
        moore_counter = 0
        print(ordered_states_sorted[qstate][0], prev_state)
        if ordered_states_sorted[qstate][0] == prev_state: # если s-ки одинаковые то одни и те же состояния
            moore_step -= 1 # вычитаем чтобы начать оттуда же
        # начинаем с текущего смещения moore_step
        for i in range(moore_step, len(keys)):
            key = keys[i]  # берем ключ с учетом смещения
            value = transitions_dict[key]  # получаем значения переходов для s-ок

            # проходим по всем состояниям автомата Мура
            for qkey, qvalue in ordered_states_sorted.items():
                # проверяем переходы для текущего входного символа
                for j in range(len(value)):
                    if qvalue == value[j]:
                        moore_counter += 1
                        moore[state].append(qkey)
                        moore_with_symbols[state].append((qkey, j))


            # когда нашли все переходы, увеличиваем сдвиг на 1 и выходим из цикла
            if moore_counter == np_df.shape[0]:
                prev_state = key
                moore_step = i + 1  # Сохраняем сдвиг для следующего состояния
                break  # Прерываем цикл по ключам для данного состояния


    print(moore)
    print(moore_with_symbols)

    updated_transitions = {}

    dot = Digraph(comment='State Machine')

    for state, next_states in moore.items():
        dot.node(state[0:2])
        for i, next_state in enumerate(next_states):
            x = moore_with_symbols[state][i][1]

            dot.edge(state[0:2], next_state[0:2], label=f'x{x+1}')

    # Сохраняем и визуализируем граф
    dot.render('moore_graph', format='png', cleanup=True)

    moore_output = []

    # Заголовки CSV-файла
    headers = [''] + [f"{ordered_states_sorted[state][1]}" for state in ordered_states_sorted]  # Выходные символы
    states_row = [''] + [key.split('/')[0] for key in moore.keys()]  # Состояния

    # Записываем строки с переходами по x1, x2, x3
    for i in range(count_x):
        row = [f'x{i+1}']
        for state in moore:
            # Смотрим в словарь moore_with_symbols, чтобы правильно выбрать переходы
            found_transition = False
            for next_state, x_index in moore_with_symbols[state]:
                if x_index == i:  # Переход для текущего x_i
                    row.append(next_state)
                    found_transition = True
                    break
            if not found_transition:
                row.append('-')  # Если нет перехода для этого x, добавляем '-'
        moore_output.append(row)

    # Собираем итоговую таблицу
    data = [headers] + [states_row] + moore_output

    # Преобразуем в DataFrame и сохраняем
    moore_df = pd.DataFrame(data)
    print(moore_df)
    moore_df.to_csv('moore_from_mili.csv', sep=';', header=False, index=False)

    print("Автомат Мура сохранен в файл moore_from_mili.csv")

file_path = 'data.csv'
df, np_df = read_csv(file_path)
mili_to_moore(df, np_df)

def moore_to_mili(df, np_df):
    """
    Преобразует автомат Мура в автомат Мили и сохраняет результат в CSV-файл.
    """
    row = df.iloc[0]
    yvalue = df.columns.to_list()
    yvalue = [col.split('.')[0] for col in yvalue]
    xvalue = row.values.tolist()


    cols = df.shape[0] - 1
    for i in range(cols):
        x = df.iloc[i+1].values
        for j in range(1, len(x)):
            ind = xvalue.index(x[j]) # нахожу по индексу кушку
            x[j] = x[j] + '/' + yvalue[ind] # нахожу по индексу кушки игрек
            df.columns = [col.replace('y', '') for col in df.columns]

    # Устанавливаем новые заголовки
    df.columns = [col if col == 'Unnamed: 0' else xvalue[idx]
                  for idx, col in enumerate(df.columns)]


    mili_df = pd.DataFrame(df)

    print(f"Граф автомата Мили сохранен как {'mili_graph'}.png")
    print(mili_df)
    mili_df.to_csv('mili.csv', sep=';', header=False, index=False)

    df = df[1:].reset_index(drop=True)
    dot = Digraph(comment='Mealy Machine')

    # Добавляем состояния как узлы
    col_names = df.columns[1:].to_list()
    print(df.columns[1:])
    states = df.iloc[0].values[1:].tolist()
    print(states, '123213')
    for state in col_names:
        print(state)
        dot.node(state)

    # Добавляем переходы как ребра
    for i, row in df.iterrows():
        current_state = row.iloc[i+1]  # Текущее состояние — первый элемент строки
        transitions = row.values[1:].tolist()
        print(i, transitions)
        for j, state in enumerate(col_names):
            dot.edge(state, transitions[j].split('/')[0], label = row.values[0] + '/' + transitions[j].split('/')[1])

    # Сохраняем граф в файл
    dot.render('mili_graph', format='png', cleanup=True)

file_path_moore = 'moore.csv'
df2, np_df2 = read_csv(file_path_moore)
moore_to_mili(df2, np_df2)