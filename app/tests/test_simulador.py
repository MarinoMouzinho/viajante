
import pytest

from app.web import simulador
from app.agent import memoria


@pytest.fixture(autouse=True)
def limpar_ambiente():
    simulador._sessoes.clear()
    simulador._contador_clientes = 0
    memoria._memorias.clear()

    yield

    simulador._sessoes.clear()
    simulador._contador_clientes = 0
    memoria._memorias.clear()


def test_criar_sessao():
    sessao = simulador.criar_sessao()

    assert sessao["id"].startswith("sess_")
    assert sessao["cliente"] == "Cliente de teste 001"
    assert sessao["estado"] == "ativa"


def test_criar_sessoes_com_identificadores_diferentes():
    sessao_1 = simulador.criar_sessao()
    sessao_2 = simulador.criar_sessao()

    assert sessao_1["id"] != sessao_2["id"]


def test_listar_sessoes():
    simulador.criar_sessao()
    simulador.criar_sessao()

    sessoes = simulador.listar_sessoes()

    assert len(sessoes) == 2


def test_buscar_sessao():
    criada = simulador.criar_sessao()

    encontrada = simulador.buscar_sessao(criada["id"])

    assert encontrada["id"] == criada["id"]


def test_buscar_sessao_inexistente():
    with pytest.raises(LookupError):
        simulador.buscar_sessao("sess_inexistente")


def test_encerrar_sessao():
    sessao = simulador.criar_sessao()

    simulador.encerrar_sessao(sessao["id"])

    assert simulador.listar_sessoes() == []


def test_encerrar_sessao_remove_historico():
    sessao = simulador.criar_sessao()

    memoria.atualizar_historico(
        sessao["id"],
        [{"role": "user", "content": "Olá!"}]
    )

    simulador.encerrar_sessao(sessao["id"])

    assert memoria.obter_historico(sessao["id"]) == []


def test_limpar_sessao_preserva_sessao():
    sessao = simulador.criar_sessao()

    memoria.atualizar_historico(
        sessao["id"],
        [{"role": "user", "content": "Olá!"}]
    )

    simulador.limpar_sessao(sessao["id"])

    assert simulador.buscar_sessao(sessao["id"])["id"] == sessao["id"]
    assert memoria.obter_historico(sessao["id"]) == []


def test_historicos_independentes_entre_sessoes():
    sessao_1 = simulador.criar_sessao()
    sessao_2 = simulador.criar_sessao()

    memoria.atualizar_historico(
        sessao_1["id"],
        [{"role": "user", "content": "Conversa 1"}]
    )

    memoria.atualizar_historico(
        sessao_2["id"],
        [{"role": "user", "content": "Conversa 2"}]
    )

    assert memoria.obter_historico(sessao_1["id"])[0]["content"] == "Conversa 1"
    assert memoria.obter_historico(sessao_2["id"])[0]["content"] == "Conversa 2"


def test_limpar_sessao_inexistente():
    with pytest.raises(LookupError):
        simulador.limpar_sessao("sess_inexistente")


def test_encerrar_sessao_inexistente():
    with pytest.raises(LookupError):
        simulador.encerrar_sessao("sess_inexistente")
