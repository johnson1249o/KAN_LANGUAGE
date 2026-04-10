from kan_lex import lexer

class SemanticError:
    def __init__(self, message, line=None):
        self.message = message
        self.line = line

    def __str__(self):
        if self.line:
            return f"[Line {self.line}] {self.message}"
        return self.message


def analyze(source):
    errors = []

    tokens_list = []
    lexer.input(source)
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)

    # track assigned variables per scope level
    scope_stack = [set()]

    def current_scope():
        return scope_stack[-1]

    def is_defined(name):
        for scope in reversed(scope_stack):
            if name in scope:
                return True
        return False

    def define(name):
        current_scope().add(name)

    i = 0
    n = len(tokens_list)

    while i < n:
        tok = tokens_list[i]

        if tok.type == 'IDENTIFIER' and i + 1 < n and tokens_list[i + 1].type == 'EQUALS':
            define(tok.value)
            # Check the RHS for issues starting at i+2
            i += 2
            # Check expression tokens on the RHS until NEWLINE or end
            j = i
            prev_was_operator = True  # expect operand first
            while j < n and tokens_list[j].type != 'NEWLINE':
                rhs = tokens_list[j]

                # Undefined variable on RHS
                if rhs.type == 'IDENTIFIER':
                    if not is_defined(rhs.value):
                        errors.append(SemanticError(
                            f"Undefined variable '{rhs.value}' used in expression",
                            rhs.lineno
                        ))

                # Division by zero: DIVIDE followed by NUMBER 0
                if rhs.type == 'DIVIDE' and j + 1 < n:
                    next_tok = tokens_list[j + 1]
                    if next_tok.type == 'NUMBER' and next_tok.value == 0:
                        errors.append(SemanticError(
                            "Division by zero detected in expression",
                            rhs.lineno
                        ))

                # type mismatch
                if rhs.type == 'STRING':
                    has_arith_left = j > 0 and tokens_list[j - 1].type in ('TIMES', 'DIVIDE', 'MINUS')
                    has_arith_right = j + 1 < n and tokens_list[j + 1].type in ('TIMES', 'DIVIDE', 'MINUS')
                    
                    plus_left = j > 0 and tokens_list[j - 1].type == 'PLUS' and j - 2 >= 0 and tokens_list[j - 2].type == 'NUMBER'
                    plus_right = j + 1 < n and tokens_list[j + 1].type == 'PLUS' and j + 2 < n and tokens_list[j + 2].type == 'NUMBER'

                    if has_arith_left or has_arith_right or plus_left or plus_right:
                        errors.append(SemanticError(
                            f"Type mismatch: string '{rhs.value}' used in arithmetic operation",
                            rhs.lineno
                        ))

                j += 1
            i = j
            continue

        if tok.type == 'IDENTIFIER':

            if i + 2 < n and tokens_list[i + 1].type == 'LSQRBRACKET' and tokens_list[i + 2].type == 'RSQRBRACKET':
                if not is_defined(tok.value):
                    errors.append(SemanticError(
                        f"Call to undefined function '{tok.value}'",
                        tok.lineno
                    ))
                i += 3
                continue

            # function definition: IDENTIFIER [[ ... ]]
            if i + 1 < n and tokens_list[i + 1].type == 'LSQRBRACKET':
                define(tok.value)
                i += 1
                continue

            # plain use of identifier
            if not is_defined(tok.value):
                # only flag if not immediately followed by EQUALS
                if not (i + 1 < n and tokens_list[i + 1].type == 'EQUALS'):
                    errors.append(SemanticError(
                        f"Undefined variable '{tok.value}'",
                        tok.lineno
                    ))

        # scope push
        if tok.type == 'LSQRBRACKET' and i + 1 < n and tokens_list[i + 1].type == 'LSQRBRACKET':
            scope_stack.append(set())

        # scope pop
        if tok.type == 'RSQRBRACKET' and i + 1 < n and tokens_list[i + 1].type == 'RSQRBRACKET':
            if len(scope_stack) > 1:
                scope_stack.pop()

        # division by zero
        if tok.type == 'DIVIDE' and i + 1 < n:
            next_tok = tokens_list[i + 1]
            if next_tok.type == 'NUMBER' and next_tok.value == 0:
                errors.append(SemanticError(
                    "Division by zero detected",
                    tok.lineno
                ))

        i += 1

    return errors


def format_results(errors):
    if not errors:
        return "Semantic analysis passed — no errors found."
    lines = ["Semantic Analysis — Issues Found:\n"]
    for e in errors:
        lines.append(f"  • {e}")
    return "\n".join(lines)
