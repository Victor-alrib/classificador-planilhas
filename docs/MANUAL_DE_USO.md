# Manual de uso

Guia para quem vai **usar** o classificador sem conhecimento de programação. É a versão em texto do manual entregue à empresa parceira.

## 1. Instalar o programa na sua conta (uma vez só)

O programa é um arquivo `.ipynb` (um *notebook*). Ele fica salvo no seu Google Drive e é aberto pelo Google Colab, uma ferramenta gratuita do Google que funciona no navegador.

### Salvar o arquivo no Drive

1. Baixe o arquivo `classificador_planilhas.ipynb` recebido por e-mail.
2. Acesse `drive.google.com` e entre com a sua conta.
3. Clique em **Novo → Upload de arquivo** e escolha o arquivo baixado.

### Abrir com o Google Colab

1. No Drive, clique com o botão direito no arquivo `.ipynb`.
2. Escolha **Abrir com → Google Colaboratory**.

Se "Google Colaboratory" não aparecer: **Abrir com → Conectar mais aplicativos**, pesquise **Colaboratory**, clique em **Instalar** e repita o passo acima. É um aplicativo oficial do Google e gratuito.

Dica: depois de aberto, salve o endereço da página nos favoritos do navegador.

## 2. Criar a senha de app do Gmail (uma vez só)

O programa precisa de uma senha especial para enviar e-mails. Ela é diferente da sua senha normal.

1. Acesse `myaccount.google.com/security`.
2. Ative a **Verificação em duas etapas**, se ainda não estiver ativa.
3. No campo de busca da página, procure **Senhas de app**.
4. Crie uma senha com o nome `Classificador`.
5. Copie a senha de 16 letras que aparecer. Ela é mostrada uma única vez.

Não compartilhe essa senha: ela permite enviar e-mails pela sua conta.

## 3. Organizar as planilhas no Drive (todo mês)

```
FATURAMENTO              ← pasta principal (o nome você escolhe)
├── Clínica A
│   └── planilha.xlsx
├── Clínica B
│   └── planilha.xlsx
└── ...
```

- Cada planilha deve estar **dentro de uma subpasta**; arquivos soltos na pasta principal são ignorados.
- Subpastas dentro de subpastas não são verificadas.
- A planilha precisa ter uma coluna chamada exatamente **Discriminação**, na primeira linha.
- PDFs, documentos e outras planilhas podem ficar nas mesmas pastas: o programa ignora o que não for de interesse.

## 4. Rodar o programa (todo mês)

1. Abra o programa no Colab.
2. Preencha os 4 campos:

| Campo | O que colocar |
|---|---|
| `PASTA_DRIVE` | Nome da pasta principal, escrito exatamente como no Drive |
| `EMAIL_REMETENTE` | O seu Gmail |
| `SENHA_APP` | A senha de 16 letras criada no passo 2 |
| `EMAIL_DESTINATARIO` | Quem vai receber as planilhas classificadas |

3. Clique no **▶** da célula de configurações e depois no **▶** da célula de processamento.
4. Na primeira execução de cada sessão, o Google pede permissão para acessar o Drive: escolha sua conta e marque **"Ver, editar, criar e excluir todos os seus arquivos do Google Drive"**.
5. Acompanhe o progresso na tela. Ao aparecer **"E-mail enviado!"**, o processo terminou.

O e-mail chega com todas as planilhas anexadas, cada uma com a coluna **Classificação** no final, e um resumo por arquivo. Linhas marcadas como **ANALISAR** e linhas **sem categoria** precisam de conferência manual.

## Problemas comuns

| Situação | O que fazer |
|---|---|
| "Pasta não encontrada" | Confira se o nome em `PASTA_DRIVE` está igual ao do Drive, com maiúsculas e minúsculas |
| "Erro ao enviar e-mail" | Confira a senha de app (sem espaços a mais) e o e-mail remetente |
| "Nenhuma planilha válida encontrada" | Verifique se as planilhas estão dentro de subpastas e se a coluna se chama exatamente `Discriminação` |
| Erro "credential propagation was unsuccessful" | Permita pop-ups para o site do Colab, use uma única conta Google no navegador e rode de novo |
| "Abrir com Colab" não aparece | Abrir com → Conectar mais aplicativos → instale o Colaboratory |
| O programa ficou parado | Aguarde alguns minutos; se nada mudar, reabra o notebook e rode de novo |
