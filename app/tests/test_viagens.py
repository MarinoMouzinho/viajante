
import json
from pathlib import Path
from app.services import viagens

DIRETORIO_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_VIAGENS = DIRETORIO_PROJETO / "app/data/viagens.json"

def test_arquivo_viagens_existe():
    assert CAMINHO_VIAGENS.exists()

def test_estrutura_json():
    with open(CAMINHO_VIAGENS, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    assert "viagens" in dados
    assert isinstance(dados["viagens"], list)

def test_viagens_possuem_titulo():
    with open(CAMINHO_VIAGENS, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    for viagem in dados["viagens"]:
        assert "titulo" in viagem
        assert viagem["titulo"]

def test_viagens_possuem_assentos():
    with open(CAMINHO_VIAGENS, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    for viagem in dados["viagens"]:
        assert "assentos" in viagem
        assert isinstance(viagem["assentos"], list)

def preparar_arquivo(tmp_path, monkeypatch, dados):
    caminho = tmp_path / "viagens.json"

    caminho.write_text(
        json.dumps(dados, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setenv("TRIPS_DATA_PATH", str(caminho))

    return caminho

def viagem_exemplo(
    id="V001",
    titulo="Excursão Serra do Rio do Rastro",
    status="disponivel",
    destino="Bom Jardim da Serra - SC",
    categorias=None
):
    return {
        "id": id,
        "titulo": titulo,
        "status": status,
        "origem": "Criciúma - SC",
        "destino": destino,
        "categorias": categorias or ["Excursão", "Turismo"]
    }

def test_carregar_viagens(tmp_path, monkeypatch):
    dados = {
        "viagens": [viagem_exemplo()]
    }

    preparar_arquivo(tmp_path, monkeypatch, dados)

    resultado = viagens.carregar_viagens()

    assert len(resultado) == 1
    assert resultado[0]["id"] == "V001"


def test_listar_viagens_disponiveis(tmp_path, monkeypatch):
    dados = {
        "viagens": [
            viagem_exemplo(id="V001"),
            viagem_exemplo(id="V002", status="cancelada"),
            viagem_exemplo(id="V003", status="encerrada")
        ]
    }

    preparar_arquivo(tmp_path, monkeypatch, dados)

    resultado = viagens.listar_viagens()

    assert len(resultado) == 1
    assert resultado[0]["id"] == "V001"


def test_listar_todas_viagens(tmp_path, monkeypatch):
    dados = {
        "viagens": [
            viagem_exemplo(id="V001"),
            viagem_exemplo(id="V002", status="cancelada")
        ]
    }

    preparar_arquivo(tmp_path, monkeypatch, dados)

    resultado = viagens.listar_viagens(disponiveis=False)

    assert len(resultado) == 2


def test_buscar_viagem_por_id(tmp_path, monkeypatch):
    dados = {
        "viagens": [
            viagem_exemplo(id="V001"),
            viagem_exemplo(id="V002")
        ]
    }

    preparar_arquivo(tmp_path, monkeypatch, dados)

    resultado = viagens.buscar_viagem_por_id("V002")

    assert resultado is not None
    assert resultado["id"] == "V002"


def test_buscar_viagem_inexistente(tmp_path, monkeypatch):
    dados = {"viagens": [viagem_exemplo()]}

    preparar_arquivo(tmp_path, monkeypatch, dados)

    resultado = viagens.buscar_viagem_por_id("V999")

    assert resultado is None


def test_buscar_por_termo(tmp_path, monkeypatch):
    dados = {
        "viagens": [
            viagem_exemplo(),
            viagem_exemplo(
                id="V002",
                titulo="Passeio Beto Carrero World",
                destino="Penha - SC"
            )
        ]
    }

    preparar_arquivo(tmp_path, monkeypatch, dados)

    resultado = viagens.buscar_viagens(termo="beto carrero")

    assert len(resultado) == 1
    assert resultado[0]["id"] == "V002"


def test_buscar_por_categoria(tmp_path, monkeypatch):
    dados = {
        "viagens": [
            viagem_exemplo(categorias=["Excursão", "Turismo"]),
            viagem_exemplo(
                id="V002",
                categorias=["Aventura", "Trilha"]
            )
        ]
    }

    preparar_arquivo(tmp_path, monkeypatch, dados)

    resultado = viagens.buscar_viagens(categoria="trilha")

    assert len(resultado) == 1
    assert resultado[0]["id"] == "V002"