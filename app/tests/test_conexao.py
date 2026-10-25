
from app.database.conexao import conectar, obter_caminho_banco


def test_conexao_banco():
    conexao = conectar()
    assert conexao is not None
    resultado = conexao.execute("SELECT 1").fetchone()
    assert resultado[0] == 1
    conexao.close()


def test_caminho_banco():
    caminho = obter_caminho_banco()
    assert caminho.is_absolute()
    assert caminho.name == "viajante.db"
