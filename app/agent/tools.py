import json
from app.services import clientes, demandas, intencoes, viagens

FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "listar_viagens",
            "description": (
                "Lista as viagens atualmente disponíveis na agência, "
                "incluindo destinos, datas e preços cadastrados."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_viagens",
            "description": (
                "Pesquisa viagens por um termo ou categoria. "
                "Utilize quando o cliente procurar um destino ou "
                "tipo específico de viagem."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "termo": {
                        "type": "string",
                        "description": (
                            "Termo de pesquisa, como destino ou "
                            "nome de uma excursão."
                        )
                    },
                    "categoria": {
                        "type": "string",
                        "description": (
                            "Categoria da viagem, quando conhecida."
                        )
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "atualizar_telefone",
            "description": (
                "Cadastra ou atualiza o telefone de contato do "
                "cliente autenticado. Utilize somente quando o "
                "cliente fornecer explicitamente um telefone."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "telefone": {
                        "type": "string",
                        "description": "Telefone fornecido pelo cliente."
                    }
                },
                "required": ["telefone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_intencao",
            "description": (
                "Registra uma intenção de reserva para uma viagem "
                "disponível. Não realiza reserva definitiva."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "viagem_id": {
                        "type": "string",
                        "description": (
                            "Identificador da viagem desejada, "
                            "obtido por meio das ferramentas de consulta."
                        )
                    },
                    "quantidade": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Quantidade de passagens desejada."
                    },
                    "preferencia_assento": {
                        "type": "string",
                        "enum": ["janela", "corredor", "indiferente"],
                        "description": "Preferência de assento do cliente."
                    }
                },
                "required": ["viagem_id", "quantidade"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_intencoes",
            "description": (
                "Consulta as intenções de reserva do cliente "
                "autenticado. Não recebe identificadores de clientes."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancelar_intencao",
            "description": (
                "Cancela uma intenção de reserva pertencente "
                "ao cliente autenticado."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "intencao_id": {
                        "type": "integer",
                        "minimum": 1,
                        "description": (
                            "Identificador da intenção que o cliente "
                            "deseja cancelar."
                        )
                    }
                },
                "required": ["intencao_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_demanda",
            "description": (
                "Registra o interesse do cliente em um destino "
                "ou evento que não possui viagem disponível."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "destino": {
                        "type": "string",
                        "description": "Destino desejado."
                    },
                    "evento": {
                        "type": "string",
                        "description": (
                            "Evento relacionado ao destino, se houver."
                        )
                    },
                    "periodo": {
                        "type": "string",
                        "description": (
                            "Período desejado para a viagem, se informado."
                        )
                    }
                },
                "required": ["destino"]
            }
        }
    }
]


def _obter_argumentos(argumentos) -> dict:
    """
    Converte os argumentos recebidos do modelo em um dicionário.
    """
    if isinstance(argumentos, str):
        try:
            argumentos = json.loads(argumentos)
        except json.JSONDecodeError as erro:
            raise ValueError(
                "Os argumentos da ferramenta não possuem JSON válido."
            ) from erro

    if argumentos is None:
        return {}

    if not isinstance(argumentos, dict):
        raise ValueError(
            "Os argumentos da ferramenta devem ser um objeto."
        )

    return argumentos


def _obter_identidade(telegram_chat_id: str | None) -> str:
    """
    Obtém a identidade autenticada fornecida pela aplicação.
    Essa informação nunca deve ser recebida dos argumentos do modelo.
    """

    if not isinstance(telegram_chat_id, str) or not telegram_chat_id.strip():
        raise ValueError(
            "Não foi possível identificar o cliente autenticado."
        )

    return telegram_chat_id


def executar_ferramenta(
    nome: str,
    argumentos=None,
    telegram_chat_id: str | None = None
) -> dict:
    """
    Executa uma ferramenta solicitada pelo modelo.
    A identidade do cliente é recebida separadamente dos argumentos
    produzidos pelo modelo.
    """

    if not isinstance(nome, str) or not nome.strip():
        return {
            "sucesso": False,
            "erro": "Nome da ferramenta inválido."
        }

    try:
        argumentos = _obter_argumentos(argumentos)

        if nome == "listar_viagens":
            resultado = viagens.listar_viagens()

        elif nome == "buscar_viagens":
            resultado = viagens.buscar_viagens(
                termo=argumentos.get("termo"),
                categoria=argumentos.get("categoria")
            )

        elif nome == "atualizar_telefone":
            identidade = _obter_identidade(telegram_chat_id)

            if "telefone" not in argumentos:
                raise ValueError(
                    "O telefone precisa ser informado."
                )

            resultado = clientes.atualizar_telefone_cliente(
                telegram_chat_id=identidade,
                telefone=argumentos["telefone"]
            )

        elif nome == "registrar_intencao":
            identidade = _obter_identidade(telegram_chat_id)

            resultado = intencoes.registrar_intencao(
                telegram_chat_id=identidade,
                viagem_id=argumentos.get("viagem_id"),
                quantidade=argumentos.get("quantidade"),
                preferencia_assento=argumentos.get(
                    "preferencia_assento",
                    "indiferente"
                )
            )

        elif nome == "consultar_intencoes":
            identidade = _obter_identidade(telegram_chat_id)

            resultado = intencoes.consultar_intencoes(
                telegram_chat_id=identidade
            )

        elif nome == "cancelar_intencao":
            identidade = _obter_identidade(telegram_chat_id)

            resultado = intencoes.cancelar_intencao(
                telegram_chat_id=identidade,
                intencao_id=argumentos.get("intencao_id")
            )

        elif nome == "registrar_demanda":
            identidade = _obter_identidade(telegram_chat_id)

            resultado = demandas.registrar_demanda(
                telegram_chat_id=identidade,
                destino=argumentos.get("destino"),
                evento=argumentos.get("evento"),
                periodo=argumentos.get("periodo")
            )

        else:
            return {
                "sucesso": False,
                "erro": f"Ferramenta desconhecida: {nome}."
            }

        return {
            "sucesso": True,
            "dados": resultado
        }

    except (ValueError, LookupError, TypeError) as erro:
        return {
            "sucesso": False,
            "erro": str(erro)
        }
