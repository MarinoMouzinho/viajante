import pytest
from app.services import intencoes, clientes, viagens

@pytest.fixture
def preparar_cenario(banco_teste, monkeypatch):
    """
    Prepara um cliente e uma viagem fictícia para os testes.
    """

    clientes.cadastrar_cliente("123456789")

    viagem_exemplo = {
        "id": "V001",
        "titulo": "Excursão Serra do Rio do Rastro",
        "status": "disponivel",
        "preco_individual": 289.90
    }

    monkeypatch.setattr(
        viagens,
        "buscar_viagem_por_id",
        lambda viagem_id: (
            viagem_exemplo if viagem_id == "V001" else None
        )
    )

    return viagem_exemplo

@pytest.fixture
def cenario_consulta(banco_teste, monkeypatch):
    """
    Prepara dois clientes e uma viagem para os testes.
    """

    viagem = {
        "id": "V001",
        "titulo": "Excursão Serra do Rio do Rastro",
        "destino": "Serra do Rio do Rastro",
        "datahora_ida": "2027-01-15T08:00:00",
        "datahora_volta": "2027-01-17T18:00:00",
        "status": "disponivel"
    }

    monkeypatch.setattr(
        viagens,
        "buscar_viagem_por_id",
        lambda viagem_id: viagem if viagem_id == "V001" else None
    )

    cliente_a = clientes.cadastrar_cliente("123456789")
    cliente_b = clientes.cadastrar_cliente("987654321")

    intencao = intencoes.registrar_intencao(
        telegram_chat_id="123456789",
        viagem_id="V001",
        quantidade=2,
        preferencia_assento="janela"
    )

    return {
        "cliente_a": cliente_a,
        "cliente_b": cliente_b,
        "intencao": intencao,
        "viagem": viagem
    }

def test_registrar_intencao(preparar_cenario):
    resultado = intencoes.registrar_intencao(
        telegram_chat_id="123456789",
        viagem_id="V001",
        quantidade=2,
        preferencia_assento="janela"
    )

    assert resultado["id"] > 0
    assert resultado["telegram_chat_id"] == "123456789"
    assert resultado["viagem_id"] == "V001"
    assert resultado["quantidade_passagens"] == 2
    assert resultado["preferencia_assento"] == "janela"
    assert resultado["status"] == "pendente"


def test_registrar_intencao_sem_preferencia(preparar_cenario):
    resultado = intencoes.registrar_intencao(
        telegram_chat_id="123456789",
        viagem_id="V001",
        quantidade=1
    )

    assert resultado["preferencia_assento"] == "indiferente"


def test_cliente_inexistente(preparar_cenario):
    with pytest.raises(LookupError):
        intencoes.registrar_intencao(
            telegram_chat_id="999999999",
            viagem_id="V001",
            quantidade=1
        )


def test_viagem_inexistente(preparar_cenario):
    with pytest.raises(LookupError):
        intencoes.registrar_intencao(
            telegram_chat_id="123456789",
            viagem_id="V999",
            quantidade=1
        )


def test_quantidade_invalida(preparar_cenario):
    with pytest.raises(ValueError):
        intencoes.registrar_intencao(
            telegram_chat_id="123456789",
            viagem_id="V001",
            quantidade=0
        )


def test_preferencia_invalida(preparar_cenario):
    with pytest.raises(ValueError):
        intencoes.registrar_intencao(
            telegram_chat_id="123456789",
            viagem_id="V001",
            quantidade=1,
            preferencia_assento="frente"
        )


def test_viagem_cancelada(preparar_cenario, monkeypatch):
    viagem_cancelada = {
        "id": "V002",
        "titulo": "Passeio cancelado",
        "status": "cancelada"
    }

    monkeypatch.setattr(
        viagens,
        "buscar_viagem_por_id",
        lambda viagem_id: viagem_cancelada
    )

    with pytest.raises(ValueError):
        intencoes.registrar_intencao(
            telegram_chat_id="123456789",
            viagem_id="V002",
            quantidade=1
        )


def test_quantidade_deve_ser_inteira(preparar_cenario):
    with pytest.raises(ValueError):
        intencoes.registrar_intencao(
            telegram_chat_id="123456789",
            viagem_id="V001",
            quantidade=1.5
        )


def test_consultar_intencoes(cenario_consulta):
    resultado = intencoes.consultar_intencoes("123456789")

    assert len(resultado) == 1
    assert resultado[0]["viagem_id"] == "V001"
    assert resultado[0]["titulo_viagem"] == (
        "Excursão Serra do Rio do Rastro"
    )
    assert resultado[0]["quantidade_passagens"] == 2
    assert resultado[0]["status"] == "pendente"


def test_consultar_intencoes_apenas_do_proprio_cliente(
    cenario_consulta
):
    intencoes.registrar_intencao(
        telegram_chat_id="987654321",
        viagem_id="V001",
        quantidade=1
    )

    resultado_a = intencoes.consultar_intencoes("123456789")
    resultado_b = intencoes.consultar_intencoes("987654321")

    assert len(resultado_a) == 1
    assert len(resultado_b) == 1

    assert resultado_a[0]["cliente_id"] != resultado_b[0]["cliente_id"]


def test_consultar_intencoes_cliente_sem_intencoes(
    cenario_consulta
):
    resultado = intencoes.consultar_intencoes("987654321")

    assert resultado == []


def test_cancelar_intencao(cenario_consulta):
    intencao_id = cenario_consulta["intencao"]["id"]

    resultado = intencoes.cancelar_intencao(
        "123456789",
        intencao_id
    )

    assert resultado["id"] == intencao_id
    assert resultado["status"] == "cancelada"


def test_impedir_cancelamento_de_intencao_de_outro_cliente(
    cenario_consulta
):
    intencao_id = cenario_consulta["intencao"]["id"]

    with pytest.raises(LookupError):
        intencoes.cancelar_intencao(
            "987654321",
            intencao_id
        )


def test_impedir_cancelamento_de_intencao_ja_cancelada(
    cenario_consulta
):
    intencao_id = cenario_consulta["intencao"]["id"]

    intencoes.cancelar_intencao("123456789", intencao_id)

    with pytest.raises(ValueError):
        intencoes.cancelar_intencao("123456789", intencao_id)


def test_impedir_cancelamento_com_id_invalido(
    cenario_consulta
):
    with pytest.raises(ValueError):
        intencoes.cancelar_intencao("123456789", 0)

    with pytest.raises(ValueError):
        intencoes.cancelar_intencao("123456789", 1.5)

    with pytest.raises(ValueError):
        intencoes.cancelar_intencao("123456789", True)


def test_consultar_intencoes_cliente_inexistente(
    cenario_consulta
):
    with pytest.raises(LookupError):
        intencoes.consultar_intencoes("111111111")
