# Resultados

> **Todos os resultados desta pasta foram obtidos com planilhas FICTÍCIAS**, geradas por `exemplos/gerar_exemplos.py`. Nenhuma planilha, nome ou valor da empresa parceira está neste repositório (LGPD).

Os arquivos foram gerados rodando o **código do notebook entregue**, sem nenhum ajuste, por meio de `executar_local.py`. Esse script troca só o Google Drive por uma pasta local e o envio pelo Gmail por um arquivo `.eml` (Python 3.13.18, pandas 3.0.5, openpyxl 3.1.5, Linux). O resultado é determinístico: rodar de novo produz as mesmas classificações.

## Arquivos desta pasta

| Arquivo | Conteúdo |
|---|---|
| `saida_demo/` | As 3 planilhas classificadas (`CLASSIFICADO_<subpasta>_<arquivo>.xlsx`), exatamente como o notebook as gera |
| `email_demo.eml` | O e-mail que seria enviado: assunto, resumo no corpo e os 3 anexos. Abre no Outlook, Thunderbird ou em qualquer cliente de e-mail |
| `log_execucao_demo.txt` | O que o notebook mostra na tela durante a execução |
| `classificacoes_demo.csv` | Cada linha classificada (subpasta, arquivo, texto da Discriminação, classificação), para leitura rápida no GitHub |
| `testes_pytest.txt` | Saída dos testes automatizados |
| `capturas/01_planilha_classificada.png` | Planilha da Clínica Alfa depois da classificação. As cores e o formato de data foram aplicados **só na imagem**, para facilitar a leitura; o arquivo gerado não tem cores |

## Pasta de exemplo

`exemplos/planilhas_exemplo/` imita a organização do Drive da empresa: uma pasta principal com uma subpasta por cliente.

| Item | O que exercita | Resultado |
|---|---|---|
| `Clinica_Alfa/faturamento_marco.xlsx` | 12 linhas com todos os tipos de regra, célula vazia e texto sem termo; tem uma segunda aba | Processada |
| `Clinica_Beta/faturamento_marco.xlsx` | Mesmo nome de arquivo da Alfa; minúsculas, plural, número no lugar de texto | Processada sem colisão de nomes |
| `Consultorio_Gama/notas_marco.xlsx` | Casos de borda que revelam limitações | Processada |
| `Clinica_Alfa/nota_fiscal_exemplo.pdf`, `observacoes.txt` | Arquivos que não são planilha | Ignorados |
| `Clinica_Alfa/controle_interno.xlsx` | Planilha sem a coluna `Discriminação` | Ignorada com aviso |
| `Consultorio_Gama/arquivo_corrompido.xlsx` | Arquivo `.xlsx` ilegível | Ignorado com aviso, sem interromper o lote |
| `Clinica_Beta/2025/faturamento_antigo.xlsx` | Planilha numa subpasta dentro da subpasta | Não é visitada (o notebook olha só um nível) |
| `leia_antes.txt` (na raiz) | Arquivo solto fora das subpastas | Ignorado |

## Classificações obtidas

26 linhas em 3 planilhas. Todas bateram com a classificação esperada **para o código atual**.

| Classificação | Linhas |
|---|---|
| CONSULTA | 9 |
| PROCEDIMENTO | 7 |
| ANALISAR | 4 |
| Sem categoria | 6 |

Resumo que vai no corpo do e-mail:

```
• Clinica_Alfa/faturamento_marco.xlsx: CONSULTA=5 | PROCEDIMENTO=3 | ANALISAR=2 | SEM CATEGORIA=2 ⚠️
• Clinica_Beta/faturamento_marco.xlsx: CONSULTA=2 | PROCEDIMENTO=2 | ANALISAR=2 | SEM CATEGORIA=1 ⚠️
• Consultorio_Gama/notas_marco.xlsx: CONSULTA=2 | PROCEDIMENTO=2 | ANALISAR=0 | SEM CATEGORIA=3 ⚠️
```

Das 6 linhas sem categoria, 3 são corretas (célula vazia, "Reembolso de despesas", um número) e **3 são falhas do código atual** diante da regra do cliente:

| Texto | Esperado pela regra | Obtido | Causa |
|---|---|---|---|
| Exames diagnósticos laboratoriais | PROCEDIMENTO | sem categoria | A lista tem só o singular `exame diagnostico`; a busca é por trecho exato |
| Consulta␣␣médica (espaço duplo) | CONSULTA | sem categoria | Espaços repetidos não são normalizados |
| Consulta↵médica (quebra de linha na célula) | CONSULTA | sem categoria | Idem |

E um caso classificado de forma **mais ampla** do que a regra pede: "Coordenação administrativa do escritório" vira CONSULTA, porque o termo `coordenacao` sozinho está na lista.

## O que é preservado na planilha

Comparação entre o original da Clínica Alfa e o arquivo gerado:

| Item | Preservado? |
|---|---|
| Dados de todas as colunas originais | Sim (conferido célula a célula pelos testes) |
| Ordem das colunas; `Classificação` entra no fim | Sim |
| Nome da aba | Sim |
| Larguras das colunas | Sim |
| Outras abas da pasta de trabalho | **Não**: só a primeira aba é lida e gravada |
| Estilo do cabeçalho (negrito, cor) | **Não** |
| Painel congelado | **Não** |
| Formato de data (`DD/MM/AAAA`) | **Não**: passa a mostrar data e hora |
| Formato de moeda (`R$ #.##0,00`) | **Não**: vira número geral |

Isso acontece porque o notebook relê a planilha com o pandas e grava um arquivo novo, copiando depois só as larguras. Os valores não mudam; a aparência sim.

## Testes automatizados

47 testes (pytest): **44 passando** e **3 falhas esperadas (`xfail`)**, que documentam as limitações acima e passam a avisar quando elas forem corrigidas. Todos rodam o código que está **dentro do notebook**:

- `test_regras.py` (32): termos de cada categoria, prioridade do ANALISAR, maiúsculas e acentos, células vazias e numéricas, limitações conhecidas.
- `test_pipeline.py` (10): busca nas subpastas, arquivos ignorados, nomes sem colisão, dados originais intactos, larguras e nome da aba, o que **não** é preservado, conteúdo do e-mail, pasta inexistente, pasta sem planilhas válidas e senha de e-mail recusada.
- `test_notebook.py` (5): estrutura de 3 células, os 4 campos do formulário, ausência de credenciais reais e de saídas salvas.

Lista completa em `testes_pytest.txt`.

## Próximas medições (com a empresa parceira)

- Taxa de acerto sobre um lote de planilhas reais, comparada a uma classificação manual usada como gabarito. Meta do projeto de extensão: ≥ 90 %.
- Tempo do processo manual anterior comparado ao tempo com a automação. Meta: redução ≥ 70 %.
- Tempo de execução com as ~50 planilhas reais de um mês.
