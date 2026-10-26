
import pytest

from app.services import clientes


def test_cadastrar_cliente(banco_teste):
    resultado = clientes.cadastrar_cliente(
        telegram_chat_id="123456789",
        telefone="+55 83 99999-9999"
    )

    assert resultado["telegram_chat_id"] == "123456789"
    assert resultado["telefone"] == "+55 83 99999-9999"


def test_cadastrar_cliente_sem_telefone(banco_teste):
    resultado = clientes.cadastrar_cliente(
        telegram_chat_id="987654321"
    )

    assert resultado["telegram_chat_id"] == "987654321"
    assert resultado["telefone"] is None


def test_impedir_cliente_duplicado(banco_teste):
    clientes.cadastrar_cliente("123456789")

    with pytest.raises(ValueError):
        clientes.cadastrar_cliente("123456789")


def test_buscar_cliente(banco_teste):
    clientes.cadastrar_cliente("123456789")

    resultado = clientes.buscar_cliente("123456789")

    assert resultado is not None
    assert resultado["telegram_chat_id"] == "123456789"


def test_buscar_cliente_inexistente(banco_teste):
    resultado = clientes.buscar_cliente("999999999")

    assert resultado is None


def test_atualizar_telefone(banco_teste):
    clientes.cadastrar_cliente("123456789")

    resultado = clientes.atualizar_telefone_cliente(
        "123456789",
        "+55 83 98888-7777"
    )

    assert resultado["telefone"] == "+55 83 98888-7777"


def test_atualizar_cliente_inexistente(banco_teste):
    with pytest.raises(LookupError):
        clientes.atualizar_telefone_cliente(
            "123456789",
            "+55 83 98888-7777"
        )


def test_validar_telegram_chat_id_invalido():
    with pytest.raises(ValueError):
        clientes.cadastrar_cliente("abc123")


def test_validar_telefone_invalido(banco_teste):
    with pytest.raises(ValueError):
        clientes.cadastrar_cliente(
            "123456789",
            "telefone inválido"
        )


def test_listar_clientes(banco_teste):
    clientes.cadastrar_cliente("111111111")
    clientes.cadastrar_cliente("222222222")

    resultado = clientes.listar_clientes()

    assert len(resultado) == 2
