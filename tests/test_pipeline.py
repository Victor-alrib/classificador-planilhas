"""Fluxo completo do notebook rodando localmente: busca, classificação, arquivo e e-mail."""

import openpyxl
import pandas as pd
import pytest

from executar_local import executar
from exemplos.gerar_exemplos import COLUNAS, ESPERADO, LARGURAS


@pytest.fixture
def execucao(pasta_exemplo, tmp_path):
    return executar(pasta_exemplo, tmp_path / "saida",
                    remetente="eu@exemplo.com", destinatario="voce@exemplo.com")


def test_processa_so_as_planilhas_validas(execucao):
    nomes = sorted(p.name for p in execucao.arquivos_gerados)
    assert nomes == [
        "CLASSIFICADO_Clinica_Alfa_faturamento_marco.xlsx",
        "CLASSIFICADO_Clinica_Beta_faturamento_marco.xlsx",
        "CLASSIFICADO_Consultorio_Gama_notas_marco.xlsx",
    ]
    assert execucao.erros == []
    assert not execucao.encerrou_antes


def test_ignora_o_que_nao_e_planilha_valida(execucao):
    log = execucao.log
    for ignorado in ["observacoes.txt", "nota_fiscal_exemplo.pdf", "2025 (ignorado)"]:
        assert ignorado in log
    assert "controle_interno.xlsx (sem coluna 'Discriminação'" in log
    assert "arquivo_corrompido.xlsx (não foi possível ler" in log
    assert "leia_antes.txt" not in log            # arquivo solto na raiz nem é listado
    assert "faturamento_antigo.xlsx" not in log   # subpasta aninhada não é visitada


def test_mesmo_nome_em_subpastas_diferentes_nao_colide(execucao):
    nomes = [p.name for p in execucao.arquivos_gerados]
    assert len(nomes) == len(set(nomes)) == 3


def test_classificacoes_e_dados_originais(execucao, pasta_exemplo):
    for (sub, arq), linhas in ESPERADO.items():
        saida = pd.read_excel(execucao.arquivos_gerados[0].parent / f"CLASSIFICADO_{sub}_{arq}")
        original = pd.read_excel(pasta_exemplo / sub / arq)
        # Colunas originais intactas, na mesma ordem; "Classificação" entra no fim
        assert list(saida.columns) == COLUNAS + ["Classificação"]
        pd.testing.assert_frame_equal(saida[COLUNAS], original[COLUNAS])
        obtido = saida["Classificação"].fillna("").tolist()
        assert obtido == [esperado for _, esperado in linhas], sub


def test_preserva_nome_da_aba_e_larguras(execucao):
    for caminho in execucao.arquivos_gerados:
        ws = openpyxl.load_workbook(caminho).active
        assert ws.title == "Faturamento"
        for letra, largura in LARGURAS.items():
            assert ws.column_dimensions[letra].width == largura


def test_limitacao_formatacao_e_outras_abas_nao_sao_preservadas(execucao, pasta_exemplo):
    """Documenta o comportamento atual: o arquivo é regravado pelo pandas.

    Ficam: dados, ordem das colunas, nome da aba e larguras.
    Perdem-se: outras abas, estilo do cabeçalho, painel congelado e formatos de número/data.
    """
    original = openpyxl.load_workbook(pasta_exemplo / "Clinica_Alfa" / "faturamento_marco.xlsx")
    saida = openpyxl.load_workbook(
        execucao.arquivos_gerados[0].parent / "CLASSIFICADO_Clinica_Alfa_faturamento_marco.xlsx")
    assert original.sheetnames == ["Faturamento", "Resumo"]
    assert saida.sheetnames == ["Faturamento"]
    assert original.active["A1"].font.b and not saida.active["A1"].font.b
    assert original.active.freeze_panes == "A2" and saida.active.freeze_panes is None
    assert original.active["E2"].number_format != saida.active["E2"].number_format


def test_email_com_todos_os_anexos_e_resumo(execucao):
    msg = execucao.mensagem
    assert msg is not None
    assert execucao.servidor_smtp == ("smtp.gmail.com", 465)
    assert execucao.login_usuario == "eu@exemplo.com"
    assert msg["From"] == "eu@exemplo.com" and msg["To"] == "voce@exemplo.com"
    assert "3 arquivo(s)" in msg["Subject"] and "planilhas_exemplo" in msg["Subject"]
    anexos = [p.get_filename() for p in msg.iter_attachments()]
    assert sorted(anexos) == sorted(p.name for p in execucao.arquivos_gerados)
    corpo = msg.get_body().get_content()
    assert "Clinica_Alfa/faturamento_marco.xlsx: CONSULTA=5 | PROCEDIMENTO=3 | ANALISAR=2" in corpo
    assert "SEM CATEGORIA=2" in corpo


def test_pasta_inexistente_encerra_sem_enviar(tmp_path):
    r = executar(tmp_path / "nao_existe", tmp_path / "saida")
    assert r.encerrou_antes and r.mensagem is None
    assert "não encontrada no Drive" in r.log


def test_pasta_sem_planilhas_validas_encerra_sem_enviar(tmp_path):
    vazia = tmp_path / "entrada" / "vazia"
    (vazia / "sub").mkdir(parents=True)
    (vazia / "sub" / "doc.pdf").write_bytes(b"%PDF-1.4")
    r = executar(vazia, tmp_path / "saida")
    assert r.encerrou_antes and r.mensagem is None
    assert "Nenhuma planilha válida" in r.log


def test_senha_recusada_nao_derruba_o_processo(pasta_exemplo, tmp_path):
    r = executar(pasta_exemplo, tmp_path / "saida", falhar_login_smtp=True)
    assert len(r.arquivos_gerados) == 3
    assert r.mensagem is None
    assert "Erro ao enviar e-mail" in r.log
    assert "CONCLUÍDO: 3/3" in r.log
