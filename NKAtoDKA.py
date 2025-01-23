import pandas as pd
df = pd.read_csv('nka_input.csv', sep=';', index_col=0, header=0, dtype=str)
df = df.dropna(axis=0, how='all')  # Удаляем строки, где все значения NaN
df = df[df.index.notna()]  # Удаляем строки с NaN в индексе
print(df)
# Убираем дробную часть из заголовков столбцов
df.columns = [col.split('.')[0] for col in df.columns]
# Убедимся, что индексы строк — строки
df.index = df.index.astype(float).astype(int).astype(str)  # Преобразуем в float, затем в int, затем в st
print(df)

def df_to_grammar(df):
    grammar = {}
    symbols = df.index.tolist()  # Символы (0, 1, 2, 3)
    states = df.columns.tolist()  # Состояния (q0, q1, q2, ...)
    symbols_without_dot = [symbol.split('.')[0] for symbol in symbols]
    for state in states:
        grammar[state] = {}
        for symbol in symbols:
            next_states = df.loc[symbol, state]
            if next_states == '-':
                grammar[state][symbol] = []
            else:
                grammar[state][symbol] = [next_states]
    return grammar
grammar = df_to_grammar(df)
print(grammar)
def nka_to_dka(grammar):
    stack = []
    dka = {}
    processed = set()
    initial_state = list(grammar.keys())[0]
    stack.append(initial_state)
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

is_left = True
dka = nka_to_dka(grammar)
print(dka)