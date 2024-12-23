from idlelib.configdialog import tracers
from idlelib.pyparse import trans
import pandas as pd
from graphviz import Digraph

is_left = False

def parse_grammar(file_path):
    grammar = {}
    file = open(file_path)
    grammar['H'] = {}
    global is_left
    for line in file:
        line = line.strip()
        print(line)
        left, right = line.split('->')
        left = left.strip()

        for r in right.split('|'):
            left = left.strip('<>')

            if len(r.strip()) == 1:
                symbol = r.strip()[0]
                transition = 'H'
            else:
                if r.strip()[0] == '<': # левосторонняя
                    symbol = r.strip()[-1]
                    transition = r.strip()[0:3]

                    is_left = True
                    print(symbol, transition)
                else:
                    symbol = r.strip()[0]
                    transition = r.strip()[2:3]

            transition = transition.strip('<>')

            if not is_left: # правостороняя
                if left not in grammar: # если нет ключа делаем
                    grammar[left] = {}
                if symbol not in grammar[left]: # если нет переходов делаем
                    grammar[left][symbol] = []
                grammar[left][symbol].append(transition)
            else: # левостороняя
                if transition not in grammar: # если нет ключа делаем
                    grammar[transition] = {}
                if symbol not in grammar[transition]: # если нет переходов делаем
                    grammar[transition][symbol] = []
                grammar[transition][symbol].append(left)
    return grammar


def grammar_to_table(grammar):
    terminals = sorted(set(symbol for transitions in grammar.values() for symbol in transitions.keys())) #терминалы
    nonterminals = sorted(grammar.keys()) # нетерминалы
    print("(terminals, nonterminals)",terminals, nonterminals)
    table = []
    for nonterminal in nonterminals:
        row_data = []
        for symbol in terminals:
            if symbol in grammar.get(nonterminal, {}):
                transitions = grammar[nonterminal][symbol]
                row_data.append(''.join(transitions))
            else:
                row_data.append('-')
        table.append(row_data)

    df = pd.DataFrame(table, index=nonterminals, columns=terminals)
    return df.T

def save_table(df, path):
    df.to_csv(path, sep=";")
path = 'grammar_input.csv'
grammar = parse_grammar(path)
print(grammar)
df = grammar_to_table(grammar)
print(df)
save_path = 'NKA.csv'
save_table(df, save_path)

def nka_to_dka(grammar):
    stack = []
    dka = {}
    processed = set()
    global is_left
    if is_left:
        stack.append('H')
    else:
        stack.append('S')
    f = 0
    while stack:
        f += 1
        print(f, f'current state: {stack}')

        current_state = stack.pop()
        transitions_by_symbol = {}
        for state in current_state:
            if state not in grammar:
                continue

            # символ и переход для состояния
            for symbol, next_states in grammar[state].items():
                print(symbol, next_states)
                if symbol not in transitions_by_symbol:
                    transitions_by_symbol[symbol] = []
                # переходы для символа
                transitions_by_symbol[symbol].extend(next_states)

        print(f"transitions_by_terminal: {transitions_by_symbol}")

        for symbol, transitions in transitions_by_symbol.items():
            print(f"transitions: {symbol, transitions}")
            #соединяем для передачи
            merged_state = ''.join(sorted(set(''.join(transition) for transition in transitions)))
            if current_state not in dka:
                dka[current_state] = {}
            dka[current_state][symbol] = merged_state

            if merged_state not in processed:
                stack.append(merged_state)
        processed.add(current_state)

    return dka

def make_final_graph(dka):
    dot = Digraph(comment='dka')
    for symbol, transitions in dka.items():
        dot.node(symbol)
    for symbol, transitions in dka.items():
        for transition, state in transitions.items():
            dot.edge(symbol, state, label=transition)
    dot.render('dka', format='png', cleanup=True)
    print("Граф сохранен как 'dka'")
dka = nka_to_dka(grammar)
print(dka)

df = grammar_to_table(dka)
print(df)
dka_save_path = 'dka.csv'
save_table(df, dka_save_path)

make_final_graph(dka)