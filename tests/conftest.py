import ast
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from executar_local import NOTEBOOK, carregar_celula_processamento  # noqa: E402
from exemplos.gerar_exemplos import gerar  # noqa: E402

FUNCOES_DE_REGRA = {"singular", "limpar_texto", "classificar_servico"}


@pytest.fixture(scope="session")
def regras():
    """Extrai do notebook só as regras (funções e listas de termos), sem rodar o resto.

    Assim os testes de regra usam o código que está no notebook entregue,
    e não uma cópia que poderia ficar desatualizada.
    """
    arvore = ast.parse(carregar_celula_processamento(NOTEBOOK))
    nos = []
    for n in arvore.body:
        if isinstance(n, ast.FunctionDef) and n.name in FUNCOES_DE_REGRA:
            nos.append(n)
        elif isinstance(n, ast.Assign) and all(
                isinstance(t, ast.Name) and t.id.startswith("TERMOS_") for t in n.targets):
            nos.append(n)
    nomes = {n.name for n in nos if isinstance(n, ast.FunctionDef)}
    assert nomes == FUNCOES_DE_REGRA, f"Funções de regra não encontradas no notebook: {nomes}"
    ns = {"pd": pd, "unicodedata": unicodedata, "re": re}
    exec(compile(ast.Module(body=nos, type_ignores=[]), "notebook[regras]", "exec"), ns)
    return ns


@pytest.fixture
def pasta_exemplo(tmp_path):
    """Gera as planilhas fictícias de exemplo numa pasta temporária."""
    return gerar(tmp_path / "entrada" / "planilhas_exemplo")
