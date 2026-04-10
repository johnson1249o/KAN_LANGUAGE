import ply.yacc as yacc
from kan_lex import tokens

start = 'program'

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'), 
)

variables = [{}] #list of dicts to make variable scopes

#walks scope stack from inner to outer to find variable
def get_var(name):
    for scope in reversed(variables):
        if name in scope:
            return scope[name]
    return name

#sets variable in innermost scope
def set_var(name, value):
    variables[-1][name] = value

#push and pop at start and end of function blocks to create new variable scopes, so they dont affect outer scopes and get cleaned up after the function ends
def push_scope():
    variables.append({})

def pop_scope():
    variables.pop()

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
    p[0] = lambda: get_var(local)

def p_expression_assign(p):
    'statement : IDENTIFIER EQUALS expression'
    local, local2 = p[1], p[3]
    def assign():
        set_var(local, local2())
        return get_var(local)
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

#handle multiple empty lines
def p_program_empty_line(p):
    'program : program NEWLINE'
    p[0] = p[1]

#if it starts with a newline
def p_program_single_empty(p):
    'program : NEWLINE'
    p[0] = []


def p_anon_function(p):
    'expression : LSQRBRACKET LSQRBRACKET program RSQRBRACKET RSQRBRACKET'
    body = p[3]
    def function():
        push_scope()
        for stmt in body:
            result = stmt()
        pop_scope()
        return result
    p[0] = function

def p_anon_try_function(p):
    'statement : LSQRBRACKET LSQRBRACKET program RSQRBRACKET program RSQRBRACKET'
    tryblock, handler = p[3], p[5]
    def try_block():
        try:
            for stmt in tryblock:
                result = stmt()
            return result
        except Exception:
            for stmt in handler:
                result = stmt()
            return result
    p[0] = try_block

def p_function_define(p):
    'expression : IDENTIFIER LSQRBRACKET LSQRBRACKET program RSQRBRACKET RSQRBRACKET'
    name, body = p[1], p[4]
    def define():
        def function():
            push_scope()
            for stmt in body:
                result = stmt()
            pop_scope()
            return result
        set_var(name, function)
    p[0] = define

def p_try_function_define(p):
    'expression : IDENTIFIER LSQRBRACKET LSQRBRACKET program RSQRBRACKET program RSQRBRACKET'
    name, tryblock, handler = p[1], p[4], p[6]
    def define():
        def try_block():
            push_scope()
            try:
                for stmt in tryblock:
                    result = stmt()
                pop_scope()
                return result
            except Exception:
                pop_scope()
                push_scope()
                for stmt in handler:
                    result = stmt()
                pop_scope()
                return result
        set_var(name, try_block)
    p[0] = define

def p_paramlist_multi(p):
    'paramlist : paramlist COMMA IDENTIFIER'
    p[0] = p[1] + [p[3]]

def p_paramlist_single(p):
    'paramlist : IDENTIFIER'
    p[0] = [p[1]]

def p_function_define_input(p):
    'expression : IDENTIFIER LSQRBRACKET paramlist LSQRBRACKET program RSQRBRACKET RSQRBRACKET'
    name, params, body = p[1], p[3], p[5]
    def define():
        def function(*args):
            push_scope()
            for param, arg in zip(params, args):
                set_var(param, arg)
            for stmt in body:
                result = stmt()
            pop_scope()
            return result
        set_var(name, function)
    p[0] = define

def p_try_function_define_input(p):
    'expression : IDENTIFIER LSQRBRACKET paramlist LSQRBRACKET program RSQRBRACKET program RSQRBRACKET'
    name, params, tryblock, handler = p[1], p[3], p[5], p[7]
    def define():
        def try_block(*args):
            push_scope()
            for param, arg in zip(params, args):
                set_var(param, arg)
            try:
                for stmt in tryblock:
                    result = stmt()
                pop_scope()
                return result
            except Exception:
                pop_scope()
                push_scope()
                for stmt in handler:
                    result = stmt()
                pop_scope()
                return result
        set_var(name, try_block)
    p[0] = define


#ply builds bottom up so even though this also uses square brackets like try block, it will be consumed into the print statement before anything goes wrong
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