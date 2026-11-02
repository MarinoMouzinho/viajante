from flask import Blueprint, jsonify, render_template, request
from app.agent import memoria
from app.agent.atividade_autonoma import executar_agente
from app.web import simulador

web = Blueprint("web", __name__)

@web.route("/")
def index():
    return render_template("index.html")

@web.route("/api/sessoes", methods=["GET"])
def obter_sessoes():
    return jsonify({
        "sucesso": True,
        "sessoes": simulador.listar_sessoes()
    })

@web.route("/api/sessoes", methods=["POST"])
def criar_sessao():
    sessao = simulador.criar_sessao()
    return jsonify({
        "sucesso": True,
        "sessao": sessao
    }), 201

@web.route("/api/sessoes/<sessao_id>", methods=["GET"])
def obter_sessao(sessao_id):
    try:
        sessao = simulador.buscar_sessao(sessao_id)
        return jsonify({
            "sucesso": True,
            "sessao": sessao
        })
    except (ValueError, LookupError) as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 404

@web.route("/api/sessoes/<sessao_id>", methods=["DELETE"])
def encerrar_sessao(sessao_id):
    try:
        simulador.encerrar_sessao(sessao_id)
        return jsonify({
            "sucesso": True,
            "mensagem": "Sessão encerrada."
        })
    except (ValueError, LookupError) as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 404


@web.route("/api/sessoes/<sessao_id>/limpar", methods=["POST"])
def limpar_sessao(sessao_id):
    try:
        simulador.limpar_sessao(sessao_id)
        return jsonify({
            "sucesso": True,
            "mensagem": "Histórico da sessão limpo."
        })
    except (ValueError, LookupError) as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 404


@web.route("/api/sessoes/<sessao_id>/mensagens", methods=["GET"])
def obter_mensagens(sessao_id):
    try:
        simulador.buscar_sessao(sessao_id)

        historico = memoria.obter_historico(sessao_id)

        mensagens = [
            {
                "role": mensagem["role"],
                "content": mensagem["content"]
            }
            for mensagem in historico
            if mensagem.get("role") in ("user", "assistant")
            and mensagem.get("content")
        ]

        return jsonify({
            "sucesso": True,
            "mensagens": mensagens
        })

    except (ValueError, LookupError) as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 404


@web.route("/api/sessoes/<sessao_id>/mensagens", methods=["POST"])
def enviar_mensagem(sessao_id):
    try:
        simulador.buscar_sessao(sessao_id)
        dados = request.get_json(silent=True)

        if not isinstance(dados, dict):
            return jsonify({
                "sucesso": False,
                "erro": "O corpo da requisição deve ser um objeto JSON."
            }), 400

        mensagem = dados.get("mensagem")

        if not isinstance(mensagem, str) or not mensagem.strip():
            return jsonify({
                "sucesso": False,
                "erro": "Digite uma mensagem antes de enviar."
            }), 400

        historico = memoria.obter_historico(sessao_id)

        resultado = executar_agente(
            mensagem=mensagem,
            telegram_chat_id=sessao_id,
            historico=historico
        )

        memoria.atualizar_historico(
            sessao_id,
            resultado["historico"]
        )

        return jsonify({
            "sucesso": True,
            "resposta": resultado["resposta"],
            "iteracoes": resultado["iteracoes"],
            "limite_atingido": resultado.get("limite_atingido", False)
        })

    except LookupError as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 404

    except ValueError as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 400

    except Exception:
        return jsonify({
            "sucesso": False,
            "erro": "Ocorreu um erro ao processar sua mensagem."
        }), 500
