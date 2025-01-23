from collections import defaultdict, deque

void_transition = '@'
end_state_name = -1

input_file = "input.txt"
output_file = "output.txt"

# convert to nka

def read_regex_from_file(filename):
    with open(filename, 'r') as file:
        regex = ''.join([line.strip() for line in file if line.strip()])
    print(regex)
    return regex


def unite_transitions(states_to_unite, transition_table, final_state):
    for state in states_to_unite:
        transition_table[state][void_transition].add(final_state)
        print(f"{state} -- {void_transition} --> {final_state}")

    states_to_unite.clear()


def get_state_name(start_flag, initial_state, curr_name):
    if not start_flag[0]:
        return curr_name

    start_flag[0] = False
    return initial_state


def add_transition(table, flag, initial_state, curr_name, symbol, next_state):
    state = get_state_name(flag, initial_state, curr_name)
    table[state][symbol].add(next_state)
    print(f"{state} -- {symbol} --> {next_state}")


def regular_expression_to_nka(regex):
    transition_table = defaultdict(lambda: defaultdict(set))
    symbols = set()

    start_flag = [False]
    curr_name = 0
    initial_states = [curr_name]
    states_to_unite = [[]]

    for i, char in enumerate(regex):
        print(f'\nшаг: {i} символ: {char} вершина: {curr_name}')
        if char.isalnum():
            symbols.add(char)

            if i + 1 < len(regex) and regex[i + 1] == '*':
                add_transition(transition_table, start_flag, initial_states[-1], curr_name, void_transition, curr_name + 1) # если звезда то по пустому в некст
                add_transition(transition_table, start_flag, initial_states[-1], curr_name + 1, char, curr_name + 1) # и из некст в себя по символу
            elif i + 1 < len(regex) and regex[i + 1] == '+':
                add_transition(transition_table, start_flag, initial_states[-1], curr_name, char, curr_name + 1) # если плюс то по символу этому в некст
                add_transition(transition_table, start_flag, initial_states[-1], curr_name + 1, char, curr_name + 1) # и из некст в себя по символу
            else:
                add_transition(transition_table, start_flag, initial_states[-1], curr_name, char, curr_name + 1) # просто переход из нынешнего в следующее состояние
            curr_name += 1
        elif char == '|':
            states_to_unite[-1].append(curr_name) # добавляем состояние для объединения
            start_flag[0] = True

        elif char == '(':
            states_to_unite.append([])
            add_transition(transition_table, start_flag, initial_states[-1], curr_name, void_transition, curr_name + 1) # делаем переход в пустую с которой начнем скобку
            initial_states.append(curr_name + 1) # само начало
            curr_name += 1
            print('начало скобок(последнее число - последняя скобка): ', initial_states)
        elif char == ')':
            states_to_unite[-1].append(curr_name)

            if i + 1 < len(regex) and regex[i + 1] == '*':
                unite_transitions(states_to_unite[-1], transition_table, initial_states[-1]) # обратно на начальную для скобки вершину
                transition_table[initial_states[-1]][void_transition].add(curr_name + 1)# из назад вперед
                print(f"{initial_states[-1]} -- {void_transition} --> {curr_name + 1}")
            elif i + 1 < len(regex) and regex[i + 1] == '+':
                unite_transitions(states_to_unite[-1], transition_table, curr_name + 1) # вперед
                transition_table[curr_name + 1][void_transition].add(initial_states[-1]) # из вперед - назад перед скобкой
                print(f"{curr_name + 1} -- {void_transition} --> {initial_states[-1]}")
            else:
                print('состояния для объединения: ', states_to_unite)
                print('стартовые состояния: ', initial_states)
                unite_transitions(states_to_unite[-1], transition_table, curr_name + 1) # просто вперед
            print('состояния для объединения: ', states_to_unite)
            print('стартовые состояния: ', initial_states)
            curr_name += 1
            initial_states.pop()
            states_to_unite.pop()


    states_to_unite[-1].append(curr_name)
    unite_transitions(states_to_unite[-1], transition_table, end_state_name)

    if '@' in symbols:
        symbols.discard('@')

    return [transition_table, symbols, curr_name + 1]


# find e-closures


def find_e_closure(table, state, closure):
    if state not in closure:
        closure.add(state)
        if '@' in table[state]:
            for next_state in table[state]['@']:
                find_e_closure(table, next_state, closure)


def compute_closure(count_states, table):
    epsilon_closures = defaultdict(set)

    for state in range(count_states):
        closure = set()
        find_e_closure(table, state, closure)
        epsilon_closures[state] = closure

    return epsilon_closures


def print_closures(epsilon_closures):
    for state, closure in epsilon_closures.items():
        print(f"{state}: ", end="")
        print(", ".join(map(str, closure)))


# convert to dka


def add_adjustment_state(count_iteration, current_name_state, adjustment_states):
    adjustment_name_state = f"{'q'}{count_iteration}"

    for child_name_state in current_name_state:
        if child_name_state == end_state_name:
            adjustment_name_state += "(end)"
            break

    adjustment_states[tuple(current_name_state)] = adjustment_name_state


def nka_to_dka(ordered_symbols, nka_table, epsilon_closures):
    dka_table = defaultdict(lambda: defaultdict(str))
    dka_states = set()
    ordered_states = []
    state_queue = deque()

    start_state = list(epsilon_closures[0])
    state_queue.append(start_state)
    dka_states.add(tuple(start_state))

    adjustment_states = {}
    add_adjustment_state(0, start_state, adjustment_states)
    ordered_states.append(adjustment_states[tuple(start_state)])

    count_iteration = 1

    while state_queue:
        current_name_state = state_queue.popleft()

        for symbol in ordered_symbols:
            unique_states = set()
            for child_name_state in current_name_state:
                if child_name_state != -1 and symbol in nka_table[child_name_state]:
                    for next_state in nka_table[child_name_state][symbol]:
                        unique_states.update(epsilon_closures[next_state])

            new_name_state = sorted(list(unique_states))

            if not new_name_state:
                dka_table[adjustment_states[tuple(current_name_state)]][symbol] = "-"
                print(f"{adjustment_states[tuple(current_name_state)]} -- {symbol} --> -")
            else:
                if tuple(new_name_state) not in dka_states:
                    add_adjustment_state(count_iteration, new_name_state, adjustment_states)
                    count_iteration += 1

                    state_queue.append(new_name_state)
                    dka_states.add(tuple(new_name_state))
                    ordered_states.append(adjustment_states[tuple(new_name_state)])

                dka_table[adjustment_states[tuple(current_name_state)]][symbol] = adjustment_states[tuple(new_name_state)]
                print(f"{adjustment_states[tuple(current_name_state)]} -- {symbol} --> {adjustment_states[tuple(new_name_state)]}")

    return [dka_table, ordered_states]


def write_to_file_dka(filename, symbols, dka_table, ordered_states):
    with open(filename, "w") as file:

        file.write(";")
        for i, state in enumerate(ordered_states):
            if i == 0:
                file.write("0")
            elif "(end)" in state:
                file.write(";2")
            else:
                file.write(";1")
        file.write("\n")


        file.write(";")
        file.write(";".join([state.replace("(end)", "") for state in ordered_states]))
        file.write("\n")


        for symbol in symbols:
            file.write(f"{symbol}")
            for state in ordered_states:
                transition = dka_table[state][symbol]
                if transition == "-":
                    file.write(";-")
                else:
                    file.write(f";{transition.replace('(end)', '')}")
            file.write("\n")


def main():
    regular_expression = read_regex_from_file(input_file)
    nka_data = regular_expression_to_nka(regular_expression)

    nka_table = nka_data[0]
    symbols = nka_data[1]
    quantity_states = nka_data[2]

    ordered_symbols = sorted(symbols)

    epsilon_closures = compute_closure(quantity_states, nka_table)
    print_closures(epsilon_closures)

    dka_data = nka_to_dka(ordered_symbols, nka_table, epsilon_closures)

    dka_table = dka_data[0]
    ordered_states = dka_data[1]

    write_to_file_dka(output_file, ordered_symbols, dka_table, ordered_states)


if __name__ == "__main__":
    main()