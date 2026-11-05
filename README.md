# BiblioPy — versão 1.0

Esta etapa apresenta uma biblioteca digital em Python com leitura do pdf, o catálogo inicial contém um livro e seus dados são lidos de `catalogo.json`

## Executar no Windows

No terminal da pasta do repositório, execute:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe main.py
```

É necessário Python 3.11 ou mais recente com Tkinter. Se `python` não estiver disponível, use `py`

## Catálogo

O arquivo `catalogo.json` guarda ID, título, autor, categoria, ano, idioma, fonte e caminho do pdf e a interface lê os campos quando inicia. Para adicionar outros livros, coloque o pdf em `pdfs/` e adicione outro objeto à lista JSON com um ID diferente 

## Bibliotecas e classes usadas

- **`tkinter`, `ttk` e `messagebox`** são nativos do python e são usados para criar a janela, a lista de livros, os botões, a área de leitura e as mensagens de erro
- **`json` e `pathlib.Path`** também fazem são nativos do python, `json` lê os dados de `catalogo.json` e `Path` encontra o catálogo e os pdfs
- **`pypdfium2`** é uma dependência externa que abre o pdf e renderiza uma página por vez
- **`Pillow`** é uma dependência externa que transforma a página renderizada em uma imagem exibível pelo Tkinter

O código da aplicação está dividido em três classes: `LivroPDFLocal` que representa um livro e valida seu pdf, `Biblioteca` que carrega e consulta o catálogo e `InterfaceBiblioteca` que cria a janela e controla a leitura, as páginas e o zoom. A função `main()` liga essas partes e inicia o programa

## CRUD versão 1.0

Por enquanto só tem o Read: o programa lê o catálogo, mostra os detalhes do livro e abre o pdf dentro da janela


## Exemplos de testes

- Carregar `catalogo.json`, encontrar o livro pelo ID e abrir o pdf incluído
- Carregar um catálogo temporário com um segundo registro
- Carregar um catálogo temporário com IDs repetidos


## Limitações e bugs conhecidos

- Esta primeira etapa abre apenas pdfs locais, não importa livros de sites ou repositórios online
- Só há um pdf no catálogo inicial, para adicionar novos livros precisa editar o json e copiar o arquivo pdf
- O app precisa do python e das dependências instaladas no computador, ainda não tem instalador ou executável independente.

## O que falta fazer

As próximas etapas acrescentarão livros vindo de endereços online e repositórios, busca, filtros, cadastro pela interface e persistência dos dados pessoais.

