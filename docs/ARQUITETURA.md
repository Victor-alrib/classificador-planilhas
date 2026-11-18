# Arquitetura

## Visão geral

O sistema tem uma única peça em produção: o notebook `notebook/classificador_planilhas.ipynb`, que roda no Google Colab da conta da empresa parceira. O restante do repositório existe para **testar e demonstrar esse notebook** fora do Colab, sem credenciais e sem dados reais.

```
classificador-planilhas/
├── notebook/classificador_planilhas.ipynb   ← versão entregue (roda no Colab)
├── executar_local.py                        ← roda a célula de processamento localmente
├── exemplos/
│   ├── gerar_exemplos.py                    ← cria a pasta de planilhas fictícias
│   └── planilhas_exemplo/                   ← pasta gerada (imita o Drive da empresa)
├── tests/                                   ← pytest sobre o código do notebook
└── docs/
```

## O notebook (3 células)

| Célula | Tipo | Conteúdo |
|---|---|---|
| 1 | Texto | Título e instrução para a usuária |
| 2 | Código com formulário (`#@param`) | `PASTA_DRIVE`, `EMAIL_REMETENTE`, `SENHA_APP`, `EMAIL_DESTINATARIO` |
| 3 | Código (fica oculto) | Todo o processamento |

A célula 3 faz quatro etapas, em sequência:

### 1. Acesso ao Drive e busca das planilhas

`drive.mount('/content/drive')` monta o Google Drive da usuária como uma pasta. O código lista as subpastas de `MyDrive/<PASTA_DRIVE>` (um nível só) e, dentro de cada uma, considera apenas arquivos `.xlsx` cuja primeira linha tenha a coluna `Discriminação`. Para isso lê só o cabeçalho (`pd.read_excel(..., nrows=0)`). Qualquer outro arquivo é listado no log como ignorado; um `.xlsx` ilegível também, sem interromper o lote.

Se a pasta não existir ou não houver nenhuma planilha válida, o notebook para com `raise SystemExit()` antes de tentar enviar e-mail.

### 2. Classificação

Duas funções:

- `limpar_texto(texto)`: converte para minúsculas, decompõe os acentos com `unicodedata.normalize('NFKD')` e descarta o que não é ASCII. Célula vazia vira `""`.
- `classificar_servico(descricao)`: procura cada termo das listas como **trecho** do texto normalizado (`termo in desc`) e aplica a prioridade:

```python
if tem_atendimento or (tem_consulta and tem_procedimento):
    return 'ANALISAR'
elif tem_consulta:
    return 'CONSULTA'
elif tem_procedimento:
    return 'PROCEDIMENTO'
else:
    return ''
```

A busca por trecho é o que permite que `procedimento` case com "procedimentos" e `hospital` com "hospitalares". É também a origem das limitações: `exame diagnostico` não está contido em "exames diagnosticos" (há um "s" no meio), e "consulta  medica", com espaço duplo, não contém `consulta medica`.

### 3. Gravação do arquivo classificado

```python
df = pd.read_excel(caminho_arquivo)
df['Classificação'] = df['Discriminação'].apply(classificar_servico)
df.to_excel(caminho_saida, index=False, sheet_name=nome_da_aba, engine='openpyxl')
```

Em seguida, abre o arquivo novo com `openpyxl` e copia as larguras de coluna do original. Por ser um arquivo **novo**, escrito a partir de um DataFrame, os valores são preservados, mas estilos, formatos de número, painéis congelados e outras abas não são (ver `resultados/resultados.md`). A correção natural é abrir o original com `openpyxl` e escrever só a coluna nova.

Os arquivos vão para `/content/`, a área temporária da sessão do Colab, com o nome `CLASSIFICADO_<subpasta>_<arquivo>.xlsx`.

### 4. Envio por e-mail

Monta um único `EmailMessage` com todos os arquivos anexados e um resumo por arquivo no corpo (contagem por categoria, quantidade sem categoria e lista de arquivos com erro). Envia por `smtplib.SMTP_SSL('smtp.gmail.com', 465)` com a senha de app. Uma falha no envio é mostrada na tela e não derruba o processo.

## Como o notebook é testado fora do Colab

O notebook precisa continuar sendo **um arquivo só, autocontido**, porque é isso que a usuária abre. Para não manter uma cópia do código em outro lugar, que poderia ficar desatualizada, `executar_local.py`:

1. lê o `.ipynb` como JSON e pega a célula que contém `drive.mount(`;
2. troca `/content/drive/MyDrive/` por uma pasta local e `/content/` pela pasta de saída, conferindo o número de ocorrências e falhando com uma mensagem clara se o notebook mudar;
3. injeta um módulo `google.colab` falso, cujo `drive.mount` não faz nada, e substitui `smtplib.SMTP_SSL` por um objeto que guarda a mensagem em vez de enviá-la;
4. executa a célula com `exec` e devolve o log, os arquivos gerados e a mensagem.

Os testes de regra (`tests/test_regras.py`) usam outra técnica: extraem do notebook, via `ast`, só as definições de `limpar_texto` e `classificar_servico` e as executam isoladas. Assim os dois tipos de teste exercitam o código que está de fato no notebook.

## Segurança e LGPD

- O notebook roda na conta Google da própria empresa. As planilhas não passam por nenhum servidor da equipe nem por serviço de terceiros além do Google.
- O repositório não contém dados reais; a pasta de exemplo é gerada por código, com textos escritos à mão.
- O formulário traz só valores de exemplo, e `tests/test_notebook.py` falha se uma senha ou e-mail real for salvo nele.
- Ponto de atenção: a senha de app digitada no formulário fica gravada no `.ipynb` quando o Colab salva o notebook no Drive da usuária. Os *Secrets* do Colab evitariam isso.
