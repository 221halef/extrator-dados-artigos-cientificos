import os
import pdfplumber
import re
import unicodedata

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
                esquerda = pagina.crop((0, 65, meio, pagina.height))
                direita = pagina.crop((meio, 65, pagina.width, pagina.height))
                texto = (esquerda.extract_text(x_tolerance=1.5) or "") + "\n" + (direita.extract_text(x_tolerance=1.5) or "")
            partes.append(texto)

    textos[nome] = "\n".join(partes)

for nome in textos:
    print(nome[:4], "-", qtd_paginas[nome], "páginas -", len(textos[nome]), "caracteres")

textos_limpos = {}

for nome, texto in textos.items():
    texto = unicodedata.normalize("NFKC", texto)
    texto = re.sub(r"[\ue000-\uf8ff\ufffd]", "", texto)
    texto = re.sub(r"([a-z])-\n([a-z])", r"\1\2", texto)
    texto = re.sub(r"[ \t]+", " ", texto)

    linhas = []
    for linha in texto.split("\n"):
        linha = linha.strip()
        if linha != "":
            linhas.append(linha)

    textos_limpos[nome] = "\n".join(linhas)

for nome in textos:
    print(nome[:4], "-", len(textos[nome]), "->", len(textos_limpos[nome]), "caracteres")

dados = {}

for nome, texto in textos_limpos.items():
    linhas = texto.split("\n")

    busca = re.match(r"(.*?), (\d{4}),", linhas[0])
    periodico = busca.group(1)
    ano = int(busca.group(2))

    titulo = []
    i = 2
    while "[" not in linhas[i]:
        titulo.append(linhas[i])
        i += 1
    titulo = " ".join(titulo)

    autores = []
    while "[" in linhas[i]:
        nome_autor = linhas[i].split(" [")[0]
        nome_autor = re.sub(r"\d+$", "", nome_autor)
        autores.append(nome_autor)
        i += 1

    busca = re.search(r"Published:[^\n]*\n(.*?)Keywords", texto, re.S)
    resumo = " ".join(busca.group(1).split())
    resumo = re.sub(r"^Abstract\s*", "", resumo)

    busca = re.search(r"Keywords:?\s*(.*?)\s*\n1\s+Introduction", texto, re.S)
    palavras = " ".join(busca.group(1).split()).rstrip(".,")
    palavras_chave = [p.strip() for p in palavras.split(",")]

    dados[nome] = {
        "titulo": titulo,
        "autores": autores,
        "periodico": periodico,
        "ano": ano,
        "resumo": resumo,
        "palavras_chave": palavras_chave,
    }

for nome, d in dados.items():
    print(nome[:4], "|", d["titulo"])
    print("   ", d["ano"], d["periodico"], "|", len(d["autores"]), "autores")
    print("   ", d["palavras_chave"])
