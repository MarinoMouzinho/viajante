
import pytest

from app.agent.contexto import (
    obter_contexto_sistema,
    criar_mensagem_sistema
)


def test_obter_contexto_sistema():
    contexto = obter_contexto_sistema()

    assert isinstance(contexto, str)
    assert "Você é o Viajante" in contexto
    assert "português brasileiro" in contexto
    assert "intenções de reserva" in contexto


def test_adicionar_informacoes_agencia():
    informacoes = {
        "nome": "Sintaxe Turismo",
        "telefone": "(83) 3333-0000",
        "endereco": "Campina Grande - PB"
    }

    contexto = obter_contexto_sistema(informacoes)

    assert "Sintaxe Turismo" in contexto
    assert "(83) 3333-0000" in contexto
    assert "Campina Grande - PB" in contexto


def test_ignorar_informacoes_vazias():
    informacoes = {
        "nome": "Sintaxe Turismo",
        "telefone": "",
        "endereco": None
    }

    contexto = obter_contexto_sistema(informacoes)

    assert "Sintaxe Turismo" in contexto
    assert "telefone:" not in contexto
    assert "endereco:" not in contexto


def test_rejeitar_informacoes_invalidas():
    with pytest.raises(ValueError):
        obter_contexto_sistema("Sintaxe Turismo")


def test_criar_mensagem_sistema():
    mensagem = criar_mensagem_sistema()

    assert mensagem["role"] == "system"
    assert isinstance(mensagem["content"], str)
    assert "Você é o Viajante" in mensagem["content"]


def test_criar_mensagem_sistema_com_dados():
    mensagem = criar_mensagem_sistema({
        "nome": "Sintaxe Turismo"
    })

    assert mensagem["role"] == "system"
    assert "Sintaxe Turismo" in mensagem["content"]
