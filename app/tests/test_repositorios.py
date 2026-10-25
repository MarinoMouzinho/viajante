
from app.database.conexao import conectar
from app.database.repositorios import inicializar_banco

def test_inicializar_banco(banco_teste):
    with conectar() as conexao:
        resultado = conexao.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """)

        tabelas = {
            linha["name"]
            for linha in resultado.fetchall()
        }
    tabelas_esperadas = {
        "clientes",
        "intencoes_reserva",
        "demandas_viagem",
        "interessados_demanda",
        "sessoes"
    }
    assert tabelas_esperadas.issubset(tabelas)

def test_inicializacao_repetida(banco_teste):
    inicializar_banco()

    with conectar() as conexao:
        resultado = conexao.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
        """)
        quantidade = resultado.fetchone()[0]
    assert quantidade >= 5