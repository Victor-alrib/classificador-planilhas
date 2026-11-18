"""Estrutura do notebook entregue e ausência de credenciais reais."""

import json
import re

from executar_local import NOTEBOOK, celulas_de_codigo


def test_tres_celulas_texto_formulario_processamento():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert [c["cell_type"] for c in nb["cells"]] == ["markdown", "code", "code"]


def test_formulario_tem_os_quatro_campos():
    form = celulas_de_codigo()[0]
    campos = re.findall(r"^(\w+)\s*=.*#@param", form, flags=re.M)
    assert campos == ["PASTA_DRIVE", "EMAIL_REMETENTE", "SENHA_APP", "EMAIL_DESTINATARIO"]


def test_formulario_so_tem_valores_de_exemplo():
    form = celulas_de_codigo()[0]
    valores = dict(re.findall(r'^(\w+)\s*=\s*"([^"]*)"', form, flags=re.M))
    assert valores["SENHA_APP"] == "xxxx xxxx xxxx xxxx"
    assert valores["EMAIL_REMETENTE"] == "seuemail@gmail.com"
    assert valores["EMAIL_DESTINATARIO"] == "destinatario@email.com"


def test_notebook_sem_saidas_salvas():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert all(not c.get("outputs") for c in nb["cells"] if c["cell_type"] == "code")


def test_celulas_compilam():
    for i, codigo in enumerate(celulas_de_codigo()):
        compile(codigo, f"celula_{i}", "exec")
