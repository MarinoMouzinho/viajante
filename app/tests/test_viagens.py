
import json
from pathlib import Path

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
