"""Regras de classificação, testadas direto sobre as funções do notebook."""

import math

import pytest


@pytest.mark.parametrize("texto, esperado", [
    # CONSULTA
    ("Consulta médica", "CONSULTA"),
    ("Consultas médicas do mês", "CONSULTA"),
    ("Consultas médicas realizadas em coordenação", "CONSULTA"),
    ("Prestação de serviços médicos", "CONSULTA"),
    ("Folha médica", "CONSULTA"),
    # PROCEDIMENTO
    ("Procedimentos médicos", "PROCEDIMENTO"),
    ("Cirurgia", "PROCEDIMENTO"),
    ("Exame diagnóstico", "PROCEDIMENTO"),
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
    "CONSULTA MÉDICA",
    "consulta medica",
    "Consulta Médica",
    "CONSULTA MEDICA",
])
def test_ignora_maiusculas_e_acentos(regras, texto):
    assert regras["classificar_servico"](texto) == "CONSULTA"


def test_erro_de_digitacao_previsto_na_lista(regras):
    assert regras["classificar_servico"]("PRESTACAO DED SERVICOS") == "CONSULTA"


@pytest.mark.parametrize("valor", [None, math.nan, "", "Reembolso de despesas", 12345])
def test_sem_correspondencia_fica_vazio(regras, valor):
    assert regras["classificar_servico"](valor) == ""


def test_nunca_cria_categoria_fora_das_regras(regras, pasta_exemplo):
    from exemplos.gerar_exemplos import ESPERADO
    textos = [t for linhas in ESPERADO.values() for t, _ in linhas]
    assert {regras["classificar_servico"](t) for t in textos} <= {"CONSULTA", "PROCEDIMENTO", "ANALISAR", ""}


def test_limpar_texto(regras):
    assert regras["limpar_texto"]("Prestação de SERVIÇOS") == "prestacao de servicos"
    assert regras["limpar_texto"](None) == ""


# ---- Limitações conhecidas do código entregue (documentadas no README) ----

@pytest.mark.xfail(strict=True, reason="A lista tem 'exame diagnostico' (singular); "
                   "o plural 'exames diagnósticos', citado na regra, não é reconhecido.")
def test_plural_exames_diagnosticos(regras):
    assert regras["classificar_servico"]("Exames diagnósticos") == "PROCEDIMENTO"


@pytest.mark.xfail(strict=True, reason="Espaços repetidos e quebras de linha não são normalizados.")
@pytest.mark.parametrize("texto", ["Consulta  médica", "Consulta\nmédica"])
def test_espacos_extras(regras, texto):
    assert regras["classificar_servico"](texto) == "CONSULTA"


def test_coordenacao_sozinha_vira_consulta(regras):
    """Comportamento atual: o termo 'coordenacao' isolado basta para CONSULTA.

    A regra fala em 'consultas médicas realizadas em coordenação'; o código é mais amplo.
    Este teste trava o comportamento para que qualquer mudança seja consciente.
    """
    assert regras["classificar_servico"]("Coordenação administrativa") == "CONSULTA"
