# Planilhas de exemplo (fictícias)

Tudo nesta pasta é **inventado**. Os textos da coluna `Discriminação` foram escritos à mão para cobrir as regras, as variações de escrita e os casos de borda. Nenhuma planilha, nome ou valor da empresa parceira foi usado.

A estrutura imita o Google Drive da empresa: uma pasta principal com uma subpasta por cliente.

```
planilhas_exemplo/
├── leia_antes.txt                       ignorado (arquivo solto na raiz)
├── Clinica_Alfa/
│   ├── faturamento_marco.xlsx           ✔ 12 linhas, todos os tipos de regra; fórmula, filtro,
│   │                                      formatos de data e moeda, painel congelado e uma 2ª aba
│   ├── controle_interno.xlsx            ignorado (sem a coluna Discriminação)
│   ├── nota_fiscal_exemplo.pdf          ignorado
│   └── observacoes.txt                  ignorado
├── Clinica_Beta/
│   ├── faturamento_marco.xlsx           ✔ mesmo nome da Alfa, para testar colisão de nomes
│   └── 2025/faturamento_antigo.xlsx     não visitado (subpasta dentro de subpasta)
└── Consultorio_Gama/
    ├── notas_marco.xlsx                 ✔ os casos que a versão 1 classificava errado
    └── arquivo_corrompido.xlsx          ignorado com aviso
```

Em `gerar_exemplos.py`:

- `ESPERADO` tem a classificação esperada de cada linha pela versão atual, conferida por `tests/test_pipeline.py`;
- `MUDANCAS_DESDE_V1` lista as linhas em que a versão 1 dava outro resultado; o teste de comparação falha se qualquer outra linha mudar.

Para regenerar: `python exemplos/gerar_exemplos.py` (a partir da raiz do repositório).
