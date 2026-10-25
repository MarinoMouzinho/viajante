import sqlite3
from pathlib import Path

from dotenv import load_dotenv
import os

DIR_PROJETO = Path(__file__).resolve().parents[2]
load_dotenv(DIR_PROJETO / ".env")

def obter_caminho_banco() -> Path:
    """
    Retorna o caminho absoluto do banco de dados
    """
    caminho = Path(os.getenv("DATABASE_PATH", "database/viajante.db"))
    if not caminho.is_absolute():
        caminho = DIR_PROJETO / caminho
    return caminho


def conectar() -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco SQLite.
    """
    caminho_banco = obter_caminho_banco()
    caminho_banco.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho_banco, timeout=30)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao

