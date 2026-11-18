"""Gera a pasta de planilhas de exemplo (100% fictícias) usada na demonstração e nos testes.

Nenhum dado aqui veio da empresa parceira. Os textos da coluna "Discriminação"
foram escritos à mão para cobrir:
- os casos previstos nas regras (CONSULTA, PROCEDIMENTO, ANALISAR);
- variações que a normalização precisa tolerar (maiúsculas, acentos, erro de digitação);
- casos de borda e limitações conhecidas (plural fora da lista, espaço duplo, termo amplo demais);
- arquivos que devem ser ignorados (PDF, TXT, planilha sem a coluna, arquivo corrompido,
  subpasta aninhada e arquivo solto na raiz).

Uso:
    python exemplos/gerar_exemplos.py            # recria exemplos/planilhas_exemplo
    python exemplos/gerar_exemplos.py DESTINO    # gera em outra pasta
"""

from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

PASTA_PADRAO = Path(__file__).resolve().parent / "planilhas_exemplo"

COLUNAS = ["Data", "Nº NF", "Tomador", "Discriminação", "Valor (R$)"]
LARGURAS = {"A": 12, "B": 9, "C": 30, "D": 52, "E": 14}

# (texto da Discriminação, classificação esperada pelo código atual)
# None = célula vazia
CLINICA_ALFA = [
    ("Consulta médica realizada em 03/03", "CONSULTA"),
    ("CONSULTAS MÉDICAS - COMPETÊNCIA MARÇO", "CONSULTA"),
    ("Prestação de serviços médicos em coordenação", "CONSULTA"),
    ("PRESTACAO DED SERVICOS MEDICOS", "CONSULTA"),          # erro de digitação já previsto na lista
    ("Folha médica referente a março", "CONSULTA"),
    ("Cirurgia de catarata", "PROCEDIMENTO"),
    ("Procedimentos médicos ambulatoriais", "PROCEDIMENTO"),
    ("Produção hospitalar - competência 03", "PROCEDIMENTO"),
    ("Atendimento ambulatorial", "ANALISAR"),                 # "atendimento" tem prioridade máxima
    ("Consulta médica e cirurgia de implante de cateter", "ANALISAR"),  # consulta + procedimento
    (None, ""),
    ("Reembolso de despesas de deslocamento", ""),
]

CLINICA_BETA = [
    ("consulta medica", "CONSULTA"),
    ("Serviços médicos prestados no hospital", "ANALISAR"),
    ("Exame diagnóstico de imagem", "PROCEDIMENTO"),
    ("Atendimentos realizados no período", "ANALISAR"),
    ("Ambulatório - plantão noturno", "PROCEDIMENTO"),
    ("Coordenação de equipe médica", "CONSULTA"),
    (12345, ""),                                              # número no lugar de texto
]

# Casos que mostram limitações do código atual (ver README, "Limitações")
CONSULTORIO_GAMA = [
    ("Consulta médica", "CONSULTA"),
    ("Exames diagnósticos laboratoriais", ""),     # a regra pede PROCEDIMENTO; a lista só tem o singular
    ("Serviços hospitalares", "PROCEDIMENTO"),     # pega pelo termo "hospital"
    ("Coordenação administrativa do escritório", "CONSULTA"),  # "coordenação" sozinho é amplo demais
    ("Consulta  médica", ""),                      # espaço duplo quebra a correspondência
    ("Consulta\nmédica", ""),                      # quebra de linha dentro da célula
    ("Hospital-dia", "PROCEDIMENTO"),
]

ESPERADO = {
    ("Clinica_Alfa", "faturamento_marco.xlsx"): CLINICA_ALFA,
    ("Clinica_Beta", "faturamento_marco.xlsx"): CLINICA_BETA,
    ("Consultorio_Gama", "notas_marco.xlsx"): CONSULTORIO_GAMA,
}

# PDF mínimo válido, só para ocupar lugar na pasta (o classificador nunca o abre)
_PDF_MINIMO = (
    b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)


def _planilha_faturamento(caminho: Path, tomador: str, linhas: list, *, aba_extra: bool = False) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Faturamento"
    ws.append(COLUNAS)
    for celula in ws[1]:
        celula.font = Font(bold=True, color="FFFFFF")
        celula.fill = PatternFill("solid", fgColor="1F3864")
    for i, (texto, _) in enumerate(linhas, start=1):
        ws.append([date(2026, 3, min(i, 28)), 1000 + i, tomador, texto, round(150 + 37.5 * i, 2)])
    for linha in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        linha[0].number_format = "DD/MM/YYYY"
    for linha in ws.iter_rows(min_row=2, min_col=5, max_col=5):
        linha[0].number_format = '"R$" #,##0.00'
    for letra, largura in LARGURAS.items():
        ws.column_dimensions[letra].width = largura
    ws.freeze_panes = "A2"
    if aba_extra:
        resumo = wb.create_sheet("Resumo")
        resumo.append(["Total de notas", len(linhas)])
    caminho.parent.mkdir(parents=True, exist_ok=True)
    wb.save(caminho)


def gerar(destino: Path = PASTA_PADRAO) -> Path:
    destino = Path(destino)
    if destino.exists():
        shutil.rmtree(destino)

    alfa = destino / "Clinica_Alfa"
    beta = destino / "Clinica_Beta"
    gama = destino / "Consultorio_Gama"

    # Planilhas válidas (a da Clínica Alfa tem uma segunda aba, para mostrar o que se perde)
    _planilha_faturamento(alfa / "faturamento_marco.xlsx", "Operadora Exemplo S.A. (fictícia)",
                          CLINICA_ALFA, aba_extra=True)
    _planilha_faturamento(beta / "faturamento_marco.xlsx", "Plano de Saúde Modelo (fictício)",
                          CLINICA_BETA)
    _planilha_faturamento(gama / "notas_marco.xlsx", "Convênio Demonstração (fictício)",
                          CONSULTORIO_GAMA)

    # Arquivos que devem ser ignorados
    (alfa / "nota_fiscal_exemplo.pdf").write_bytes(_PDF_MINIMO)
    (alfa / "observacoes.txt").write_text("Arquivo de texto qualquer.\n", encoding="utf-8")

    sem_coluna = Workbook()
    sem_coluna.active.append(["Item", "Descrição", "Quantidade"])
    sem_coluna.active.append(["Luvas", "Material de consumo", 10])
    sem_coluna.save(alfa / "controle_interno.xlsx")

    (gama / "arquivo_corrompido.xlsx").write_bytes(b"isto nao e um arquivo xlsx de verdade")

    # Subpasta aninhada: o notebook só olha um nível abaixo da pasta escolhida
    _planilha_faturamento(beta / "2025" / "faturamento_antigo.xlsx", "Arquivo antigo (fictício)",
                          [("Consulta médica", "CONSULTA")])

    # Arquivo solto na raiz da pasta: também é ignorado
    (destino / "leia_antes.txt").write_text("Arquivo solto na raiz.\n", encoding="utf-8")
    return destino


if __name__ == "__main__":
    pasta = gerar(Path(sys.argv[1]) if len(sys.argv) > 1 else PASTA_PADRAO)
    print(f"Exemplos gerados em: {pasta}")
