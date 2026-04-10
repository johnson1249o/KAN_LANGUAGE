import ply.lex as lex

keywords = {
    'println': 'PRINTLN',
}

tokens = (
   'IDENTIFIER',
   'STRING',
   'NUMBER',
   'PLUS',
   'MINUS',
   'EQUALS',
   'TIMES',
   'DIVIDE',
   'LSQRBRACKET',
   'RSQRBRACKET',
   'LPARENTH',
   'RPARENTH',
   'NEWLINE',
   'COMMA',
)+ tuple(keywords.values())

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_EQUALS  = r'\='
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LSQRBRACKET = r'\['
t_RSQRBRACKET = r'\]'
t_LPARENTH = r'\('
t_RPARENTH = r'\)'
t_COMMA = r','
t_ignore  = ' \t'


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, 'IDENTIFIER') #if in keyword dict use that type otherwise use identifier
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1] #everything except first and last character which are the quotes
    return t

#unless put in a function that turns it into an int, the value will stay a string, so numbers get put in here
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    # 1 or more numbers, and in the group theres \. which means an actual decimal point, \d+ 1 or moore again then question mark in the group to mark it as optional, so int or float is possible
    
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
        
    return t

#count and return newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    print(f"Illegal character: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()
    