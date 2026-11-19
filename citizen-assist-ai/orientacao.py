"""Modelo de uma orientação carregada da base JSON."""


class Orientacao:
    def __init__(self, dados):
        self.id = int(dados["id"])
        self.categoria = str(dados["categoria"])
        self.titulo = str(dados["titulo"])
        self.palavras_chave = list(dados["palavras_chave"])
        self.resposta = str(dados["resposta"])
        self.documentos = list(dados["documentos"])
        self.onde = str(dados["onde"])
        self.fonte = str(dados["fonte"])
        self.verificado_em = str(dados["verificado_em"])

    def exibir(self):
        """Apresenta a orientação em linguagem simples no terminal."""
        print(f"\n>> {self.titulo} [{self.categoria}]")
        print(self.resposta)
        print("Documentos ou itens a conferir:")
        if self.documentos:
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("  - A base não registra documentos específicos para esta orientação.")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
