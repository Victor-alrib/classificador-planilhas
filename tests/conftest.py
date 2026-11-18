import ast
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from executar_local import NOTEBOOK, carregar_celula_processamento  # noqa: E402
from exemplos.gerar_exemplos import gerar  # noqa: E402


@pytest.fixture(scope="session")
def regras():
    """Extrai do notebook só as funções de classificação, sem rodar o resto da célula.

    Assim os testes de regra usam o código que está no notebook entregue,
    e não uma cópia que poderia ficar desatualizada.
    """
    arvore = ast.parse(carregar_celula_processamento(NOTEBOOK))
    funcoes = [n for n in arvore.body
               if isinstance(n, ast.FunctionDef) and n.name in {"limpar_texto", "classificar_servico"}]
    assert len(funcoes) == 2, "Funções de classificação não encontradas no notebook"
    ns = {"pd": pd, "unicodedata": unicodedata}
    exec(compile(ast.Module(body=funcoes, type_ignores=[]), "notebook[regras]", "exec"), ns)
    return ns


@pytest.fixture
def pasta_exemplo(tmp_path):
    """Gera as planilhas fictícias de exemplo numa pasta temporária."""
    return gerar(tmp_path / "entrada" / "planilhas_exemplo")
