# Manual de uso

Guia para quem vai **usar** o classificador sem conhecimento de programação. É a versão em texto do manual entregue à empresa parceira (versão 2 do programa).

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

## 3. Guardar a senha no Colab (opcional, uma vez só)

Assim você não precisa digitar a senha toda vez. Se pular este passo, o programa pede a senha a cada execução.

1. Com o programa aberto no Colab, clique no **ícone de chave** na barra da esquerda (*Secrets*).
2. Clique em **Adicionar novo secret**.
3. Em **Nome**, escreva exatamente `SENHA_APP`. Em **Valor**, cole a senha de app.
4. Ligue a chave **Acesso ao notebook**.

A senha fica guardada só na sua conta Google; ela não aparece no notebook nem vai junto se você compartilhar o arquivo.

## 4. Organizar as planilhas no Drive (todo mês)

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
- A planilha precisa ter uma coluna chamada exatamente **Discriminação**, na primeira linha da primeira aba.
- PDFs, documentos e outras planilhas podem ficar nas mesmas pastas: o programa ignora o que não for de interesse.

## 5. Rodar o programa (todo mês)

1. Abra o programa no Colab.
2. Preencha os 3 campos:

| Campo | O que colocar |
|---|---|
| `PASTA_DRIVE` | Nome da pasta principal, escrito exatamente como no Drive |
| `EMAIL_REMETENTE` | O seu Gmail |
| `EMAIL_DESTINATARIO` | Quem vai receber as planilhas classificadas |

3. Clique no **▶** da célula de configurações e depois no **▶** da célula de processamento.
4. Na primeira execução de cada sessão, o Google pede permissão para acessar o Drive: escolha sua conta e marque **"Ver, editar, criar e excluir todos os seus arquivos do Google Drive"**.
5. Se você guardou a senha no passo 3, o Colab pode perguntar se o notebook pode usá-la: clique em **Conceder acesso**. Se não guardou, aparece uma caixa pedindo a senha de app: cole a senha e tecle **Enter**. O que você digita não aparece na tela.
6. Acompanhe o progresso na tela. Ao aparecer **"E-mail enviado!"**, o processo terminou.

O e-mail chega com todas as planilhas anexadas, cada uma com a coluna **Classificação** no final e a formatação original mantida, e um resumo por arquivo. Linhas marcadas como **ANALISAR** e linhas **sem categoria** precisam de conferência manual.

## Problemas comuns

| Situação | O que fazer |
|---|---|
| "Pasta não encontrada" | Confira se o nome em `PASTA_DRIVE` está igual ao do Drive, com maiúsculas e minúsculas |
| "Senha de app não informada" | A caixa de senha foi deixada em branco. Rode a célula de processamento de novo e cole a senha |
| "Erro ao enviar e-mail" | Confira a senha de app e o e-mail remetente. Se a senha estiver nos *Secrets*, confira se o nome é exatamente `SENHA_APP` |
| "Nenhuma planilha válida encontrada" | Verifique se as planilhas estão dentro de subpastas e se a coluna se chama exatamente `Discriminação` |
| Erro "credential propagation was unsuccessful" | Permita pop-ups para o site do Colab, use uma única conta Google no navegador e rode de novo |
| "Abrir com Colab" não aparece | Abrir com → Conectar mais aplicativos → instale o Colaboratory |
| O programa ficou parado | Veja se há uma caixa de senha ou um pedido de acesso esperando resposta; se não houver, aguarde alguns minutos e, se nada mudar, reabra o notebook e rode de novo |
