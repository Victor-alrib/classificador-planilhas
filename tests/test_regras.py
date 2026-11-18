"""Regras de classificação, testadas direto sobre o código do notebook."""

import math

import pytest


@pytest.mark.parametrize("texto, esperado", [
    # CONSULTA
    ("Consulta médica", "CONSULTA"),
    ("Consultas médicas do mês", "CONSULTA"),
    ("Consultas médicas realizadas em coordenação", "CONSULTA"),
    ("Atividades realizadas em coordenação com a clínica", "CONSULTA"),
    ("Prestação de serviços médicos", "CONSULTA"),
    ("Serviços médicos prestados", "CONSULTA"),
    ("Folha médica", "CONSULTA"),
    # PROCEDIMENTO
    ("Procedimentos médicos", "PROCEDIMENTO"),
    ("Cirurgia", "PROCEDIMENTO"),
    ("Exame diagnóstico", "PROCEDIMENTO"),
    ("Exames diagnósticos", "PROCEDIMENTO"),
    ("Serviços hospitalares", "PROCEDIMENTO"),
    ("Ambulatório", "PROCEDIMENTO"),
    ("Hospital", "PROCEDIMENTO"),
    ("Produção", "PROCEDIMENTO"),
    # ANALISAR
    ("Atendimentos do mês", "ANALISAR"),
    ("Atendimento", "ANALISAR"),
    ("Consulta médica e cirurgia", "ANALISAR"),
])
def test_termos_da_especificacao(regras, texto, esperado):
    assert regras["classificar_servico"](texto) == esperado


def test_prioridade_analisar_vence_as_outras(regras):
    c = regras["classificar_servico"]
    assert c("Atendimento - consulta médica") == "ANALISAR"
    assert c("Atendimento - cirurgia") == "ANALISAR"
    assert c("Folha médica de produção hospitalar") == "ANALISAR"


@pytest.mark.parametrize("texto", [
    "CONSULTA MÉDICA", "consulta medica", "Consulta Médica", "CONSULTA MEDICA",
])
def test_ignora_maiusculas_e_acentos(regras, texto):
    assert regras["classificar_servico"](texto) == "CONSULTA"


def test_erro_de_digitacao_previsto_na_lista(regras):
    assert regras["classificar_servico"]("PRESTACAO DED SERVICOS") == "CONSULTA"


@pytest.mark.parametrize("valor", [None, math.nan, "", "   ", "Reembolso de despesas", 12345])
def test_sem_correspondencia_fica_vazio(regras, valor):
    assert regras["classificar_servico"](valor) == ""


def test_nunca_cria_categoria_fora_das_regras(regras):
    from exemplos.gerar_exemplos import ESPERADO
    textos = [t for linhas in ESPERADO.values() for t, _ in linhas]
    assert {regras["classificar_servico"](t) for t in textos} <= {"CONSULTA", "PROCEDIMENTO", "ANALISAR", ""}


# ---- Correções da versão 2 ----

@pytest.mark.parametrize("texto, esperado", [
    ("Exames diagnósticos laboratoriais", "PROCEDIMENTO"),
    ("Hospitais conveniados", "PROCEDIMENTO"),
    ("Cirurgias eletivas", "PROCEDIMENTO"),
    ("Produções de fevereiro", "PROCEDIMENTO"),
    ("Exames diagnósticos; consultas médicas", "ANALISAR"),
])
def test_plural(regras, texto, esperado):
    assert regras["classificar_servico"](texto) == esperado


@pytest.mark.parametrize("texto", [
    "Consulta  médica",       # espaço duplo
    "Consulta\nmédica",       # quebra de linha dentro da célula
    "Consulta\tmédica",       # tabulação
    "Consulta médica",   # espaço não separável (comum ao copiar de sistemas)
    "Consulta-médica",        # hífen
    "Consulta médica.",       # pontuação no fim
    "  Consulta médica  ",    # espaços nas pontas
])
def test_espacos_e_pontuacao(regras, texto):
    assert regras["classificar_servico"](texto) == "CONSULTA"


@pytest.mark.parametrize("texto", [
    "Coordenação administrativa do escritório",
    "Coordenação de equipe médica",
    "Coordenação",
])
def test_coordenacao_sozinha_nao_e_consulta(regras, texto):
    """A regra fala em 'realizadas em coordenação'; a palavra sozinha não basta."""
    assert regras["classificar_servico"](texto) == ""


@pytest.mark.parametrize("plural, singular", [
    ("consultas", "consulta"), ("exames", "exame"), ("diagnosticos", "diagnostico"),
    ("hospitalares", "hospitalar"), ("producoes", "producao"), ("hospitais", "hospital"),
    ("atendimentos", "atendimento"), ("servicos", "servico"), ("itens", "item"),
    ("consulta", "consulta"), ("mes", "mes"),
])
def test_singular(regras, plural, singular):
    assert regras["singular"](plural) == singular


def test_limpar_texto(regras):
    assert regras["limpar_texto"]("Prestação de SERVIÇOS") == "prestacao de servico"
    assert regras["limpar_texto"]("Exames\n diagnósticos;") == "exame diagnostico"
    assert regras["limpar_texto"](None) == ""


def test_termos_passam_pela_mesma_limpeza_do_texto(regras):
    for nome in ("CONSULTA", "PROCEDIMENTO", "ANALISAR"):
        termos, limpos = regras[f"TERMOS_{nome}"], regras[f"TERMOS_{nome}_LIMPOS"]
        assert limpos == [regras["limpar_texto"](t) for t in termos]
        assert all(limpos), f"termo vazio em TERMOS_{nome}"


def test_termo_amplo_mantido_procedimento(regras):
    """Comportamento mantido da versão 1: 'procedimento' sozinho já é PROCEDIMENTO.

    A regra fala em 'procedimentos médicos'; o termo foi mantido amplo de propósito.
    Este teste trava o comportamento para que qualquer mudança seja consciente.
    """
    assert regras["classificar_servico"]("Procedimentos ambulatoriais") == "PROCEDIMENTO"
