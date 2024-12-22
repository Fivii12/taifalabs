from idlelib.pyparse import trans
import pandas as pd

def parse_grammar(file_path):
    grammar = {}
    inner_transition = {}
    file = open(file_path)
    is_right = False
    grammar['H'] = {}
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

                    is_right = True
                    print(symbol, transition)
                else:
                    symbol = r.strip()[0]
                    transition = r.strip()[2:3]
            transition = transition.strip('<>')
            if not is_right: # левосторонняя
                if left not in grammar: # если нет ключа делаем
                    grammar[left] = {}
                if symbol not in grammar[left]: # если нет переходов делаем
                    grammar[left][symbol] = []
                grammar[left][symbol].append(transition)
            else: # правосторонняя
                if transition not in grammar: # если нет ключа делаем
                    grammar[transition] = {}
                if symbol not in grammar[transition]: # если нет переходов делаем
                    grammar[transition][symbol] = []
                grammar[transition][symbol].append(left)
    return grammar


def grammar_to_table(grammar):
    # Создадим список всех символов для строк и столбцов
    terminals = sorted(set(symbol for transitions in grammar.values() for symbol in transitions.keys())) #терминалы
    nonterminals = sorted(grammar.keys()) # нетерминалы
    # Подготовим таблицу
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

    # Создаем DataFrame для красивого вывода
    df = pd.DataFrame(table, index=nonterminals, columns=terminals)
    return df.T
def save_table(df, path):
    df.to_csv(path, sep=";")
path = 'grammar_input_right.csv'
grammar = parse_grammar(path)
print(grammar)
df = grammar_to_table(grammar)
print(df)
save_path = 'NKA.csv'
save_table(df, save_path)