
import pytest

from app.services import clientes, demandas


@pytest.fixture
def preparar_cenario(banco_teste):
    cliente = clientes.cadastrar_cliente("123456789")

    return cliente


def test_registrar_nova_demanda(preparar_cenario):
    resultado = demandas.registrar_demanda(
        telegram_chat_id="123456789",
        destino="Aracuarinha",
        evento="Festa de Aracuarinha",
        periodo="Dezembro de 2026"
    )

    assert resultado["id"] > 0
    assert resultado["destino"] == "aracuarinha"
    assert resultado["evento"] == "festa de aracuarinha"
    assert resultado["periodo"] == "dezembro de 2026"
    assert resultado["status"] == "ativa"
    assert resultado["demanda_criada"] is True
    assert resultado["interesse_novo"] is True


def test_reutilizar_demanda_existente(preparar_cenario):
    primeira = demandas.registrar_demanda(
        "123456789",
        "Aracuarinha",
        "Festa de Aracuarinha",
        "Dezembro de 2026"
    )

    segunda = demandas.registrar_demanda(
        "123456789",
        "ARACUARINHA",
        "FESTA DE ARACUARINHA",
        "DEZEMBRO DE 2026"
    )

    assert primeira["id"] == segunda["id"]
    assert primeira["demanda_criada"] is True
    assert segunda["demanda_criada"] is False
    assert segunda["interesse_novo"] is False


def test_dois_clientes_compartilham_demanda(preparar_cenario):
    clientes.cadastrar_cliente("987654321")

    primeira = demandas.registrar_demanda(
        "123456789",
        "Aracuarinha",
        "Festa",
        "Dezembro de 2026"
    )

    segunda = demandas.registrar_demanda(
        "987654321",
        "Aracuarinha",
        "Festa",
        "Dezembro de 2026"
    )

    assert primeira["id"] == segunda["id"]
    assert primeira["demanda_criada"] is True
    assert segunda["demanda_criada"] is False
    assert segunda["interesse_novo"] is True


def test_cliente_nao_cadastrado(preparar_cenario):
    with pytest.raises(LookupError):
        demandas.registrar_demanda(
            "111111111",
            "Aracuarinha"
        )


def test_destino_obrigatorio(preparar_cenario):
    with pytest.raises(ValueError):
        demandas.registrar_demanda(
            "123456789",
            ""
        )


def test_destino_deve_ser_textual(preparar_cenario):
    with pytest.raises(ValueError):
        demandas.registrar_demanda(
            "123456789",
            123
        )


def test_evento_opcional(preparar_cenario):
    resultado = demandas.registrar_demanda(
        "123456789",
        "Aracuarinha"
    )

    assert resultado["evento"] == ""
    assert resultado["periodo"] == ""


def test_normalizacao_de_espacos(preparar_cenario):
    resultado = demandas.registrar_demanda(
        "123456789",
        "  Festa   de   Aracuarinha  "
    )

    assert resultado["destino"] == "festa de aracuarinha"


def test_listar_demandas(preparar_cenario):
    demandas.registrar_demanda(
        "123456789",
        "Aracuarinha",
        "Festa",
        "Dezembro de 2026"
    )

    resultado = demandas.listar_demandas()

    assert len(resultado) == 1
    assert resultado[0]["destino"] == "aracuarinha"
    assert resultado[0]["quantidade_interessados"] == 1


def test_listar_demandas_todas(preparar_cenario):
    demandas.registrar_demanda(
        "123456789",
        "Aracuarinha"
    )

    resultado = demandas.listar_demandas("todas")

    assert len(resultado) == 1


def test_listar_demandas_status_invalido(preparar_cenario):
    with pytest.raises(ValueError):
        demandas.listar_demandas("pendente")


def test_buscar_demanda(preparar_cenario):
    criada = demandas.registrar_demanda(
        "123456789",
        "Aracuarinha",
        "Festa",
        "Dezembro de 2026"
    )

    resultado = demandas.buscar_demanda(criada["id"])

    assert resultado["id"] == criada["id"]
    assert resultado["destino"] == "aracuarinha"
    assert resultado["quantidade_interessados"] == 1


def test_buscar_demanda_inexistente(preparar_cenario):
    with pytest.raises(LookupError):
        demandas.buscar_demanda(999)


def test_buscar_demanda_id_invalido(preparar_cenario):
    with pytest.raises(ValueError):
        demandas.buscar_demanda(0)

    with pytest.raises(ValueError):
        demandas.buscar_demanda("1")


def test_listar_interessados(preparar_cenario):
    demandas.registrar_demanda(
        "123456789",
        "Aracuarinha"
    )

    cliente = clientes.cadastrar_cliente("987654321")

    demanda = demandas.registrar_demanda(
        "987654321",
        "Aracuarinha"
    )

    resultado = demandas.listar_interessados(demanda["id"])

    assert len(resultado) == 2

    identificadores = {
        interessado["telegram_chat_id"]
        for interessado in resultado
    }

    assert identificadores == {"123456789", "987654321"}


def test_listar_interessados_demanda_inexistente(preparar_cenario):
    with pytest.raises(LookupError):
        demandas.listar_interessados(999)


def test_listar_interessados_id_invalido(preparar_cenario):
    with pytest.raises(ValueError):
        demandas.listar_interessados(-1)
