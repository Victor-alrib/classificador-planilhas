"""Estrutura do notebook e ausência de credenciais."""

import json
import re

from executar_local import NOTEBOOK, NOTEBOOK_V1, celulas_de_codigo


def test_tres_celulas_texto_formulario_processamento():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert [c["cell_type"] for c in nb["cells"]] == ["markdown", "code", "code"]


def test_formulario_tem_tres_campos_e_nenhuma_senha():
    form = celulas_de_codigo()[0]
    campos = re.findall(r"^(\w+)\s*=.*#@param", form, flags=re.M)
    assert campos == ["PASTA_DRIVE", "EMAIL_REMETENTE", "EMAIL_DESTINATARIO"]
    assert "SENHA" not in form.upper()


def test_senha_vem_dos_secrets_ou_da_caixa_de_senha():
    codigo = celulas_de_codigo()[1]
    assert "userdata.get('SENHA_APP')" in codigo
    assert "getpass.getpass(" in codigo
    assert "print(SENHA_APP" not in codigo and "{SENHA_APP}" not in codigo


def test_formulario_so_tem_valores_de_exemplo():
    form = celulas_de_codigo()[0]
    valores = dict(re.findall(r'^(\w+)\s*=\s*"([^"]*)"', form, flags=re.M))
    assert valores["EMAIL_REMETENTE"] == "seuemail@gmail.com"
    assert valores["EMAIL_DESTINATARIO"] == "destinatario@email.com"


def test_notebooks_sem_saidas_salvas():
    for caminho in (NOTEBOOK, NOTEBOOK_V1):
        nb = json.loads(caminho.read_text(encoding="utf-8"))
        assert all(not c.get("outputs") for c in nb["cells"] if c["cell_type"] == "code")


def test_versao_1_preservada_no_historico():
    form_v1 = celulas_de_codigo(NOTEBOOK_V1)[0]
    assert 'SENHA_APP = "xxxx xxxx xxxx xxxx"' in form_v1   # só o valor de exemplo


def test_celulas_compilam():
    for caminho in (NOTEBOOK, NOTEBOOK_V1):
        for i, codigo in enumerate(celulas_de_codigo(caminho)):
            compile(codigo, f"{caminho.name}_celula_{i}", "exec")
