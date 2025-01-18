from collections import defaultdict, deque

void_transition = '@'
end_state_name = -1

input_file = "input.txt"
output_file = "output.txt"

# CONVERT TO NFA


def read_regex_from_file(filename):
    with open(filename, 'r') as file:
        regex = ''.join([line.strip() for line in file if line.strip()])
    print(regex)
    return regex


def finalize_transitions(states_to_finalize, transition_table, final_state):
    for state in states_to_finalize:
        transition_table[state][void_transition].add(final_state)
        print(f"{state} -- {void_transition} --> {final_state}")

    states_to_finalize.clear()


def get_state_name(start_flag, initial_state, curr_name):
    if not start_flag[0]:
        return curr_name

    start_flag[0] = False
    return initial_state


def add_transition(table, flag, initial_state, curr_name, symbol, next_state):
    state = get_state_name(flag, initial_state, curr_name)
    table[state][symbol].add(next_state)
    print(f"{state} -- {symbol} --> {next_state}")


def regular_expression_to_nfa(regex):
    transition_table = defaultdict(lambda: defaultdict(set))
    symbols = set()

    start_flag = [False]
    curr_name = 0
    initial_states = [curr_name]
    states_to_finalize = [[]] #

    for i, char in enumerate(regex):
        if char.isalnum():
            symbols.add(char)

            if i + 1 < len(regex) and regex[i + 1] == '*':
                add_transition(transition_table, start_flag, initial_states[-1], curr_name, void_transition, curr_name + 1)
                add_transition(transition_table, start_flag, initial_states[-1], curr_name + 1, char, curr_name + 1)
            elif i + 1 < len(regex) and regex[i + 1] == '+':
                add_transition(transition_table, start_flag, initial_states[-1], curr_name, char, curr_name + 1)
                add_transition(transition_table, start_flag, initial_states[-1], curr_name + 1, char, curr_name + 1)
            else:
                add_transition(transition_table, start_flag, initial_states[-1], curr_name, char, curr_name + 1)
            curr_name += 1
        elif char == '|':
            states_to_finalize[-1].append(curr_name)
            start_flag[0] = True
        elif char == '(':
            states_to_finalize.append([])
            add_transition(transition_table, start_flag, initial_states[-1], curr_name, void_transition, curr_name + 1)
            initial_states.append(curr_name + 1)
            curr_name += 1
        elif char == ')':
            states_to_finalize[-1].append(curr_name)

            if i + 1 < len(regex) and regex[i + 1] == '*':
                finalize_transitions(states_to_finalize[-1], transition_table, initial_states[-1])
                transition_table[initial_states[-1]][void_transition].add(curr_name + 1)
                print(f"{initial_states[-1]} -- {void_transition} --> {curr_name + 1}")
            elif i + 1 < len(regex) and regex[i + 1] == '+':
                finalize_transitions(states_to_finalize[-1], transition_table, curr_name + 1)
                transition_table[curr_name + 1][void_transition].add(initial_states[-1])
                print(f"{curr_name + 1} -- {void_transition} --> {initial_states[-1]}")
            else:
                finalize_transitions(states_to_finalize[-1], transition_table, curr_name + 1)

            curr_name += 1
            initial_states.pop()
            states_to_finalize.pop()

    states_to_finalize[-1].append(curr_name)
    finalize_transitions(states_to_finalize[-1], transition_table, end_state_name)

    if '@' in symbols:
        symbols.discard('@')

    return [transition_table, symbols, curr_name + 1]


# EPSILON CLOSURES


def dfs(table, state, closure):
    if state not in closure:
        closure.add(state)
        if '@' in table[state]:
            for next_state in table[state]['@']:
                dfs(table, next_state, closure)


def compute_closure(count_states, table):
    epsilon_closures = {}

    for state in range(count_states):
        closure = set()
        dfs(table, state, closure)
        epsilon_closures[state] = closure

    return epsilon_closures


def print_closures(epsilon_closures):
    for state, closure in epsilon_closures.items():
        print(f"{state}: ", end="")
        print(", ".join(map(str, closure)))


# CONVERT TO DFA

def nla_to_dla(grammar, epsilon_closures):
    stack = deque()
    dka = {}
    processed = set()
    stack.append('0')
    f = 0
    qstates = {}
    all_states = []
    while stack:
        is_end = ''
        f += 1
        print(f, f'current state: {stack}')

        current_state = stack.popleft()
        state_for_q = current_state
        for check_state in current_state:
            for aditional_state in epsilon_closures[int(check_state)]:
                if str(aditional_state) not in current_state:
                    if aditional_state == -1:
                        is_end = '(end)'
                    else:
                        current_state += str(aditional_state)

        current_state = sorted(current_state)
        new_state = f'q{f - 1}{is_end}'
        all_states.append(new_state)
        qstates[state_for_q] = ''.join(new_state)
        # eclose
        merged_current_state = ''
        transitions_by_symbol = {}
        for one_state in current_state:

            for state in str(one_state):
                state = int(state)
                if state not in grammar:
                    continue

                # символ и переход для состояния
                for symbol, next_states in grammar[state].items():
                    if symbol == "@":
                        continue
                    print(symbol, next_states)
                    if symbol not in transitions_by_symbol:
                        transitions_by_symbol[symbol] = []
                    # переходы для символа
                    transitions_by_symbol[symbol].extend(next_states)

        print(f"transitions_by_terminal: {transitions_by_symbol}")
        merged_state = ''
        for symbol, transitions in transitions_by_symbol.items():
            print(f"transitions: {symbol, transitions}")
            #соединяем для передачи
            merged_state = ''.join(sorted(set(''.join(str(transition)) for transition in transitions)))
            merged_current_state = ''
            for current_state_1 in current_state:
                merged_current_state += str(current_state_1)
            if state_for_q not in dka:
                dka[state_for_q] = {}
            dka[state_for_q][symbol] = merged_state

            if merged_state not in processed:
                stack.append(merged_state)
                processed.add(merged_state)
        processed.add(merged_current_state)

    a = replace_values(dka, qstates)

    return a, all_states

def replace_values(transitions, reverse_mapping):
    new_transitions = {}
    for state, transitions_dict in transitions.items():
        new_transitions[reverse_mapping.get(state, state)] = {
            symbol: reverse_mapping.get(next_state, next_state)
            for symbol, next_state in transitions_dict.items()
        }
    return new_transitions

def write_to_file_dfa(filename, symbols, dfa_table, ordered_states):
    with open(filename, "w") as file:
        file.write(";" + ";".join(ordered_states) + "\n")

        for symbol in symbols:
            file.write(f"{symbol}")
            for state in ordered_states:
                file.write(f";{dfa_table[state][symbol]}")
            file.write("\n")


def main():
    regular_expression = read_regex_from_file(input_file)
    nfa_data = regular_expression_to_nfa(regular_expression)

    symbols = nfa_data[1]
    ordered_symbols = sorted(symbols)
    nfa_table = nfa_data[0]
    quantity_states = nfa_data[2]

    epsilon_closures = compute_closure(quantity_states, nfa_table)
    print_closures(epsilon_closures)

   # dfa_data = nka_to_dka(nfa_table, epsilon_closures)
    dfa_data = nla_to_dla(nfa_table, epsilon_closures)
    dfa_table = dfa_data[0]
    ordered_states_t = dfa_data[1]
    #
    write_to_file_dfa(output_file, ordered_symbols, dfa_table, ordered_states_t)


if __name__ == "__main__":
    main()