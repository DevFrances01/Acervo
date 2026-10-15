<div align="center">

<img src="/assets/banner/banner.jpg" alt="">

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-orange.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg)](https://github.com/devfrances/Acervo)

</div>

# Acervo 📚

Um aplicativo desktop desenvolvido em Python para organizar, importar e visualizar arquivos PDF de forma simples, prática e eficiente.

---

## 🎯 Objetivo do Projeto

Criar uma ferramenta local para facilitar o armazenamento e a organização de documentos PDF, priorizando a praticidade, a organização estruturada e a validação básica dos arquivos importados.

---

## ✨ Funcionalidades

* **Importação de PDFs:** Permite selecionar arquivos PDF do computador para adicioná-los rapidamente à biblioteca.
* **Organização de Documentos:** Armazena os arquivos importados em uma pasta dedicada ao acervo (`meus_pdfs/`).
* **Visualização por Miniaturas:** Utiliza miniaturas em cache para facilitar a identificação visual dos documentos.
* **Interface Gráfica Moderna:** Desenvolvida em desktop com **CustomTkinter**, proporcionando uma experiência de usuário limpa e intuitiva.
* **Validação de PDFs:** Emprega um módulo separado (`protecao_pdf.py`) para realizar verificações prévias nos arquivos antes da importação.
* **Tratamento de Erros:** Identifica e reporta arquivos que não passam pelas verificações previstas pelo aplicativo.

---

## 🛡️ Validação e Proteção de Arquivos

O projeto conta com um módulo independente chamado `protecao_pdf.py`, cuja responsabilidade é validar os arquivos PDF antes da efetiva importação. As verificações realizadas incluem:

* Conferência da extensão `.pdf`.
* Verificação da existência e do tamanho do arquivo.
* Identificação de arquivos vazios.
* Tentativa de abertura do documento.
* Verificação da existência de páginas válidas.
* Identificação de documentos protegidos por senha, conforme as regras implementadas.

> **⚠️ Importante:** Estas verificações não constituem uma análise antivírus. Um PDF aprovado ainda pode conter conteúdo malicioso ou explorar vulnerabilidades de leitores de documentos. Portanto, a validação básica garante apenas a integridade estrutural do arquivo, mas não assegura que ele seja totalmente seguro.

---


* **`main.py`**: Inicialização e funcionamento principal do aplicativo.
* **`protecao_pdf.py`**: Módulo responsável pela validação dos PDFs.
* **`meus_pdfs/`**: Diretório destinado aos documentos importados.
* **`.cache/thumbnails/`**: Diretório utilizado para armazenar miniaturas em cache.
* **`README.md`**: Documentação e apresentação do projeto.

*Nota: A estrutura acima representa a organização prevista; os diretórios podem ser criados automaticamente pelo aplicativo ou variar conforme a versão.*

---

## 🚀 Como Executar

1. Instale uma versão compatível do **Python**.
2. Instale as dependências utilizadas pelo projeto.
3. Execute o arquivo principal:

```bash
python main.py
```

*As dependências necessárias devem ser instaladas conforme os `imports` e a versão atual do código.*

---

## 🔒 Privacidade e Armazenamento

O Acervo foi concebido como um aplicativo local. Os documentos importados são armazenados no diretório configurado pelo próprio projeto.

O armazenamento local, por si só, não representa criptografia nem garante proteção contra acesso indevido. A segurança também depende das permissões do sistema operacional e dos cuidados com os arquivos importados.

---

## 📌 Status do Projeto

Projeto em desenvolvimento, sujeito a melhorias, correções e adição de funcionalidades.

---
