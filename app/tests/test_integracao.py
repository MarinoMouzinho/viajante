
import pytest

from app.services import clientes, demandas, intencoes, viagens


@pytest.fixture
def ambiente_integracao(banco_teste, monkeypatch):
    """
    Prepara o banco temporário e simula uma viagem disponível.
    """

    viagem_teste = {
        "id": "V001",
        "titulo": "Excursão Serra do Rio do Rastro",
        "destino": "Serra do Rio do Rastro",
        "status": "disponivel",
        "datahora_ida": "2026-12-10T06:00:00",
        "datahora_volta": "2026-12-12T18:00:00"
    }

    def buscar_viagem(viagem_id):
        if viagem_id == "V001":
            return viagem_teste

        return None

    monkeypatch.setattr(
        viagens,
        "buscar_viagem_por_id",
        buscar_viagem
    )

    return {
        "viagem": viagem_teste
    }


def test_fluxo_cadastro_e_atualizacao_cliente(ambiente_integracao):
    """
    Testa o cadastro de um cliente e a atualização do telefone.
    """

    cliente = clientes.cadastrar_cliente(
        telegram_chat_id="123456789",
        nome_telegram="Marino"
    )

    assert cliente["id"] > 0
    assert cliente["telegram_chat_id"] == "123456789"
    assert cliente["nome_telegram"] == "Marino"
    assert cliente["telefone"] is None

    atualizado = clientes.atualizar_telefone_cliente(
        telegram_chat_id="123456789",
        telefone="+55 (83) 99999-9999"
    )

    assert atualizado["telefone"] == "+55 (83) 99999-9999"


def test_fluxo_completo_intencao_reserva(ambiente_integracao):
    """
    Testa o cadastro do cliente, registro, consulta e cancelamento
    de uma intenção de reserva.
    """

    cliente = clientes.cadastrar_cliente("123456789")

    intencao = intencoes.registrar_intencao(
        telegram_chat_id="123456789",
        viagem_id="V001",
        quantidade=2,
        preferencia_assento="janela"
    )

    assert intencao["cliente_id"] == cliente["id"]
    assert intencao["viagem_id"] == "V001"
    assert intencao["quantidade_passagens"] == 2
    assert intencao["status"] == "pendente"

    intencoes_cliente = intencoes.consultar_intencoes(
        "123456789"
    )

    assert len(intencoes_cliente) == 1
    assert intencoes_cliente[0]["id"] == intencao["id"]
    assert intencoes_cliente[0]["titulo_viagem"] == (
        "Excursão Serra do Rio do Rastro"
    )

    cancelada = intencoes.cancelar_intencao(
        telegram_chat_id="123456789",
        intencao_id=intencao["id"]
    )

    assert cancelada["status"] == "cancelada"

    intencoes_cliente = intencoes.consultar_intencoes(
        "123456789"
    )

    assert intencoes_cliente[0]["status"] == "cancelada"


def test_cliente_nao_acessa_intencao_de_outro(
    ambiente_integracao
):
    """
    Verifica se um cliente não consegue consultar ou cancelar
    uma intenção pertencente a outro cliente.
    """

    clientes.cadastrar_cliente("123456789")
    clientes.cadastrar_cliente("987654321")

    intencao = intencoes.registrar_intencao(
        telegram_chat_id="123456789",
        viagem_id="V001",
        quantidade=1
    )

    # O segundo cliente não deve visualizar a intenção.
    resultado = intencoes.consultar_intencoes("987654321")

    assert resultado == []

    # O segundo cliente não deve conseguir cancelar a intenção.
    with pytest.raises(LookupError):
        intencoes.cancelar_intencao(
            telegram_chat_id="987654321",
            intencao_id=intencao["id"]
        )

    # A intenção original deve continuar pendente.
    intencoes_cliente = intencoes.consultar_intencoes(
        "123456789"
    )

    assert intencoes_cliente[0]["status"] == "pendente"


def test_fluxo_completo_demanda_viagem(ambiente_integracao):
    """
    Testa o cadastro de clientes, criação de demanda,
    associação de interessados e consulta.
    """

    clientes.cadastrar_cliente("123456789")
    clientes.cadastrar_cliente("987654321")

    primeira = demandas.registrar_demanda(
        telegram_chat_id="123456789",
        destino="Aracuarinha",
        evento="Festa de Aracuarinha",
        periodo="Dezembro de 2026"
    )

    segunda = demandas.registrar_demanda(
        telegram_chat_id="987654321",
        destino="Aracuarinha",
        evento="Festa de Aracuarinha",
        periodo="Dezembro de 2026"
    )

    # A segunda manifestação deve reutilizar a demanda.
    assert primeira["id"] == segunda["id"]
    assert primeira["demanda_criada"] is True
    assert segunda["demanda_criada"] is False

    # Os dois clientes devem estar associados à mesma demanda.
    assert primeira["interesse_novo"] is True
    assert segunda["interesse_novo"] is True

    demanda = demandas.buscar_demanda(primeira["id"])

    assert demanda["destino"] == "aracuarinha"
    assert demanda["quantidade_interessados"] == 2

    interessados = demandas.listar_interessados(
        primeira["id"]
    )

    assert len(interessados) == 2

    identificadores = {
        interessado["telegram_chat_id"]
        for interessado in interessados
    }

    assert identificadores == {
        "123456789",
        "987654321"
    }


def test_cliente_nao_duplica_interesse_na_mesma_demanda(
    ambiente_integracao
):
    """
    Verifica se um cliente pode manifestar interesse novamente
    sem gerar uma associação duplicada.
    """

    clientes.cadastrar_cliente("123456789")

    primeira = demandas.registrar_demanda(
        telegram_chat_id="123456789",
        destino="Aracuarinha",
        evento="Festa",
        periodo="Dezembro de 2026"
    )

    segunda = demandas.registrar_demanda(
        telegram_chat_id="123456789",
        destino="Aracuarinha",
        evento="Festa",
        periodo="Dezembro de 2026"
    )

    assert primeira["id"] == segunda["id"]
    assert primeira["interesse_novo"] is True
    assert segunda["interesse_novo"] is False

    interessados = demandas.listar_interessados(
        primeira["id"]
    )

    assert len(interessados) == 1
