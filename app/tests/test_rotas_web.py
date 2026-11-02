
import pytest

from app.web.server import criar_aplicacao
from app.web import simulador, routes
from app.agent import memoria


@pytest.fixture
def cliente_web():
    aplicacao = criar_aplicacao()
    aplicacao.config["TESTING"] = True

    simulador._sessoes.clear()
    simulador._contador_clientes = 0
    memoria._memorias.clear()

    with aplicacao.test_client() as cliente:
        yield cliente

    simulador._sessoes.clear()
    simulador._contador_clientes = 0
    memoria._memorias.clear()


def test_pagina_inicial(cliente_web):
    resposta = cliente_web.get("/")

    assert resposta.status_code == 200


def test_criar_sessao_pela_api(cliente_web):
    resposta = cliente_web.post("/api/sessoes")

    dados = resposta.get_json()

    assert resposta.status_code == 201
    assert dados["sucesso"] is True
    assert dados["sessao"]["id"].startswith("sess_")


def test_enviar_mensagem_sem_conteudo(cliente_web):
    sessao = simulador.criar_sessao()

    resposta = cliente_web.post(
        f"/api/sessoes/{sessao['id']}/mensagens",
        json={"mensagem": ""}
    )

    assert resposta.status_code == 400

def test_enviar_mensagem_com_sessao_inexistente(cliente_web):
    resposta = cliente_web.post(
        "/api/sessoes/sess_inexistente/mensagens",
        json={"mensagem": "Olá"}
    )

    assert resposta.status_code == 404

def test_processar_mensagem_com_agente(cliente_web, monkeypatch):
    sessao = simulador.criar_sessao()

    def agente_simulado(mensagem, telegram_chat_id, historico):
        assert mensagem == "Olá!"
        assert telegram_chat_id == sessao["id"]

        return {
            "resposta": "Olá! Como posso ajudar?",
            "historico": [
                {
                    "role": "system",
                    "content": "Instruções do agente"
                },
                {
                    "role": "user",
                    "content": "Olá!"
                },
                {
                    "role": "assistant",
                    "content": "Olá! Como posso ajudar?"
                }
            ],
            "iteracoes": 0
        }

    monkeypatch.setattr(
        routes,
        "executar_agente",
        agente_simulado
    )

    resposta = cliente_web.post(
        f"/api/sessoes/{sessao['id']}/mensagens",
        json={"mensagem": "Olá!"}
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert dados["sucesso"] is True
    assert dados["resposta"] == "Olá! Como posso ajudar?"


def test_historico_e_salvo_apos_resposta(cliente_web, monkeypatch):
    sessao = simulador.criar_sessao()

    def agente_simulado(mensagem, telegram_chat_id, historico):
        return {
            "resposta": "Tudo certo!",
            "historico": [
                {"role": "system", "content": "Instruções"},
                {"role": "user", "content": mensagem},
                {"role": "assistant", "content": "Tudo certo!"}
            ],
            "iteracoes": 0
        }

    monkeypatch.setattr(
        routes,
        "executar_agente",
        agente_simulado
    )

    cliente_web.post(
        f"/api/sessoes/{sessao['id']}/mensagens",
        json={"mensagem": "Teste"}
    )

    resposta = cliente_web.get(
        f"/api/sessoes/{sessao['id']}/mensagens"
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200
    assert len(dados["mensagens"]) == 2
    assert dados["mensagens"][0]["content"] == "Teste"
    assert dados["mensagens"][1]["content"] == "Tudo certo!"


def test_historico_de_sessao_inexistente(cliente_web):
    resposta = cliente_web.get(
        "/api/sessoes/sess_inexistente/mensagens"
    )

    assert resposta.status_code == 404
