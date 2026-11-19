"""Fluxo de atendimento, histórico, indicadores e exportação CSV."""
import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path


CAMPOS_CSV = [
    "data", "origem", "pergunta", "id_orientacao", "encontrou",
    "ajudou", "tentativas", "tempo_segundos"
]


class Assistente:
    def __init__(self, nome, base, caminho_historico, caminho_avaliacoes, caminho_csv):
        self.nome = nome
        self.base = base
        self.caminho_historico = Path(caminho_historico)
        self.caminho_avaliacoes = Path(caminho_avaliacoes)
        self.caminho_csv = Path(caminho_csv)
        self.caminho_historico.parent.mkdir(parents=True, exist_ok=True)
        self.historico = self._ler_lista_json(self.caminho_historico, "histórico")
        self.avaliacoes = self._ler_lista_json(self.caminho_avaliacoes, "avaliações de facilidade")

    @staticmethod
    def _ler_lista_json(caminho, nome):
        if not caminho.exists():
            return []
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            if isinstance(dados, list):
                return dados
            print(f"Aviso: o arquivo de {nome} não contém uma lista; será iniciado vazio.")
        except (json.JSONDecodeError, OSError) as erro:
            print(f"Aviso: não foi possível ler o arquivo de {nome} ({erro}); será iniciado vazio.")
        return []

    @staticmethod
    def _contem_dado_pessoal(texto):
        """Não aceita consultas com e-mail ou oito ou mais dígitos, mesmo separados por pontuação."""
        quantidade_digitos = sum(1 for caractere in texto if caractere.isdigit())
        return "@" in texto or quantidade_digitos >= 8

    @staticmethod
    def _perguntar_sn(mensagem, permitir_voltar=False):
        while True:
            resposta = input(mensagem).strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            if permitir_voltar and resposta == "0":
                return None
            print("Entrada inválida. Digite s para sim ou n para não" + (", ou 0 para voltar" if permitir_voltar else "") + ".")

    @staticmethod
    def _confianca(pontos):
        if pontos >= 6:
            return "ALTA"
        if pontos >= 3:
            return "MÉDIA"
        return "BAIXA"

    def _salvar_historico(self):
        try:
            self.caminho_historico.write_text(
                json.dumps(self.historico, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as erro:
            print(f"Aviso: não foi possível salvar o histórico ({erro}).")

    def _salvar_avaliacoes(self):
        try:
            self.caminho_avaliacoes.write_text(
                json.dumps(self.avaliacoes, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as erro:
            print(f"Aviso: não foi possível salvar as avaliações ({erro}).")

    def registrar(self, origem, pergunta, orientacao, encontrou, ajudou, tentativas, tempo_segundos):
        """Guarda os campos pedidos no enunciado; não registra consultas recusadas por privacidade."""
        registro = {
            "data": datetime.now().date().isoformat(),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao.id if orientacao is not None else None,
            "encontrou": bool(encontrou),
            "ajudou": bool(ajudou),
            "tentativas": int(tentativas),
            "tempo_segundos": round(float(tempo_segundos), 1),
        }
        self.historico.append(registro)
        self._salvar_historico()
        return registro

    @staticmethod
    def _mostrar_resultados(resultados):
        pontos, melhor = resultados[0]
        confianca = Assistente._confianca(pontos)
        print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
        melhor.exibir()
        alternativas = resultados[1:3]
        if alternativas:
            print("\nOutras orientações que talvez ajudem:")
            for pontos_alt, orientacao_alt in alternativas:
                print(f"  - {orientacao_alt.titulo} [{orientacao_alt.categoria}] — {pontos_alt} pontos")

    def perguntar(self):
        inicio = time.time()
        pergunta_inicial = ""
        ultima_pergunta = ""
        tentativas = 0
        orientacao_final = None
        ajudou = False

        while True:
            if tentativas == 0:
                texto = input("\nDigite sua dúvida (0 para voltar): ").strip()
            else:
                texto = input("Reformule sua dúvida (0 para finalizar): ").strip()

            if texto == "0":
                if tentativas == 0:
                    return
                break
            if not texto:
                print("A pergunta está vazia. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if self._contem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone, e-mail ou outros dados pessoais. Essa entrada não foi registrada; reescreva sem esses dados.")
                continue

            if not pergunta_inicial:
                pergunta_inicial = texto
            ultima_pergunta = texto
            tentativas += 1
            orientacao_final = None
            ajudou = False
            resultados = self.base.buscar(texto)

            if resultados:
                self._mostrar_resultados(resultados)
                orientacao_final = resultados[0][1]
                retorno = self._perguntar_sn("Essa orientação resolveu sua dúvida? (s/n; 0 para voltar): ", permitir_voltar=True)
                if retorno is True:
                    ajudou = True
                    break
                if retorno is None:
                    break
                tentar_novamente = self._perguntar_sn("Deseja tentar outra formulação? (s/n): ")
                if tentar_novamente:
                    continue
                break

            print("\nNão encontrei uma orientação com pontuação suficiente na base.")
            categorias = self.base.categorias()
            if categorias:
                print("Você pode navegar pelas categorias: " + "; ".join(categorias) + ".")
            print("Tente termos como: Cartão SUS, vacinação, Meu SUS Digital, ônibus gratuito ou Carteira da Pessoa Idosa.")
            tentar_novamente = self._perguntar_sn("Deseja reformular a pergunta? (s/n): ")
            if tentar_novamente:
                continue
            break

        if tentativas > 0 and pergunta_inicial:
            tempo_total = round(time.time() - inicio, 1)
            self.registrar(
                origem="pergunta",
                pergunta=pergunta_inicial,
                orientacao=orientacao_final,
                encontrou=orientacao_final is not None,
                ajudou=ajudou,
                tentativas=tentativas,
                tempo_segundos=tempo_total,
            )
            print(f"Atendimento registrado em {tempo_total:.1f} segundos.")

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("Não há categorias para exibir. Verifique data/base_conhecimento.json.")
            return

        while True:
            print("\nCATEGORIAS")
            for indice, categoria in enumerate(categorias, start=1):
                print(f"{indice} - {categoria}")
            print("0 - Voltar ao menu principal")
            opcao = input("Escolha uma categoria: ").strip()
            if opcao == "0":
                return
            if not opcao.isdigit() or not (1 <= int(opcao) <= len(categorias)):
                print("Opção inválida. Escolha uma categoria da lista ou 0 para voltar.")
                continue
            self._navegar_categoria(categorias[int(opcao) - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\nCATEGORIA: {categoria}")
            for indice, orientacao in enumerate(orientacoes, start=1):
                print(f"{indice} - {orientacao.titulo}")
            print("0 - Voltar às categorias")
            opcao = input("Escolha uma orientação: ").strip()
            if opcao == "0":
                return
            if not opcao.isdigit() or not (1 <= int(opcao) <= len(orientacoes)):
                print("Opção inválida. Escolha uma orientação da lista ou 0 para voltar.")
                continue

            inicio = time.time()
            orientacao = orientacoes[int(opcao) - 1]
            orientacao.exibir()
            retorno = self._perguntar_sn("Essa orientação ajudou? (s/n; 0 para voltar): ", permitir_voltar=True)
            ajudou = retorno is True
            self.registrar(
                origem="categoria",
                pergunta=orientacao.titulo,
                orientacao=orientacao,
                encontrou=True,
                ajudou=ajudou,
                tentativas=1,
                tempo_segundos=round(time.time() - inicio, 1),
            )
            print("Atendimento por categoria registrado.")

    def indicadores(self):
        registros = self.historico
        print("\nINDICADORES DO CITIZEN ASSIST AI")
        if not registros:
            print("Ainda não há atendimentos registrados.")
            print("Facilidade de uso: " + self._texto_facilidade())
            return

        total = len(registros)
        encontrados = [registro for registro in registros if registro.get("encontrou")]
        ajudaram = [registro for registro in registros if registro.get("ajudou")]
        tempo_encontradas = [float(registro.get("tempo_segundos", 0)) for registro in encontrados]
        media_tempo = sum(tempo_encontradas) / len(tempo_encontradas) if tempo_encontradas else 0
        tentativas = [int(registro.get("tentativas", 1)) for registro in registros]

        print(f"Atendimentos registrados: {total}")
        print(f"Resposta encontrada (%): {len(encontrados) / total * 100:.1f}%")
        print(f"Taxa de acerto — a orientação ajudou (%): {len(ajudaram) / total * 100:.1f}%")
        print(f"Tempo médio para encontrar uma resposta: {media_tempo:.1f} segundos")
        print(f"Tentativas por atendimento: {sum(tentativas) / len(tentativas):.2f}")
        print(f"Facilidade de uso (1 a 5): {self._texto_facilidade()}")

        sem_solucao = []
        for registro in registros:
            if not registro.get("encontrou") or not registro.get("ajudou"):
                pergunta = str(registro.get("pergunta", "(pergunta não informada)"))
                if pergunta not in sem_solucao:
                    sem_solucao.append(pergunta)
        print("Dúvidas sem solução ou em que a orientação não ajudou:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  - Nenhuma registrada.")

    def _texto_facilidade(self):
        notas = []
        for avaliacao in self.avaliacoes:
            try:
                nota = int(avaliacao.get("facilidade"))
                if 1 <= nota <= 5:
                    notas.append(nota)
            except (AttributeError, TypeError, ValueError):
                continue
        if not notas:
            return "sem avaliação registrada"
        return f"{sum(notas) / len(notas):.2f}/5 ({len(notas)} avaliação(ões))"

    def registrar_facilidade_uso(self):
        while True:
            nota_texto = input("Antes de sair, avalie a facilidade de uso de 1 a 5: ").strip()
            if nota_texto.isdigit() and 1 <= int(nota_texto) <= 5:
                self.avaliacoes.append({
                    "data": datetime.now().date().isoformat(),
                    "facilidade": int(nota_texto),
                })
                self._salvar_avaliacoes()
                return int(nota_texto)
            print("Nota inválida. Digite um número de 1 a 5.")

    def exportar_csv(self):
        """Exporta o histórico usando csv.DictWriter, como no material da Aula 09."""
        try:
            self.caminho_csv.parent.mkdir(parents=True, exist_ok=True)
            with self.caminho_csv.open("w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for registro in self.historico:
                    linha = {campo: registro.get(campo, "") for campo in CAMPOS_CSV}
                    escritor.writerow(linha)
            return self.caminho_csv
        except OSError as erro:
            print(f"Não foi possível exportar o CSV ({erro}).")
            return None
