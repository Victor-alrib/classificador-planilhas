"""Executa o código do notebook fora do Google Colab.

O notebook `notebook/classificador_planilhas.ipynb` é a versão entregue à empresa
parceira. Ele foi escrito para o Colab: lê as planilhas do Google Drive e envia o
resultado pelo Gmail. Este módulo roda **exatamente o mesmo código** da célula de
processamento e troca só os três pontos de contato com o mundo externo:

- o Google Drive montado em `/content/drive/MyDrive` vira uma pasta local;
- a pasta temporária `/content`, onde o notebook grava os arquivos classificados,
  vira outra pasta local;
- o envio por SMTP é substituído por um objeto que guarda a mensagem (e,
  opcionalmente, a grava num arquivo `.eml`, que abre em qualquer cliente de e-mail).

Assim, os testes e a demonstração exercitam o código real do notebook, sem
credenciais e sem dados reais. Se alguém mudar o notebook de um jeito que quebre
essa substituição, `carregar_celula_processamento` falha com uma mensagem clara.

Uso:
    python executar_local.py                       # roda sobre exemplos/planilhas_exemplo
    python executar_local.py --entrada MINHA_PASTA --saida SAIDA
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import smtplib
import sys
import types
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent
NOTEBOOK = RAIZ / "notebook" / "classificador_planilhas.ipynb"
EXEMPLOS = RAIZ / "exemplos" / "planilhas_exemplo"

# Caminhos do Colab usados pelo notebook
_DRIVE_COLAB = "/content/drive/MyDrive/"
_TEMP_COLAB = "/content/"


def celulas_de_codigo(caminho: Path = NOTEBOOK) -> list[str]:
    """Devolve o código-fonte de cada célula de código do notebook, em ordem."""
    nb = json.loads(caminho.read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def carregar_celula_processamento(caminho: Path = NOTEBOOK) -> str:
    """Devolve o código da célula de processamento (a que monta o Drive)."""
    candidatas = [c for c in celulas_de_codigo(caminho) if "drive.mount(" in c]
    if len(candidatas) != 1:
        raise RuntimeError(
            f"Esperava 1 célula com drive.mount(), encontrei {len(candidatas)}."
        )
    return candidatas[0]


def _adaptar_caminhos(codigo: str, raiz_drive: Path, pasta_temp: Path) -> str:
    """Troca os caminhos do Colab por pastas locais e confere que a troca foi completa."""
    if codigo.count(_DRIVE_COLAB) != 1:
        raise RuntimeError(f"O notebook mudou: esperava 1 ocorrência de {_DRIVE_COLAB!r}.")
    codigo = codigo.replace(_DRIVE_COLAB, raiz_drive.as_posix().rstrip("/") + "/")
    # Restam dois usos de /content/: o argumento de drive.mount() (ignorado aqui)
    # e a pasta onde os arquivos classificados são gravados.
    if codigo.count(_TEMP_COLAB) != 2:
        raise RuntimeError(f"O notebook mudou: esperava 2 ocorrências de {_TEMP_COLAB!r}.")
    return codigo.replace(_TEMP_COLAB, pasta_temp.as_posix().rstrip("/") + "/")


@dataclass
class _SMTPFalso:
    """Imita smtplib.SMTP_SSL: registra o login e guarda a mensagem em vez de enviar."""

    host: str
    port: int
    registro: "Execucao"
    falhar_login: bool = False

    def __enter__(self):
        self.registro.servidor_smtp = (self.host, self.port)
        return self

    def __exit__(self, *exc):
        return False

    def login(self, usuario: str, senha: str) -> None:
        self.registro.login_usuario = usuario
        if self.falhar_login:
            raise smtplib.SMTPAuthenticationError(535, b"Senha de app recusada (simulado)")

    def send_message(self, msg: EmailMessage) -> None:
        self.registro.mensagem = msg


@dataclass
class Execucao:
    """O que aconteceu numa execução do notebook."""

    log: str = ""
    encerrou_antes: bool = False  # o notebook parou com SystemExit (pasta inválida, nada a processar)
    arquivos_gerados: list[Path] = field(default_factory=list)
    resumo: list[str] = field(default_factory=list)
    erros: list[str] = field(default_factory=list)
    mensagem: EmailMessage | None = None
    login_usuario: str | None = None
    servidor_smtp: tuple[str, int] | None = None
    pontos_de_montagem: list[str] = field(default_factory=list)


def executar(
    pasta_planilhas: Path,
    pasta_saida: Path,
    *,
    remetente: str = "remetente@exemplo.com",
    destinatario: str = "destinatario@exemplo.com",
    senha_app: str = "senha-ficticia",
    falhar_login_smtp: bool = False,
    notebook: Path = NOTEBOOK,
    mostrar_log: bool = False,
) -> Execucao:
    """Roda a célula de processamento do notebook sobre `pasta_planilhas`.

    `pasta_planilhas` faz o papel da pasta escolhida no campo PASTA_DRIVE do
    formulário; a pasta-mãe dela faz o papel de "Meu Drive".
    """
    pasta_planilhas = Path(pasta_planilhas).resolve()
    pasta_saida = Path(pasta_saida).resolve()
    pasta_saida.mkdir(parents=True, exist_ok=True)

    registro = Execucao()
    codigo = _adaptar_caminhos(
        carregar_celula_processamento(notebook), pasta_planilhas.parent, pasta_saida
    )

    # Módulo google.colab falso: só o drive.mount() é usado pelo notebook.
    drive = types.SimpleNamespace(
        mount=lambda caminho, force_remount=False: registro.pontos_de_montagem.append(caminho)
    )
    colab = types.ModuleType("google.colab")
    colab.drive = drive
    google = types.ModuleType("google")
    google.colab = colab

    # Valores que, no Colab, vêm do formulário (célula 2).
    ns: dict = {
        "__name__": "__notebook__",
        "PASTA_DRIVE": pasta_planilhas.name,
        "EMAIL_REMETENTE": remetente,
        "SENHA_APP": senha_app,
        "EMAIL_DESTINATARIO": destinatario,
    }

    saida = io.StringIO()
    fabrica_smtp = lambda host, port: _SMTPFalso(host, port, registro, falhar_login_smtp)  # noqa: E731
    with mock.patch.dict(sys.modules, {"google": google, "google.colab": colab}), \
            mock.patch.object(smtplib, "SMTP_SSL", fabrica_smtp), \
            contextlib.redirect_stdout(saida):
        try:
            exec(compile(codigo, f"{notebook.name}[processamento]", "exec"), ns)
        except SystemExit:
            registro.encerrou_antes = True

    registro.log = saida.getvalue()
    registro.arquivos_gerados = [Path(p) for p in ns.get("arquivos_gerados", [])]
    registro.resumo = list(ns.get("resumo_geral", []))
    registro.erros = list(ns.get("erros", []))
    if mostrar_log:
        print(registro.log, end="")
    return registro


def main(argv: list[str] | None = None) -> int:
    # Repositório publicado: resultados/ fica ao lado deste arquivo.
    # Pasta de trabalho (codigo/ + resultados/): fica um nível acima.
    resultados_padrao = (
        RAIZ / "resultados" if (RAIZ / "resultados").is_dir() else RAIZ.parent / "resultados"
    )
    p = argparse.ArgumentParser(description="Roda o classificador do notebook localmente.")
    p.add_argument("--entrada", type=Path, default=EXEMPLOS,
                   help="Pasta com as subpastas de planilhas (padrão: exemplos sintéticos).")
    p.add_argument("--saida", type=Path, default=resultados_padrao / "saida_demo",
                   help="Pasta onde gravar as planilhas classificadas.")
    p.add_argument("--eml", type=Path, default=None,
                   help="Arquivo .eml onde gravar o e-mail que seria enviado.")
    args = p.parse_args(argv)

    if not args.entrada.is_dir():
        print(f"Pasta de entrada não encontrada: {args.entrada}", file=sys.stderr)
        if args.entrada == EXEMPLOS:
            print("Gere os exemplos antes:  python exemplos/gerar_exemplos.py", file=sys.stderr)
        return 1

    r = executar(args.entrada, args.saida, mostrar_log=True)
    eml = args.eml or args.saida.parent / "email_demo.eml"
    if r.mensagem is not None:
        eml.write_bytes(r.mensagem.as_bytes())
        try:
            mostrado = os.path.relpath(eml)
        except ValueError:  # Windows: outra unidade de disco
            mostrado = str(eml)
        print(f"\n[local] E-mail NÃO foi enviado; a mensagem foi gravada em: {mostrado}")
    return 0 if r.arquivos_gerados else 1


if __name__ == "__main__":
    raise SystemExit(main())
