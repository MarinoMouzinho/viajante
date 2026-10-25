
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
                telegram_id TEXT NOT NULL,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (demanda_id, telegram_id),

                FOREIGN KEY (demanda_id)
                    REFERENCES demandas_viagem(id),

                FOREIGN KEY (telegram_id)
                    REFERENCES clientes(telegram_id)
            )
        """)
        conexao.commit()
    finally:
        conexao.close()
