"""Citizen Assist AI — assistente de orientação ao cidadão para pessoas idosas."""
from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento

PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_DADOS = PASTA_PROJETO / "data"


def main():
    print("=" * 62)
    print("CITIZEN ASSIST AI | Orientação para pessoas idosas")
    print("=" * 62)
    print("Informação simples, com fonte oficial e sem coleta de dados pessoais.\n")

    base = BaseConhecimento(PASTA_DADOS / "base_conhecimento.json")
    base.carregar()
    assistente = Assistente(
        nome="Citizen Assist AI",
        base=base,
        caminho_historico=PASTA_DADOS / "historico.json",
        caminho_avaliacoes=PASTA_DADOS / "avaliacoes.json",
        caminho_csv=PASTA_DADOS / "atendimentos.csv",
    )

    while True:
        print("\nMENU PRINCIPAL")
        print("1 - Digitar uma dúvida")
        print("2 - Navegar por categorias")
        print("3 - Ver indicadores e dúvidas sem solução")
        print("4 - Exportar atendimentos para CSV")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            assistente.perguntar()
        elif opcao == "2":
            assistente.navegar()
        elif opcao == "3":
            assistente.indicadores()
        elif opcao == "4":
            caminho = assistente.exportar_csv()
            if caminho is not None:
                print(f"Arquivo exportado: {caminho}")
        elif opcao == "0":
            assistente.registrar_facilidade_uso()
            print("Obrigado por usar o Citizen Assist AI. Até logo!")
            break
        else:
            print("Opção inválida. Escolha um número do menu; o programa continua aberto.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma encerrado pelo usuário.")
