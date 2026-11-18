# Resultados

> **Todos os resultados desta pasta foram obtidos com planilhas FICTÍCIAS**, geradas por `exemplos/gerar_exemplos.py`. Nenhuma planilha, nome ou valor da empresa parceira está neste repositório (LGPD).

Os arquivos foram gerados rodando o **código da versão 2 do notebook**, sem nenhum ajuste, por meio de `executar_local.py`. Esse script troca só o Google Drive por uma pasta local, a senha por um *Secret* simulado e o envio pelo Gmail por um arquivo `.eml`. Ambiente: Python 3.13.18, pandas 3.0.5, openpyxl 3.1.5, Linux. O resultado é determinístico: rodar de novo produz as mesmas classificações.

## Arquivos desta pasta

| Arquivo | Conteúdo |
|---|---|
| `saida_demo/` | As 3 planilhas classificadas (`CLASSIFICADO_<subpasta>_<arquivo>.xlsx`), exatamente como o notebook as gera |
| `email_demo.eml` | O e-mail que seria enviado: assunto, resumo no corpo e os 3 anexos. Abre no Outlook, Thunderbird ou em qualquer cliente de e-mail |
| `log_execucao_demo.txt` | O que o notebook mostra na tela durante a execução |
| `classificacoes_demo.csv` | Cada linha, com a classificação da versão 2 e a da versão 1 lado a lado |
| `testes_pytest.txt` | Saída dos testes automatizados |
| `capturas/01_planilha_classificada.png` | Primeira aba da planilha da Clínica Alfa gerada pela versão 2, renderizada sem nenhuma alteração de formatação |

## Pasta de exemplo

`exemplos/planilhas_exemplo/` imita a organização do Drive da empresa: uma pasta principal com uma subpasta por cliente.

| Item | O que exercita | Resultado |
|---|---|---|
| `Clinica_Alfa/faturamento_marco.xlsx` | 12 linhas com todos os tipos de regra; cabeçalho colorido, formatos de data e moeda, coluna com fórmula, filtro, painel congelado e uma segunda aba | Processada, formatação intacta |
| `Clinica_Beta/faturamento_marco.xlsx` | Mesmo nome de arquivo da Alfa; minúsculas, plural, número no lugar de texto, "coordenação" sozinha | Processada sem colisão de nomes |
| `Consultorio_Gama/notas_marco.xlsx` | Os casos que a versão 1 classificava errado | Processada |
| `Clinica_Alfa/nota_fiscal_exemplo.pdf`, `observacoes.txt` | Arquivos que não são planilha | Ignorados |
| `Clinica_Alfa/controle_interno.xlsx` | Planilha sem a coluna `Discriminação` | Ignorada com aviso |
| `Consultorio_Gama/arquivo_corrompido.xlsx` | Arquivo `.xlsx` ilegível | Ignorado com aviso, sem interromper o lote |
| `Clinica_Beta/2025/faturamento_antigo.xlsx` | Planilha numa subpasta dentro da subpasta | Não é visitada (o notebook olha só um nível) |
| `leia_antes.txt` (na raiz) | Arquivo solto fora das subpastas | Ignorado |

## Classificações obtidas (versão 2)

29 linhas em 3 planilhas, todas iguais à classificação esperada pelas regras.

| Classificação | Versão 2 | Versão 1 |
|---|---|---|
| CONSULTA | 10 | 11 |
| PROCEDIMENTO | 9 | 7 |
| ANALISAR | 5 | 4 |
| Sem categoria | 5 | 7 |

As 5 linhas sem categoria na versão 2 estão corretas pela regra: uma célula vazia, "Reembolso de despesas de deslocamento", um número no lugar de texto e duas descrições com "coordenação" sozinha.

Resumo que vai no corpo do e-mail:

```
• Clinica_Alfa/faturamento_marco.xlsx: CONSULTA=5 | PROCEDIMENTO=3 | ANALISAR=2 | SEM CATEGORIA=2 ⚠️
• Clinica_Beta/faturamento_marco.xlsx: CONSULTA=1 | PROCEDIMENTO=2 | ANALISAR=2 | SEM CATEGORIA=2 ⚠️
• Consultorio_Gama/notas_marco.xlsx: CONSULTA=4 | PROCEDIMENTO=4 | ANALISAR=1 | SEM CATEGORIA=1 ⚠️
```

## O que mudou da versão 1 para a 2

As duas versões rodaram sobre os mesmos arquivos. Só estas 7 linhas mudaram; as outras 22 saíram iguais.

| Texto da Discriminação | Versão 1 | Versão 2 | Correção |
|---|---|---|---|
| Exames diagnósticos laboratoriais | sem categoria | PROCEDIMENTO | Plural |
| Hospitais conveniados | sem categoria | PROCEDIMENTO | Plural |
| Exames diagnósticos; consultas médicas | CONSULTA | ANALISAR | Plural: agora os dois tipos são reconhecidos |
| Consulta␣␣médica (espaço duplo) | sem categoria | CONSULTA | Espaços |
| Consulta↵médica (quebra de linha) | sem categoria | CONSULTA | Espaços |
| Coordenação administrativa do escritório | CONSULTA | sem categoria | "Coordenação" sozinha |
| Coordenação de equipe médica | CONSULTA | sem categoria | "Coordenação" sozinha |

As duas últimas dependem de como se lê a regra do cliente ("consultas médicas realizadas em coordenação"). A versão 2 exige a expressão "realizadas em coordenação". **Confirmar com a empresa antes de trocar a versão em uso.**

## O que é preservado na planilha

Comparação entre o original da Clínica Alfa e o arquivo gerado por cada versão:

| Item | Versão 1 | Versão 2 |
|---|---|---|
| Valores de todas as células originais | Sim | Sim |
| Fórmulas (coluna "Valor líquido") | **Não**: viram valores ou ficam vazias | Sim |
| Outras abas da pasta de trabalho | **Não** | Sim |
| Estilo do cabeçalho (negrito, cor) | **Não** | Sim |
| Formatos de data e moeda | **Não** | Sim |
| Painel congelado | **Não** | Sim |
| Filtro no cabeçalho | **Não** | Sim, e a coluna nova entra no filtro |
| Larguras das colunas e nome da aba | Sim | Sim |
| Células com estilo diferente do original | 48 atributos | 0 |

## Testes automatizados

**85 testes** (pytest), **todos passando**. Todos rodam o código que está **dentro do notebook**:

- `test_regras.py` (60): termos de cada categoria, prioridade do ANALISAR, maiúsculas e acentos, plural, espaços e pontuação, "coordenação" sozinha, singularização palavra a palavra, células vazias e numéricas.
- `test_pipeline.py` (18): busca nas subpastas, arquivos ignorados, nomes sem colisão, classificação, dados e fórmulas intactos em todas as abas, estilos preservados célula a célula, coluna nova no estilo do cabeçalho e no filtro, nova execução sobre arquivo já classificado, linha vazia, conteúdo do e-mail, as três formas de obter a senha (Secrets, digitada, nenhuma), senha recusada, pasta inexistente e pasta sem planilhas válidas. Inclui a comparação com a versão 1, que falha se qualquer linha além das 7 previstas mudar.
- `test_notebook.py` (7): estrutura de 3 células, formulário só com os 3 campos e sem senha, ausência de saídas salvas e versão 1 preservada no histórico.

Lista completa em `testes_pytest.txt`.

## Próximas validações (com a empresa parceira)

- Taxa de acerto sobre um lote de planilhas reais, comparada a uma classificação manual usada como gabarito. Meta do projeto de extensão: ≥ 90 %.
- Tempo do processo manual anterior comparado ao tempo com a automação. Meta: redução ≥ 70 %.
- Tempo de execução com as ~50 planilhas reais de um mês.
- Versão 2 rodando no Google Colab da empresa (*Secrets* e caixa de senha), que nos testes daqui são simulados.
