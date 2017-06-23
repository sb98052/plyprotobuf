__author__ = "Sapan Bhatia"

__copyright__ = "Copyright (C) 2017 Open Networking Lab"
__version__ = "1.0"

import ply.lex as lex
import ply.yacc as yacc

from helpers import LexHelper, LU

class FOLLexer(object):
    keywords = ('forall', 'exists', 'true', 'false', 'not')

    tokens = ['ESCAPE', 'COLON', 'IMPLIES', 'OR', 'AND', 'LPAREN', 'RPAREN', 'EQUALS', 'SYMBOL', 'LT', 'RT'] + [k.upper() for k in keywords]
    # literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_ignore_LINE_COMMENT = '//.*'
    t_COLON = '\\:'
    t_IMPLIES = '\\-\\>'
    t_OR = '\\|'
    t_LT = '\\<'
    t_RT = '\\>'
    t_AND = '\\&'
    t_LPAREN = '\\('
    t_RPAREN = '\\)'

    t_EQUALS = '\\='

    literals = '()+-*/=?:,.^|&~!=[]{};<>@%'

    t_ignore = ' \t\f'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_newline2(self, t):
        r'(\r\n)+'
        t.lexer.lineno += len(t.value) / 2

    t_ESCAPE = r'{{ (.|\n)*? }}'

    def t_BLOCK_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    def t_SYMBOL(self, t):
        '[A-Za-z_$][\.A-Za-z0-9_+$]*'
        if t.value in FOLLexer.keywords:
            t.type = t.value.upper()
        return t

    def t_error(self, t):
        print("Illegal character '{}' ({}) in line {}".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno))
        t.lexer.skip(1)
 
    
    
class FOLParser(object):
    tokens = FOLLexer.tokens
    offset = 0
    lh = LexHelper()

    def setOffset(self, of):
        self.offset = of
        self.lh.offset = of

    def p_empty(self, p):
        '''empty :'''
        pass

    def p_term_constant(self, p):
        '''term :   FALSE
                    | TRUE'''
        p[0] = p[1]

    def p_fole_not(self, p):
        '''fole : NOT fole'''
        p[0] = {p[1]: p[2]}

    def p_fole_term(self, p):
        '''fole : term'''
        p[0] = p[1]

    def p_term_symbol(self, p):
        '''term : SYMBOL'''
        p[0] = p[1]

    def p_term_python(self, p):
        '''fole : ESCAPE '''
        p[0] = {'python': p[1]}

    def p_fole_group(self, p):
        "fole : LPAREN fole RPAREN"
        p[0] = p[2]

    def p_fole_equals(self, p):
        "fole : term EQUALS term"
        p[0] = {'=': (p[1], p[3])}

    def p_fole_binary(self, p):
        '''fole : fole AND fole
                  | fole OR fole
                  | fole IMPLIES fole'''
        p[0] = {p[2]: [p[1], p[3]]}

    def p_fole_quant(self, p):
        '''fole :     FORALL SYMBOL COLON fole
                      | EXISTS SYMBOL COLON fole'''
        p[0] = {p[1]: [p[2], p[4]]}

    
    def p_goal(self, p):
        '''goal : LT fole RT'''
        p[0] = p[2]

    def p_error(self, p):
        print('error: {}'.format(p))
