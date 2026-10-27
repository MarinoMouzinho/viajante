
import json

from app.agent.contexto import criar_mensagem_sistema
from app.agent.tools import FERRAMENTAS, executar_ferramenta
from app.agent.modelo import gerar_resposta


def executar_agente(
    mensagem: str,
    telegram_chat_id: str,
    historico: list | None = None,
    max_iteracoes: int = 5
) -> dict:
    """
    Executa o ciclo do agente Viajante.
    """

    if not isinstance(mensagem, str) or not mensagem.strip():
        raise ValueError("A mensagem não pode estar vazia.")

    if (
        not isinstance(telegram_chat_id, str)
        or not telegram_chat_id.strip()
    ):
        raise ValueError("A identidade do cliente é obrigatória.")

    if (
        not isinstance(max_iteracoes, int)
        or isinstance(max_iteracoes, bool)
        or max_iteracoes < 1
    ):
        raise ValueError("O limite de iterações deve ser um inteiro positivo.")

    if historico is None:
        mensagens = [criar_mensagem_sistema()]
    elif isinstance(historico, list):
        mensagens = historico.copy()
    else:
        raise ValueError("O histórico deve ser uma lista.")

    if not mensagens or mensagens[0].get("role") != "system":
        mensagens.insert(0, criar_mensagem_sistema())

    mensagens.append({
        "role": "user",
        "content": mensagem.strip()
    })

    iteracoes = 0

    for rodada in range(max_iteracoes + 1):

        resposta = gerar_resposta(
            mensagens=mensagens,
            ferramentas=FERRAMENTAS
        )

        mensagem_assistente = resposta.choices[0].message

        # Converte a mensagem do SDK em dicionário
        mensagem_assistente = mensagem_assistente.model_dump(
            exclude_none=True
        )

        mensagens.append(mensagem_assistente)

        chamadas = mensagem_assistente.get("tool_calls")

        if not chamadas:
            conteudo = mensagem_assistente.get("content")

            return {
                "resposta": conteudo or "",
                "historico": mensagens,
                "iteracoes": iteracoes
            }

        if rodada == max_iteracoes:
            return {
                "resposta": (
                    "Não consegui concluir sua solicitação neste momento. "
                    "Por favor, tente novamente ou solicite atendimento humano."
                ),
                "historico": mensagens,
                "iteracoes": iteracoes,
                "limite_atingido": True
            }

        iteracoes += 1

        for chamada in chamadas:

            nome_ferramenta = chamada["function"]["name"]
            argumentos = chamada["function"]["arguments"]

            resultado = executar_ferramenta(
                nome=nome_ferramenta,
                argumentos=argumentos,
                telegram_chat_id=telegram_chat_id
            )

            conteudo_resultado = json.dumps(
                resultado,
                ensure_ascii=False,
                default=str
            )

            mensagens.append({
                "role": "tool",
                "tool_call_id": chamada["id"],
                "name": nome_ferramenta,
                "content": conteudo_resultado
            })

    return {
        "resposta": (
            "Não foi possível concluir sua solicitação. "
            "Tente novamente mais tarde."
        ),
        "historico": mensagens,
        "iteracoes": iteracoes,
        "limite_atingido": True
    }
