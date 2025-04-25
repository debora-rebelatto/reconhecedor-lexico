import re
import json

class AnalisadorLexico:
    def __init__(self, token_file, afd_file):
        self.tabela_tokens = self.ler_tokens(token_file)
        self.afd = self.ler_afd(afd_file)
        self.simbolos = []
        self.fita_saida = []
        self.current_line = 1

    def ler_tokens(self, arquivo):
        tokens = []
        try:
            with open(arquivo, 'r') as f:
                for linha in f:
                    tipo, padrao = linha.strip().split(' ', 1)
                    tokens.append((tipo, re.compile(padrao)))
        except FileNotFoundError:
            print(f"Erro: Arquivo {arquivo} não encontrado.")
            return []
        return tokens

    def ler_afd(self, arquivo):
        try:
            with open(arquivo, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo {arquivo} não encontrado.")
            return {}

    def reconhecer_token_afd(self, lexema, pos):
        current_state = self.afd.get('estado_inicial', 'q0')
        estados_finais = set(self.afd.get('estados_finais', []))
        transicoes = self.afd.get('transicoes', {})
        matched = ""
        last_valid_pos = pos
        last_valid_state = None

        i = pos
        while i < len(lexema):
            char = lexema[i]
            if current_state in transicoes and char in transicoes[current_state]:
                matched += char
                current_state = transicoes[current_state][char]
                if current_state in estados_finais:
                    last_valid_pos = i + 1
                    last_valid_state = current_state
                i += 1
            else:
                break

        if last_valid_state in estados_finais:
            token_value = lexema[pos:last_valid_pos]
            return 'simbolo_especial' if token_value in self.afd['alfabeto'] else 'identificador', token_value, last_valid_pos
        return None, None, pos

    def reconhecer_token_regex(self, lexema):
        for tipo, padrao in self.tabela_tokens:
            if padrao.fullmatch(lexema):
                return tipo
        return None

    def analisar_sentencas(self, arquivo_codigo):
        try:
            with open(arquivo_codigo, 'r') as arquivo:
                codigo = arquivo.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo {arquivo_codigo} não encontrado.")
            return

        self.current_line = 1
        pos = 0
        while pos < len(codigo):
            if codigo[pos].isspace():
                if codigo[pos] == '\n':
                    self.current_line += 1
                pos += 1
                continue

            if codigo[pos] in self.afd.get('alfabeto', []):
                tipo, token_value, new_pos = self.reconhecer_token_afd(codigo, pos)
                if tipo:
                    self.fita_saida.append((self.current_line, token_value, tipo))
                    if tipo == 'identificador':
                        self.simbolos.append({
                            "linha": self.current_line,
                            "identificador": token_value,
                            "rotulo": f"ID_{len(self.simbolos) + 1}"
                        })
                    pos = new_pos
                    continue

            for i in range(len(codigo), pos - 1, -1):
                lexema = codigo[pos:i]
                tipo = self.reconhecer_token_regex(lexema)
                if tipo:
                    self.fita_saida.append((self.current_line, lexema, tipo))
                    if tipo == 'identificador':
                        self.simbolos.append({
                            "linha": self.current_line,
                            "identificador": lexema,
                            "rotulo": f"ID_{len(self.simbolos) + 1}"
                        })
                    pos = i
                    matched = True
                    break

            if not matched:
                print(f"[Erro] Token inválido na linha {self.current_line}: {codigo[pos]}")
                pos += 1

    def imprimir_resultados(self):
        print("FITA DE SAÍDA:")
        print("Line | Token Type       | Value")
        print("-----|------------------|-------")
        for linha, valor, tipo in self.fita_saida:
            print(f"{linha:<4} | {tipo:<16} | {valor}")

        print("\nTABELA DE SÍMBOLOS:")
        print("Line | Identifier | Label")
        print("-----|------------|-------")
        for simb in self.simbolos:
            print(f"{simb['linha']:<4} | {simb['identificador']:<10} | {simb['rotulo']}")

def main():
    analisador = AnalisadorLexico('tokens.txt', 'afd.json')
    analisador.analisar_sentencas('codigo_fonte.txt')
    analisador.imprimir_resultados()

if __name__ == "__main__":
    main()