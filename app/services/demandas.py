
from app.database import repositorios
from app.services import clientes


def validar_texto_demanda(
    valor: str | None,
    campo: str,
    obrigatorio: bool = False
) -> str:
    """
    Valida e normaliza os textos utilizados em uma demanda.
    """

    if valor is None:
        if obrigatorio:
            raise ValueError(f"{campo} não informado.")

        return ""

    if not isinstance(valor, str):
        raise ValueError(f"{campo} deve ser informado como texto.")

    valor = " ".join(valor.strip().split())

    if obrigatorio and not valor:
        raise ValueError(f"{campo} não pode ser vazio.")

    return valor.casefold()


def registrar_demanda(
    telegram_chat_id: str,
    destino: str,
    evento: str | None = None,
    periodo: str | None = None
) -> dict:
    """
    Registra uma demanda de viagem e associa o cliente interessado.
    """

    telegram_chat_id = clientes.validar_telegram_chat_id(
        telegram_chat_id
    )

    destino = validar_texto_demanda(
        destino,
        "Destino",
        obrigatorio=True
    )

    evento = validar_texto_demanda(
        evento,
        "Evento"
    )

    periodo = validar_texto_demanda(
        periodo,
        "Período"
    )

    cliente = clientes.buscar_cliente(telegram_chat_id)

    if not cliente:
        raise LookupError("Cliente não encontrado.")

    demanda = repositorios.registrar_demanda(
        cliente_id=cliente["id"],
        destino=destino,
        evento=evento,
        periodo=periodo
    )

    return {
        **demanda,
        "telegram_chat_id": telegram_chat_id
    }


def validar_demanda_id(demanda_id: int) -> int:
    """
    Valida o identificador interno de uma demanda.
    """

    if isinstance(demanda_id, bool) or not isinstance(demanda_id, int):
        raise ValueError("O ID da demanda deve ser um número inteiro.")

    if demanda_id <= 0:
        raise ValueError("ID da demanda inválido.")

    return demanda_id


def listar_demandas(status: str = "ativa") -> list:
    """
    Lista demandas de acordo com seu status.

    Valores aceitos:
    - ativa
    - inativa
    - todas
    """

    if not isinstance(status, str):
        raise ValueError("Status da demanda inválido.")

    status = status.strip().casefold()

    if status == "todas":
        return repositorios.listar_demandas(status=None)

    if status not in ("ativa", "inativa"):
        raise ValueError(
            "Status inválido. Utilize ativa, inativa ou todas."
        )

    return repositorios.listar_demandas(status=status)


def buscar_demanda(demanda_id: int) -> dict:
    """
    Busca uma demanda específica pelo seu identificador.
    """

    demanda_id = validar_demanda_id(demanda_id)

    demanda = repositorios.obter_demanda(demanda_id)

    if not demanda:
        raise LookupError("Demanda não encontrada.")

    return demanda


def listar_interessados(demanda_id: int) -> list:
    """
    Lista os clientes interessados em uma demanda específica.
    """

    demanda_id = validar_demanda_id(demanda_id)

    demanda = repositorios.obter_demanda(demanda_id)

    if not demanda:
        raise LookupError("Demanda não encontrada.")

    return repositorios.listar_interessados_demanda(demanda_id)