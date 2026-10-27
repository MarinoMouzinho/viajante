
import pytest
from app.agent import modelo

def test_obter_modelo(monkeypatch):
    monkeypatch.setenv(
        "LLM_MODEL",
        "openai/gpt-oss-20b"
    )
    assert modelo.obter_modelo() == "openai/gpt-oss-20b"

def test_obter_modelo_sem_configuracao(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)

    with pytest.raises(RuntimeError):
        modelo.obter_modelo()

def test_obter_cliente(monkeypatch):
    cliente_falso = object()
    chamadas = []

    def criar_cliente(api_key):
        chamadas.append(api_key)
        return cliente_falso

    monkeypatch.setattr(modelo, "_cliente", None)
    monkeypatch.setattr(modelo, "Groq", criar_cliente)
    monkeypatch.setenv("GROQ_API_KEY", "chave_teste")

    primeiro = modelo.obter_cliente()
    segundo = modelo.obter_cliente()

    assert primeiro is cliente_falso
    assert segundo is cliente_falso
    assert chamadas == ["chave_teste"]


def test_obter_cliente_sem_chave(monkeypatch):
    monkeypatch.setattr(modelo, "_cliente", None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        modelo.obter_cliente()


def test_gerar_resposta(monkeypatch):
    resposta_falsa = object()
    chamadas = []

    class ClienteFalso:
        class chat:
            class completions:
                @staticmethod
                def create(**parametros):
                    chamadas.append(parametros)
                    return resposta_falsa

    monkeypatch.setattr(
        modelo,
        "obter_cliente",
        lambda: ClienteFalso()
    )

    monkeypatch.setattr(
        modelo,
        "obter_modelo",
        lambda: "openai/gpt-oss-20b"
    )

    mensagens = [
        {
            "role": "user",
            "content": "Olá!"
        }
    ]

    resultado = modelo.gerar_resposta(mensagens)

    assert resultado is resposta_falsa
    assert chamadas[0]["model"] == "openai/gpt-oss-20b"
    assert chamadas[0]["messages"] == mensagens
    assert "tools" not in chamadas[0]


def test_gerar_resposta_com_ferramentas(monkeypatch):
    chamadas = []

    class ClienteFalso:
        class chat:
            class completions:
                @staticmethod
                def create(**parametros):
                    chamadas.append(parametros)
                    return "resposta"

    monkeypatch.setattr(
        modelo,
        "obter_cliente",
        lambda: ClienteFalso()
    )

    monkeypatch.setattr(
        modelo,
        "obter_modelo",
        lambda: "openai/gpt-oss-20b"
    )

    ferramentas = [
        {
            "type": "function",
            "function": {
                "name": "listar_viagens",
                "description": "Lista as viagens disponíveis.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    modelo.gerar_resposta(
        mensagens=[{"role": "user", "content": "Quais viagens existem?"}],
        ferramentas=ferramentas
    )

    assert chamadas[0]["tools"] == ferramentas
    assert chamadas[0]["tool_choice"] == "auto"


def test_gerar_resposta_sem_mensagens():
    with pytest.raises(ValueError):
        modelo.gerar_resposta([])


def test_gerar_resposta_com_limite_invalido():
    with pytest.raises(ValueError):
        modelo.gerar_resposta(
            [{"role": "user", "content": "Olá"}],
            max_completion_tokens=0
        )
