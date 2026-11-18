"""Fluxo completo do notebook rodando localmente: busca, classificação, arquivo e e-mail."""

import shutil

import openpyxl
import pandas as pd
import pytest

from executar_local import NOTEBOOK_V1, executar
from exemplos.gerar_exemplos import COLUNA_FORMULA, COLUNAS, ESPERADO, MUDANCAS_DESDE_V1

ALFA = "CLASSIFICADO_Clinica_Alfa_faturamento_marco.xlsx"


@pytest.fixture
def execucao(pasta_exemplo, tmp_path):
    return executar(pasta_exemplo, tmp_path / "saida",
                    remetente="eu@exemplo.com", destinatario="voce@exemplo.com")


def _classificacoes(caminho, n_linhas):
    ws = openpyxl.load_workbook(caminho).worksheets[0]
    col = [c.value for c in ws[1]].index("Classificação") + 1
    return [ws.cell(row=r, column=col).value or "" for r in range(2, n_linhas + 2)]


def _estilo(celula):
    return tuple(repr(getattr(celula, a)) for a in
                 ("number_format", "font", "fill", "border", "alignment"))


# ---- Busca e classificação ----

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


def test_classificacoes(execucao):
    pasta = execucao.arquivos_gerados[0].parent
    for (sub, arq), linhas in ESPERADO.items():
        obtido = _classificacoes(pasta / f"CLASSIFICADO_{sub}_{arq}", len(linhas))
        assert obtido == [esperado for _, esperado in linhas], sub


# ---- Preservação da planilha ----

def test_dados_e_formulas_originais_intactos(execucao, pasta_exemplo):
    pasta = execucao.arquivos_gerados[0].parent
    for (sub, arq) in ESPERADO:
        original = openpyxl.load_workbook(pasta_exemplo / sub / arq)
        saida = openpyxl.load_workbook(pasta / f"CLASSIFICADO_{sub}_{arq}")
        assert saida.sheetnames == original.sheetnames, sub
        for nome in original.sheetnames:
            a, b = original[nome], saida[nome]
            for linha in a.iter_rows():
                for c in linha:
                    assert b[c.coordinate].value == c.value, (sub, nome, c.coordinate)


def test_classificacao_entra_como_ultima_coluna(execucao):
    pasta = execucao.arquivos_gerados[0].parent
    for (sub, arq) in ESPERADO:
        saida = pd.read_excel(pasta / f"CLASSIFICADO_{sub}_{arq}")
        extra = [COLUNA_FORMULA] if sub == "Clinica_Alfa" else []
        assert list(saida.columns) == COLUNAS + extra + ["Classificação"], sub


def test_formatacao_preservada(execucao, pasta_exemplo):
    original = openpyxl.load_workbook(pasta_exemplo / "Clinica_Alfa" / "faturamento_marco.xlsx")
    saida = openpyxl.load_workbook(execucao.arquivos_gerados[0].parent / ALFA)
    a, b = original.worksheets[0], saida.worksheets[0]
    for linha in a.iter_rows():
        for c in linha:
            assert _estilo(b[c.coordinate]) == _estilo(c), c.coordinate
    for letra, dim in a.column_dimensions.items():
        assert b.column_dimensions[letra].width == dim.width, letra
    assert b.freeze_panes == a.freeze_panes == "A2"
    assert b.title == a.title == "Faturamento"
    assert saida["Resumo"]["B1"].value == original["Resumo"]["B1"].value


def test_coluna_nova_segue_o_estilo_do_cabecalho_e_entra_no_filtro(execucao):
    ws = openpyxl.load_workbook(execucao.arquivos_gerados[0].parent / ALFA).worksheets[0]
    assert ws["G1"].value == "Classificação"
    assert repr(ws["G1"].font) == repr(ws["F1"].font) and ws["G1"].font.b
    assert repr(ws["G1"].fill) == repr(ws["F1"].fill)
    assert ws["G2"].number_format == "General"   # não herda o formato de moeda da vizinha
    assert ws.column_dimensions["G"].width == 16
    assert ws.auto_filter.ref == "A1:G13"


def test_rodar_de_novo_sobre_arquivo_classificado_nao_duplica_coluna(execucao, tmp_path):
    entrada = tmp_path / "segunda" / "pasta"
    (entrada / "Clinica_Alfa").mkdir(parents=True)
    shutil.copy(execucao.arquivos_gerados[0].parent / ALFA, entrada / "Clinica_Alfa" / "faturamento_marco.xlsx")
    r = executar(entrada, tmp_path / "saida2")
    ws = openpyxl.load_workbook(r.arquivos_gerados[0]).worksheets[0]
    cabecalho = [c.value for c in ws[1]]
    assert cabecalho.count("Classificação") == 1 and ws.max_column == 7


def test_linha_totalmente_vazia_nao_conta_como_sem_categoria(tmp_path):
    entrada = tmp_path / "entrada" / "pasta"
    (entrada / "Sub").mkdir(parents=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Discriminação", "Valor"])
    ws.append(["Consulta médica", 100])
    ws.append([None, None])
    ws.append(["Cirurgia", 200])
    wb.save(entrada / "Sub" / "p.xlsx")
    r = executar(entrada, tmp_path / "saida")
    assert r.resumo == ["• Sub/p.xlsx: CONSULTA=1 | PROCEDIMENTO=1 | ANALISAR=0"]
    assert _classificacoes(r.arquivos_gerados[0], 3) == ["CONSULTA", "", "PROCEDIMENTO"]


# ---- Senha e e-mail ----

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
    assert "Consultorio_Gama/notas_marco.xlsx: CONSULTA=4 | PROCEDIMENTO=4 | ANALISAR=1 | SEM CATEGORIA=1" in corpo


def test_senha_dos_secrets_sem_espacos_e_sem_aparecer_no_log(execucao):
    assert execucao.login_senha == "abcdefghijklmnop"
    assert not execucao.senha_pedida_na_tela
    assert "Senha de app lida dos Secrets" in execucao.log
    assert "abcd" not in execucao.log


def test_sem_secret_a_senha_e_pedida_na_tela(pasta_exemplo, tmp_path):
    r = executar(pasta_exemplo, tmp_path / "saida", senha_via="digitada")
    assert r.senha_pedida_na_tela
    assert r.login_senha == "abcdefghijklmnop"
    assert r.mensagem is not None


def test_sem_senha_nao_envia_mas_gera_os_arquivos(pasta_exemplo, tmp_path):
    r = executar(pasta_exemplo, tmp_path / "saida", senha_via="nenhuma")
    assert len(r.arquivos_gerados) == 3
    assert r.mensagem is None and r.login_usuario is None
    assert "Senha de app não informada" in r.log


def test_senha_recusada_nao_derruba_o_processo(pasta_exemplo, tmp_path):
    r = executar(pasta_exemplo, tmp_path / "saida", falhar_login_smtp=True)
    assert len(r.arquivos_gerados) == 3
    assert r.mensagem is None
    assert "Erro ao enviar e-mail" in r.log
    assert "CONCLUÍDO: 3/3" in r.log


def test_pasta_inexistente_encerra_sem_pedir_senha(tmp_path):
    r = executar(tmp_path / "nao_existe", tmp_path / "saida", senha_via="digitada")
    assert r.encerrou_antes and r.mensagem is None and not r.senha_pedida_na_tela
    assert "não encontrada no Drive" in r.log


def test_pasta_sem_planilhas_validas_encerra_sem_enviar(tmp_path):
    vazia = tmp_path / "entrada" / "vazia"
    (vazia / "sub").mkdir(parents=True)
    (vazia / "sub" / "doc.pdf").write_bytes(b"%PDF-1.4")
    r = executar(vazia, tmp_path / "saida")
    assert r.encerrou_antes and r.mensagem is None
    assert "Nenhuma planilha válida" in r.log


# ---- Comparação com a versão 1 ----

def test_v2_so_muda_as_linhas_corrigidas(pasta_exemplo, tmp_path):
    """Roda a versão 1 (a primeira entregue) e a 2 nos mesmos arquivos.

    Só as linhas listadas em MUDANCAS_DESDE_V1 podem mudar de classificação.
    """
    v1 = executar(pasta_exemplo, tmp_path / "v1", notebook=NOTEBOOK_V1)
    v2 = executar(pasta_exemplo, tmp_path / "v2")
    mudancas = {}
    for (sub, arq), linhas in ESPERADO.items():
        nome = f"CLASSIFICADO_{sub}_{arq}"
        c1 = pd.read_excel(tmp_path / "v1" / nome)["Classificação"].fillna("").tolist()
        c2 = _classificacoes(tmp_path / "v2" / nome, len(linhas))
        for (texto, _), a, b in zip(linhas, c1, c2):
            if a != b:
                mudancas[texto] = a
    assert mudancas == MUDANCAS_DESDE_V1
    assert len(v1.arquivos_gerados) == len(v2.arquivos_gerados) == 3
