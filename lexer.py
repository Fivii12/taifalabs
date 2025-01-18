import sys
import re

# Определение токенов
tokens = [
    # Ключевые слова
    'ARRAY', 'BEGIN', 'ELSE', 'END', 'IF', 'OF', 'OR', 'PROGRAM', 'PROCEDURE', 'THEN', 'TYPE', 'VAR',
    # Операторы и знаки пунктуации
    'MULTIPLICATION', 'PLUS', 'MINUS', 'DIVIDE', 'SEMICOLON', 'COMMA', 'LEFT_PAREN', 'RIGHT_PAREN',
    'LEFT_BRACKET', 'RIGHT_BRACKET', 'EQ', 'GREATER', 'LESS', 'LESS_EQ', 'GREATER_EQ', 'NOT_EQ', 'COLON',
    'ASSIGN', 'DOT',
    # Литералы и идентификаторы
    'IDENTIFIER', 'STRING', 'INTEGER', 'FLOAT',
    # Комментарии
    'LINE_COMMENT', 'BLOCK_COMMENT',
    # Специальные
    'BAD', 'EOF'
]

# Регулярные выражения для токенов
token_regex = [
    # ключевые слова (регистронезависимые)
    (r'\b(?i:array)\b', 'ARRAY'),
    (r'\b(?i:begin)\b', 'BEGIN'),
    (r'\b(?i:else)\b', 'ELSE'),
    (r'\b(?i:end)\b', 'END'),
    (r'\b(?i:if)\b', 'IF'),
    (r'\b(?i:of)\b', 'OF'),
    (r'\b(?i:or)\b', 'OR'),
    (r'\b(?i:program)\b', 'PROGRAM'),
    (r'\b(?i:procedure)\b', 'PROCEDURE'),
    (r'\b(?i:then)\b', 'THEN'),
    (r'\b(?i:type)\b', 'TYPE'),
    (r'\b(?i:var)\b', 'VAR'),
    # операторы и пунктуация
    (r'\*', 'MULTIPLICATION'),
    (r'\+', 'PLUS'),
    (r'-', 'MINUS'),
    (r'/', 'DIVIDE'),
    (r';', 'SEMICOLON'),
    (r',', 'COMMA'),
    (r'\(', 'LEFT_PAREN'),
    (r'\)', 'RIGHT_PAREN'),
    (r'\[', 'LEFT_BRACKET'),
    (r'\]', 'RIGHT_BRACKET'),
    (r'=', 'EQ'),
    (r'>', 'GREATER'),
    (r'<', 'LESS'),
    (r'<=', 'LESS_EQ'),
    (r'>=', 'GREATER_EQ'),
    (r'<>', 'NOT_EQ'),
    (r':=', 'ASSIGN'),
    (r':', 'COLON'),
    (r'\.', 'DOT'),
    # литералы идентификаторы
    (r'[a-zA-Z_][a-zA-Z0-9_]{0,255}', 'IDENTIFIER'),
    (r"'[^']*'", 'STRING'),
    (r'\d+\.\d+([eE][+-]?\d+)?', 'FLOAT'),
    (r'\d{1,16}', 'INTEGER'),
    # комментарии
    (r'//.*', 'LINE_COMMENT'),
    (r'\{[^}]*\}', 'BLOCK_COMMENT'),
    # пробелы и конец строки
    (r'[ \t]+', None),
    (r'\n', None),
    # некорректные символы
    (r'[^\s]', 'BAD')
]

# Класс для хранения информации о токене
class Token:
    def __init__(self, type, lexeme, line, column):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __str__(self):
        return f'{self.type} ({self.line}, {self.column}) "{self.lexeme}"'

# Лексический анализатор
class PascalLexer:
    def __init__(self, input_file):
        self.input_file = input_file
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        self.buffer = ""
        self.position = 0

    def next_token(self):
        if self.position >= len(self.buffer):
            return None  # Конец файла

        for regex, token_type in token_regex:
            match = re.match(regex, self.buffer[self.position:])
            if match:
                lexeme = match.group(0)
                if token_type is None:
                    # Пропускаем пробелы и символы новой строки
                    if '\n' in lexeme:
                        self.current_line += lexeme.count('\n')
                        self.current_column = 1
                    else:
                        self.current_column += len(lexeme)
                    self.position += len(lexeme)
                    return self.next_token()
                token = Token(token_type, lexeme, self.current_line, self.current_column)
                self.position += len(lexeme)
                self.current_column += len(lexeme)
                if token_type in ['LINE_COMMENT', 'BLOCK_COMMENT']:
                    # Пропускаем комментарии
                    return self.next_token()
                return token

        # Если не удалось распознать токен, возвращаем BAD
        lexeme = self.buffer[self.position]
        token = Token('BAD', lexeme, self.current_line, self.current_column)
        self.position += 1
        self.current_column += 1
        return token

    def tokenize(self):
        with open(self.input_file, 'r') as file:
            self.buffer = file.read()

        tokens = []
        while True:
            token = self.next_token()
            if token is None:
                break
            tokens.append(token)
        return tokens

# Основная функция
def main():
    if len(sys.argv) != 3:
        print("Usage: python PascalLexer.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    lexer = PascalLexer(input_file)
    tokens = lexer.tokenize()

    with open(output_file, 'w') as output:
        for token in tokens:
            print(token)  # Печатает токен в консоль
            output.write(str(token) + '\n')

if __name__ == "__main__":
    main()