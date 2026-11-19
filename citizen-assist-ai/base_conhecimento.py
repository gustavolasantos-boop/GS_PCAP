"""Carregamento, normalização e busca pontuada na base de conhecimento."""
import json
import re
import unicodedata
from pathlib import Path

from orientacao import Orientacao

CAMPOS_OBRIGATORIOS = {
    "id", "categoria", "titulo", "palavras_chave", "resposta",
    "documentos", "onde", "fonte", "verificado_em"
}


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos ou pontuação e com espaços simples."""
    if not isinstance(texto, str):
        return "  "
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON; arquivo ausente/corrompido não encerra o programa."""
        try:
            conteudo = self.caminho.read_text(encoding="utf-8")
            dados = json.loads(conteudo)
        except FileNotFoundError:
            print(f"Aviso: base de conhecimento não encontrada: {self.caminho}")
            self.orientacoes = []
            return self.orientacoes
        except (json.JSONDecodeError, OSError) as erro:
            print(f"Aviso: não foi possível ler a base de conhecimento ({erro}).")
            self.orientacoes = []
            return self.orientacoes

        if not isinstance(dados, list):
            print("Aviso: a base JSON deve conter uma lista de orientações.")
            self.orientacoes = []
            return self.orientacoes

        orientacoes_carregadas = []
        for indice, registro in enumerate(dados, start=1):
            if not isinstance(registro, dict) or not CAMPOS_OBRIGATORIOS.issubset(registro):
                print(f"Aviso: registro {indice} ignorado porque faltam campos obrigatórios.")
                continue
            try:
                if not isinstance(registro["palavras_chave"], list) or not isinstance(registro["documentos"], list):
                    raise ValueError("palavras_chave e documentos devem ser listas")
                orientacao = Orientacao(registro)
                if not orientacao.palavras_chave or len(orientacao.palavras_chave) < 3:
                    print(f"Aviso: orientação {orientacao.id} sem pelo menos três palavras-chave; registro ignorado.")
                    continue
                orientacoes_carregadas.append(orientacao)
            except (TypeError, ValueError, KeyError) as erro:
                print(f"Aviso: registro {indice} ignorado ({erro}).")

        self.orientacoes = orientacoes_carregadas
        if not self.orientacoes:
            print("Aviso: a base foi carregada, mas não há orientações válidas.")
        return self.orientacoes

    def categorias(self):
        """Retorna as categorias únicas na ordem em que aparecem no JSON."""
        resultado = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in resultado:
                resultado.append(orientacao.categoria)
        return resultado

    def por_categoria(self, categoria):
        """Retorna uma lista de orientações de uma categoria."""
        return [orientacao for orientacao in self.orientacoes if orientacao.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Aplica as regras do enunciado: palavra-chave +3; palavra no título +1."""
        pergunta_normalizada = normalizar(pergunta)
        pontuacao = 0

        for palavra_chave in orientacao.palavras_chave:
            chave_normalizada = normalizar(palavra_chave)
            if chave_normalizada.strip() and chave_normalizada in pergunta_normalizada:
                pontuacao += 3

        palavras_pergunta = set(pergunta_normalizada.split())
        palavras_titulo = set(normalizar(orientacao.titulo).split())
        for palavra in palavras_pergunta:
            if len(palavra) >= 4 and palavra in palavras_titulo:
                pontuacao += 1

        return pontuacao

    def buscar(self, pergunta):
        """Devolve tuplas (pontos, orientação), ordenadas da maior para a menor pontuação."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos >= 3:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda item: item[0], reverse=True)
        return resultados
