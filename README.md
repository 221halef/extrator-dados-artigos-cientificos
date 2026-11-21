# Extrator de dados de artigos científicos

Pipeline em Python que lê artigos científicos em PDF, extrai informações estruturadas com regex e regras textuais, organiza tudo em um DataFrame do Pandas e exporta um dataset em CSV.

Projeto da disciplina de **Ciência de Dados** do **Instituto Federal do Ceará (IFCE), Campus Boa Viagem**.

## Sobre o projeto

Eu uso 10 artigos do **Journal of Information and Data Management (JIDM), vol. 17, nº 1, 2026**, todos ligados a Ciência de Dados, Banco de Dados, Machine Learning e áreas correlatas. A partir dos PDFs, o programa:

1. lê os arquivos da pasta `artigos/`;
2. extrai o texto respeitando o layout de duas colunas;
3. limpa o texto;
4. extrai os campos de cada artigo (título, autores, resumo, conclusão etc.);
5. monta um DataFrame com uma linha por artigo;
6. faz uma análise simples dos dados;
7. exporta o resultado para `dataset_artigos.csv`.

A extração usa apenas **regex, regras textuais e padrões estruturais do documento** (posição, fonte e tamanho do texto). Nenhum modelo de IA é usado para extrair as informações.

## Estrutura do repositório

```
.
├── artigos/               # 10 artigos do JIDM em PDF
├── main.py                # pipeline completo
├── dataset_artigos.csv    # dataset final gerado
└── README.md
```

## Dataset gerado

O arquivo `dataset_artigos.csv` tem 10 linhas (uma por artigo) e 12 colunas:

| Coluna | Descrição |
|---|---|
| `titulo` | Título do artigo |
| `autores` | Autores, separados por `;` |
| `periodico` | Nome do periódico |
| `ano` | Ano de publicação |
| `resumo` | Texto do resumo |
| `conclusao` | Texto da seção de conclusão |
| `palavras_chave` | Palavras-chave, separadas por `;` |
| `qtd_autores` | Quantidade de autores |
| `qtd_paginas` | Quantidade de páginas |
| `qtd_caracteres` | Quantidade de caracteres do texto limpo |
| `qtd_palavras` | Quantidade de palavras do texto limpo |
| `qtd_secoes` | Quantidade de seções numeradas identificadas |

## Como instalar

**Pré-requisito:** Python 3.11 ou superior (testado com Python 3.12).

1. Clone o repositório e entre na pasta:

```bash
git clone https://github.com/221halef/extrator-dados-artigos-cientificos.git


cd extrator-dados-artigos-cientificos
```
ou

```bash
git clone git@github.com:221halef/extrator-dados-artigos-cientificos.git


cd extrator-dados-artigos-cientificos
```


2. (Opcional, recomendado) Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows, a ativação é `.venv\Scripts\activate`.

3. Instale as dependências:

```bash
pip install pdfplumber pandas
```

## Como executar

```bash
python main.py
```

O programa mostra no terminal cada etapa (PDFs encontrados, contagem de caracteres antes e depois da limpeza, campos extraídos, DataFrame e análise) e gera o arquivo `dataset_artigos.csv` na raiz do projeto.

## Como a extração funciona

| Etapa | O que eu faço |
|---|---|
| Leitura | Listo os arquivos `.pdf` da pasta `artigos/` e abro cada um com o `pdfplumber`. |
| Extração do texto | Uso `extract_text(x_tolerance=1.5)` para evitar palavras coladas. A página 1 é lida inteira (o cabeçalho ocupa a largura toda). Nas demais páginas, ignoro os 65 primeiros pontos (cabeçalho repetido) e leio a coluna esquerda e depois a direita. |
| Limpeza | Normalizo o texto com `unicodedata` (NFKC), removo ícones e caracteres inválidos, junto palavras hifenizadas na quebra de linha, tiro espaços duplicados e linhas vazias. Mantenho as quebras de linha, pois as próximas etapas dependem delas. |
| Periódico e ano | Regex na primeira linha do texto (`Journal ..., 2026, ...`). |
| Título | Linhas depois da linha da licença, até a primeira linha de autor (linha com `[`). |
| Autores | Texto antes de ` [` em cada linha de autor, sem o número de afiliação no final do nome. |
| Resumo | Texto entre a linha `Published:` e `Keywords`, removendo a palavra `Abstract` quando existe. |
| Palavras-chave | Texto entre `Keywords` e `1 Introduction`, separado por vírgula. |
| Seções | Reabro os PDFs e mantenho só os caracteres em **negrito com fonte maior que 12** (padrão dos títulos de seção). Aceito linhas no formato `N Título`. |
| Conclusão | Texto entre o título `N Conclusion...` e o primeiro marcador de fim (`Acknowledgements`, `Funding`, `References` etc.). |
| Quantidades | `len()` de autores e seções, páginas lidas do PDF, e caracteres/palavras calculados no texto limpo. |

## Resultados da análise

- **Artigo com maior resumo:** *HDP+: Leveraging Anomaly and Change Point Detection for Pump-and-Dump in Cryptocurrency Exchanges* (263 palavras).
- **Média de palavras por artigo:** 8.501,5.
- **Média de autores por artigo:** 3,5.
- **Distribuição de páginas:** 9 páginas (1 artigo), 10 (6 artigos), 11 (1), 13 (1) e 15 (1).
- **Palavras mais frequentes** (sem *stopwords* e sem as referências): `data` (639), `model` (237), `dataset` (220), `time` (215) e `performance` (198).

## Dificuldades e limitações

- Em alguns PDFs o `pdfplumber` juntava palavras. Resolvi com `x_tolerance=1.5`.
- A leitura em duas colunas misturava as linhas. Resolvi cortando a página ao meio.
- Tabelas e pseudocódigos geravam falsos títulos de seção. Resolvi usando fonte em negrito e tamanho como critério.
- A junção de palavras hifenizadas é aproximada: um composto quebrado na linha, como `state-of-the-art`, pode virar `state-of-theart`.
- Alguns nomes de seção ficam cortados quando o título ocupa duas linhas. A contagem de seções não é afetada.
- No começo da introdução (página 1), as duas colunas continuam misturadas. Isso não afeta os campos extraídos.
- Os métodos dependem do layout do JIDM. Para outro periódico, seria preciso ajustar os regex, o corte das colunas e os marcadores de fim da conclusão.
- O desafio extra (DOI, referências, instituições, e-mails, nomes das seções e países) não foi implementado nesta versão.

## Artigos utilizados

Todos os artigos foram publicados no **Journal of Information and Data Management (JIDM), vol. 17, nº 1, 2026**, e estão sob a licença **[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**, que permite copiar e redistribuir o material desde que haja crédito aos autores. Os PDFs foram incluídos neste repositório **sem nenhuma alteração**, e os direitos sobre os artigos continuam com seus autores.

O título de cada artigo leva à sua página no site do JIDM. O DOI é o impresso no cabeçalho do próprio PDF. Alguns DOIs ainda podem não ser reconhecidos pelo `doi.org`, por isso o link usado é o da página do periódico.

| Artigo | Autores | DOI |
|---|---|---|
| [Leveraging LLMs for Topic Modeling and Classification in Brazilian Funk Lyrics](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5578) | Jesus Daniel Yepez Rojas, Bruno Tavares Santos, Fabíola de Carvalho Leite Peres, Karin Becker | 10.5753/jidm.2026.5578 |
| [Incremental Schema Evolution in Document-oriented Databases](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5700) | Eleonília Monteiro Rodrigues, Carlos Eduardo S. Pires, Dimas Cassimiro do N. Filho | 10.5753/jidm.2026.5700 |
| [HDP+: Leveraging Anomaly and Change Point Detection for Pump-and-Dump in Cryptocurrency Exchanges](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5728) | Matheus S. Moura, Laís Baroni, Eduardo Ogasawara, Diogo S. Mendonça | 10.5753/jidm.2026.5728 |
| [From Legacy to Modern Systems: An Enterprise-ready Workflow for Database Migrations](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5730) | Gustavo Moraes, Victor Misael, Angelo Brayner | 10.5753/jidm.2026.5730 |
| [Evaluating Data Drift Detection and Its Effects on Machine Learning System Performance](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5738) | Lucas Helfstein Rocha, Kelly Rosa Braghetto | 10.5753/jidm.2026.5738 |
| [Characterizing the Socioenvironmental and Behavioral Profile of Individuals with OCD Using the PNS 2019 Database](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5780) | Anna Puga Campos Rodrigues, Luis Enrique Zárate | 10.5753/jidm.2026.5780 |
| [A heuristic Data-Centric AI approach to predict non-contact injuries in elite football players](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5855) | Matheus Santos Melo, Juliano Spineti, Diego Nunes Brandão, Lucas Giusti Tavares, Jorge de Abreu Soares | 10.5753/jidm.2026.5855 |
| [Incorporating LGPD Requirements and Restrictions into Database Design](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5859) | Patrícia Vieira, José Maria Monteiro, Javam Machado, Angelo Brayner | 10.5753/jidm.2026.5859 |
| [POI Type Embedding Techniques for Recommendation Systems: A Comparative Analysis](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5929) | Diogo Alves Silveira, Salatiel Dantas Silva, Nícolas Moreira Nobre Leite, Claudio E. C. Campelo | 10.5753/jidm.2026.5929 |
| [How Effectively Do LLMs Automate Data Analysis? A Comparative Study with ChatGPT’s Data Analyst, Grok, and Qwen](https://journals-sol.sbc.org.br/index.php/jidm/article/view/5963) | Carlos D. S. Nogueira, Darlan S. Almeida, Beatriz A. de Miranda, Claudio E. C. Campelo | 10.5753/jidm.2026.5963 |

## Bibliotecas utilizadas

- [pdfplumber](https://github.com/jsvine/pdfplumber): leitura de PDFs e extração de texto.
- [pandas](https://pandas.pydata.org/): construção do DataFrame, análise e exportação do CSV.
- Biblioteca padrão do Python: `os`, `re`, `unicodedata` e `collections`.
