# Arquitetura

## Visão geral

O sistema tem uma única peça em produção: o notebook `notebook/classificador_planilhas.ipynb`, que roda no Google Colab da conta da empresa parceira. O restante do repositório existe para **testar e demonstrar esse notebook** fora do Colab, sem credenciais e sem dados reais.

```
classificador-planilhas/
├── notebook/
│   ├── classificador_planilhas.ipynb        ← versão 2 (atual)
│   └── historico/classificador_planilhas_v1.ipynb   ← versão 1 (em uso na empresa)
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
| 2 | Código com formulário (`#@param`) | `PASTA_DRIVE`, `EMAIL_REMETENTE`, `EMAIL_DESTINATARIO` |
| 3 | Código (fica oculto) | Todo o processamento |

A célula 3 faz cinco etapas, em sequência.

### 1. Acesso ao Drive e busca das planilhas

`drive.mount('/content/drive')` monta o Google Drive da usuária como uma pasta. O código lista, em ordem alfabética, as subpastas de `MyDrive/<PASTA_DRIVE>` (um nível só) e, dentro de cada uma, considera apenas arquivos `.xlsx` cuja primeira aba tenha a coluna `Discriminação` na primeira linha. Para decidir, lê só o cabeçalho (`pd.read_excel(..., nrows=0)`). Qualquer outro arquivo é listado no log como ignorado; um `.xlsx` ilegível também, sem interromper o lote.

Se a pasta não existir ou não houver nenhuma planilha válida, o notebook para com `raise SystemExit()`, antes de pedir a senha.

### 2. Senha de app

`obter_senha_app()` tenta ler o *Secret* `SENHA_APP` do Colab (`google.colab.userdata.get`). Se ele não existir ou o acesso não for liberado, abre uma caixa de senha com `getpass.getpass`, que esconde o que é digitado. A senha fica só na memória da sessão: não é impressa nem gravada no notebook. Os espaços da senha ("abcd efgh ijkl mnop") são removidos.

### 3. Classificação

Três funções e três listas de termos:

- `singular(palavra)`: leva plurais comuns do português ao singular, por regras de terminação (`-oes → -ao`, `-ais → -al`, `-eis → -el`, `-ois → -ol`, `-res → -r`, `-zes → -z`, `-ns → -m`, `-s → ""`). Palavras com até 3 letras ficam como estão.
- `limpar_texto(texto)`: minúsculas; remove acentos com `unicodedata.normalize('NFKD')`; troca qualquer sequência que não seja letra ou número por um espaço (pontuação, espaços repetidos, quebras de linha); aplica `singular` a cada palavra. Célula vazia vira `""`.
- `TERMOS_CONSULTA`, `TERMOS_PROCEDIMENTO`, `TERMOS_ANALISAR`: escritos como na regra do cliente, com acentos, e passados por `limpar_texto` uma vez (`TERMOS_*_LIMPOS`).
- `classificar_servico(descricao)`: procura cada termo limpo como **trecho** do texto limpo e aplica a prioridade:

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

Como texto e termos passam pela mesma limpeza, "Exames diagnósticos;" e "exame diagnóstico" viram ambos `exame diagnostico`. A busca continua sendo por trecho, como na regra do cliente ("quando a descrição **contiver**"): por isso `hospital` também casa com "hospitalar" e "hospital-dia".

### 4. Gravação do arquivo classificado

`gravar_planilha_classificada(origem, destino)`:

1. abre a planilha original com `openpyxl` duas vezes: uma normal, que mantém fórmulas e formatação e é a que será salva; e uma com `data_only=True`, para ler o **resultado** das fórmulas;
2. na primeira aba, localiza `Discriminação` no cabeçalho e escolhe a coluna de saída: a `Classificação` existente, se o arquivo já foi classificado, ou a primeira coluna livre;
3. copia o estilo da célula vizinha para o cabeçalho e para cada célula nova, com formato numérico "Geral";
4. classifica cada linha que tenha algum dado; linhas totalmente vazias são puladas e não entram na contagem;
5. ajusta a largura da coluna nova e, se o cabeçalho tiver filtro, estende o filtro até ela;
6. salva como `/content/CLASSIFICADO_<subpasta>_<arquivo>.xlsx`, na área temporária da sessão do Colab.

Tudo o que não é a coluna nova fica como estava: outras abas, fórmulas, estilos, formatos, larguras, células mescladas e painéis congelados. A versão 1 relia a planilha com o pandas e gravava um arquivo novo, o que perdia tudo isso.

### 5. Envio por e-mail

Monta um único `EmailMessage` com todos os arquivos anexados e um resumo por arquivo no corpo (contagem por categoria, quantidade sem categoria e lista de arquivos com erro). Envia por `smtplib.SMTP_SSL('smtp.gmail.com', 465)`. Sem senha, ou com falha no envio, o problema é mostrado na tela e o processo termina normalmente.

## Como o notebook é testado fora do Colab

O notebook precisa continuar sendo **um arquivo só, autocontido**, porque é isso que a usuária abre. Para não manter uma cópia do código em outro lugar, que poderia ficar desatualizada, `executar_local.py`:

1. lê o `.ipynb` como JSON e pega a célula que contém `drive.mount(`;
2. troca `/content/drive/MyDrive/` por uma pasta local e `/content/` pela pasta de saída, conferindo o número de ocorrências e falhando com uma mensagem clara se o notebook mudar;
3. injeta um módulo `google.colab` falso, com `drive.mount` que não faz nada e `userdata.get` que devolve (ou não) a senha; substitui `getpass.getpass` e `smtplib.SMTP_SSL` por objetos que registram a chamada em vez de abrir uma caixa ou enviar o e-mail;
4. executa a célula com `exec` e devolve o log, os arquivos gerados, a mensagem e a senha usada no login.

Os módulos falsos são retirados depois da execução sem descarregar os que o notebook importou, porque o numpy não pode ser carregado duas vezes no mesmo processo.

Os testes de regra (`tests/test_regras.py`) usam outra técnica: extraem do notebook, via `ast`, só as funções de regra e as listas de termos e as executam isoladas. O teste `test_v2_so_muda_as_linhas_corrigidas` roda a versão 1 e a 2 sobre os mesmos arquivos e falha se mudar qualquer linha além das previstas em `exemplos/gerar_exemplos.py` (`MUDANCAS_DESDE_V1`).

## Segurança e LGPD

- O notebook roda na conta Google da própria empresa. As planilhas não passam por nenhum servidor da equipe nem por serviço de terceiros além do Google.
- O repositório não contém dados reais; a pasta de exemplo é gerada por código, com textos escritos à mão.
- O formulário não tem campo de senha; a senha vem dos *Secrets* do Colab ou é digitada na hora, e `tests/test_notebook.py` falha se o formulário voltar a pedir senha.
