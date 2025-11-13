import sys
from enum import Enum, auto
from dataclasses import dataclass

# ==================================================================
# TokenType: Sem alterações
# ==================================================================
class TokenType(Enum):
    # Palavras-chave básicas e o 'while' adicionado
    INT, FLOAT, PRINT, IF, ELSE, WHILE = auto(), auto(), auto(), auto(), auto(), auto()
    
    # Símbolos literais e identificadores
    IDENTIFIER, NUMBER, STRING_LITERAL = auto(), auto(), auto()
    
    # Operadores aritméticos
    PLUS, MINUS, STAR, SLASH = auto(), auto(), auto(), auto()
    
    # Atribuição e comparação
    ASSIGN = auto() # =
    GREATER, GREATER_EQUAL, LESS, LESS_EQUAL = auto(), auto(), auto(), auto() # >, >=, <, <=
    NOT_EQUAL, EQUAL = auto(), auto() # !=, ==
    
    # Delimitadores
    LEFT_PAREN, RIGHT_PAREN = auto(), auto() # ( )
    LEFT_CURLY, RIGHT_CURLY = auto(), auto() # { }
    SEMICOLON = auto() # ;
    DOT = auto() # .
    COLON = auto() # :
    
    # Operadores lógicos
    OP_LOGICO_AND, OP_LOGICO_OR = auto(), auto() # &&, ||
    
    # Palavras-chave específicas da nova gramática
    KEYWORD_LET, KEYWORD_CONST = auto(), auto()
    KEYWORD_FUNCTION, KEYWORD_MAIN = auto(), auto()
    KEYWORD_TYPE_NUMBER, KEYWORD_TYPE_FLOAT = auto(), auto()
    KEYWORD_READ, KEYWORD_CONSOLELOG = auto(), auto()


KEYWORDS = {
    # Mapeamento de Palavras-chave
    "int": TokenType.KEYWORD_TYPE_NUMBER,
    "float": TokenType.KEYWORD_TYPE_FLOAT, 
    
    "print": TokenType.PRINT,
    "if": TokenType.IF, "else": TokenType.ELSE, "while": TokenType.WHILE,
    
    "let": TokenType.KEYWORD_LET, "const": TokenType.KEYWORD_CONST,
    "read": TokenType.KEYWORD_READ,
    "function": TokenType.KEYWORD_FUNCTION, "main": TokenType.KEYWORD_MAIN,
    "number": TokenType.KEYWORD_TYPE_NUMBER,
    "console": TokenType.KEYWORD_CONSOLELOG,
}

# ==================================================================
# Token: Sem alterações
# ==================================================================
@dataclass
class Token:
    type: TokenType
    text: str
    def __str__(self): return f"Token(type={self.type.name}, text='{self.text}')"

# ==================================================================
# Scanner: Sem alterações
# ==================================================================
class Scanner:
    def __init__(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.source_code = file.read()
        except IOError as e:
            print(f"Erro ao ler o arquivo '{filename}': {e}")
            sys.exit(1)
        
        self.pos = 0
        self.line = 1
        self.column = 1

    def is_eof(self) -> bool: return self.pos >= len(self.source_code)
    
    def peek(self) -> str | None:
        return None if self.is_eof() else self.source_code[self.pos]

    def _advance(self) -> str:
        """Consome o próximo caractere e atualiza a linha/coluna."""
        char = self.source_code[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def next_token(self) -> Token | None:
        while True:
            start_line, start_col = self.line, self.column
            while not self.is_eof() and self.peek().isspace(): self._advance()
            if self.is_eof(): return None

            if self.peek() == '#':
                while not self.is_eof() and self.peek() != '\n': self._advance()
                continue
            # Tratamento de comentário de múltiplas linhas (/* */)
            if self.peek() == '/' and self.pos + 1 < len(self.source_code) and self.source_code[self.pos + 1] == '*':
                self._advance(); self._advance() 
                while not self.is_eof():
                    if self.peek() == '*' and self.pos + 1 < len(self.source_code) and self.source_code[self.pos + 1] == '/':
                        self._advance(); self._advance() 
                        break
                    else:
                        self._advance()
                else:
                    raise RuntimeError(f"Erro Léxico (Linha {start_line}, Coluna {start_col}): Comentário de múltiplas linhas não foi fechado.")
                continue
            break
        
        if self.is_eof(): return None

        start_line, start_col = self.line, self.column
        current_char_peek = self.peek()
        
        # 1. Literais de String (CADEIA)
        if current_char_peek == '"':
            self._advance() # Consome o aspas inicial
            content = ""
            while not self.is_eof() and self.peek() != '"':
                content += self._advance()
            if self.is_eof():
                raise RuntimeError(f"Erro Léxico (Linha {start_line}, Coluna {start_col}): String não fechada.")
            self._advance() # Consome o aspas final
            return Token(TokenType.STRING_LITERAL, content)

        # 2. Números (NUMINT/NUMREAL)
        if current_char_peek.isdigit() or (current_char_peek == '.' and self.pos + 1 < len(self.source_code) and self.source_code[self.pos + 1].isdigit()):
            content = ""
            if self.peek().isdigit():
                content += self._advance()
                while not self.is_eof() and self.peek().isdigit(): content += self._advance()
            if not self.is_eof() and self.peek() == '.':
                if self.pos + 1 < len(self.source_code) and self.source_code[self.pos + 1].isdigit():
                    content += self._advance()
                    while not self.is_eof() and self.peek().isdigit(): content += self._advance()
            return Token(TokenType.NUMBER, content)

        # 3. Identificadores e Palavras-chave
        if current_char_peek.isalpha() or current_char_peek == '_':
            content = self._advance()
            while not self.is_eof() and (self.peek().isalnum() or self.peek() == '_'):
                content += self._advance()
            token_type = KEYWORDS.get(content, TokenType.IDENTIFIER)
            return Token(token_type, content)

        # 4. Operadores e Delimitadores de um ou dois caracteres
        current_char = self._advance()
        if current_char == '+': return Token(TokenType.PLUS, current_char)
        if current_char == '-': return Token(TokenType.MINUS, current_char)
        if current_char == '*': return Token(TokenType.STAR, current_char)
        if current_char == '/': return Token(TokenType.SLASH, current_char)
        if current_char == '(': return Token(TokenType.LEFT_PAREN, current_char)
        if current_char == ')': return Token(TokenType.RIGHT_PAREN, current_char)
        if current_char == '{': return Token(TokenType.LEFT_CURLY, current_char)
        if current_char == '}': return Token(TokenType.RIGHT_CURLY, current_char)
        if current_char == ';': return Token(TokenType.SEMICOLON, current_char)
        if current_char == ':': return Token(TokenType.COLON, current_char)
        if current_char == '.': return Token(TokenType.DOT, current_char)
        
        # Operadores de dois caracteres (==, >=, <=, !=) e Lógicos (&&, ||)
        
        # Comparação (==) e Atribuição (=)
        if current_char == '=':
            if self.peek() == '=': self._advance(); return Token(TokenType.EQUAL, '==') 
            else: return Token(TokenType.ASSIGN, '=')
        
        # Relacionais (>, >=, <, <=)
        if current_char == '>':
            if self.peek() == '=': self._advance(); return Token(TokenType.GREATER_EQUAL, '>=')
            else: return Token(TokenType.GREATER, '>')
        if current_char == '<':
            if self.peek() == '=': self._advance(); return Token(TokenType.LESS_EQUAL, '<=')
            else: return Token(TokenType.LESS, '<')
        if current_char == '!':
            if self.peek() == '=': self._advance(); return Token(TokenType.NOT_EQUAL, '!=')
            
        # Lógicos (&&, ||)
        if current_char == '&':
            if self.peek() == '&': self._advance(); return Token(TokenType.OP_LOGICO_AND, '&&')
        if current_char == '|':
            if self.peek() == '|': self._advance(); return Token(TokenType.OP_LOGICO_OR, '||')
        
        raise RuntimeError(f"Erro Léxico (Linha {start_line}, Coluna {start_col}): Caractere não reconhecido: '{current_char}'")

# ==================================================================
# Parser: LOG SIMPLIFICADO
# ==================================================================
class Parser:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.lookahead = self.scanner.next_token()
        
    def _advance(self):
        self.lookahead = self.scanner.next_token()

    def match(self, expected_type: TokenType, text: str = None):
        if self.lookahead is None:
            raise RuntimeError(f"Erro Sintático: Esperado {expected_type.name}, mas encontrado FIM DE ARQUIVO.")
        
        if self.lookahead.type == expected_type:
            if text and self.lookahead.text != text:
                 current_token_name = self.lookahead.type.name
                 raise RuntimeError(f"Erro Sintático: Esperado '{text}', mas encontrado {current_token_name} ('{self.lookahead.text}')")
            
            # 💡 PRINT SIMPLIFICADO: Apenas o token consumido
            print(f"[Match] Consumido: {self.lookahead.type.name} ('{self.lookahead.text}')")
            self._advance()
        else:
            current_token_name = self.lookahead.type.name
            raise RuntimeError(f"Erro Sintático: Esperado {expected_type.name} ({text if text else expected_type.name}), mas encontrado {current_token_name} ('{self.lookahead.text}')")

    # Os logs de ENTROU/SAIU foram removidos de todas as funções abaixo:

    def program(self):
        self.match(TokenType.KEYWORD_FUNCTION)
        self.match(TokenType.KEYWORD_MAIN)
        self.match(TokenType.LEFT_PAREN)
        self.match(TokenType.RIGHT_PAREN)
        self.match(TokenType.LEFT_CURLY)
        self.corpo()
        self.match(TokenType.RIGHT_CURLY)
        if self.lookahead is not None:
             raise RuntimeError(f"Erro Sintático: Tokens inesperados após o final do programa ('{self.lookahead.text}').")

    def corpo(self):
        self.declaracoes()
        self.comandos()

    def declaracoes(self):
        while self.lookahead is not None and self.lookahead.type in [TokenType.KEYWORD_LET, TokenType.KEYWORD_CONST]:
            self.declaracao()

    def declaracao(self):
        if self.lookahead.type == TokenType.KEYWORD_LET:
            self.match(TokenType.KEYWORD_LET)
        elif self.lookahead.type == TokenType.KEYWORD_CONST:
            self.match(TokenType.KEYWORD_CONST)
        else:
            raise RuntimeError(f"Erro Sintático: Esperado 'let' ou 'const', mas encontrado {self.lookahead.type.name}.")
            
        self.match(TokenType.IDENTIFIER)
        self.match(TokenType.COLON)
        self.tipo()
        self.match(TokenType.SEMICOLON)

    def tipo(self):
        if self.lookahead.type == TokenType.KEYWORD_TYPE_NUMBER:
            self.match(TokenType.KEYWORD_TYPE_NUMBER)
        elif self.lookahead.type == TokenType.KEYWORD_TYPE_FLOAT:
            self.match(TokenType.KEYWORD_TYPE_FLOAT)
        else:
            raise RuntimeError(f"Erro Sintático: Esperado 'number' ou 'float', mas encontrado {self.lookahead.type.name}.")

    def comandos(self):
        while self.lookahead is not None and self.lookahead.type in [
            TokenType.IDENTIFIER, TokenType.KEYWORD_READ, TokenType.KEYWORD_CONSOLELOG, 
            TokenType.IF, TokenType.WHILE, TokenType.LEFT_CURLY
        ]:
            self.comando()

    def comando(self):
        if self.lookahead.type == TokenType.IDENTIFIER:
            self.atribuicao()
        elif self.lookahead.type == TokenType.KEYWORD_READ:
            self.leitura()
        elif self.lookahead.type == TokenType.KEYWORD_CONSOLELOG:
            self.escrita()
        elif self.lookahead.type == TokenType.IF:
            self.condicional()
        elif self.lookahead.type == TokenType.WHILE:
            self.repeticao()
        elif self.lookahead.type == TokenType.LEFT_CURLY:
            self.blocoInterno()
        else:
            raise RuntimeError(f"Erro Sintático: Token inesperado no início de um comando: {self.lookahead.type.name} ('{self.lookahead.text}')")

    def atribuicao(self):
        self.match(TokenType.IDENTIFIER)
        self.match(TokenType.ASSIGN)
        self.expressaoAritmetica()
        self.match(TokenType.SEMICOLON)

    def leitura(self):
        self.match(TokenType.KEYWORD_READ)
        self.match(TokenType.LEFT_PAREN)
        self.match(TokenType.IDENTIFIER)
        self.match(TokenType.RIGHT_PAREN)
        self.match(TokenType.SEMICOLON)

    def escrita(self):
        self.match(TokenType.KEYWORD_CONSOLELOG)
        self.match(TokenType.DOT)
        self.match(TokenType.IDENTIFIER, text='log')
        self.match(TokenType.LEFT_PAREN)
        
        if self.lookahead.type == TokenType.IDENTIFIER:
            self.match(TokenType.IDENTIFIER)
        elif self.lookahead.type == TokenType.STRING_LITERAL:
            self.match(TokenType.STRING_LITERAL)
        else:
            raise RuntimeError(f"Erro Sintático: Esperado IDENTIFIER ou STRING_LITERAL em escrita, encontrado {self.lookahead.type.name}.")
            
        self.match(TokenType.RIGHT_PAREN)
        self.match(TokenType.SEMICOLON)

    def condicional(self):
        self.match(TokenType.IF)
        self.match(TokenType.LEFT_PAREN)
        self.expressaoRelacional()
        self.match(TokenType.RIGHT_PAREN)
        self.blocoInterno()
        
        if self.lookahead is not None and self.lookahead.type == TokenType.ELSE:
            self.match(TokenType.ELSE)
            self.blocoInterno()

    def repeticao(self):
        self.match(TokenType.WHILE)
        self.match(TokenType.LEFT_PAREN)
        self.expressaoRelacional()
        self.match(TokenType.RIGHT_PAREN)
        self.blocoInterno()

    def blocoInterno(self):
        self.match(TokenType.LEFT_CURLY)
        self.comandos()
        self.match(TokenType.RIGHT_CURLY)

    # Expressões Aritméticas
    def expressaoAritmetica(self):
        self.termo()
        self.EAP()

    def EAP(self):
        if self.lookahead is not None:
            if self.lookahead.type == TokenType.PLUS:
                self.match(TokenType.PLUS)
                self.termo()
                self.EAP()
            elif self.lookahead.type == TokenType.MINUS:
                self.match(TokenType.MINUS)
                self.termo()
                self.EAP()

    def termo(self):
        self.fator()
        self.TP()

    def TP(self):
        if self.lookahead is not None:
            if self.lookahead.type == TokenType.STAR:
                self.match(TokenType.STAR)
                self.fator()
                self.TP()
            elif self.lookahead.type == TokenType.SLASH:
                self.match(TokenType.SLASH)
                self.fator()
                self.TP()

    def fator(self):
        if self.lookahead.type == TokenType.NUMBER:
            self.match(TokenType.NUMBER)
        elif self.lookahead.type == TokenType.IDENTIFIER:
            self.match(TokenType.IDENTIFIER)
        elif self.lookahead.type == TokenType.LEFT_PAREN:
            self.match(TokenType.LEFT_PAREN)
            self.expressaoAritmetica()
            self.match(TokenType.RIGHT_PAREN)
        else:
            raise RuntimeError(f"Erro Sintático: Esperado número, identificador ou '(', encontrado {self.lookahead.type.name} ('{self.lookahead.text}').")

    # Expressões Relacionais
    def expressaoRelacional(self):
        if self.lookahead.type in [TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LEFT_PAREN]:
            self.termoRelacionalBase()
        else:
             raise RuntimeError(f"Erro Sintático: Esperado início de expressão relacional, encontrado {self.lookahead.type.name}.")

        self.expressaoRelacionalP()

    def expressaoRelacionalP(self):
        if self.lookahead is not None and self.lookahead.type in [TokenType.OP_LOGICO_AND, TokenType.OP_LOGICO_OR]:
            self.operadorLogico()
            self.termoRelacionalBase()
            self.expressaoRelacionalP()

    def termoRelacionalBase(self):
        if self.lookahead.type in [TokenType.NUMBER, TokenType.IDENTIFIER]:
            self.expressaoAritmetica()
            self.OP_REL() 
            self.expressaoAritmetica()
        elif self.lookahead.type == TokenType.LEFT_PAREN:
            self.match(TokenType.LEFT_PAREN)
            self.expressaoRelacional()
            self.match(TokenType.RIGHT_PAREN)
        else:
             raise RuntimeError(f"Erro Sintático: Esperado início de termo relacional (expressão ou parênteses), encontrado {self.lookahead.type.name}.")
             
    def OP_REL(self):
        if self.lookahead.type in [TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL, TokenType.EQUAL, TokenType.NOT_EQUAL]:
            self._advance()
        else:
            raise RuntimeError(f"Erro Sintático: Esperado operador relacional, encontrado {self.lookahead.type.name}.")

    def operadorLogico(self):
        if self.lookahead.type == TokenType.OP_LOGICO_AND:
            self.match(TokenType.OP_LOGICO_AND)
        elif self.lookahead.type == TokenType.OP_LOGICO_OR:
            self.match(TokenType.OP_LOGICO_OR)
        else:
            raise RuntimeError(f"Erro Sintático: Esperado operador lógico ('&&' ou '||'), encontrado {self.lookahead.type.name}.")

# ==================================================================
# Função Principal: Inicia o Parser
# ==================================================================
def main():
    filename = "programa_completo.mc"
    print(f"\n--- INICIANDO ANÁLISE SINTÁTICA DE '{filename}' ---\n")
    scanner = Scanner(filename)
    parser = Parser(scanner) 

    try:
        parser.program() 
        print("\n--- STATUS ---\n✅ Análise Sintática concluída com sucesso!")
    except RuntimeError as e:
        print(f"\n--- STATUS ---\n❌ ERRO DE ANÁLISE: {e}")

if __name__ == "__main__":
    main()