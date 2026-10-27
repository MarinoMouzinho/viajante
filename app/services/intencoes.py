from app.database import repositorios
from app.services import clientes, viagens

PREFERENCIAS_ASSENTO = {
    "janela",
    "corredor",
    "indiferente"
}

def registrar_intencao(
    telegram_chat_id: str,
    viagem_id: str,
    quantidade: int,
    preferencia_assento: str = "indiferente"
) -> dict:
    """
    Registra uma intenção de reserva para uma viagem disponível.
    """

    telegram_chat_id = clientes.validar_telegram_chat_id(
        telegram_chat_id
    )

    if not isinstance(viagem_id, str) or not viagem_id.strip():
        raise ValueError("ID da viagem inválido.")

    viagem_id = viagem_id.strip()

    if isinstance(quantidade, bool) or not isinstance(quantidade, int):
        raise ValueError("A quantidade deve ser um número inteiro.")

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    if not isinstance(preferencia_assento, str):
        raise ValueError("Preferência de assento inválida.")

    preferencia_assento = preferencia_assento.strip().casefold()

    if preferencia_assento not in PREFERENCIAS_ASSENTO:
        raise ValueError(
            "Preferência inválida. Utilize janela, corredor ou indiferente."
        )

    cliente = clientes.buscar_cliente(telegram_chat_id)

    if not cliente:
        raise LookupError("Cliente não encontrado.")

    viagem = viagens.buscar_viagem_por_id(viagem_id)

    if not viagem:
        raise LookupError("Viagem não encontrada.")

    if viagem["status"] != "disponivel":
        raise ValueError(
            "Esta viagem não está disponível para novas intenções."
        )

    intencao_id = repositorios.inserir_intencao(
        cliente_id=cliente["id"],
        viagem_id=viagem_id,
        quantidade_passagens=quantidade,
        preferencia_assento=preferencia_assento
    )

    return {
        "id": intencao_id,
        "cliente_id": cliente["id"],
        "telegram_chat_id": telegram_chat_id,
        "viagem_id": viagem_id,
        "titulo_viagem": viagem["titulo"],
        "quantidade_passagens": quantidade,
        "preferencia_assento": preferencia_assento,
        "status": "pendente"
    }


def consultar_intencoes(telegram_chat_id: str) -> list:
    """
    Consulta todas as intenções de reserva de um cliente,
    incluindo informações da viagem correspondente.
    """

    telegram_chat_id = clientes.validar_telegram_chat_id(
        telegram_chat_id
    )

    cliente = clientes.buscar_cliente(telegram_chat_id)

    if not cliente:
        raise LookupError("Cliente não encontrado.")

    intencoes = repositorios.listar_intencoes_cliente(
        cliente["id"]
    )

    resultado = []

    for intencao in intencoes:
        viagem = viagens.buscar_viagem_por_id(
            intencao["viagem_id"]
        )

        dados_intencao = dict(intencao)

        if viagem:
            dados_intencao.update({
                "titulo_viagem": viagem.get("titulo"),
                "destino": viagem.get("destino"),
                "datahora_ida": viagem.get("datahora_ida"),
                "datahora_volta": viagem.get("datahora_volta")
            })
        else:
            dados_intencao.update({
                "titulo_viagem": "Viagem não encontrada",
                "destino": None,
                "datahora_ida": None,
                "datahora_volta": None
            })

        resultado.append(dados_intencao)

    return resultado


def cancelar_intencao(
    telegram_chat_id: str,
    intencao_id: int
) -> dict:
    """
    Cancela uma intenção pendente pertencente ao cliente.
    """

    telegram_chat_id = clientes.validar_telegram_chat_id(
        telegram_chat_id
    )

    if isinstance(intencao_id, bool) or not isinstance(intencao_id, int):
        raise ValueError("O ID da intenção deve ser um número inteiro.")

    if intencao_id <= 0:
        raise ValueError("O ID da intenção deve ser maior que zero.")

    cliente = clientes.buscar_cliente(telegram_chat_id)

    if not cliente:
        raise LookupError("Cliente não encontrado.")

    intencao = repositorios.obter_intencao(
        intencao_id=intencao_id,
        cliente_id=cliente["id"]
    )

    if not intencao:
        raise LookupError(
            "Intenção não encontrada ou não pertence a este cliente."
        )

    if intencao["status"] != "pendente":
        raise ValueError(
            "Somente intenções pendentes podem ser canceladas."
        )

    cancelado = repositorios.cancelar_intencao(
        intencao_id=intencao_id,
        cliente_id=cliente["id"]
    )

    if not cancelado:
        raise ValueError(
            "Não foi possível cancelar a intenção. "
            "Verifique se ela ainda está pendente."
        )

    intencao["status"] = "cancelada"

    return intencao