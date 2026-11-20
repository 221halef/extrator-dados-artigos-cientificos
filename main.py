import os
import pdfplumber

pasta = "artigos"

arquivos = []
for nome in sorted(os.listdir(pasta)):
    if nome.endswith(".pdf"):
        arquivos.append(os.path.join(pasta, nome))

print("Total de PDFs encontrados:", len(arquivos))

for caminho in arquivos:
    with pdfplumber.open(caminho) as pdf:
        print(os.path.basename(caminho), "->", len(pdf.pages), "páginas")

textos = {}
qtd_paginas = {}

for caminho in arquivos:
    nome = os.path.basename(caminho)
    partes = []

    with pdfplumber.open(caminho) as pdf:
        qtd_paginas[nome] = len(pdf.pages)

        for i, pagina in enumerate(pdf.pages):
            if i == 0:
                texto = pagina.extract_text(x_tolerance=1.5) or ""
            else:
                meio = pagina.width / 2
                esquerda = pagina.crop((0, 0, meio, pagina.height))
                direita = pagina.crop((meio, 0, pagina.width, pagina.height))
                texto = (esquerda.extract_text(x_tolerance=1.5) or "") + "\n" + (direita.extract_text(x_tolerance=1.5) or "")
            partes.append(texto)

    textos[nome] = "\n".join(partes)

for nome in textos:
    print(nome[:4], "-", qtd_paginas[nome], "páginas -", len(textos[nome]), "caracteres")
