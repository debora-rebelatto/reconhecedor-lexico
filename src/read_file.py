def read_file():
  with open('input.txt', 'r', encoding='utf-8') as f:
      conteudo = f.read()
      print(conteudo)