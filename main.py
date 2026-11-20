import os
import pdfplumber
import re
import unicodedata
import pandas as pd
from collections import Counter

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

def so_titulos(obj):
    return obj["object_type"] != "char" or ("Bold" in obj["fontname"] and obj["size"] > 12)

secoes = {}

for caminho in arquivos:
    nome = os.path.basename(caminho)
    lista = []

    with pdfplumber.open(caminho) as pdf:
        for i, pagina in enumerate(pdf.pages):
            if i == 0:
                partes = [pagina]
            else:
                meio = pagina.width / 2
                partes = [pagina.crop((0, 65, meio, pagina.height)), pagina.crop((meio, 65, pagina.width, pagina.height))]

            for parte in partes:
                titulos = parte.filter(so_titulos)
                texto = titulos.extract_text(x_tolerance=1.5) or ""
                for linha in texto.split("\n"):
                    for pedaco in re.split(r" (?=\d{1,2} [A-Z])", linha):
                        if re.match(r"\d{1,2} [A-Z]", pedaco):
                            lista.append(pedaco)

    secoes[nome] = lista

fins = ["Acknowledgements", "Acknowledgments", "Funding", "Authors’ Contributions", "Competing interests", "Availability of data and materials", "Declarations", "References", "REFERENCES"]

conclusoes = {}

for nome, texto in textos_limpos.items():
    linhas = texto.split("\n")

    inicio = None
    for i, linha in enumerate(linhas):
        if re.match(r"^\d+ Conclusion", linha):
            inicio = i
            break

    fim = len(linhas)
    for i in range(inicio + 1, len(linhas)):
        if linhas[i] in fins:
            fim = i
            break

    conclusoes[nome] = " ".join(linhas[inicio + 1:fim])

for nome in textos_limpos:
    print(nome[:4], "-", len(secoes[nome]), "seções -", len(conclusoes[nome].split()), "palavras na conclusão")

linhas_df = []

for nome in textos_limpos:
    texto = " ".join(textos_limpos[nome].split())
    d = dados[nome]

    linhas_df.append({
        "titulo": d["titulo"],
        "autores": d["autores"],
        "periodico": d["periodico"],
        "ano": d["ano"],
        "resumo": d["resumo"],
        "conclusao": conclusoes[nome],
        "palavras_chave": d["palavras_chave"],
        "qtd_autores": len(d["autores"]),
        "qtd_paginas": qtd_paginas[nome],
        "qtd_caracteres": len(texto),
        "qtd_palavras": len(texto.split()),
        "qtd_secoes": len(secoes[nome]),
    })

df = pd.DataFrame(linhas_df)

print(df.shape)
print(df[["ano", "qtd_autores", "qtd_paginas", "qtd_caracteres", "qtd_palavras", "qtd_secoes"]])

tamanhos = df["resumo"].str.split().str.len()
posicao = tamanhos.idxmax()
print("Artigo com maior resumo:", df.loc[posicao, "titulo"])
print("Palavras no resumo:", tamanhos[posicao])

print("Média de palavras por artigo:", round(df["qtd_palavras"].mean(), 1))

stopwords = ["the", "and", "for", "that", "with", "this", "are", "from", "was", "were", "have", "has", "had", "can", "which", "also", "such", "been", "their", "these", "our", "not", "but", "its", "may", "than", "then", "when", "where", "each", "both", "other", "more", "most", "into", "between", "through", "over", "only", "all", "any", "one", "two", "will", "would", "could", "should", "while", "however", "they", "them", "there", "those", "about", "after", "before", "does", "did", "being", "how", "what", "who", "whose", "per", "via", "et", "fig", "figure", "table", "used", "using", "use", "based", "result", "results"]

contagem = Counter()
for texto in textos_limpos.values():
    sem_referencias = texto.split("\nReferences\n")[0]
    for palavra in re.findall(r"[a-z]{3,}", sem_referencias.lower()):
        if palavra not in stopwords:
            contagem[palavra] += 1

print("Palavras mais frequentes:")
for palavra, qtd in contagem.most_common(15):
    print("  ", palavra, qtd)

print("Distribuição de páginas:")
print(df["qtd_paginas"].value_counts().sort_index())

print("Média de autores por artigo:", df["qtd_autores"].mean())
