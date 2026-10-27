
from app.agent.modelo import gerar_resposta


resposta = gerar_resposta(
    mensagens=[
        {
            "role": "user",
            "content": (
                "Responda em português brasileiro: "
                "qual é sua função em uma agência de viagens?"
            )
        }
    ]
)

mensagem = resposta.choices[0].message

print("Resposta da Groq:")
print(mensagem.content)
