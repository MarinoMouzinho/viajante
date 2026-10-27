from copy import deepcopy

_memorias: dict[str, list[dict]] = {}

def obter_historico(telegram_chat_id: str) -> list[dict]:
    """
    Retorna uma cópia do histórico de conversas do cliente.
    """
    if not isinstance(telegram_chat_id, str) or not telegram_chat_id.strip():
        raise ValueError("O ID do Telegram é obrigatório.")

    return deepcopy(_memorias.get(telegram_chat_id, []))


def atualizar_historico(
    telegram_chat_id: str,
    historico: list[dict]
) -> None:
    """
    Atualiza o histórico de conversas de um cliente.
    """

    if not isinstance(telegram_chat_id, str) or not telegram_chat_id.strip():
        raise ValueError("O ID do Telegram é obrigatório.")

    if not isinstance(historico, list):
        raise ValueError("O histórico deve ser uma lista.")

    _memorias[telegram_chat_id] = deepcopy(historico)


def limpar_historico(telegram_chat_id: str) -> None:
    """
    Remove o histórico de conversas de um cliente.
    """

    if not isinstance(telegram_chat_id, str) or not telegram_chat_id.strip():
        raise ValueError("O ID do Telegram é obrigatório.")

    _memorias.pop(telegram_chat_id, None)
