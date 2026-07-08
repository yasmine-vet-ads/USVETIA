"""Testes do banco SQLite do projeto USVETIA.

Execute com:

    pytest

Os testes usam apenas dados fictícios, não dependem da planilha real, não usam
imagens reais, não incluem dados pessoais e não chamam APIs externas.
"""

import json
import sqlite3

from src.database import DB_PATH, get_connection, init_db

TABELAS_ESPERADAS = {
    "exames",
    "imagens",
    "selecao_amostra",
    "prompts",
    "analises_api",
    "respostas_json",
    "revisoes",
}


def _reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_database_file_can_be_created():
    _reset_db()

    init_db()

    assert DB_PATH.exists()
    assert DB_PATH.is_file()

    _reset_db()


def test_schema_tables_columns_and_foreign_keys():
    _reset_db()
    init_db()

    with get_connection() as connection:
        tabelas = {
            linha[0]
            for linha in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        colunas_exames = {
            linha[1] for linha in connection.execute("PRAGMA table_info(exames)")
        }
        foreign_keys_imagens = connection.execute("PRAGMA foreign_key_list(imagens)").fetchall()

    assert TABELAS_ESPERADAS.issubset(tabelas)
    assert "codigo_exame" in colunas_exames
    assert any(
        chave[2] == "exames"
        and chave[3] == "id_exame"
        and chave[4] == "id_exame"
        for chave in foreign_keys_imagens
    )

    _reset_db()


def test_insert_related_records_without_external_dependencies():
    _reset_db()
    init_db()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO exames (codigo_exame, grupo_amostra, especie, quantidade_imagens)
            VALUES (?, ?, ?, ?)
            """,
            ("USVET_TESTE", "piloto", "ficticio", 1),
        )
        id_exame = cursor.lastrowid

        cursor = connection.execute(
            """
            INSERT INTO imagens (id_exame, codigo_exame, nome_arquivo, tipo_imagem, anonimizada)
            VALUES (?, ?, ?, ?, ?)
            """,
            (id_exame, "USVET_TESTE", "imagem_teste_nao_real.png", "ultrassom", "sim"),
        )
        id_imagem = cursor.lastrowid

        schema_json = json.dumps(
            {
                "orgao_ou_regiao_avaliada": "string ou null",
                "qualidade_da_imagem": "string ou null",
                "sugestao_de_texto_revisavel": "string ou null",
            },
            ensure_ascii=False,
        )
        cursor = connection.execute(
            """
            INSERT INTO prompts (versao, nome_prompt, texto_prompt, schema_json, finalidade)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "teste",
                "Prompt fictício de teste",
                "Prompt estrutural fictício para teste automatizado.",
                schema_json,
                "Teste automatizado sem chamada externa.",
            ),
        )
        id_prompt = cursor.lastrowid

        cursor = connection.execute(
            """
            INSERT INTO analises_api (id_exame, id_prompt, codigo_exame, modelo, modo_teste)
            VALUES (?, ?, ?, ?, ?)
            """,
            (id_exame, id_prompt, "USVET_TESTE", "modelo_ficticio", "sim"),
        )
        id_analise = cursor.lastrowid

        cursor = connection.execute(
            """
            INSERT INTO respostas_json (id_analise, codigo_exame, resposta_json, json_valido)
            VALUES (?, ?, ?, ?)
            """,
            (id_analise, "USVET_TESTE", '{"teste": true}', "sim"),
        )
        id_resposta = cursor.lastrowid

        cursor = connection.execute(
            """
            INSERT INTO revisoes (id_analise, codigo_exame, revisor, concordancia)
            VALUES (?, ?, ?, ?)
            """,
            (id_analise, "USVET_TESTE", "revisor_ficticio", "não avaliado"),
        )
        id_revisao = cursor.lastrowid

        assert id_exame is not None
        assert id_imagem is not None
        assert id_prompt is not None
        assert id_analise is not None
        assert id_resposta is not None
        assert id_revisao is not None

        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM imagens
            WHERE id_exame = ? AND codigo_exame = ?
            """,
            (id_exame, "USVET_TESTE"),
        ).fetchone()[0]
        assert total == 1

    _reset_db()
