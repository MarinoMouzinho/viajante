from types import SimpleNamespace
import pytest
from app.agent import atividade_autonoma

def criar_resposta(conteudo=None, tool_calls=None):
    """
    Simula uma resposta serializada do SDK Groq.
    """

    dados = {
        "role": "assistant",
        "content": conteudo
    }

    if tool_calls is not None:
        dados["tool_calls"] = tool_calls

    mensagem = SimpleNamespace(
        model_dump=lambda exclude_none=True: {
            chave: valor
            for chave, valor in dados.items()
            if valor is not None
        }
    )

    return SimpleNamespace(
        choices=[
            SimpleNamespace(message=mensagem)
        ]
    )


def criar_chamada_ferramenta(
    nome,
    argumentos,
    identificador="call_123"
):
    return {
        "id": identificador,
        "type": "function",
        "function": {
            "name": nome,
            "arguments": argumentos
        }
    }


def test_resposta_sem_ferramentas(monkeypatch):
    monkeypatch.setattr(
        atividade_autonoma,
        "gerar_resposta",
        lambda **kwargs: criar_resposta(
            conteudo="Olá! Como posso ajudar?"
        )
    )

    resultado = atividade_autonoma.executar_agente(
        mensagem="Olá!",
        telegram_chat_id="123456789"
    )

    assert resultado["resposta"] == "Olá! Como posso ajudar?"
    assert resultado["iteracoes"] == 0
    assert resultado["historico"][0]["role"] == "system"
    assert resultado["historico"][1]["role"] == "user"


def test_execucao_de_ferramenta(monkeypatch):
    respostas = [
        criar_resposta(
            tool_calls=[
                criar_chamada_ferramenta(
                    "listar_viagens",
                    "{}"
                )
            ]
        ),
        criar_resposta(
            conteudo="Encontrei uma viagem disponível!"
        )
    ]

    chamadas_modelo = []
    chamadas_ferramenta = []

    def gerar_resposta(**kwargs):
        chamadas_modelo.append(kwargs)
        return respostas.pop(0)

    def executar_ferramenta(
        nome,
        argumentos,
        telegram_chat_id
    ):
        chamadas_ferramenta.append({
            "nome": nome,
            "argumentos": argumentos,
            "telegram_chat_id": telegram_chat_id
        })

        return {
            "sucesso": True,
            "dados": [{"id": "V001"}]
        }

    monkeypatch.setattr(
        atividade_autonoma,
        "gerar_resposta",
        gerar_resposta
    )

    monkeypatch.setattr(
        atividade_autonoma,
        "executar_ferramenta",
        executar_ferramenta
    )

    resultado = atividade_autonoma.executar_agente(
        mensagem="Quais viagens estão disponíveis?",
        telegram_chat_id="123456789"
    )

    assert resultado["resposta"] == (
        "Encontrei uma viagem disponível!"
    )

    assert resultado["iteracoes"] == 1

    assert chamadas_ferramenta[0]["nome"] == "listar_viagens"
    assert chamadas_ferramenta[0]["telegram_chat_id"] == "123456789"

    historico = resultado["historico"]

    assert historico[2]["role"] == "assistant"
    assert historico[3]["role"] == "tool"
    assert historico[3]["tool_call_id"] == "call_123"
    assert historico[4]["role"] == "assistant"

    assert len(chamadas_modelo) == 2


def test_identidade_autenticada_nao_e_substituida(
    monkeypatch
):
    chamadas = []

    resposta = criar_resposta(
        tool_calls=[
            criar_chamada_ferramenta(
                "consultar_intencoes",
                '{"telegram_chat_id": "999999999"}'
            )
        ]
    )

    respostas = [
        resposta,
        criar_resposta(conteudo="Você não possui intenções.")
    ]

    monkeypatch.setattr(
        atividade_autonoma,
        "gerar_resposta",
        lambda **kwargs: respostas.pop(0)
    )

    def executar_ferramenta(
        nome,
        argumentos,
        telegram_chat_id
    ):
        chamadas.append(telegram_chat_id)
        return {"sucesso": True, "dados": []}

    monkeypatch.setattr(
        atividade_autonoma,
        "executar_ferramenta",
        executar_ferramenta
    )

    atividade_autonoma.executar_agente(
        mensagem="Consulte minhas intenções.",
        telegram_chat_id="123456789"
    )

    assert chamadas == ["123456789"]


def test_limite_de_iteracoes(monkeypatch):
    chamadas_ferramenta = []
    chamadas_modelo = []

    resposta = criar_resposta(
        tool_calls=[
            criar_chamada_ferramenta(
                "listar_viagens",
                "{}"
            )
        ]
    )

    def gerar_resposta(**kwargs):
        chamadas_modelo.append(kwargs)
        return resposta

    def executar_ferramenta(**kwargs):
        chamadas_ferramenta.append(kwargs)
        return {"sucesso": True, "dados": []}

    monkeypatch.setattr(
        atividade_autonoma,
        "gerar_resposta",
        gerar_resposta
    )

    monkeypatch.setattr(
        atividade_autonoma,
        "executar_ferramenta",
        executar_ferramenta
    )

    resultado = atividade_autonoma.executar_agente(
        mensagem="Consulte as viagens.",
        telegram_chat_id="123456789",
        max_iteracoes=1
    )

    assert resultado["limite_atingido"] is True
    assert resultado["iteracoes"] == 1
    assert len(chamadas_ferramenta) == 1
    assert len(chamadas_modelo) == 2


def test_historico_anterior_e_preservado(monkeypatch):
    historico = [
        {
            "role": "system",
            "content": "Instruções anteriores."
        },
        {
            "role": "user",
            "content": "Olá!"
        },
        {
            "role": "assistant",
            "content": "Olá, como posso ajudar?"
        }
    ]

    monkeypatch.setattr(
        atividade_autonoma,
        "gerar_resposta",
        lambda **kwargs: criar_resposta(
            conteudo="Posso ajudar com viagens."
        )
    )

    resultado = atividade_autonoma.executar_agente(
        mensagem="Quero consultar viagens.",
        telegram_chat_id="123456789",
        historico=historico
    )

    assert resultado["historico"][0]["content"] == (
        "Instruções anteriores."
    )

    assert resultado["historico"][1]["content"] == "Olá!"

    assert resultado["historico"][-1]["content"] == (
        "Posso ajudar com viagens."
    )

    assert len(historico) == 3


def test_rejeitar_mensagem_vazia():
    with pytest.raises(ValueError):
        atividade_autonoma.executar_agente(
            mensagem=" ",
            telegram_chat_id="123456789"
        )


def test_rejeitar_identidade_vazia():
    with pytest.raises(ValueError):
        atividade_autonoma.executar_agente(
            mensagem="Olá",
            telegram_chat_id=""
        )


def test_rejeitar_limite_invalido():
    with pytest.raises(ValueError):
        atividade_autonoma.executar_agente(
            mensagem="Olá",
            telegram_chat_id="123456789",
            max_iteracoes=0
        )
