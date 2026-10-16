
from pathlib import Path
import sys

import customtkinter as ctk
from PIL import Image


# ==========================================
# CONFIGURAÇÕES
# ==========================================

NOME_APP = "Acervo"
VERSAO = "1.1.0"

LARGURA_JANELA = 650
ALTURA_JANELA = 480

FUNDO = "#111318"
SUPERFICIE = "#111318"
TEXTO = "#F5F6FA"
CINZA = "#9BA3B4"

VERMELHO = "#E53935"
VERMELHO_HOVER = "#C62828"


# ==========================================
# LOCALIZAÇÃO DOS ARQUIVOS
# ==========================================

if getattr(sys, "frozen", False):
    # Executando pelo .exe do PyInstaller.
    PASTA_PROJETO = Path(sys._MEIPASS)
    PASTA_SRC = PASTA_PROJETO / "src"
else:
    # Executando pelo Python.
    PASTA_SRC = Path(__file__).resolve().parent
    PASTA_PROJETO = PASTA_SRC.parent


# ==========================================
# CAMINHOS DA LOGO
# ==========================================

CAMINHOS_LOGO = [
    PASTA_PROJETO / "assets" / "logo" / "logo.png",
    PASTA_SRC / "assets" / "logo" / "logo.png",
    PASTA_PROJETO / "logo.png",
    PASTA_SRC / "logo.png",
]


def encontrar_logo():
    """Procura a logo nos caminhos configurados."""

    for caminho in CAMINHOS_LOGO:
        if caminho.is_file():
            return caminho

    return None


# ==========================================
# TELA DE BOAS-VINDAS
# ==========================================

class BoasVindas(ctk.CTkToplevel):

    def __init__(self, parent, ao_avancar, ao_cancelar):
        super().__init__(parent)

        self.ao_avancar = ao_avancar
        self.ao_cancelar = ao_cancelar
        self.logo = None

        # Configuração da janela.
        self.title(f"{NOME_APP} - Boas-vindas")
        self.geometry(
            f"{LARGURA_JANELA}x{ALTURA_JANELA}"
        )
        self.resizable(False, False)
        self.configure(fg_color=FUNDO)

        # Centraliza a janela.
        self.update_idletasks()

        x = (
            self.winfo_screenwidth() - LARGURA_JANELA
        ) // 2

        y = (
            self.winfo_screenheight() - ALTURA_JANELA
        ) // 2

        self.geometry(
            f"{LARGURA_JANELA}x{ALTURA_JANELA}+{x}+{y}"
        )

        # Mantém a apresentação ligada à janela principal.
        self.transient(parent)
        self.grab_set()

        # Fechar no X equivale a cancelar.
        self.protocol(
            "WM_DELETE_WINDOW",
            self.cancelar
        )

        self.criar_interface()

    # ======================================
    # CONSTRUIR INTERFACE
    # ======================================

    def criar_interface(self):

        quadro = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color=SUPERFICIE
        )

        quadro.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # ----------------------------------
        # LOGO
        # ----------------------------------

        self.exibir_logo(quadro)

        # ----------------------------------
        # NOME DO APLICATIVO
        # ----------------------------------

        ctk.CTkLabel(
            quadro,
            text=NOME_APP,
            font=("Arial", 40, "bold"),
            text_color=TEXTO
        ).pack(pady=(0, 5))

        # ----------------------------------
        # VERSÃO
        # ----------------------------------

        ctk.CTkLabel(
            quadro,
            text=f"Versão {VERSAO}",
            font=("Arial", 13),
            text_color=CINZA
        ).pack(pady=(0, 20))

        # ----------------------------------
        # MENSAGEM DE BOAS-VINDAS
        # ----------------------------------

        ctk.CTkLabel(
            quadro,
            text=(
                "Bem-vindo ao Acervo!\n\n"
                "Organize e acesse seus documentos PDF\n"
                "em um só lugar.\n\n"
                "Clique em Avançar para continuar."
            ),
            font=("Arial", 15),
            text_color=TEXTO,
            justify="center"
        ).pack(pady=(0, 20))

        # ----------------------------------
        # BOTÕES
        # ----------------------------------

        botoes = ctk.CTkFrame(
            quadro,
            fg_color="transparent"
        )

        botoes.pack(pady=5)

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            width=120,
            height=35,
            fg_color="transparent",
            border_width=1,
            border_color="#272C37",
            hover_color="#272C37",
            text_color=TEXTO,
            command=self.cancelar
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            botoes,
            text="Avançar",
            width=120,
            height=35,
            fg_color=VERMELHO,
            hover_color=VERMELHO_HOVER,
            text_color="#FFFFFF",
            command=self.abrir_main
        ).pack(side="left", padx=8)

    # ======================================
    # EXIBIR LOGO
    # ======================================

    def exibir_logo(self, quadro):

        caminho_logo = encontrar_logo()

        if caminho_logo is None:
            self.mostrar_nome_logo(quadro)
            return

        try:
            with Image.open(caminho_logo) as original:
                imagem = original.convert("RGBA")

            self.logo = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(100, 100)
            )

            ctk.CTkLabel(
                quadro,
                text="",
                image=self.logo
            ).pack(pady=(25, 10))

        except (OSError, ValueError) as erro:
            print(
                f"Não foi possível carregar a logo: {erro}"
            )
            self.mostrar_nome_logo(quadro)

    # ======================================
    # LOGO ALTERNATIVA
    # ======================================

    @staticmethod
    def mostrar_nome_logo(quadro):

        ctk.CTkLabel(
            quadro,
            text=NOME_APP,
            font=("Arial", 28, "bold"),
            text_color=TEXTO
        ).pack(pady=(35, 20))

    # ======================================
    # BOTÃO AVANÇAR
    # ======================================

    def abrir_main(self):

        self.grab_release()
        self.destroy()

        self.ao_avancar()

    # ======================================
    # BOTÃO CANCELAR
    # ======================================

    def cancelar(self):

        self.grab_release()
        self.destroy()

        self.ao_cancelar()
