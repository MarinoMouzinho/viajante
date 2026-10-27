
import pytest

from app.agent import memoria


@pytest.fixture(autouse=True)
def limpar_memorias():
    memoria._memorias.clear()
    yield
    memoria._memorias.clear()


def test_historico_inicial_vazio():
    historico = memoria.obter_historico("123456")

    assert historico == []


def test_atualizar_e_obter_historico():
    historico = [
        {"role": "user", "content": "Olá!"},
        {"role": "assistant", "content": "Olá! Como posso ajudar?"}
    ]

    memoria.atualizar_historico("123456", historico)

    resultado = memoria.obter_historico("123456")

    assert resultado == historico


def test_historicos_independentes_por_cliente():
    memoria.atualizar_historico(
        "123456",
        [{"role": "user", "content": "Minha primeira mensagem"}]
    )

    memoria.atualizar_historico(
        "654321",
        [{"role": "user", "content": "Outra conversa"}]
    )

    historico_1 = memoria.obter_historico("123456")
    historico_2 = memoria.obter_historico("654321")

    assert historico_1[0]["content"] == "Minha primeira mensagem"
    assert historico_2[0]["content"] == "Outra conversa"


def test_historico_retorna_copia():
    historico = [{"role": "user", "content": "Olá!"}]

    memoria.atualizar_historico("123456", historico)

    resultado = memoria.obter_historico("123456")
    resultado.append({"role": "assistant", "content": "Resposta"})

    assert len(memoria.obter_historico("123456")) == 1


def test_atualizar_historico_nao_mantem_referencia():
    historico = [{"role": "user", "content": "Olá!"}]

    memoria.atualizar_historico("123456", historico)

    historico.append({"role": "assistant", "content": "Resposta"})

    assert len(memoria.obter_historico("123456")) == 1


def test_limpar_historico():
    memoria.atualizar_historico(
        "123456",
        [{"role": "user", "content": "Olá!"}]
    )

    memoria.limpar_historico("123456")

    assert memoria.obter_historico("123456") == []


@pytest.mark.parametrize("telegram_chat_id", ["", "   ", None])
def test_rejeitar_id_invalido(telegram_chat_id):
    with pytest.raises(ValueError):
        memoria.obter_historico(telegram_chat_id)


def test_rejeitar_historico_invalido():
    with pytest.raises(ValueError):
        memoria.atualizar_historico("123456", "historico inválido")
