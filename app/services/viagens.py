import json
import os
from pathlib import Path
from dotenv import load_dotenv

DIRETORIO_PROJETO = Path(__file__).resolve().parents[2]
load_dotenv(DIRETORIO_PROJETO / ".env")

def obter_caminho_viagens() -> Path:
    """
    Retorna o caminho do arquivo de viagens.
    """
    caminho = Path(os.getenv("TRIPS_DATA_PATH", "app/data/viagens.json"))
    if not caminho.is_absolute():
        caminho = DIRETORIO_PROJETO / caminho
    return caminho

def carregar_viagens() -> list:
    """
    Carrega as viagens cadastradas no JSON. Retorna uma lista de dicionários.
    """

    caminho = obter_caminho_viagens()
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de viagens não encontrado: {caminho}"
        )
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict) or not isinstance(dados.get("viagens"), list):
        raise ValueError(
            "Estrutura inválida no arquivo de viagens."
        )

    viagens = dados["viagens"]
    ids = set()
    for viagem in viagens:
        if not isinstance(viagem, dict):
            raise ValueError("Registro de viagem inválido.")

        campos_obrigatorios = ("id", "titulo", "status")
        for campo in campos_obrigatorios:
            if not viagem.get(campo):
                raise ValueError(f"Viagem sem o campo obrigatório: {campo}")
        if viagem["id"] in ids:
            raise ValueError(f"Identificador de viagem duplicado: {viagem['id']}")

        ids.add(viagem["id"])
        if viagem["status"] not in ("disponivel", "cancelada", "encerrada"):
            raise ValueError(f"Status inválido na viagem {viagem['id']}.")
        
    return viagens


def listar_viagens(disponiveis: bool = True) -> list:
    """
    Lista as viagens cadastradas. Padrão: Somente viagens disponíveis.
    """

    viagens = carregar_viagens()
    if disponiveis:
        viagens = [ viagem for viagem in viagens if viagem["status"] == "disponivel"]
    return viagens

def buscar_viagem_por_id(viagem_id: str) -> dict | None:
    """
    Localiza uma viagem pelo seu identificador.
    """

    viagens = carregar_viagens()
    for viagem in viagens:
        if viagem["id"] == viagem_id:
            return viagem
    return None

def buscar_viagens(
    termo: str | None = None,
    categoria: str | None = None
) -> list:
    """
    Busca viagens disponíveis por título, origem,
    destino ou categoria.
    """

    viagens = listar_viagens()
    if termo:
        termo = termo.strip().casefold()
        viagens = [
            viagem
            for viagem in viagens
            if termo in viagem["titulo"].casefold()
            or termo in viagem["origem"].casefold()
            or termo in viagem["destino"].casefold()
        ]

    if categoria:
        categoria = categoria.strip().casefold()
        viagens = [
            viagem
            for viagem in viagens
            if any(
                categoria in item.casefold()
                for item in viagem.get("categorias", [])
            )
        ]
    return viagens