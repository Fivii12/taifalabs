import unittest
import os
from lexer import PascalLexer, Token  # Замените на ваш модуль

class TestPascalLexer(unittest.TestCase):
    def setUp(self):
        # Создаем временные файлы для тестов
        self.test_files = {
            "empty.pas": "",
            "whitespace.pas": "   \n  \t  \n",
            "keywords.pas": "PROGRAM program Program",
            "identifiers.pas": "var x1, _y2, z_3: integer;",
            "floats.pas": "x := 3.14 + 2.5e-10;",
            "unclosed_string.pas": "'unclosed string",
            "invalid_characters.pas": "@begin",
            "mixed_tokens.pas": "x := 42 + 3.14; // комментарий",
            "multiline_comment.pas": "{комментарий\nна\nнесколько\nстрок}",
            "keyword_as_identifier.pas": "var procedure: integer;",
        }
        for filename, content in self.test_files.items():
            with open(filename, "w") as f:
                f.write(content)

    def tearDown(self):
        # Удаляем временные файлы после тестов
        for filename in self.test_files:
            if os.path.exists(filename):
                os.remove(filename)

    def test_empty_file(self):
        lexer = PascalLexer("empty.pas")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 0)

    def test_whitespace_only(self):
        lexer = PascalLexer("whitespace.pas")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 0)

    def test_keywords_case_insensitive(self):
        lexer = PascalLexer("keywords.pas")
        tokens = lexer.tokenize()
        expected_types = ["PROGRAM", "PROGRAM", "PROGRAM"]
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_identifiers(self):
        lexer = PascalLexer("identifiers.pas")
        tokens = lexer.tokenize()
        expected_lexemes = ["x1", "_y2", "z_3", "integer"]
        self.assertEqual([token.lexeme for token in tokens if token.type == "IDENTIFIER"], expected_lexemes)

    def test_floats(self):
        lexer = PascalLexer("floats.pas")
        tokens = lexer.tokenize()
        expected_lexemes = ["3.14", "2.5e-10"]
        self.assertEqual([token.lexeme for token in tokens if token.type == "FLOAT"], expected_lexemes)

    def test_unclosed_string(self):
        lexer = PascalLexer("unclosed_string.pas")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[-1].type, "BAD")

    def test_invalid_characters(self):
        lexer = PascalLexer("invalid_characters.pas")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, "BAD")

    def test_mixed_tokens(self):
        lexer = PascalLexer("mixed_tokens.pas")
        tokens = lexer.tokenize()
        expected_types = ["IDENTIFIER", "ASSIGN", "INTEGER", "PLUS", "FLOAT", "SEMICOLON", "LINE_COMMENT"]
        self.assertEqual([token.type for token in tokens], expected_types)

    def test_multiline_comment(self):
        lexer = PascalLexer("multiline_comment.pas")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, "BLOCK_COMMENT")

    def test_keyword_as_identifier(self):
        lexer = PascalLexer("keyword_as_identifier.pas")
        tokens = lexer.tokenize()
        expected_types = ["VAR", "IDENTIFIER", "COLON", "IDENTIFIER", "SEMICOLON"]
        self.assertEqual([token.type for token in tokens], expected_types)

if __name__ == "__main__":
    unittest.main()