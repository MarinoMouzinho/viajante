
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
                cliente_id INTEGER NOT NULL,
                destino TEXT NOT NULL,
                evento TEXT NOT NULL DEFAULT '',
                periodo TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'ativa'
                    CHECK (status IN ('ativa', 'inativa')),
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id),
                UNIQUE (cliente_id, destino, evento, periodo)
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
             CREATE TABLE IF NOT EXISTS interessados_demanda (
                demanda_id INTEGER NOT NULL,
                telegram_chat_id TEXT NOT NULL,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (demanda_id, telegram_chat_id),

                FOREIGN KEY (demanda_id)
                    REFERENCES demandas_viagem(id),

                FOREIGN KEY (telegram_chat_id)
                    REFERENCES clientes(telegram_chat_id)
            )
        """)
        conexao.commit()
    finally:
        conexao.close()

def inserir_cliente(telegram_chat_id: str, telefone: str | None = None):
    """
    Insere um novo cliente no banco de dados.
    """

    with closing(conectar()) as conexao:
        with conexao:
            conexao.execute("""
                INSERT INTO clientes (telegram_chat_id, telefone)
                VALUES (?, ?)
            """, (telegram_chat_id, telefone))


def obter_cliente(telegram_chat_id: str) -> dict | None:
    """
    Busca um cliente pelo identificador do Telegram.
    """

    with closing(conectar()) as conexao:
        resultado = conexao.execute("""
            SELECT telegram_chat_id, telefone, criado_em
            FROM clientes
            WHERE telegram_chat_id = ?
        """, (telegram_chat_id,))

        cliente = resultado.fetchone()

        return dict(cliente) if cliente else None


def atualizar_telefone(telegram_chat_id: str, telefone: str):
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
            SELECT telegram_chat_id, telefone, criado_em
            FROM clientes
            ORDER BY criado_em DESC
        """)

        return [dict(cliente) for cliente in resultado.fetchall()]