import sys
import re

# определение токенов
tokens = [
    # ключевые слова
    'ARRAY', 'BEGIN', 'ELSE', 'END', 'IF', 'OF', 'OR', 'PROGRAM', 'PROCEDURE', 'THEN', 'TYPE', 'VAR',
    # операторы и знаки пунктуации
    'MULTIPLICATION', 'PLUS', 'MINUS', 'DIVIDE', 'SEMICOLON', 'COMMA', 'LEFT_PAREN', 'RIGHT_PAREN',
    'LEFT_BRACKET', 'RIGHT_BRACKET', 'EQ', 'GREATER', 'LESS', 'LESS_EQ', 'GREATER_EQ', 'NOT_EQ', 'COLON',
    'ASSIGN', 'DOT',
    # литералы и идентификаторы
    'IDENTIFIER', 'STRING', 'INTEGER', 'FLOAT',
    # комментарии
    'LINE_COMMENT', 'BLOCK_COMMENT',
    # специальные
    'BAD', 'EOF'
]

RESERVED_KEYWORDS = {
    'array': 'ARRAY',
    'begin': 'BEGIN',
    'else': 'ELSE',
    'end': 'END',
    'if': 'IF',
    'of': 'OF',
    'or': 'OR',
    'program': 'PROGRAM',
    'procedure': 'PROCEDURE',
    'then': 'THEN',
    'type': 'TYPE',
    'var': 'VAR',
}

# регулярные выражения для токенов
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
    # комментарии
    (r'//.*', 'LINE_COMMENT'),
    (r'\{[^}]*\}', 'BLOCK_COMMENT'),
    # литералы идентификаторы
    (r'[a-zA-Z_][a-zA-Z0-9_]{0,255}', 'IDENTIFIER'),
    (r"'[^']*'", 'STRING'),
    (r'\d+\.\d+([eE][+-]?\d+)?', 'FLOAT'),
    (r'\d{1,16}', 'INTEGER'),
    # операторы и пунктуация
    (r':=', 'ASSIGN'),
    (r':', 'COLON'),
    (r'\.', 'DOT'),
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
    (r'<=', 'LESS_EQ'),
    (r'>=', 'GREATER_EQ'),
    (r'<>', 'NOT_EQ'),
    (r'=', 'EQ'),
    (r'>', 'GREATER'),
    (r'<', 'LESS'),
    # пробелы и конец строки
    (r'[ \t]+', None),
    (r'\n', None),
    # некорректные символы
    (r'\{[^}]*', 'BAD'),
    (r'[^\s]', 'BAD')
]

# класс для хранения информации о токене
class Token:
    def __init__(self, type, lexeme, line, column):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __str__(self):
        return f'{self.type} ({self.line}, {self.column}) "{self.lexeme}"'

# лексер
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
            return None  # конец файла

        for regex, token_type in token_regex:
            match = re.match(regex, self.buffer[self.position:])
            if match:
                lexeme = match.group(0)
                if token_type is None:

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
                    # пропускаем комментарии
                    return self.next_token()
                if token_type == 'IDENTIFIER' and lexeme.lower() in RESERVED_KEYWORDS:
                    return Token('BAD', lexeme, self.current_line, self.current_column)
                return token

        # если не удалось распознать токен, возвращаем BAD
        lexeme = self.buffer[self.position]
        token = Token('BAD', lexeme, self.current_line, self.current_column)
        print(token)
        self.position += 1
        self.current_column += 1
        return token

    def tokenize(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
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
        print("использование: python lexer.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    lexer = PascalLexer(input_file)
    tokens = lexer.tokenize()

    with open(output_file, 'w', encoding='utf-8') as output:
        for token in tokens:
            print(token)
            output.write(str(token) + '\n')

if __name__ == "__main__":
    main()