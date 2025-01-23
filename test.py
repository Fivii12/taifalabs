# import unittest
# import os
# from lexer import PascalLexer, Token  # Импортируем ваш лексер и класс Token
#
# class TestPascalLexer(unittest.TestCase):
#     def setUp(self):
#         self.test_files = {
#             "empty.pas": "",
#             "whitespace.pas": "   \n  \t  \n",
#             "invalid.pas": "@ # $ %",
#             "unclosed_string.pas": "'unclosed string",
#             "unclosed_comment.pas": "{ unclosed comment",
#             "keyword_as_identifier.pas": "var procedure: integer;",
#             "boundary_numbers.pas": "9999999999999999 3.14e-100 'max_string'",
#             "mixed_tokens.pas": "x := 42 + 3.14; // комментарий",
#         }
#         for filename, content in self.test_files.items():
#             with open(filename, "w") as f:
#                 f.write(content)
#
#     def tearDown(self):
#         # Удаляем временные файлы после тестов
#         for filename in self.test_files:
#             if os.path.exists(filename):
#                 os.remove(filename)
#
#     def test_empty_file(self):
#         lexer = PascalLexer("empty.pas")
#         tokens = lexer.tokenize()
#         self.assertEqual(len(tokens), 0)
#
#     def test_whitespace_only(self):
#         lexer = PascalLexer("whitespace.pas")
#         tokens = lexer.tokenize()
#         self.assertEqual(len(tokens), 0)
#
#     def test_invalid_characters(self):
#         lexer = PascalLexer("invalid.pas")
#         tokens = lexer.tokenize()
#         self.assertTrue(all(token.type == "BAD" for token in tokens))
#
#     def test_unclosed_string(self):
#         lexer = PascalLexer("unclosed_string.pas")
#         tokens = lexer.tokenize()
#         self.assertEqual(tokens[-1].type, "BAD")
#
#     def test_unclosed_comment(self):
#         lexer = PascalLexer("unclosed_comment.pas")
#         tokens = lexer.tokenize()
#         self.assertEqual(tokens[-1].type, "BAD")
#
#     def test_keyword_as_identifier(self):
#         lexer = PascalLexer("keyword_as_identifier.pas")
#         tokens = lexer.tokenize()
#         expected_types = ["VAR", "IDENTIFIER", "COLON", "IDENTIFIER", "SEMICOLON"]
#         self.assertEqual([token.type for token in tokens], expected_types)
#
#     def test_boundary_numbers(self):
#         lexer = PascalLexer("boundary_numbers.pas")
#         tokens = lexer.tokenize()
#         expected_lexemes = ["9999999999999999", "3.14e-100", "'max_string'"]
#         self.assertEqual([token.lexeme for token in tokens], expected_lexemes)
#
#     def test_mixed_tokens(self):
#         lexer = PascalLexer("mixed_tokens.pas")
#         tokens = lexer.tokenize()
#         expected_types = [
#             "IDENTIFIER", "ASSIGN", "INTEGER", "PLUS", "FLOAT", "SEMICOLON", "LINE_COMMENT"
#         ]
#         self.assertEqual([token.type for token in tokens], expected_types)
#
# if __name__ == "__main__":
#     unittest.main()