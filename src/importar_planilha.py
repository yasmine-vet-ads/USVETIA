"""Importa a planilha de curadoria de exames do projeto USVETIA.

O script lê a aba ``Curadoria_Exames`` da planilha local
``data/input/Planilha_Curadoria_Exames_UsVet_IA.xlsx`` e carrega os dados nas
tabelas ``exames`` e ``selecao_amostra`` do SQLite. Ele não inventa dados
faltantes, não cria dados clínicos fictícios, não chama API, não gera laudo e
não interpreta imagens.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import get_connection, init_db

PLANILHA_PADRAO = PROJECT_ROOT / "data" / "input" / "Planilha_Curadoria_Exames_UsVet_IA.xlsx"
ABA_PRINCIPAL = "Curadoria_Exames"

COLUNAS_OBRIGATORIAS = [
    "codigo_exame",
    "grupo_amostra",
    "data_exame",
    "periodo_base",
    "especie",
    "sexo",
    "idade",
    "peso_kg",
    "orgao_regiao_principal",
    "outros_orgaos_avaliados",
    "tipo_caso",
    "normal_ou_alterado",
    "descricao_tecnica_associada",
    "quantidade_imagens",
    "qualidade_imagem",
    "clareza_diagnostica",
    "dados_identificaveis_na_imagem",
    "dados_identificaveis_no_texto",
    "anonimizacao_possivel",
    "status_anonimizacao",
    "incluido_na_amostra",
    "motivo_exclusao",
    "prioridade_processamento",
    "status_processamento",
    "observacoes_curadoria",
]

COLUNAS_ESPERADAS = COLUNAS_OBRIGATORIAS

COLUNAS_EXAMES = [
    "codigo_exame",
    "grupo_amostra",
    "data_exame",
    "periodo_base",
    "especie",
    "sexo",
    "idade",
    "peso_kg",
    "orgao_regiao_principal",
    "outros_orgaos_avaliados",
    "tipo_caso",
    "normal_ou_alterado",
    "descricao_tecnica_associada",
    "quantidade_imagens",
    "status_processamento",
]

COLUNAS_SELECAO = [
    "codigo_exame",
    "grupo_amostra",
    "qualidade_imagem",
    "clareza_diagnostica",
    "dados_identificaveis_na_imagem",
    "dados_identificaveis_no_texto",
    "anonimizacao_possivel",
    "status_anonimizacao",
    "incluido_na_amostra",
    "motivo_exclusao",
    "prioridade_processamento",
    "observacoes_curadoria",
]


def validar_colunas(colunas: list[str]) -> bool:
    """Valida se a planilha contém todas as colunas obrigatórias."""
    return set(COLUNAS_OBRIGATORIAS).issubset(set(colunas))


def _normalizar_valor(valor):
    """Converte células vazias/NaN em ``None`` para persistir como NULL."""
    if valor is None:
        return None
    if valor != valor:
        return None
    if isinstance(valor, str):
        valor_limpo = valor.strip()
        return valor_limpo if valor_limpo else None
    if hasattr(valor, "isoformat"):
        return valor.isoformat()
    return valor


def _linha_para_dict(linha, colunas):
    return {coluna: _normalizar_valor(linha[coluna]) for coluna in colunas}


def _validar_dataframe(dataframe):
    if validar_colunas(list(dataframe.columns)):
        return

    faltantes = sorted(set(COLUNAS_OBRIGATORIAS) - set(dataframe.columns))
    raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(faltantes))


def _upsert_exame(connection, dados_exame):
    colunas = COLUNAS_EXAMES
    placeholders = ", ".join(f":{coluna}" for coluna in colunas)
    atualizacoes = ", ".join(
        f"{coluna} = excluded.{coluna}"
        for coluna in colunas
        if coluna != "codigo_exame"
    )

    connection.execute(
        f"""
        INSERT INTO exames ({", ".join(colunas)})
        VALUES ({placeholders})
        ON CONFLICT(codigo_exame) DO UPDATE SET {atualizacoes}
        """,
        dados_exame,
    )

    cursor = connection.execute(
        "SELECT id_exame FROM exames WHERE codigo_exame = :codigo_exame",
        {"codigo_exame": dados_exame["codigo_exame"]},
    )
    return cursor.fetchone()[0]


def _upsert_selecao_amostra(connection, id_exame, dados_selecao):
    dados = dict(dados_selecao)
    dados["id_exame"] = id_exame

    colunas = ["id_exame", *COLUNAS_SELECAO]
    placeholders = ", ".join(f":{coluna}" for coluna in colunas)
    atualizacoes = ", ".join(
        f"{coluna} = excluded.{coluna}"
        for coluna in colunas
        if coluna != "codigo_exame"
    )

    connection.execute(
        f"""
        INSERT INTO selecao_amostra ({", ".join(colunas)})
        VALUES ({placeholders})
        ON CONFLICT(codigo_exame) DO UPDATE SET {atualizacoes}
        """,
        dados,
    )


def importar_planilha(caminho_planilha=PLANILHA_PADRAO):
    """Importa a planilha de curadoria para ``exames`` e ``selecao_amostra``."""
    caminho = Path(caminho_planilha)
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")

    import pandas as pd

    dataframe = pd.read_excel(caminho, sheet_name=ABA_PRINCIPAL, engine="openpyxl")
    _validar_dataframe(dataframe)

    init_db()
    codigos_processados = set()

    with get_connection() as connection:
        for _, linha in dataframe.iterrows():
            codigo_exame = _normalizar_valor(linha["codigo_exame"])
            if codigo_exame is None:
                continue

            dados_exame = _linha_para_dict(linha, COLUNAS_EXAMES)
            dados_selecao = _linha_para_dict(linha, COLUNAS_SELECAO)

            id_exame = _upsert_exame(connection, dados_exame)
            _upsert_selecao_amostra(connection, id_exame, dados_selecao)
            codigos_processados.add(codigo_exame)

        total_selecao = connection.execute("SELECT COUNT(*) FROM selecao_amostra").fetchone()[0]

    total_piloto = int((dataframe["grupo_amostra"].astype(str).str.lower() == "piloto").sum())
    total_principal = int((dataframe["grupo_amostra"].astype(str).str.lower() == "principal").sum())

    resumo = {
        "total_linhas_lidas": len(dataframe),
        "total_exames_importados_ou_atualizados": len(codigos_processados),
        "total_exames_piloto": total_piloto,
        "total_exames_principais": total_principal,
        "total_registros_selecao_amostra": total_selecao,
    }

    print(f"Total de linhas lidas: {resumo['total_linhas_lidas']}")
    print(
        "Total de exames importados ou atualizados: "
        f"{resumo['total_exames_importados_ou_atualizados']}"
    )
    print(f"Total de exames piloto: {resumo['total_exames_piloto']}")
    print(f"Total de exames principais: {resumo['total_exames_principais']}")
    print(f"Total de registros em selecao_amostra: {resumo['total_registros_selecao_amostra']}")

    return resumo


if __name__ == "__main__":
    importar_planilha()
