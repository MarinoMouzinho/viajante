from datetime import datetime
from threading import Lock
from uuid import uuid4

from app.agent import memoria

_sessoes: dict[str, dict] = {}
_contador_clientes = 0
_trava = Lock()

def criar_sessao() -> dict:
    """
    Cria uma nova sessão.
    """

    global _contador_clientes

    with _trava:
        _contador_clientes += 1
        identificador = f"sess_{uuid4().hex[:12]}"
        sessao = {
            "id": identificador,
            "cliente": f"Cliente de teste {_contador_clientes:03d}",
            "estado": "ativa",
            "criada_em": datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
        }
        _sessoes[identificador] = sessao
        memoria.atualizar_historico(identificador, [])
        return sessao.copy()


def listar_sessoes() -> list[dict]:
    """
    Retorna todas as sessões ativas do simulador.
    """
    with _trava:
        return [
            sessao.copy()
            for sessao in _sessoes.values()
        ]


def buscar_sessao(sessao_id: str) -> dict:
    """
    Busca uma sessão pelo identificador.
    """

    if not isinstance(sessao_id, str) or not sessao_id.strip():
        raise ValueError("O id da sessão é obrigatório.")

    with _trava:
        sessao = _sessoes.get(sessao_id)
        if sessao is None:
            raise LookupError("Sessão não encontrada.")
        return sessao.copy()


def encerrar_sessao(sessao_id: str) -> None:
    """
    Encerra uma sessão e remove seu histórico da memória.
    """

    if not isinstance(sessao_id, str) or not sessao_id.strip():
        raise ValueError("O id da sessão é obrigatório.")
    with _trava:
        if sessao_id not in _sessoes:
            raise LookupError("Sessão não encontrada.")
        del _sessoes[sessao_id]
        memoria.limpar_historico(sessao_id)


def limpar_sessao(sessao_id: str) -> None:
    """
    Limpa o histórico de uma sessão sem encerrá-la.
    """

    if not isinstance(sessao_id, str) or not sessao_id.strip():
        raise ValueError("O id da sessão é obrigatório.")
    with _trava:
        if sessao_id not in _sessoes:
            raise LookupError("Sessão não encontrada.")

        memoria.limpar_historico(sessao_id)
