
import sqlite3

from app.database.conexao import obter_caminho_banco

def test_caminho_banco():
    caminho = obter_caminho_banco()
    assert caminho.is_absolute()
    assert caminho.name == "viajante.db"


def test_conexao_sqlite(tmp_path):
    caminho = tmp_path / "teste.db"
    conexao = sqlite3.connect(caminho)
    resultado = conexao.execute("SELECT 1").fetchone()
    assert resultado[0] == 1
    conexao.close()