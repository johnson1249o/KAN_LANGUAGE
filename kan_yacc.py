import ply.yacc as yacc
from kan_lex import tokens

start = 'program'

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'), 
)

variables = {}

#evaluate inner expression first just from writing this
def p_expression_group(p):
    'expression : LPARENTH expression RPARENTH'
    group = p[2]
    p[0] = group

# without lambda, everything is computed at parse time, lambda turns it into a function that gets called at execution time. so instead of try blocks erroring at parse time, they error at execution time
# and can be caught
# but p is a local ply object that becomes invalid when the rule is done, so the values need to be captured as local variables 

def p_expression_plus(p):
    'expression : expression PLUS expression'
    local, local2 = p[1], p[3]
    p[0] = lambda: local() + local2()

def p_expression_minus(p):
    'expression : expression MINUS expression'
    local, local2 = p[1], p[3]
    p[0] = lambda: local() - local2()

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    local = p[2]
    p[0] = lambda: -local()

def p_expression_times(p):
    'expression : expression TIMES expression'
    local, local2 = p[1], p[3]
    p[0] = lambda: local() * local2()

def p_expression_divide(p):
    'expression : expression DIVIDE expression'
    local, local2 = p[1], p[3]
    p[0] = lambda: local() / local2()

def p_expression_number(p):
    'expression : NUMBER'
    number = p[1]
    p[0] = lambda: number

def p_expression_string(p):
    'expression : STRING'
    string = p[1]
    p[0] = lambda: string

#turn identifier into an expression so it can be used for everything
def p_expression_identifier(p):
    'expression : IDENTIFIER'
    local = p[1]
    p[0] = lambda: variables.get(local,local)

def p_expression_assign(p):
    'statement : IDENTIFIER EQUALS expression'
    local, local2 = p[1], p[3]
    def assign():
        variables[local] = local2()
        return variables[local]
    p[0] = assign

#not doing computation just collecting statements into a lis, no lamda needed

#turns expr into statements
def p_statement_expr(p):
    'statement : expression'
    p[0] = p[1]

#handles every newline, grows the program one line at a time
def p_program_multi(p):
    'program : program statement NEWLINE'
    p[0] = p[1] + [p[2]]

#same as above but for the last line without newline because it errors without it
def p_program_multi_eof(p):
    'program : program statement'
    p[0] = p[1] + [p[2]]

#if the entire program is one line with a newline
def p_program_single(p):
    'program : statement NEWLINE'
    p[0] = [p[1]]

#if the entire program is one line
def p_program_no_newline(p):
    'program : statement'
    p[0] = [p[1]]


def p_statement_try(p):
    'statement : LSQRBRACKET LSQRBRACKET statement RSQRBRACKET NEWLINE statement RSQRBRACKET'
    tryblock, handler = p[3], p[6]
    def try_block():
        try:
            return tryblock()
        except Exception:
            return handler()
    p[0] = try_block

#ply buils bottom up so even though this also uses square brackets like try block, it will be consumed into the print statement before anything goes wrong
def p_statement_println(p):
    'statement : PRINTLN LSQRBRACKET arglist RSQRBRACKET'
    args = p[3]
    def println():
        print(*[a() for a in args])
        return "" # so it doesnt return none and look ugly in terminal
    p[0] = println

def p_arglist_multi(p):
    'arglist : arglist COMMA expression'
    arg, expr = p[1], p[3]
    p[0] = arg + [expr]

def p_arglist_single(p):
    'arglist : expression'
    expr = p[1]
    p[0] = [expr]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' (type {p.type}) on line {p.lineno}")
    else:
        print("Syntax error at end of input")

parser = yacc.yacc()