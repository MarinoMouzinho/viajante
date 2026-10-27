from contextlib import closing
from app.database.conexao import conectar

def inicializar_banco():
    """
    Cria as tabelas iniciais do banco de dados, caso ainda não existam.
    """
    conexao = conectar()
    try:
        conexao.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_chat_id TEXT NOT NULL UNIQUE,
                nome_telegram TEXT,
                telefone TEXT,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS intencoes_reserva (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                viagem_id TEXT NOT NULL,
                quantidade_passagens INTEGER NOT NULL
                    CHECK (quantidade_passagens > 0),
                preferencia_assento TEXT,
                status TEXT NOT NULL DEFAULT 'pendente'
                    CHECK (status IN (
                        'pendente',
                        'cancelada',
                        'concluida'
                    )),
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id)
            );
            CREATE TABLE IF NOT EXISTS demandas_viagem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destino TEXT NOT NULL,
                evento TEXT NOT NULL DEFAULT '',
                periodo TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'ativa'
                    CHECK (status IN ('ativa', 'inativa')),
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (destino, evento, periodo)
            );
            CREATE TABLE IF NOT EXISTS interessados_demanda (
                demanda_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (demanda_id, cliente_id),
                FOREIGN KEY (demanda_id)
                    REFERENCES demandas_viagem(id),
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id)
            );
            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL UNIQUE,
                estado TEXT NOT NULL DEFAULT 'ativa'
                    CHECK (estado IN (
                        'ativa',
                        'aguardando_humano',
                        'atendimento_humano'
                    )),
                atualizada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id)
            );
        """)

        conexao.commit()
    finally:
        conexao.close()

def inserir_cliente(
    telegram_chat_id: str,
    telefone: str | None = None,
    nome_telegram: str | None = None
) -> int:
    """
    Insere um novo cliente e retorna seu ID interno.
    """
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.execute("""
                INSERT INTO clientes (
                    telegram_chat_id,
                    nome_telegram,
                    telefone
                )
                VALUES (?, ?, ?)
            """, (
                telegram_chat_id,
                nome_telegram,
                telefone
            ))

            return cursor.lastrowid


def obter_cliente(telegram_chat_id: str) -> dict | None:
    """
    Busca um cliente pelo identificador do Telegram.
    """
    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT
                id,
                telegram_chat_id,
                nome_telegram,
                telefone,
                criado_em
            FROM clientes
            WHERE telegram_chat_id = ?
        """, (telegram_chat_id,))
        cliente = resultado.fetchone()
        return dict(cliente) if cliente else None


def obter_cliente_por_id(cliente_id: int) -> dict | None:
    """
    Busca um cliente pelo seu identificador interno.
    """
    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT
                id,
                telegram_chat_id,
                nome_telegram,
                telefone,
                criado_em
            FROM clientes
            WHERE id = ?
        """, (cliente_id,))
        cliente = resultado.fetchone()
        return dict(cliente) if cliente else None


def atualizar_telefone(telegram_chat_id: str, telefone: str) -> bool:
    """
    Atualiza o telefone de um cliente existente.
    """
    with closing(conectar()) as conexao:
        with conexao:
            resultado = conexao.execute("""
                UPDATE clientes
                SET telefone = ?
                WHERE telegram_chat_id = ?
            """, (telefone, telegram_chat_id))
            return resultado.rowcount > 0


def listar_clientes() -> list:
    """
    Retorna todos os clientes cadastrados.
    """
    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT
                id,
                telegram_chat_id,
                nome_telegram,
                telefone,
                criado_em
            FROM clientes
            ORDER BY criado_em DESC
        """)
        return [dict(cliente) for cliente in resultado.fetchall()]

def inserir_intencao(
    cliente_id: int,
    viagem_id: str,
    quantidade_passagens: int,
    preferencia_assento: str
) -> int:
    """
    Insere uma intenção de reserva e retorna seu ID.
    Recebe o ID interno do cliente, não o identificador do Telegram.
    """
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.execute("""
                INSERT INTO intencoes_reserva (
                    cliente_id,
                    viagem_id,
                    quantidade_passagens,
                    preferencia_assento
                )
                VALUES (?, ?, ?, ?)
            """, (
                cliente_id,
                viagem_id,
                quantidade_passagens,
                preferencia_assento
            ))
            return cursor.lastrowid


def obter_intencao(
    intencao_id: int,
    cliente_id: int
) -> dict | None:
    """
    Busca uma intenção pertencente a um cliente específico.
    """
    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT
                id,
                cliente_id,
                viagem_id,
                quantidade_passagens,
                preferencia_assento,
                status,
                criado_em
            FROM intencoes_reserva
            WHERE id = ?
              AND cliente_id = ?
        """, (intencao_id, cliente_id))
        intencao = resultado.fetchone()
        return dict(intencao) if intencao else None


def listar_intencoes_cliente(cliente_id: int) -> list:
    """
    Lista as intenções de um cliente.
    """
    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT
                id,
                cliente_id,
                viagem_id,
                quantidade_passagens,
                preferencia_assento,
                status,
                criado_em
            FROM intencoes_reserva
            WHERE cliente_id = ?
            ORDER BY criado_em DESC
        """, (cliente_id,))
        return [dict(intencao) for intencao in resultado.fetchall()]

def cancelar_intencao(
    intencao_id: int,
    cliente_id: int
) -> bool:
    """
    Cancela uma intenção pendente pertencente ao cliente.
    Retorna True se o cancelamento foi realizado.
    """
    with closing(conectar()) as conexao:
        with conexao:
            resultado = conexao.execute("""
                UPDATE intencoes_reserva
                SET status = 'cancelada'
                WHERE id = ?
                  AND cliente_id = ?
                  AND status = 'pendente'
            """, (intencao_id, cliente_id))
            return resultado.rowcount > 0


def registrar_demanda(
    cliente_id: int,
    destino: str,
    evento: str = "",
    periodo: str = ""
) -> dict:
    """
    Registra uma demanda de viagem e associa o cliente interessado.
    Se a demanda já existir, reutiliza seu registro.
    Se o cliente já estiver associado, não duplica o relacionamento.
    """

    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.execute("""
                INSERT OR IGNORE INTO demandas_viagem (
                    destino,
                    evento,
                    periodo
                )
                VALUES (?, ?, ?)
            """, (destino, evento, periodo))

            demanda_criada = cursor.rowcount > 0

            resultado = conexao.execute("""
                SELECT id, destino, evento, periodo, status, criado_em
                FROM demandas_viagem
                WHERE destino = ?
                  AND evento = ?
                  AND periodo = ?
            """, (destino, evento, periodo))

            demanda = resultado.fetchone()

            if demanda is None:
                raise RuntimeError("Não foi possível localizar a demanda.")

            demanda_id = demanda["id"]

            conexao.execute("""
                UPDATE demandas_viagem
                SET status = 'ativa'
                WHERE id = ?
            """, (demanda_id,))

            cursor = conexao.execute("""
                INSERT OR IGNORE INTO interessados_demanda (
                    demanda_id,
                    cliente_id
                )
                VALUES (?, ?)
            """, (demanda_id, cliente_id))

            interesse_novo = cursor.rowcount > 0

            return {
                "id": demanda_id,
                "destino": demanda["destino"],
                "evento": demanda["evento"],
                "periodo": demanda["periodo"],
                "status": "ativa",
                "demanda_criada": demanda_criada,
                "interesse_novo": interesse_novo
            }


def listar_demandas(status: str | None = "ativa") -> list:
    """
    Lista demandas e a quantidade de clientes interessados.

    Se status for None, retorna demandas ativas e inativas.
    """

    with closing(conectar()) as conexao:
        if status is None:
            resultado = conexao.execute("""
                SELECT
                    d.id,
                    d.destino,
                    d.evento,
                    d.periodo,
                    d.status,
                    d.criado_em,
                    COUNT(i.cliente_id) AS quantidade_interessados
                FROM demandas_viagem d
                LEFT JOIN interessados_demanda i
                    ON i.demanda_id = d.id
                GROUP BY d.id
                ORDER BY d.criado_em DESC
            """)
        else:
            resultado = conexao.execute("""
                SELECT
                    d.id,
                    d.destino,
                    d.evento,
                    d.periodo,
                    d.status,
                    d.criado_em,
                    COUNT(i.cliente_id) AS quantidade_interessados
                FROM demandas_viagem d
                LEFT JOIN interessados_demanda i
                    ON i.demanda_id = d.id
                WHERE d.status = ?
                GROUP BY d.id
                ORDER BY d.criado_em DESC
            """, (status,))

        return [dict(demanda) for demanda in resultado.fetchall()]


def obter_demanda(demanda_id: int) -> dict | None:
    """
    Busca uma demanda pelo ID, incluindo a quantidade de interessados.
    """

    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT
                d.id,
                d.destino,
                d.evento,
                d.periodo,
                d.status,
                d.criado_em,
                COUNT(i.cliente_id) AS quantidade_interessados
            FROM demandas_viagem d
            LEFT JOIN interessados_demanda i
                ON i.demanda_id = d.id
            WHERE d.id = ?
            GROUP BY d.id
        """, (demanda_id,))

        demanda = resultado.fetchone()

        return dict(demanda) if demanda else None


def listar_interessados_demanda(demanda_id: int) -> list:
    """
    Lista os clientes interessados em uma demanda específica.
    """

    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT
                c.id AS cliente_id,
                c.telegram_chat_id,
                c.nome_telegram,
                c.telefone,
                i.criado_em AS interessado_desde
            FROM interessados_demanda i
            INNER JOIN clientes c
                ON c.id = i.cliente_id
            WHERE i.demanda_id = ?
            ORDER BY i.criado_em ASC
        """, (demanda_id,))

        return [dict(cliente) for cliente in resultado.fetchall()]