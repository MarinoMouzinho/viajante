import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

DIRETORIO_PROJETO = Path(__file__).resolve().parents[2]
load_dotenv(DIRETORIO_PROJETO / ".env")
_cliente = None

def obter_modelo() -> str:
    """
    Retorna o identificador do modelo configurado no ambiente.
    """

    modelo = os.getenv("LLM_MODEL", "").strip()
    if not modelo:
        raise RuntimeError(
            "O modelo LLM não foi configurado no arquivo .env."
        )
    return modelo

def obter_cliente() -> Groq:
    """
    Inicializa e retorna o cliente da Groq.
    """

    global _cliente
    if _cliente is None:
        chave_api = os.getenv("GROQ_API_KEY", "").strip()
        if not chave_api:
            raise RuntimeError(
                "A chave da API Groq não foi configurada no .env."
            )
        _cliente = Groq(api_key=chave_api)
    return _cliente


def gerar_resposta(
    mensagens: list,
    ferramentas: list | None = None,
    escolha_ferramenta: str = "auto",
    max_completion_tokens: int = 1024
):
    """
    Envia mensagens ao modelo e retorna a resposta.
    Ferramentas por meio de tool calling.
    """

    if not isinstance(mensagens, list) or not mensagens:
        raise ValueError(
            "A lista de mensagens não pode estar vazia."
        )

    if ferramentas is not None and not isinstance(ferramentas, list):
        raise ValueError(
            "As ferramentas devem ser fornecidas em uma lista."
        )

    if max_completion_tokens <= 0:
        raise ValueError(
            "O limite de tokens deve ser maior que zero."
        )

    parametros = {
        "model": obter_modelo(),
        "messages": mensagens,
        "max_completion_tokens": max_completion_tokens
    }

    if ferramentas:
        parametros["tools"] = ferramentas
        parametros["tool_choice"] = escolha_ferramenta
    
    cliente = obter_cliente()
    resposta = cliente.chat.completions.create(
        **parametros
    )

    return resposta
