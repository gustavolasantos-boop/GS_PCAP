# Citizen Assist AI — orientação para pessoas idosas

**Disciplina:** Pensamento Computacional e Automação com Python — GS 2026.2  
**Público:** pessoas idosas e familiares/cuidadores que buscam orientações sobre Cartão SUS, vacinação e transporte gratuito.

## 1. Problema e objetivo

Informações sobre serviços públicos podem estar espalhadas em diferentes páginas e nem sempre são fáceis de localizar. O Citizen Assist AI é um assistente de terminal que busca em uma base local de orientações oficiais, mostra a fonte e a data de verificação, permite navegar por categorias e guarda indicadores sem solicitar ou registrar nome, CPF, telefone ou e-mail.

O programa é um protótipo educacional: não realiza agendamentos, não consulta sistemas do governo em tempo real e não substitui a UBS, a Secretaria de Saúde, a prefeitura, o CRAS ou a empresa de transporte.

## 2. Público, problema e ODS

- **Público escolhido:** pessoas idosas, especialmente quem precisa de orientações simples para acessar serviços básicos.
- **Problema:** dificuldade para descobrir onde obter/consultar o Cartão SUS, como conferir vacinas e quais regras se aplicam ao transporte gratuito.
- **ODS relacionados:** **ODS 3 — Saúde e Bem-Estar**, por facilitar a localização de informação oficial sobre vacinação e serviços do SUS; **ODS 10 — Redução das Desigualdades**, por apoiar o acesso à informação e a direitos da pessoa idosa; **ODS 11 — Cidades e Comunidades Sustentáveis**, pela orientação sobre transporte coletivo acessível.

## 3. Estrutura do repositório

```text
citizen-assist-ai/
├── README.md
├── main.py
├── orientacao.py
├── base_conhecimento.py
├── assistente.py
├── ENTREGA_FIAP.txt
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    ├── avaliacoes.json
    └── atendimentos.csv
```

As quatro partes principais em Python são `main.py`, `orientacao.py`, `base_conhecimento.py` e `assistente.py`. A pasta `data/` contém a base JSON, o histórico de atendimentos, as notas de facilidade de uso e a exportação CSV.

## 4. Como executar

Requisitos: Python 3.10 ou superior. O projeto usa somente a biblioteca padrão; não é necessário instalar pacotes externos.

1. Extraia o ZIP.
2. Abra o terminal na pasta `citizen-assist-ai`.
3. Execute:

```bash
python main.py
```

No Windows, também pode ser necessário usar `py main.py`.

### Menu

1. **Digitar uma dúvida:** consulta a base por texto livre. Se não houver resultado suficiente, o programa sugere reformular a pergunta.
2. **Navegar por categorias:** mostra categorias e títulos numerados; `0` volta à tela anterior.
3. **Ver indicadores:** apresenta percentuais, tempo médio, tentativas, facilidade e dúvidas sem solução.
4. **Exportar CSV:** gera/atualiza `data/atendimentos.csv`.
5. **Sair:** solicita uma nota de facilidade de uso de 1 a 5.

## 5. Base de conhecimento

O arquivo `data/base_conhecimento.json` contém **11 orientações**, em três categorias: `Cartão SUS e saúde digital`, `Vacinação` e `Transporte gratuito`. Todos os registros incluem `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`. Cada orientação tem ao menos três palavras-chave, URL oficial e data de verificação.

As informações foram conferidas em **19/11/2026**. Regras locais podem variar, especialmente para transporte entre 60 e 65 anos e para cronogramas de vacinação. Quando a fonte oficial consultada não especifica documentos, a resposta diz para confirmar com o órgão responsável em vez de inventar uma lista.

### Fontes oficiais consultadas

1. Ministério da Saúde — FAQ sobre emissão do Cartão Nacional de Saúde pelo Meu SUS Digital: https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao/9-como-faco-o-cartao
2. Ministério da Saúde — Meu SUS Digital, serviços disponíveis e registros de vacinação: https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao
3. Ministério da Saúde — Vacinação da Pessoa Idosa: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-pessoa-idosa/vacinacao-da-pessoa-idosa/vacinacao-da-pessoa-idosa/
4. Ministério da Saúde — Calendário Nacional de Vacinação da Pessoa Idosa, 2026: https://www.gov.br/saude/pt-br/vacinacao/arquivos/calendario-nacional-de-vacinacao-idoso/view
5. Ministério dos Direitos Humanos — Estatuto da Pessoa Idosa, art. 39, transporte urbano e semiurbano: https://www.gov.br/mdh/pt-br/centrais-de-conteudo/pessoa-idosa/estatuto-da-pessoa-idosa.pdf/
6. Ministério da Saúde — Direitos da Pessoa Idosa, incluindo transporte urbano e interestadual: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-pessoa-idosa/direitos/direitos/
7. Gov.br / Ministério do Desenvolvimento e Assistência Social — Emitir Carteira da Pessoa Idosa: https://www.gov.br/pt-br/servicos/adquirir-carteira-do-idoso
8. Ministério do Desenvolvimento e Assistência Social — Carteira da Pessoa Idosa e apoio do CRAS: https://www.gov.br/mds/pt-br/acoes-e-programas/suas/servicos-e-programas/carteira-da-pessoa-idosa

## 6. Regra de busca e confiança

A função `normalizar()` converte o texto para minúsculas, remove acentos e pontuação e padroniza os espaços. Em seguida, `BaseConhecimento.pontuar()` atribui:

- **+3 pontos** para cada palavra-chave da orientação encontrada na pergunta;
- **+1 ponto** para cada palavra única da pergunta com quatro ou mais letras que também apareça no título.

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, ordenada da maior para a menor pontuação. O programa mostra a melhor orientação e até duas alternativas. A confiança é **ALTA** a partir de 6 pontos e **MÉDIA** de 3 a 5 pontos. Resultados abaixo de 3 pontos não são exibidos como resposta.

**Exemplo:** para “Como faço o cartão do SUS?”, a orientação “Solicitar um novo Cartão SUS (CNS)” recebe +3 por “cartao do sus”, +3 por “sus” e +1 porque “cartao” aparece no título. Total: **7 pontos, confiança ALTA**. A pontuação é reproduzível e pode ser acompanhada diretamente no JSON e no método `pontuar()`.

## 7. Classes e conceitos de programação

- `Orientacao`: modela um registro da base e o exibe na tela.
- `BaseConhecimento`: lê o JSON, lista categorias, filtra por categoria, normaliza, pontua e busca.
- `Assistente`: compõe um objeto `BaseConhecimento`, coordena o atendimento, valida entradas, registra histórico, calcula indicadores e exporta CSV.

A organização reutiliza conceitos estudados no material de aula: dicionários e listas da Aula 07; leitura segura de JSON e tratamento de arquivos do Mini CRM da Aula 08; `csv.DictWriter` da Aula 09; classes, atributos, métodos, `self` e composição da Aula 10. O projeto usa `json`, `csv`, `pathlib`, `re`, `unicodedata` e `time`, todos da biblioteca padrão.

## 8. Privacidade, erros e limitações

- O assistente **não solicita** nome, CPF, telefone ou e-mail.
- Uma entrada com `@` ou oito ou mais dígitos (inclusive dígitos separados por pontuação) é recusada e não entra no histórico.
- Perguntas vazias, opções fora da faixa, letras em menus e respostas fora de `s/n` são tratadas sem encerrar o programa.
- Base JSON ausente/corrompida resulta em aviso e lista vazia, não em encerramento inesperado.
- Todo resultado mostra fonte, data de verificação e o aviso: **“este assistente NÃO é um canal oficial.”**
- A busca é baseada em regras e palavras-chave; pode não reconhecer sinônimos, perguntas muito longas ou dúvidas municipais específicas. Nesse caso, sugere navegação por categoria ou reformulação.
- A base não acessa dados pessoais, não consulta disponibilidade real, não reserva transporte e não agenda vacinação. O usuário deve confirmar informações locais com o órgão responsável.

## 9. Teste com usuários e indicadores

O conjunto de teste registra **3 participantes representados apenas pelos códigos P1, P2 e P3**, com **12 atendimentos no total** (4 por participante). Os registros não incluem nomes nem dados pessoais. O histórico de demonstração está em `data/historico.json`; a exportação correspondente está em `data/atendimentos.csv`; as notas de facilidade estão em `data/avaliacoes.json`. 

### Resultados dos atendimentos — `atendimentos.csv`

| Data | Pergunta realizada | ID da orientação | Encontrou? | Ajudou? | Tentativas | Tempo (s) |
|---|---|---:|---|---|---:|---:|
| 19/11/2026 | Como faço o Cartão SUS? | 1 | Sim | Sim | 1 | 18,2 |
| 19/11/2026 | Como vejo o número do CNS no celular? | 2 | Sim | Sim | 1 | 15,8 |
| 19/11/2026 | Quais vacinas preciso conferir depois dos 60 anos? | 3 | Sim | Sim | 1 | 22,1 |
| 19/11/2026 | A vacina da gripe é todo ano? | 4 | Sim | Sim | 2 | 33,4 |
| 19/11/2026 | Qual é o reforço da COVID-19 para pessoa idosa? | 5 | Sim | Não | 1 | 26,0 |
| 19/11/2026 | Onde vejo minha carteira de vacinação digital? | 2 | Sim | Sim | 1 | 19,5 |
| 19/11/2026 | A vacina que tomei não aparece no aplicativo | 6 | Sim | Sim | 2 | 40,7 |
| 19/11/2026 | Idoso tem ônibus gratuito? | 8 | Sim | Sim | 1 | 13,2 |
| 19/11/2026 | Como consigo a carteira do idoso para viajar? | 10 | Sim | Não | 2 | 43,0 |
| 19/11/2026 | Qual é o procedimento para renovar a CNH? | — | Não | Não | 2 | 56,3 |
| 19/11/2026 | Quais documentos preciso para emitir a Carteira da Pessoa Idosa? | 10 | Sim | Sim | 1 | 28,9 |
| 19/11/2026 | Tenho dúvida sobre gratuidade no ônibus municipal | 8 | Sim | Sim | 1 | 16,1 |


### Análise dos resultados

Dos 12 atendimentos registrados, o assistente encontrou uma orientação em 11 casos, alcançando uma taxa de respostas encontradas de 91,7%. Em nove atendimentos, a orientação foi considerada útil, correspondendo a 75,0% do total.

O tempo médio para encontrar uma resposta foi de 25,2 segundos, considerando somente os 11 atendimentos em que uma orientação foi encontrada. A média foi de 1,33 tentativas por atendimento, e a facilidade de uso recebeu nota média de 4,33 de 5.

A pergunta sobre a renovação da CNH não foi respondida porque o assunto está fora do escopo da base de conhecimento. Já as perguntas sobre o reforço da COVID-19 e a Carteira da Pessoa Idosa para viajar encontraram orientações, mas essas respostas não foram consideradas suficientes para resolver as dúvidas. Esses casos indicam oportunidades de melhoria na clareza das respostas e na orientação sobre os próximos passos.

Como melhoria, podem ser adicionadas novas palavras-chave e explicações mais específicas, mantendo as informações vinculadas a fontes oficiais. O histórico em JSON e a exportação CSV permitem acompanhar os resultados e identificar quais dúvidas precisam de atenção.


Resultados calculados a partir dos 12 atendimentos registrados:

- **Resposta encontrada:** 91,7% (11 de 12 atendimentos).
- **Taxa de acerto — a orientação ajudou:** 75,0% (9 de 12 atendimentos).
- **Tempo médio para encontrar resposta:** 25,2 segundos, considerando os 11 atendimentos com orientação encontrada.
- **Tentativas por atendimento:** média de 1,33 tentativas.
- **Facilidade de uso:** média de 4,33/5, com base em três avaliações.

Dúvidas que permaneceram sem solução ou sem avaliação positiva no conjunto registrado: “Qual é o reforço da COVID-19 para pessoa idosa?”, “Como consigo a carteira do idoso para viajar?” e “Qual é o procedimento para renovar a CNH?”. As perguntas sobre dose individual devem ser confirmadas com a equipe de saúde; renovação da CNH está fora do escopo escolhido. A melhoria incorporada à base foi incluir expressões como **“ônibus gratuito idoso”**, **“passe livre 65”** e **“gratuidade ônibus municipal”** para ampliar a recuperação de perguntas de transporte urbano. Ainda é necessário validar o comportamento com perguntas locais e conferir a base periodicamente, pois normas e calendários podem mudar.

> Os arquivos `historico.json`, `avaliacoes.json` e `atendimentos.csv` já contêm registros de demonstração para permitir visualizar indicadores e exportação ao executar o programa. Ao realizar novos testes, os atendimentos são acrescentados automaticamente.


