from bisect import insort
from fnmatch import translate
from glob import escape
from inspect import stack
from os.path import splitext

import pandas as pd
import numpy as np
from graphviz import Digraph
def read_csv_data(input_file):
    df = pd.read_csv(input_file, sep=';')
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
                array.append(transition[1:]) # подумать если есть s или нет как исправить

    return array
def init(array, rows_len):
    yarray = []
    transitions = []
    yarray, secarr = get_y_full(array)
    transitions = get_transition(array)
    yarray_grouped = []
    transitions_grouped = []
    secarr_grouped = []
    for i in range(0, len(yarray), rows_len):
        group = yarray[i:i + rows_len]
        transitionGroup = transitions[i:i + rows_len]
        secarr_group = secarr[i:i + rows_len]
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
        #сделать if на случай начала 0  или 1

        groups[key].append(i + 1)  # Добавляем индекс в соответствующую группу
    return groups


def get_group_for_state(state, grouped_indices):
    for i in range(len(grouped_indices)):
        if state in grouped_indices[i]:
            return i

def make_group_transitions(groups, transtions_grouped, start_number):
    final_aray = []
    for i in range(len(groups)): # по объединенным по y
        second_aray = []
        for j, state in enumerate(groups[i]): # по индексу(состоянию)
            aray = []
            for elem in transtions_grouped[state - start_number ]: # по переходу start_number для того чтобы учесть 0 1 2 3 начало кароч

                a = get_group_for_state(int(elem), groups)
                aray.append(a)
            second_aray.append(aray)
        final_aray.append(second_aray)
    return final_aray



def make_new_group_indeces(mid_aray, grouped_indices):
    mid_groups = {}
    for i, group in enumerate(mid_aray):  # по объединенным по индексам
        for j, state in enumerate(group):  # по внутренностям групп
            # Создаем уникальный ключ, добавляя индекс внешнего массива
            key = (i, tuple(state))
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

def make_mini_mili(secarr_grouped, new_grouped_indices, rows_len):
    mini_mili = []
    for i in range(len(new_grouped_indices)):

        for state in new_grouped_indices[i]:
            mini_mili.append(secarr_grouped[state - 1])
            break

    new_mini_mili = []
    transitions = get_transition(mini_mili)
    transitions_grouped = []
    for i in range(0, len(transitions), rows_len):
        transitionGroup = transitions[i:i + rows_len]
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

def split_arr(array, rows_len):
    splited_mili = []
    for i in range(0, len(array), rows_len):
        splited_mili.append(array[i:i + rows_len])
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


    dot.render('mili_graph', format='png', cleanup=True)

def find_start_number(arr):
    min_number = 100000000000000000
    finalelem = ''
    for i, array in enumerate(arr):
        for j, elem in enumerate(array):
            finalelem = elem
            if len(elem) > 1:
                finalelem = int(elem[1])
            if finalelem < min_number:
                min_number = finalelem
    return min_number


def mili_minimization():
    filename = 'mili_input.csv'

    rows_names, arrays = read_csv_data(filename)
    rows_len = len(rows_names)

    yarray_grouped, transitions_grouped, secarr_grouped = init(arrays, rows_len)
    print('yarray_grouped', yarray_grouped)
    print('transitions_grouped', transitions_grouped)
    print('secarr_grouped', secarr_grouped)
    groups = make_new_group_ygrek(yarray_grouped)
    print('groups', groups)
    grouped_indices = list(groups.values())
    print('grouped_indices', grouped_indices)
    start_number = find_start_number(grouped_indices)
    print(start_number)

    while True:
        mid_array = make_group_transitions(grouped_indices, transitions_grouped, start_number)
        print('mid_array', mid_array)

        mid_groups = make_new_group_indeces(mid_array, grouped_indices)
        new_grouped_indices = list(mid_groups.values())
        print('new_grouped_indices', new_grouped_indices)

        # Если группы не изменились, завершаем процесс
        if new_grouped_indices == grouped_indices:
            break

        grouped_indices = new_grouped_indices

    full_states_mili = make_mini_mili(secarr_grouped, new_grouped_indices, rows_len)# доделатть визуализацию и представление в виде графа финальное
    splitted_arr = split_arr(full_states_mili, rows_len)
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

def read_csv_data_moore(input_file):
    df = pd.read_csv(input_file, sep=';')

    ygreks = df.columns.values[1:]
    ygreks_without_collisions = []
    for i in range(len(ygreks)):
        ygreks_without_collisions.append(ygreks[i].split('.')[0])



    arrays = [df[col].values[1:] for col in df.columns]
    col_names = [df[col].values[:1] for col in df.columns]

    return arrays[0], arrays[1:], col_names[1:], ygreks_without_collisions  # Пропускаем первый столбец, если нужно

def make_new_group_ygrek_moore(yarray_grouped):
    groups = {}
    for i, group in enumerate(yarray_grouped):
        if group not in groups:
            groups[group] = []  # Создаём запись для группы
        groups[group].append(i)  # Добавляем индекс (с 1, если нужно)
    return groups

def initmoore(array, col_len,rows_len):
    transitions = []
    transitions = get_transition_moore(array)
    transitions_grouped = []
    for i in range(0, col_len*rows_len, rows_len):
        transitionGroup = transitions[i:i + rows_len]
        transitions_grouped.append(transitionGroup)

    return transitions_grouped

def get_transition_moore(arr):
    numbers = '1234567890'
    transition = ''
    array = []
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            transition = arr[i][j]
            if transition[0] in numbers:
                array.append(transition)
            else:
                array.append(transition[1:]) # подумать если есть s или нет как исправить

    return array

def make_group_transitions_moore(groups, transtions_grouped, start_number):
    final_aray = []
    for i in range(len(groups)): # по объединенным по y
        second_aray = []
        for j, state in enumerate(groups[i]): # по индексу(состоянию)
            aray = []
            for elem in transtions_grouped[state]: # по переходу

                a = get_group_for_state(int(str(int(elem) - start_number)), groups)
                aray.append(a)
            second_aray.append(aray)
        final_aray.append(second_aray)
    return final_aray


def make_moore_dataframe_and_graph(new_grouped_indices, transitions, rows_names, yarray):
    # Создаем список для хранения строк
    dot = Digraph(comment='Final State Machine')

    rows = []
    col_arr = []
    print(transitions[0])
    yarr = []
    # Создаем узлы для групп
    for group_id, states in enumerate(new_grouped_indices):
        col_arr.append(f'q{group_id}')
        if states[0] in yarray:
            yarr.append(states[0])
        for j, elem in enumerate(yarray):
            if states[0] == j:
                yarr.append(elem)

    print(yarr)

    alltransitions = []
    for i, group in enumerate(transitions):
        for transition in group:
            unique_transitions = []
            if transition not in unique_transitions:
                unique_transitions.append(transition)

        alltransitions.append(unique_transitions)
    print(alltransitions)

    print(col_arr)
    for group_id, states in enumerate(alltransitions):
        print(states)
        for group_transition_id, group_transition in enumerate(states):
            row = []
            for transition in group_transition:
                row.append(f'q{transition}')
            rows.append(row)
    for id, group in enumerate(rows):
        for j, elem in enumerate(group):
            dot.edge(col_arr[id], elem, label = f'{rows_names[j]}')
    transposed_rows = list(zip(*rows))
    transposed_rows = [list(col) for col in transposed_rows]
    print(transposed_rows)
    print(yarr)
    print(col_arr)

    #Создаем DataFrame
    dot.render('final_state_machine', format='png', cleanup=True)

    df = pd.DataFrame(transposed_rows, columns=[yarr, col_arr])
    print(df.columns)
    # Сбрасываем индексацию, чтобы её не было
    return df


def moore_minimization():
    filename = 'moore_input.csv'
    rows_names, arrays, col_names, ygreks = read_csv_data_moore(filename)
    print(ygreks)
    print(col_names)
    print(rows_names)
    print(arrays)

    col_len = len(col_names)
    rows_len = len(rows_names)
    groups = make_new_group_ygrek_moore(ygreks)
    grouped_indices = list(groups.values())
    print('grouped_indices', grouped_indices)
    print('yarray_grouped', ygreks)
    start_number = find_start_number(col_names)

    transitions_grouped= initmoore(arrays, col_len, rows_len)
    print('transitions_grouped',transitions_grouped)

    while True:
        mid_array = make_group_transitions_moore(grouped_indices, transitions_grouped, start_number)
        print('mid_array', mid_array)

        mid_groups = make_new_group_indeces(mid_array, grouped_indices)
        new_grouped_indices = list(mid_groups.values())
        print('new_grouped_indices', new_grouped_indices)

        # Если группы не изменились, завершаем процесс
        if new_grouped_indices == grouped_indices:
            break

        grouped_indices = new_grouped_indices
    print(new_grouped_indices)
    column_names = get_column_names(grouped_indices)
    moore_df = make_moore_dataframe_and_graph(new_grouped_indices, mid_array, rows_names, ygreks)
    print(moore_df)
    moore_df.to_csv('moore_output.csv', sep=';')

moore_minimization()
