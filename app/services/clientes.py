
from app.database import repositorios


def validar_telegram_chat_id(telegram_chat_id: str) -> str:
    """
    Valida e normaliza o identificador do Telegram.
    """

    if not isinstance(telegram_chat_id, str):
        raise ValueError("O ID do Telegram deve ser textual.")

    telegram_chat_id = telegram_chat_id.strip()

    if not telegram_chat_id or not telegram_chat_id.isdigit():
        raise ValueError("ID do Telegram inválido.")

    return telegram_chat_id


def validar_telefone(telefone: str | None) -> str | None:
    """
    Valida o telefone informado pelo cliente.
    """

    if telefone is None:
        return None

    if not isinstance(telefone, str):
        raise ValueError("O telefone deve ser informado como texto.")

    telefone = telefone.strip()

    if not telefone:
        return None

    digitos = "".join(
        caractere
        for caractere in telefone
        if caractere.isdigit()
    )

    caracteres_permitidos = set("0123456789+()- ")

    if (
        any(caractere not in caracteres_permitidos
            for caractere in telefone)
        or len(digitos) < 8
        or len(digitos) > 15
    ):
        raise ValueError("Número de telefone inválido.")

    return telefone


def validar_nome_telegram(nome_telegram: str | None) -> str | None:
    """
    Valida e normaliza o nome recebido do Telegram.
    """

    if nome_telegram is None:
        return None

    if not isinstance(nome_telegram, str):
        raise ValueError("O nome deve ser informado como texto.")

    nome_telegram = nome_telegram.strip()

    return nome_telegram or None


def cadastrar_cliente(
    telegram_chat_id: str,
    telefone: str | None = None,
    nome_telegram: str | None = None
) -> dict:
    """
    Cadastra um novo cliente.
    """

    telegram_chat_id = validar_telegram_chat_id(telegram_chat_id)
    telefone = validar_telefone(telefone)
    nome_telegram = validar_nome_telegram(nome_telegram)

    if repositorios.obter_cliente(telegram_chat_id):
        raise ValueError("Cliente já cadastrado.")

    repositorios.inserir_cliente(
        telegram_chat_id=telegram_chat_id,
        telefone=telefone,
        nome_telegram=nome_telegram
    )

    return repositorios.obter_cliente(telegram_chat_id)


def buscar_cliente(telegram_chat_id: str) -> dict | None:
    """
    Consulta um cliente pelo identificador do Telegram.
    """

    telegram_chat_id = validar_telegram_chat_id(telegram_chat_id)

    return repositorios.obter_cliente(telegram_chat_id)


def buscar_cliente_por_id(cliente_id: int) -> dict | None:
    """
    Consulta um cliente pelo identificador interno.
    """

    if isinstance(cliente_id, bool) or not isinstance(cliente_id, int):
        raise ValueError("ID interno do cliente inválido.")

    if cliente_id <= 0:
        raise ValueError("ID interno do cliente inválido.")

    return repositorios.obter_cliente_por_id(cliente_id)


def atualizar_telefone_cliente(
    telegram_chat_id: str,
    telefone: str
) -> dict:
    """
    Atualiza o telefone de um cliente cadastrado.
    """

    telegram_chat_id = validar_telegram_chat_id(telegram_chat_id)
    telefone = validar_telefone(telefone)

    if telefone is None:
        raise ValueError("O telefone não pode ser vazio.")

    atualizado = repositorios.atualizar_telefone(
        telegram_chat_id,
        telefone
    )

    if not atualizado:
        raise LookupError("Cliente não encontrado.")

    return repositorios.obter_cliente(telegram_chat_id)

def listar_clientes() -> list:
    """
    Lista os clientes cadastrados.
    """
    return repositorios.listar_clientes()