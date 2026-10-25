<div align='center'>
    <h1>Viajante</h1>
    <p italic>Agente Conversacional para Reserva de Viagens</p>
</div>

## Diretórios
```bash
viajante/
├── app/
│   ├── agent/ # Agente Conversacional
│   │   ├── __init__.py
│   │   ├── ambiente.py
│   │   ├── atividade_autonoma.py
│   │   ├── contexto.py
│   │   ├── controlador.py
│   │   ├── estado.py
│   │   ├── ferramentas.py
│   │   ├── memoria.py
│   │   └── modelo.py
│   │
│   ├── bot/ # Bot no telegram
│   │   ├── __init__.py
│   │   └── telegram.py # Conexao com Telegram
│   │
│   ├── data/ # dados
│   │   └── viagens.json # arquivo de dados
│   │
│   ├── database/ # conexao com banco de dados
│   │   ├── __init__.py
│   │   ├── conexao.py # sqlite
│   │   └── repositorios.py 
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── viagens.py 
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_controlador.py
│   │   ├── test_tools.py
│   │   └── test_viagens.py
│   │
│   └── main.py
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```


## Responsabilidades:
[ ] Conversar com cliente
[ ] Tirar dúvidas sobre a empresa
[ ] Apresentar viagens disponíveis
[ ] Realizar intenção de reserva de assento(s) em uma viagem para o usuario
[ ] Informar à gestão das reservas realizadas no momento da reserva
[ ] Gestão decide se confirma ou cancela