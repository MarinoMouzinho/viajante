
import pytest
import sqlite3

from app.database.repositorios import inicializar_banco

@pytest.fixture
def banco_teste(tmp_path, monkeypatch):
    """
    Cria um banco SQLite temporário para os testes.
    """
    caminho_banco = tmp_path / "banco_teste.db"

    def conectar_teste():
        conexao = sqlite3.connect(caminho_banco)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    monkeypatch.setattr(
        "app.database.repositorios.conectar",
        conectar_teste
    )

    inicializar_banco()
    yield caminho_banco
