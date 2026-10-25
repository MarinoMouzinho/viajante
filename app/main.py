
from app.database.repositorios import inicializar_banco


def main():
    inicializar_banco()

    print("Viajante iniciado!")
    print("Banco de dados inicializado com sucesso.")


if __name__ == "__main__":
    main()
