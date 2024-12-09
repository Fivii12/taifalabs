from bisect import insort
from os.path import splitext

import pandas as pd
import numpy as np
from graphviz import Digraph
def read_csv_data():
    df = pd.read_csv('mili_input.csv', sep=';')
    print(df)
    arrays = [df[col].values for col in df.columns]
    return arrays[0], arrays[1:]  # Пропускаем первый столбец, если нужно



def get_y_full(arr):
    array = []
    secarr = []
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            array.append(arr[i][j].split('/')[1])
            secarr.append(arr[i][j])
    return array, secarr
def get_transition(arr):
    numbers = '1234567890'
    transition = ''
    array = []
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            transition = arr[i][j].split('/')[0]
            if transition[0] in numbers:
                array.append(transition)
            else:
                array.append(transition[1]) # подумать если есть s или нет как исправить

    return array
def init(array):
    yarray = []
    transitions = []
    yarray, secarr = get_y_full(array)
    transitions = get_transition(array)
    yarray_grouped = []
    transitions_grouped = []
    secarr_grouped = []
    for i in range(0, len(yarray), 3):
        group = yarray[i:i + 3]
        transitionGroup = transitions[i:i + 3]
        secarr_group = secarr[i:i + 3]
        secarr_grouped.append(secarr_group)
        yarray_grouped.append(group)
        transitions_grouped.append(transitionGroup)

    return yarray_grouped, transitions_grouped, secarr_grouped
# Словарь для группировки

# Проходим по массиву
def make_new_group_ygrek(yarray_grouped):
    groups = {}
    for i, group in enumerate(yarray_grouped):
        key = tuple(group)  # Преобразуем группу в кортеж (чтобы использовать как ключ)
        if key not in groups:
            groups[key] = []  # Если ключа ещё нет, создаём запись
        groups[key].append(i + 1)  # Добавляем индекс в соответствующую группу
    return groups


def get_group_for_state(state, grouped_indices):
    for i in range(len(grouped_indices)):
        if state in grouped_indices[i]:
            return i

def make_group_transitions(groups, transtions_grouped):
    final_aray = []
    for i in range(len(groups)): # по объединенным по y
        second_aray = []
        for j, state in enumerate(groups[i]): # по индексу(состоянию)
            aray = []
            for elem in transtions_grouped[state - 1]: # по переходу
                a = get_group_for_state(int(elem), groups)
                aray.append(a)
            second_aray.append(aray)
        final_aray.append(second_aray)
    return final_aray



def make_new_group_indeces(mid_aray, grouped_indices):
    mid_groups = {}
    for i, group in enumerate(mid_aray): # по объединенным по индексам
        for j, state in enumerate(group): # по внутренностям групп
            key = tuple(state)  # Преобразуем группу в кортеж (чтобы использовать как ключ)
            if key not in mid_groups:
                mid_groups[key] = []  # Если ключа ещё нет, создаём запись
            mid_groups[key].append(grouped_indices[i][j])  # Добавляем индекс в соответствующую группу
    return mid_groups



def check_if_last(aray):
    for group in aray:
        for state in group:
            for state2 in group:
                if state != state2:
                    return False
    return True

def make_mini_mili(secarr_grouped, new_grouped_indices):
    mini_mili = []
    for i in range(len(new_grouped_indices)):

        for state in new_grouped_indices[i]:
            mini_mili.append(secarr_grouped[state - 1])
            break

    new_mini_mili = []
    transitions = get_transition(mini_mili)
    transitions_grouped = []
    for i in range(0, len(transitions), 3):
        transitionGroup = transitions[i:i + 3]
        transitions_grouped.append(transitionGroup)
    for group in mini_mili:
        new_group = []
        for j, elem in enumerate(transitions_grouped):  # Предполагаем, что каждый элемент внутри группы - это одно состояние
            for l, finalelem in enumerate(elem):
                # Для каждого состояния находим группу, к которой оно относится
                for i, group_indices in enumerate(new_grouped_indices):
                    if int(finalelem) in group_indices:
                        new_group.append(f's{i}/' + mini_mili[j][l].split('/')[1])  # Заменяем состояние на номер группы
                        break
                new_mini_mili.append(new_group)


    print("Mini Mili:", mini_mili)
    print("New Mini Mili:", new_mini_mili[0])
    return new_mini_mili[0]

def split_arr(array):
    splited_mili = []
    for i in range(0, len(array), 3):
        splited_mili.append(array[i:i + 3])
    return splited_mili
def get_column_names(arr):
    column_names = []
    for i in range(len(arr)):
        column_names.append(f's{i}')
    return column_names
def make_graph(column_names, rows_names, splitted_arr):
    dot = Digraph(comment='State Machine')
    for i, col_name in enumerate(column_names):
        for j in range(len(rows_names)):
            dot.edge(col_name, splitted_arr[i][j].split('/')[0], label=f'{rows_names[j]}/{splitted_arr[i][j].split("/")[1]}')


    dot.render('moore_graph', format='png', cleanup=True)

def mili_minimization():
    rows_names, arrays = read_csv_data()
    yarray_grouped, transitions_grouped, secarr_grouped = init(arrays)
    print('yarray_grouped', yarray_grouped)
    print('transitions_grouped', transitions_grouped)
    print('secarr_grouped', secarr_grouped)

    groups = make_new_group_ygrek(yarray_grouped)
    grouped_indices = list(groups.values())
    print('grouped_indices', grouped_indices)

    while True:
        mid_array = make_group_transitions(grouped_indices, transitions_grouped)
        print('mid_array', mid_array)

        mid_groups = make_new_group_indeces(mid_array, grouped_indices)
        new_grouped_indices = list(mid_groups.values())
        print('new_grouped_indices', new_grouped_indices)

        # Если группы не изменились, завершаем процесс
        if new_grouped_indices == grouped_indices:
            break

        grouped_indices = new_grouped_indices
    full_states_mili = make_mini_mili(secarr_grouped, new_grouped_indices)# доделатть визуализацию и представление в виде графа финальное
    splitted_arr = split_arr(full_states_mili)
    column_names = get_column_names(splitted_arr)
    splitted_arr_transposed = np.array(splitted_arr).T # T чтобы перевернуть(транспонирование)

    print(splitted_arr)
    print(rows_names)
    print(column_names)



    mili_final_df = pd.DataFrame(splitted_arr_transposed, index=rows_names, columns=column_names)
    mili_final_df.to_csv('mili_final.csv', sep=';')


    make_graph(column_names, rows_names, splitted_arr)

    is_last = check_if_last(mid_array)
    print(is_last)

# Запуск минимизации
mili_minimization()
