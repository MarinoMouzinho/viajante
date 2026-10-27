
from app.agent.atividade_autonoma import executar_agente

while(1):
    entrada = input(">> ").strip()

    if "sair" not in entrada :
        resultado = executar_agente(
            mensagem=entrada,
            telegram_chat_id="123456789"
        )

        print("\nResposta do Viajante:")
        print(resultado["resposta"])

        print("\nCiclos de ferramentas executados:")
        print(resultado["iteracoes"])
    else:
        break
