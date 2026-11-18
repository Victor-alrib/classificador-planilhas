# Histórico de versões

## Versão 2 — correções encontradas pelos testes

Ainda **não validada com a empresa parceira**, que continua usando a versão 1. A versão 1 está guardada em `notebook/historico/classificador_planilhas_v1.ipynb`.

### Classificação

- **Plural reconhecido.** O texto e os termos da regra passam pela mesma limpeza, que leva cada palavra ao singular: "exames diagnósticos" vira "exame diagnostico", "hospitais" vira "hospital" e "produções" vira "producao". Na v1, "Exames diagnósticos", termo que está na própria regra do cliente, ficava sem categoria.
- **Espaços, quebras de linha e pontuação não atrapalham mais.** Qualquer sequência de caracteres que não seja letra ou número vira um espaço só. Na v1, "Consulta␣␣médica" e "Consulta↵médica" ficavam sem categoria.
- **"Coordenação" sozinha não classifica mais como CONSULTA.** O termo passou a ser "realizadas em coordenação", como está na regra do cliente. Na v1, "Coordenação administrativa do escritório" virava CONSULTA. **Esta é a única mudança que depende de interpretação da regra: confirmar com a empresa.**
- Os termos agora estão escritos como na regra do cliente (com acentos), em três listas no início do código, para facilitar a conferência.

Efeito nos exemplos fictícios: 7 de 29 linhas mudam de classificação, todas listadas em `resultados/resultados.md` e travadas pelo teste `test_v2_so_muda_as_linhas_corrigidas`. As outras 22 saem iguais nas duas versões.

### Planilha gerada

- **A planilha original é preservada.** A v2 abre o arquivo original com `openpyxl` e só acrescenta a coluna `Classificação` na primeira aba. Ficam todas as abas, fórmulas, estilos, formatos de data e moeda, larguras, painel congelado e filtro. A v1 regravava a planilha pelo pandas e perdia tudo isso, exceto as larguras e o nome da aba.
- A coluna nova copia o estilo do cabeçalho vizinho e entra no filtro do cabeçalho, se houver.
- Rodar sobre um arquivo já classificado atualiza a coluna existente em vez de criar outra.
- Linhas totalmente vazias no meio da planilha não são mais contadas como "sem categoria".

### Senha de app

- **A senha saiu do formulário.** Na v1, ela era digitada num campo do formulário e ficava gravada no notebook quando o Colab salvava o arquivo. Na v2, ela é lida dos *Secrets* do Colab (nome `SENHA_APP`) ou digitada numa caixa que esconde o texto e não é salva.
- Os espaços da senha ("abcd efgh ijkl mnop") são removidos antes do login.
- Sem senha, as planilhas são processadas, mas o e-mail não é enviado, com uma mensagem clara.

### Outros

- As subpastas e os arquivos são processados em ordem alfabética, então o log e o e-mail saem sempre na mesma ordem.

## Versão 1 — entregue à empresa parceira

Busca as planilhas nas subpastas do Google Drive, classifica a coluna `Discriminação` por regras, grava `CLASSIFICADO_<subpasta>_<arquivo>.xlsx` e envia tudo num único e-mail pelo Gmail. Formulário com 4 campos: pasta, e-mail remetente, senha de app e e-mail de destino.
