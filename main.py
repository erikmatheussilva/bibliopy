
# json lê o catálogo e path encontra arquivos a partir da pasta do projeto
import json
from pathlib import Path

# tkinter cria a janela, os botões e as mensagens de erro
import tkinter as tk
from tkinter import messagebox, ttk

# pdfium lê e desenha o pdf e pillow entrega a imagem pronta ao tkinter
from PIL import ImageTk
import pypdfium2 as pdfium


class LivroPDFLocal:
    # representa um livro do catálogo que possui um pdf no computador


    def __init__(self, dados, pasta):
        # recebe um registro do json e a pasta onde está o catálogo
        # cada chave de dados corresponde a um campo em catalogo.json
        self.id = dados["id"]
        self.titulo = dados["titulo"]
        self.autor = dados["autor"]
        self.genero = dados["genero"]
        self.ano = dados["ano"]
        self.idioma = dados["idioma"]
        self.fonte = dados["fonte"]
        self.arquivo = pasta / dados["arquivo"]

    def abrir(self):
        # confere se o arquivo é pdf e devolve o documento aberto

        if not self.arquivo.is_file():
            raise FileNotFoundError(f"PDF não encontrado: {self.arquivo}")
        # open("rb") abre um arquivo no modo de leitura binária pois pdfs são arquivos binários, então armazena em "as arquivo"
        with self.arquivo.open("rb") as arquivo:
            if arquivo.read(5) != b"%PDF-":
                raise ValueError("O arquivo selecionado não é um PDF válido.")
        return pdfium.PdfDocument(str(self.arquivo))


class Biblioteca:
    # carrega os livros do json e oferece uma busca simples por ID.

    def __init__(self, caminho):
        # lê o arquivo do catálogo e cria um LivroPDFLocal por registro
        # utf-8 permite ler títulos e autores com acentos.
        with caminho.open("r", encoding="utf-8") as arquivo:
            registros = json.load(arquivo)
        if not isinstance(registros, list) or not registros:
            raise ValueError("O catálogo deve conter uma lista de livros.")

        self.livros = []
        # ids guarda os números já encontrados durante a leitura do JSON.
        ids = set()
        for dados in registros:
            livro = LivroPDFLocal(dados, caminho.parent)
            if livro.id in ids:
                raise ValueError(f"ID repetido no catálogo: {livro.id}")
            ids.add(livro.id)
            self.livros.append(livro)
        # ordena a lista por título
        self.livros.sort(key=lambda livro: livro.titulo.lower())

    def obter_livro(self, id_livro):
        # devolve o livro com o ID informado
        for livro in self.livros:
            if livro.id == id_livro:
                return livro
        return None


class InterfaceBiblioteca:
    # cuida da janela e responde as ações do usuário, recebe Biblioteca pronta, mostra seus livros e mantém o pdf aberto
    

    def __init__(self, biblioteca):
        self.biblioteca = biblioteca
        # None indica que ainda não há PDF ou imagem abertos 
        self.documento = None
        self.imagem = None
        self.id_aberto = None
        self.pagina = 0
        self.zoom = 1.0

        # cria a janela principal do aplicativo
        self.janela = tk.Tk()
        self.janela.title("BiblioPy — Biblioteca Digital")
        # define tamanho inicial da janela
        self.janela.geometry("1000x700")
        # conecta o botão de fechar ao metodo fechar()
        self.janela.protocol("WM_DELETE_WINDOW", self.fechar)

        # cria o container
        principal = ttk.Frame(self.janela, padding=12)
        principal.pack(fill="both", expand=True)

        # cria a coluna lateral com a lista de livros, detalhes e botão de abrir
        lateral = ttk.Frame(principal)
        lateral.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(lateral, text="BiblioPy", font=("Arial", 16, "bold")).pack()
        ttk.Label(lateral, text="Livros").pack(anchor="w", pady=(12, 0))

        # cria a lista de livros
        self.lista = tk.Listbox(lateral, width=34, exportselection=False)
        self.lista.pack(fill="both", expand=True, pady=8)
        # conecta o evento de select do tkinter ao metodo selecionar()
        self.lista.bind("<<ListboxSelect>>", self.selecionar)
        for livro in biblioteca.livros:
            self.lista.insert("end", livro.titulo)

        self.detalhes = ttk.Label(lateral, wraplength=240, justify="left")
        self.detalhes.pack(anchor="w", pady=8)
        ttk.Button(lateral, text="Ler no BiblioPy", command=self.abrir_livro).pack(
            fill="x"
        )
        # cria o leitor de pdf
        leitor = ttk.Frame(principal)
        leitor.pack(side="left", fill="both", expand=True)
        # cria as ações do leitor
        barra = ttk.Frame(leitor)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Button(barra, text="◀ Anterior", command=self.anterior).pack(side="left")
        self.texto_pagina = ttk.Label(barra, text="Nenhum PDF aberto")
        self.texto_pagina.pack(side="left", padx=8)
        ttk.Button(barra, text="Próxima ▶", command=self.proxima).pack(side="left")
        ttk.Button(barra, text="Zoom +", command=self.aumentar_zoom).pack(side="right")
        self.texto_zoom = ttk.Label(barra, text="100%")
        self.texto_zoom.pack(side="right", padx=6)
        ttk.Button(barra, text="Zoom −", command=self.diminuir_zoom).pack(side="right")

        # area onde o pdf é carregado
        area = ttk.Frame(leitor)
        area.pack(fill="both", expand=True)
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(area, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(area, orient="horizontal", command=self.canvas.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(
            yscrollcommand=vertical.set, xscrollcommand=horizontal.set
        )

        self.lista.selection_set(0)
        self.selecionar()

    def livro_selecionado(self):
        # devolve o livro préviamente selecionado ou nada se não houver seleção
        
        selecao = self.lista.curselection()
        if selecao:
            return self.biblioteca.livros[selecao[0]]
        return None

    def selecionar(self, evento=None):
        # atualiza os detalhes quando o usuário seleciona outro livro
        
        livro = self.livro_selecionado()
        if livro is None:
            return
        self.detalhes.config(
            text=(
                f"{livro.titulo}\nAutor: {livro.autor}\nCategoria: {livro.genero}\n"
                f"Ano: {livro.ano}\nIdioma: {livro.idioma}\nFonte: {livro.fonte}"
            )
        )
        # fecha o pdf anterior e sobrescreve as informações com o novo pdf selecionado
        if livro.id != self.id_aberto:
            self.fechar_pdf()

    def abrir_livro(self):
        # abre o pdf selecionado e tenta mostrar a primeira página.

        
        livro = self.livro_selecionado()
        if livro is None:
            return
        try:
            novo = livro.abrir()
            # verifica se o tem conteudo
            if len(novo) == 0:
                novo.close()
                raise ValueError("O PDF não contém páginas.")
        # captura os possiveis erros de abertura do pdf e retorna mensagem de erro para o usuário
        except (OSError, ValueError, pdfium.PdfiumError) as erro:
            messagebox.showerror("Erro ao abrir o PDF", str(erro), parent=self.janela)
            return

        # o anterior é fechado depois que o novo abriu sem erro.
        self.fechar_pdf()
        self.documento = novo
        self.id_aberto = livro.id
        if not self.mostrar_pagina(0, 1.0):
            self.fechar_pdf()

    def mostrar_pagina(self, numero, zoom):
        # monta as paginas do pdf

        # valida se a página existe
        if self.documento is None or not 0 <= numero < len(self.documento):
            return False

        pagina = None
        bitmap = None
        imagem_pil = None
        # abre a página do PDF
        try:
            pagina = self.documento[numero]
            # renderiza em bitmap com o zoom desejado, converte para PIL e depois para Tkinter
            bitmap = pagina.render(scale=1.2 * zoom)
            imagem_pil = bitmap.to_pil()
            imagem_tk = ImageTk.PhotoImage(imagem_pil, master=self.janela)
            largura, altura = imagem_pil.size
        # trata erros de conversão e renderização
        except (OSError, ValueError, pdfium.PdfiumError, tk.TclError) as erro:
            messagebox.showerror("Erro ao mostrar a página", str(erro), parent=self.janela)
            return False
        # limpa os valores temporários da memória, mesmo que tenha erro
        finally:
            if imagem_pil is not None:
                imagem_pil.close()
            if bitmap is not None:
                bitmap.close()
            if pagina is not None:
                pagina.close()
        # guarda a imagem da página atual
        self.imagem = imagem_tk
        self.canvas.delete("all")
        # inicia a imagem no canto superior esquerdo do canvas e define a área de rolagem
        self.canvas.create_image(0, 0, anchor="nw", image=self.imagem)
        self.canvas.configure(scrollregion=(0, 0, largura, altura))
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.pagina = numero
        self.zoom = zoom

        # atualiza o texto da pagina e do zoom
        self.texto_pagina.config(text=f"Página {numero + 1} de {len(self.documento)}")
        self.texto_zoom.config(text=f"{round(zoom * 100)}%")
        return True

    def anterior(self):
        self.mostrar_pagina(self.pagina - 1, self.zoom)

    def proxima(self):
        self.mostrar_pagina(self.pagina + 1, self.zoom)

    def diminuir_zoom(self):
        self.mostrar_pagina(self.pagina, max(0.5, self.zoom - 0.25))

    def aumentar_zoom(self):
        self.mostrar_pagina(self.pagina, min(2.0, self.zoom + 0.25))

    def fechar_pdf(self):
        if self.documento is not None:
            self.documento.close()
        self.documento = None
        self.imagem = None
        self.id_aberto = None
        self.canvas.delete("all")
        self.texto_pagina.config(text="Nenhum PDF aberto")
        self.texto_zoom.config(text="100%")

    def fechar(self):
        self.fechar_pdf()
        self.janela.destroy()
    # mantem o programa em execução enquanto o usuário usa a interface.
    def executar(self):
        self.janela.mainloop()


def main():
    # define o caminho do catálogo.json a partir da pasta do projeto
    caminho = Path(__file__).resolve().parent / "catalogo.json"
    try:
        # passa o catalogo para a classe Biblioteca que vai ler o json e tenta carregar os livros, se tiver erro mostra mensagem
        biblioteca = Biblioteca(caminho)
    except (OSError, ValueError, KeyError, TypeError) as erro:
        messagebox.showerror("Erro no catálogo", str(erro))
        return 1
    InterfaceBiblioteca(biblioteca).executar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
