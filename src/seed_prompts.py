"""Insere ou atualiza o prompt base do protótipo acadêmico Us.Vet IA.

O script apenas grava um prompt estrutural na tabela ``prompts`` do SQLite. Ele
não chama API externa, não executa análise, não emite diagnóstico e não substitui
a revisão do médico-veterinário.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import get_connection, init_db

NOME_PROMPT = "Prompt Base Us.Vet IA - Imagem + Descrição"
VERSAO_PROMPT = "v1.0"
FINALIDADE_PROMPT = (
    "Análise assistida de imagem ultrassonográfica veterinária associada à "
    "descrição técnica da ultrassonografista."
)

TEXTO_PROMPT = """
Você está apoiando o protótipo acadêmico Us.Vet IA, um sistema experimental e
assistivo para organização de achados em exames ultrassonográficos veterinários.

Analise a imagem ultrassonográfica veterinária anonimizada em conjunto com a
descrição técnica fornecida pela ultrassonografista. Retorne achados estruturados
e revisáveis. Não emita diagnóstico definitivo, não gere laudo final e não
substitua a avaliação, validação ou revisão do médico-veterinário.

A resposta deve:
- descrever o órgão ou região avaliada;
- indicar a qualidade da imagem;
- listar achados visuais sugeridos, quando sustentados pela imagem;
- registrar a localização topográfica dos achados;
- considerar os achados informados pela ultrassonografista;
- apontar concordância ou divergência com a descrição técnica;
- indicar omissões possíveis, sem inventar achados;
- sinalizar achados não sustentados pela imagem ou pelo texto fornecido;
- explicitar limitações da análise;
- sugerir um texto revisável, estruturado e dependente de validação veterinária.

Use linguagem técnica, cautelosa e compatível com o caráter acadêmico,
experimental e assistivo do sistema. Sempre informe que a saída deve ser revisada
por médico-veterinário antes de qualquer uso clínico.
""".strip()

SCHEMA_JSON = json.dumps(
    {
        "orgao_ou_regiao_avaliada": "string ou null",
        "qualidade_da_imagem": "string ou null",
        "achados_visuais_sugeridos": ["string"],
        "localizacao_topografica": "string ou null",
        "achados_informados_pela_ultrassonografista": ["string"],
        "concordancia_com_a_descricao": "string ou null",
        "omissoes_possiveis": ["string"],
        "achados_nao_sustentados": ["string"],
        "limitacoes": ["string"],
        "sugestao_de_texto_revisavel": "string ou null",
        "aviso_revisao_veterinaria": "string",
    },
    ensure_ascii=False,
    indent=2,
)


def seed_prompt_base() -> str:
    """Insere ou atualiza o prompt base, evitando duplicidade por nome e versão."""
    init_db()
    dados_prompt = {
        "versao": VERSAO_PROMPT,
        "nome_prompt": NOME_PROMPT,
        "texto_prompt": TEXTO_PROMPT,
        "schema_json": SCHEMA_JSON,
        "finalidade": FINALIDADE_PROMPT,
        "ativo": "sim",
    }

    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id_prompt
            FROM prompts
            WHERE nome_prompt = :nome_prompt AND versao = :versao
            """,
            dados_prompt,
        )
        existente = cursor.fetchone()

        if existente:
            dados_prompt["id_prompt"] = existente[0]
            connection.execute(
                """
                UPDATE prompts
                SET texto_prompt = :texto_prompt,
                    schema_json = :schema_json,
                    finalidade = :finalidade,
                    ativo = :ativo
                WHERE id_prompt = :id_prompt
                """,
                dados_prompt,
            )
            return "Prompt base atualizado com sucesso."

        connection.execute(
            """
            INSERT INTO prompts (versao, nome_prompt, texto_prompt, schema_json, finalidade, ativo)
            VALUES (:versao, :nome_prompt, :texto_prompt, :schema_json, :finalidade, :ativo)
            """,
            dados_prompt,
        )
        return "Prompt base inserido com sucesso."


if __name__ == "__main__":
    print(seed_prompt_base())
