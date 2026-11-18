# Planilhas de exemplo (fictícias)

Tudo nesta pasta é **inventado**. Os textos da coluna `Discriminação` foram escritos à mão para cobrir as regras, as variações que a normalização precisa aceitar e os casos de borda. Nenhuma planilha, nome ou valor da empresa parceira foi usado.

A estrutura imita o Google Drive da empresa: uma pasta principal com uma subpasta por cliente.

```
planilhas_exemplo/
├── leia_antes.txt                       ignorado (arquivo solto na raiz)
├── Clinica_Alfa/
│   ├── faturamento_marco.xlsx           ✔ 12 linhas, todos os tipos de regra; tem uma 2ª aba
│   ├── controle_interno.xlsx            ignorado (sem a coluna Discriminação)
│   ├── nota_fiscal_exemplo.pdf          ignorado
│   └── observacoes.txt                  ignorado
├── Clinica_Beta/
│   ├── faturamento_marco.xlsx           ✔ mesmo nome da Alfa, para testar colisão de nomes
│   └── 2025/faturamento_antigo.xlsx     não visitado (subpasta dentro de subpasta)
└── Consultorio_Gama/
    ├── notas_marco.xlsx                 ✔ casos que mostram as limitações
    └── arquivo_corrompido.xlsx          ignorado com aviso
```

A classificação esperada de cada linha está em `gerar_exemplos.py` (`ESPERADO`) e é conferida por `tests/test_pipeline.py`.

Para regenerar: `python exemplos/gerar_exemplos.py` (a partir da raiz do repositório).
