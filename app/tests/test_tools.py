
import pytest

from app.agent import tools


def test_ferramentas_definidas():
    nomes = {
        ferramenta["function"]["name"]
        for ferramenta in tools.FERRAMENTAS
    }

    assert nomes == {
        "listar_viagens",
        "buscar_viagens",
        "atualizar_telefone",
        "registrar_intencao",
        "consultar_intencoes",
        "cancelar_intencao",
        "registrar_demanda"
    }


def test_ferramentas_nao_expoem_identidade():
    for ferramenta in tools.FERRAMENTAS:
        propriedades = ferramenta["function"]["parameters"]["properties"]

        assert "telegram_chat_id" not in propriedades
        assert "cliente_id" not in propriedades


def test_listar_viagens(monkeypatch):
    viagens_teste = [
        {"id": "V001", "titulo": "Excursão de teste"}
    ]

    monkeypatch.setattr(
        tools.viagens,
        "listar_viagens",
        lambda: viagens_teste
    )

    resultado = tools.executar_ferramenta(
        "listar_viagens",
        {}
    )

    assert resultado["sucesso"] is True
    assert resultado["dados"] == viagens_teste


def test_buscar_viagens(monkeypatch):
    chamadas = []

    def buscar_viagens(termo=None, categoria=None):
        chamadas.append({
            "termo": termo,
            "categoria": categoria
        })
        return []

    monkeypatch.setattr(
        tools.viagens,
        "buscar_viagens",
        buscar_viagens
    )

    resultado = tools.executar_ferramenta(
        "buscar_viagens",
        {
            "termo": "Serra",
            "categoria": "Turismo"
        }
    )

    assert resultado["sucesso"] is True
    assert chamadas[0]["termo"] == "Serra"
    assert chamadas[0]["categoria"] == "Turismo"


def test_registrar_intencao_utiliza_identidade_autenticada(
    monkeypatch
):
    chamadas = []

    def registrar_intencao(**kwargs):
        chamadas.append(kwargs)
        return {"id": 1, "status": "pendente"}

    monkeypatch.setattr(
        tools.intencoes,
        "registrar_intencao",
        registrar_intencao
    )

    resultado = tools.executar_ferramenta(
        "registrar_intencao",
        {
            "viagem_id": "V001",
            "quantidade": 2,
            "telegram_chat_id": "999999999"
        },
        telegram_chat_id="123456789"
    )

    assert resultado["sucesso"] is True
    assert chamadas[0]["telegram_chat_id"] == "123456789"
    assert chamadas[0]["quantidade"] == 2


def test_consultar_intencoes_utiliza_identidade_autenticada(
    monkeypatch
):
    chamadas = []

    def consultar_intencoes(telegram_chat_id):
        chamadas.append(telegram_chat_id)
        return []

    monkeypatch.setattr(
        tools.intencoes,
        "consultar_intencoes",
        consultar_intencoes
    )

    resultado = tools.executar_ferramenta(
        "consultar_intencoes",
        {},
        telegram_chat_id="123456789"
    )

    assert resultado["sucesso"] is True
    assert chamadas == ["123456789"]


def test_cancelar_intencao(monkeypatch):
    chamadas = []

    def cancelar_intencao(telegram_chat_id, intencao_id):
        chamadas.append((telegram_chat_id, intencao_id))
        return {"id": intencao_id, "status": "cancelada"}

    monkeypatch.setattr(
        tools.intencoes,
        "cancelar_intencao",
        cancelar_intencao
    )

    resultado = tools.executar_ferramenta(
        "cancelar_intencao",
        {"intencao_id": 5},
        telegram_chat_id="123456789"
    )

    assert resultado["sucesso"] is True
    assert chamadas == [("123456789", 5)]


def test_registrar_demanda(monkeypatch):
    chamadas = []

    def registrar_demanda(**kwargs):
        chamadas.append(kwargs)
        return {"id": 1, "destino": "aracuarinha"}

    monkeypatch.setattr(
        tools.demandas,
        "registrar_demanda",
        registrar_demanda
    )

    resultado = tools.executar_ferramenta(
        "registrar_demanda",
        {
            "destino": "Aracuarinha",
            "evento": "Festa",
            "periodo": "Dezembro"
        },
        telegram_chat_id="123456789"
    )

    assert resultado["sucesso"] is True
    assert chamadas[0]["telegram_chat_id"] == "123456789"
    assert chamadas[0]["destino"] == "Aracuarinha"


def test_ferramenta_sem_identidade_autenticada():
    resultado = tools.executar_ferramenta(
        "consultar_intencoes",
        {}
    )

    assert resultado["sucesso"] is False
    assert "autenticado" in resultado["erro"]


def test_ferramenta_desconhecida():
    resultado = tools.executar_ferramenta(
        "ferramenta_inexistente",
        {}
    )

    assert resultado["sucesso"] is False
    assert "desconhecida" in resultado["erro"]


def test_argumentos_json():
    resultado = tools._obter_argumentos(
        '{"termo": "Serra"}'
    )

    assert resultado == {"termo": "Serra"}


def test_argumentos_json_invalido():
    with pytest.raises(ValueError):
        tools._obter_argumentos("{json inválido}")


def test_argumentos_em_formato_invalido():
    with pytest.raises(ValueError):
        tools._obter_argumentos(["valor"])
