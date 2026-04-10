from kan_lex import lexer
from kan_yacc import parser, variables

with open("test_temp.txt", "r") as f:
    data = f.read()

print(" TOKENS ")
lexer.input(data)
for tok in lexer:
    print(tok)

print("\n PARSER")
result = parser.parse(data, lexer=lexer)

print("\n EXECUTION")
for stmt in result:
    value = stmt()
    print(value)