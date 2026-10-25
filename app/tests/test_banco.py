
import sqlite3

from app.database import repositorios


def test_inicializar_banco(monkeypatch, tmp_path):
    caminho_teste = tmp_path / "teste.db"
    def conectar_banco_teste():
        conexao = sqlite3.connect(caminho_teste)
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    monkeypatch.setattr(
        repositorios,
        "conectar",
        conectar_banco_teste
    )

    repositorios.inicializar_banco()
    conexao = sqlite3.connect(caminho_teste)
    tabelas = conexao.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """).fetchall()
    nomes_tabelas = {tabela[0] for tabela in tabelas}
    conexao.close()

    assert "clientes" in nomes_tabelas
    assert "intencoes_reserva" in nomes_tabelas
    assert "demandas_viagem" in nomes_tabelas
    assert "sessoes" in nomes_tabelas
