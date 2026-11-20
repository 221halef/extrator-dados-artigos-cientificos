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
