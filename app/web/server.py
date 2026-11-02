from flask import Flask
from app.web.routes import web

def criar_aplicacao() -> Flask:
    aplicacao = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    aplicacao.register_blueprint(web)
    return aplicacao

app = criar_aplicacao()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )