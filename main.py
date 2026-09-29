from game.engine import GameEngine


game = GameEngine()


def mostrar_menu():

    print("\n" + "=" * 50)
    print("QUEM MORA ONDE? - SIMULADOR V2")
    print("=" * 50)

    print("\n1 - Iniciar nova partida")
    print("2 - Simular montagem CORRETA")
    print("3 - Simular montagem INCORRETA")
    print("4 - Verificar bairro")
    print("5 - Ver status")
    print("6 - Simular RETIRADA de todas as peças")
    print("0 - Encerrar")


while True:

    mostrar_menu()

    opcao = input("\nEscolha: ").strip()

    if opcao == "1":

        game.iniciar_partida()

    elif opcao == "2":

        game.simular_montagem_correta()

    elif opcao == "3":

        game.simular_montagem_incorreta()

    elif opcao == "4":

        game.verificar()

    elif opcao == "5":

        game.mostrar_status()

    elif opcao == "6":

        game.simular_retirada_das_pecas()

    elif opcao == "0":

        print("\nEncerrando simulador...")
        break

    else:

        print("\n❌ Opção inválida.")