
import os
import sys
import shutil
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from src.bemVindo import BoasVindas
import customtkinter as ctk
import pymupdf as fitz
from PIL import Image, ImageDraw


# =========================================================
# CONFIGURAÇÕES
# =========================================================

APP_NAME = "Acervo"
APP_VERSION = "1.1.0"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

GRID_COLUMNS = 5
CARD_WIDTH = 190
CARD_HEIGHT = 260

THUMB_WIDTH = 145
THUMB_HEIGHT = 175
THUMBNAIL_SCALE = 1.3

# Cores
BG = "#111318"
SIDEBAR = "#171A21"
SURFACE = "#1C2029"
SURFACE_HOVER = "#272C37"
BORDER = "#303541"

RED = "#E53935"
RED_HOVER = "#C62828"

TEXT = "#F5F6FA"
MUTED = "#9BA3B4"
WHITE = "#FFFFFF"


# =========================================================
# DIRETÓRIOS
# =========================================================

BASE_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)

PDF_DIR = BASE_DIR / "meus_pdfs"
CACHE_DIR = BASE_DIR / ".cache" / "thumbnails"

PDF_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# FUNÇÕES DE ARQUIVO
# =========================================================

def abrir_pdf(caminho):
    """Abre o PDF no leitor padrão do sistema."""
    try:
        caminho = str(caminho)

        if sys.platform.startswith("win"):
            os.startfile(caminho)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", caminho])
        else:
            subprocess.Popen(["xdg-open", caminho])

    except Exception as erro:
        messagebox.showerror(
            "Erro ao abrir PDF",
            f"Não foi possível abrir o documento.\n\n{erro}"
        )


def criar_capa_padrao():
    """Cria uma capa padrão quando não é possível gerar a miniatura."""
    imagem = Image.new(
        "RGB",
        (THUMB_WIDTH, THUMB_HEIGHT),
        SURFACE
    )

    desenho = ImageDraw.Draw(imagem)

    desenho.rounded_rectangle(
        (30, 35, 115, 140),
        radius=9,
        fill=WHITE
    )

    desenho.text(
        (47, 78),
        "PDF",
        fill=WHITE
    )

    return imagem


def obter_miniatura(caminho):
    """Gera ou reutiliza a miniatura da primeira página do PDF."""
    caminho = Path(caminho)

    try:
        modificacao = caminho.stat().st_mtime_ns

        cache_file = CACHE_DIR / (
            f"{caminho.stem}_{modificacao}.png"
        )

        if cache_file.exists():
            try:
                with Image.open(cache_file) as imagem:
                    return imagem.convert("RGB")
            except (OSError, ValueError):
                pass

        with fitz.open(caminho) as documento:
            if documento.page_count == 0:
                return criar_capa_padrao()

            pagina = documento.load_page(0)

            pix = pagina.get_pixmap(
                matrix=fitz.Matrix(
                    THUMBNAIL_SCALE,
                    THUMBNAIL_SCALE
                ),
                alpha=False
            )

            imagem = Image.frombytes(
                "RGB",
                (pix.width, pix.height),
                pix.samples
            )

        imagem.thumbnail((THUMB_WIDTH, THUMB_HEIGHT))

        fundo = Image.new(
            "RGB",
            (THUMB_WIDTH, THUMB_HEIGHT),
            "#FFFFFF"
        )

        x = (THUMB_WIDTH - imagem.width) // 2
        y = (THUMB_HEIGHT - imagem.height) // 2

        fundo.paste(imagem, (x, y))

        try:
            fundo.save(
                cache_file,
                format="PNG",
                optimize=False
            )
        except OSError:
            pass

        return fundo

    except Exception:
        return criar_capa_padrao()


def listar_pdfs():
    """Lista os PDFs da biblioteca local."""
    try:
        return sorted(
            (
                arquivo
                for arquivo in PDF_DIR.iterdir()
                if arquivo.is_file()
                and arquivo.suffix.lower() == ".pdf"
            ),
            key=lambda arquivo: arquivo.name.lower()
        )
    except OSError:
        return []


# =========================================================
# APLICAÇÃO ACERVO
# =========================================================

class Acervo(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(f"{APP_NAME} | Biblioteca de PDFs")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.miniaturas = []
        self.versao_carregamento = 0

        self.criar_interface()
        self.atualizar_biblioteca()

    # =====================================================
    # INTERFACE
    # =====================================================

    def criar_interface(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.criar_sidebar()
        self.criar_area_principal()

    # =====================================================
    # BARRA LATERAL
    # =====================================================

    def criar_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=SIDEBAR
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        # -------------------------------------------------
        # CABEÇALHO
        # -------------------------------------------------

        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        logo_frame.pack(
            fill="x",
            padx=22,
            pady=(28, 35)
        )

        ctk.CTkLabel(
            logo_frame,
            text=APP_NAME,
            font=("Segoe UI", 29, "bold"),
            text_color=TEXT,
            fg_color="transparent"
        ).pack(side="left")

        # -------------------------------------------------
        # MENU
        # -------------------------------------------------

        ctk.CTkLabel(
            self.sidebar,
            text="BIBLIOTECA",
            font=("Segoe UI", 10, "bold"),
            text_color=MUTED,
            anchor="w"
        ).pack(
            fill="x",
            padx=22,
            pady=(0, 10)
        )

        self.botao_biblioteca = ctk.CTkButton(
            self.sidebar,
            text="  Meus documentos",
            anchor="w",
            height=42,
            corner_radius=9,
            fg_color="#302126",
            hover_color="#40262D",
            text_color=WHITE,
            font=("Segoe UI", 13),
            command=self.atualizar_biblioteca
        )

        self.botao_biblioteca.pack(
            fill="x",
            padx=12,
            pady=4
        )

        self.botao_importar = ctk.CTkButton(
            self.sidebar,
            text="  +  Importar PDFs",
            anchor="w",
            height=42,
            corner_radius=9,
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            font=("Segoe UI", 13, "bold"),
            command=self.importar_pdfs
        )

        self.botao_importar.pack(
            fill="x",
            padx=12,
            pady=4
        )

        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=BORDER
        ).pack(
            fill="x",
            padx=18,
            pady=(25, 15)
        )

        # -------------------------------------------------
        # INFORMAÇÕES DE ARMAZENAMENTO
        # -------------------------------------------------

        ctk.CTkLabel(
            self.sidebar,
            text="ARMAZENAMENTO LOCAL",
            font=("Segoe UI", 9, "bold"),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=22
        )

        ctk.CTkLabel(
            self.sidebar,
            text="Seus documentos ficam armazenados no computador.",
            font=("Segoe UI", 10),
            text_color=MUTED,
            wraplength=175,
            justify="left"
        ).pack(
            anchor="w",
            padx=22,
            pady=(7, 0)
        )

        # -------------------------------------------------
        # RODAPÉ SEM LOGO
        # -------------------------------------------------

        rodape = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        rodape.pack(
            side="bottom",
            fill="x",
            padx=18,
            pady=18
        )

        ctk.CTkLabel(
            rodape,
            text=f"{APP_NAME}\nv{APP_VERSION}",
            font=("Segoe UI", 10),
            text_color="#697183",
            justify="left"
        ).pack(
            side="left",
            anchor="center"
        )

    # =====================================================
    # ÁREA PRINCIPAL
    # =====================================================

    def criar_area_principal(self):
        self.main_area = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )

        self.main_area.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(28, 15)
        )

        titulo_area = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        titulo_area.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            titulo_area,
            text="Minha biblioteca",
            font=("Segoe UI", 27, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            titulo_area,
            text="Todos os seus documentos em um só lugar.",
            font=("Segoe UI", 12),
            text_color=MUTED
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        self.botao_atualizar = ctk.CTkButton(
            header,
            text="Atualizar",
            width=100,
            height=36,
            corner_radius=9,
            fg_color=SURFACE,
            hover_color=SURFACE_HOVER,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            command=self.atualizar_biblioteca
        )

        self.botao_atualizar.pack(
            side="right",
            padx=(10, 0)
        )

        self.contador = ctk.CTkLabel(
            self.main_area,
            text="0 documentos",
            font=("Segoe UI", 12, "bold"),
            text_color=MUTED
        )

        self.contador.grid(
            row=1,
            column=0,
            sticky="w",
            padx=30,
            pady=(0, 15)
        )

        self.area_pdfs = ctk.CTkScrollableFrame(
            self.main_area,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#454B59",
            scrollbar_button_hover_color=RED
        )

        self.area_pdfs.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(25, 18),
            pady=(0, 15)
        )

        for coluna in range(GRID_COLUMNS):
            self.area_pdfs.grid_columnconfigure(
                coluna,
                weight=1,
                uniform="pdf_colunas"
            )

    # =====================================================
    # ATUALIZAÇÃO DA BIBLIOTECA
    # =====================================================

    def atualizar_biblioteca(self):
        self.versao_carregamento += 1
        versao_atual = self.versao_carregamento

        for widget in self.area_pdfs.winfo_children():
            widget.destroy()

        self.miniaturas.clear()

        arquivos = listar_pdfs()
        quantidade = len(arquivos)

        texto = (
            f"{quantidade} documento"
            if quantidade == 1
            else f"{quantidade} documentos"
        )

        self.contador.configure(text=texto)

        if not arquivos:
            self.mostrar_biblioteca_vazia()
            return

        self.contador.configure(
            text=f"{texto} • Carregando capas..."
        )

        threading.Thread(
            target=self.carregar_capas,
            args=(arquivos, versao_atual),
            daemon=True
        ).start()

    # =====================================================
    # BIBLIOTECA VAZIA
    # =====================================================

    def mostrar_biblioteca_vazia(self):
        vazio = ctk.CTkFrame(
            self.area_pdfs,
            fg_color=SURFACE,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )

        vazio.grid(
            row=0,
            column=0,
            columnspan=GRID_COLUMNS,
            sticky="ew",
            padx=8,
            pady=30
        )

        ctk.CTkLabel(
            vazio,
            text="▤",
            font=("Segoe UI", 48),
            text_color=RED
        ).pack(pady=(28, 5))

        ctk.CTkLabel(
            vazio,
            text="Sua biblioteca está vazia",
            font=("Segoe UI", 19, "bold"),
            text_color=TEXT
        ).pack(pady=(5, 5))

        ctk.CTkLabel(
            vazio,
            text="Importe um PDF para começar sua coleção.",
            font=("Segoe UI", 12),
            text_color=MUTED
        ).pack(pady=(0, 15))

        ctk.CTkButton(
            vazio,
            text="Importar documentos",
            height=38,
            fg_color=RED,
            hover_color=RED_HOVER,
            command=self.importar_pdfs
        ).pack(pady=(0, 28))

    # =====================================================
    # MINIATURAS DOS PDFs
    # =====================================================

    def carregar_capas(self, arquivos, versao):
        resultados = []

        for arquivo in arquivos:
            try:
                imagem = obter_miniatura(arquivo)
            except Exception:
                imagem = criar_capa_padrao()

            resultados.append((arquivo, imagem))

        try:
            self.after(
                0,
                lambda: self.exibir_documentos(
                    resultados,
                    versao
                )
            )
        except Exception:
            pass

    def exibir_documentos(self, resultados, versao):
        if versao != self.versao_carregamento:
            return

        for widget in self.area_pdfs.winfo_children():
            widget.destroy()

        self.miniaturas.clear()

        for indice, (arquivo, imagem) in enumerate(resultados):
            linha = indice // GRID_COLUMNS
            coluna = indice % GRID_COLUMNS

            cartao = ctk.CTkFrame(
                self.area_pdfs,
                width=CARD_WIDTH,
                height=CARD_HEIGHT,
                fg_color=SURFACE,
                corner_radius=12,
                border_width=1,
                border_color=BORDER
            )

            cartao.grid(
                row=linha,
                column=coluna,
                padx=7,
                pady=7,
                sticky="n"
            )

            cartao.grid_propagate(False)

            capa = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(THUMB_WIDTH, THUMB_HEIGHT)
            )

            self.miniaturas.append(capa)

            ctk.CTkButton(
                cartao,
                text="",
                image=capa,
                width=THUMB_WIDTH,
                height=THUMB_HEIGHT,
                fg_color="#252A34",
                hover_color=SURFACE_HOVER,
                corner_radius=7,
                command=lambda caminho=arquivo: abrir_pdf(caminho)
            ).pack(pady=(12, 8))

            nome = arquivo.stem

            if len(nome) > 23:
                nome = nome[:20] + "..."

            ctk.CTkLabel(
                cartao,
                text=nome,
                font=("Segoe UI", 12, "bold"),
                text_color=TEXT,
                anchor="w"
            ).pack(
                fill="x",
                padx=12
            )

            ctk.CTkLabel(
                cartao,
                text="Documento PDF",
                font=("Segoe UI", 10),
                text_color=MUTED,
                anchor="w"
            ).pack(
                fill="x",
                padx=12,
                pady=(3, 0)
            )

            cartao.bind(
                "<Enter>",
                lambda evento, widget=cartao:
                    widget.configure(border_color=RED)
            )

            cartao.bind(
                "<Leave>",
                lambda evento, widget=cartao:
                    widget.configure(border_color=BORDER)
            )

        quantidade = len(resultados)

        texto = (
            f"{quantidade} documento"
            if quantidade == 1
            else f"{quantidade} documentos"
        )

        self.contador.configure(text=texto)

    # =====================================================
    # IMPORTAR DOCUMENTOS
    # =====================================================

    def importar_pdfs(self):
        arquivos = filedialog.askopenfilenames(
            parent=self,
            title="Selecionar documentos PDF",
            filetypes=[
                ("Arquivos PDF", "*.pdf"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not arquivos:
            return

        importados = 0
        ignorados = 0
        erros = []

        for origem_str in arquivos:
            origem = Path(origem_str)

            try:
                with fitz.open(origem) as documento:
                    if documento.page_count == 0:
                        raise ValueError(
                            "O PDF não possui páginas."
                        )

                destino = PDF_DIR / origem.name

                if destino.exists():
                    base = origem.stem
                    extensao = origem.suffix
                    numero = 1

                    while destino.exists():
                        destino = PDF_DIR / (
                            f"{base} ({numero}){extensao}"
                        )
                        numero += 1

                shutil.copy2(origem, destino)
                importados += 1

            except Exception as erro:
                ignorados += 1
                erros.append(f"{origem.name}: {erro}")

        self.atualizar_biblioteca()

        if erros:
            detalhes = "\n".join(erros[:5])

            if len(erros) > 5:
                detalhes += (
                    f"\n... e mais {len(erros) - 5} erro(s)."
                )

            messagebox.showwarning(
                "Importação concluída com avisos",
                f"Importados: {importados}\n"
                f"Com erro: {ignorados}\n\n"
                f"{detalhes}",
                parent=self
            )
        else:
            messagebox.showinfo(
                "Importação concluída",
                f"{importados} PDF(s) importado(s) com sucesso.",
                parent=self
            )


# =========================================================
# INICIALIZAÇÃO
# =========================================================


if __name__ == "__main__":
    app = Acervo()

    # Esconde a janela principal enquanto mostra as boas-vindas.
    app.withdraw()

    # Abre a tela de boas-vindas.
    tela_boas_vindas = BoasVindas(
        parent=app,
        ao_avancar=app.deiconify,
        ao_cancelar=app.destroy
    )

    app.mainloop()
