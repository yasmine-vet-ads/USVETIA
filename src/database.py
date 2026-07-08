"""Utilitários SQLite do protótipo acadêmico Us.Vet IA.

Este banco pertence ao protótipo acadêmico Us.Vet IA. O sistema é
experimental e assistivo: respostas futuras da IA deverão ser tratadas como
sugestões estruturadas revisáveis e não substituem a revisão do
médico-veterinário.

Este módulo apenas inicializa a estrutura local do banco SQLite. Ele não insere
dados clínicos, não chama APIs externas e não cria interface de usuário.
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_DIR = PROJECT_ROOT / "data" / "db"
DB_PATH = DB_DIR / "usvet_ia.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def get_connection(db_path=DB_PATH):
    """Retorna uma conexão SQLite com chaves estrangeiras ativadas.

    A conexão é destinada ao protótipo acadêmico, experimental e assistivo
    Us.Vet IA. Conteúdos gerados futuramente por IA devem ser considerados
    sugestões estruturadas revisáveis e nunca substituem a revisão do
    médico-veterinário.
    """
    caminho_banco = Path(db_path)
    caminho_banco.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(caminho_banco)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    """Cria ou atualiza o banco SQLite local a partir de ``sql/schema.sql``.

    Esta função executa apenas o schema estrutural do protótipo acadêmico
    Us.Vet IA. Ela não insere dados clínicos, não executa chamadas de API e não
    cria interface. O sistema permanece experimental e assistivo, com respostas
    futuras da IA tratadas como sugestões revisáveis pelo médico-veterinário.
    """
    caminho_schema = Path(schema_path)
    if not caminho_schema.exists():
        raise FileNotFoundError(f"Schema não encontrado: {caminho_schema}")

    with get_connection(db_path) as connection:
        connection.executescript(caminho_schema.read_text(encoding="utf-8"))

    return Path(db_path)


if __name__ == "__main__":
    init_db()
    print("Banco de dados criado ou atualizado com sucesso.")
