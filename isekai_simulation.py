"""Simulador de vida estilo isekai.

Este módulo implementa um jogo de simulação baseado em escolhas onde o
jogador renasce em um novo mundo após um acidente, recebe bênçãos do deus
Gem e tenta prosperar em sua nova vida. O jogo é totalmente textual e
pode ser executado diretamente com Python.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from textwrap import fill
from typing import Dict, List, Tuple


def wrap(text: str) -> str:
    """Quebra o texto em múltiplas linhas para facilitar a leitura."""

    return fill(text, width=88)


@dataclass
class Escolha:
    """Representa uma opção que o jogador pode selecionar."""

    nome: str
    descricao: str
    atributos: Dict[str, int]

    def apresentar(self) -> str:
        atributos_texto = ", ".join(f"{chave}: {valor:+d}" for chave, valor in self.atributos.items())
        return f"{self.nome} — {self.descricao} ({atributos_texto})"


@dataclass
class Personagem:
    """Estado atual do personagem do jogador."""

    nome: str
    mundo: Escolha
    origem: Escolha
    poder: Escolha
    legado: Escolha
    atributos: Dict[str, int] = field(default_factory=lambda: {
        "vigor": 0,
        "mana": 0,
        "sorte": 0,
        "carisma": 0,
    })
    gloria: int = 0
    cicatrizes: int = 0

    def aplicar_escolhas(self) -> None:
        """Aplica os modificadores das escolhas aos atributos."""

        for escolha in (self.mundo, self.origem, self.poder, self.legado):
            for chave, valor in escolha.atributos.items():
                self.atributos[chave] = self.atributos.get(chave, 0) + valor

    def resolver_evento(self, evento: "Evento") -> str:
        """Resolve um evento e retorna a narração associada."""

        resultado, descricao = evento.resolver(self)
        if resultado == "gloria":
            self.gloria += 1
        elif resultado == "cicatriz":
            self.cicatrizes += 1
        return descricao

    def epilogo(self) -> str:
        """Cria um epílogo baseado no desempenho do personagem."""

        diferenca = self.gloria - self.cicatrizes
        if diferenca >= 3:
            destino = (
                "Você se torna uma lenda viva, venerado em canções e invocado"
                " como patrono de heróis por gerações."
            )
        elif diferenca >= 1:
            destino = (
                "Sua jornada foi marcada por vitórias e amizades sinceras;"
                " seu nome permanece em memória nas guildas locais."
            )
        elif diferenca == 0:
            destino = (
                "Você encontra um equilíbrio delicado entre desafios e glórias,"
                " levando uma vida tranquila mas cheia de histórias para contar."
            )
        else:
            destino = (
                "As cicatrizes acumuladas cobram seu preço. Ainda assim,"
                " você segue firme, provando que coragem também é resistir."
            )

        resumo_atributos = ", ".join(
            f"{chave.capitalize()}: {valor}"
            for chave, valor in self.atributos.items()
        )
        return wrap(
            f"No fim da aventura, {self.nome} registra {self.gloria} feitos gloriosos"
            f" e {self.cicatrizes} cicatrizes memoráveis. {destino} A síntese do seu"
            f" potencial: {resumo_atributos}."
        )


class Evento:
    """Um acontecimento que pode alterar o destino do jogador."""

    def __init__(self, titulo: str, descricao: str, escolhas: List[Tuple[str, str, str]]):
        self.titulo = titulo
        self.descricao = descricao
        self.escolhas = escolhas

    def apresentar(self) -> str:
        cabecalho = f"\n=== {self.titulo} ===\n{wrap(self.descricao)}\n"
        opcoes = []
        for indice, (identificador, texto, _resultado) in enumerate(self.escolhas, start=1):
            opcoes.append(f"  {indice}. {texto} [{identificador}]")
        return cabecalho + "\n".join(opcoes)

    def resolver(self, personagem: Personagem) -> Tuple[str, str]:
        indice = solicitar_indice(len(self.escolhas))
        identificador, texto, resultado = self.escolhas[indice]
        narrativa = self._narrativa(resultado, personagem)
        return resultado, wrap(f"Você opta por {texto.lower()}. {narrativa}")

    def _narrativa(self, resultado: str, personagem: Personagem) -> str:
        """Gera um texto dinâmico baseado no resultado."""

        sorte = personagem.atributos.get("sorte", 0)
        mana = personagem.atributos.get("mana", 0)
        carisma = personagem.atributos.get("carisma", 0)
        vigor = personagem.atributos.get("vigor", 0)

        if resultado == "gloria":
            bonus = random.randint(0, 2) + max(sorte, carisma) // 2
            return (
                "O mundo sorri para você. Seus aliados celebram, e o deus Gem"
                f" concede uma bênção adicional de {bonus} pontos de inspiração."
            )
        if resultado == "cicatriz":
            penalidade = random.randint(0, 2) - min(vigor, sorte) // 3
            return (
                "O desafio cobra seu preço; uma nova cicatriz surge, mas também"
                f" deixa lições que reforçam sua determinação ({penalidade:+d})."
            )
        if resultado == "mistico":
            retorno = random.randint(1, 6) + mana
            personagem.atributos["mana"] = personagem.atributos.get("mana", 0) + 1
            return (
                "Seu poder místico pulsa intensamente, revelando segredos antigos."
                f" Você acumula {retorno} ecos arcanos e aperfeiçoa sua mana."
            )
        return "As engrenagens do destino giram silenciosamente dessa vez."


def solicitar_indice(total: int) -> int:
    """Solicita um índice válido ao jogador."""

    while True:
        try:
            escolha = int(input("\nEscolha uma opção: ")) - 1
        except ValueError:
            print("Digite o número da opção desejada.")
            continue
        if 0 <= escolha < total:
            return escolha
        print("Opção inválida, tente novamente.")


def solicitar_nome() -> str:
    while True:
        nome = input("Como você se chama no mundo original? ").strip()
        if nome:
            return nome
        print("Um herói precisa de um nome, nem que seja emprestado!")


def apresentar_opcoes(titulo: str, opcoes: List[Escolha]) -> Escolha:
    print(f"\n--- {titulo} ---")
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"  {indice}. {opcao.apresentar()}")
    indice = solicitar_indice(len(opcoes))
    return opcoes[indice]


MUNDOS = [
    Escolha(
        "Reino de Aerilon",
        "Um mundo onde cidades flutuam e a magia alimenta as rotas comerciais.",
        {"mana": 2, "carisma": 1},
    ),
    Escolha(
        "Império Ferromar",
        "Terras forjadas pelo aço e pelo vapor, onde a disciplina fala mais alto.",
        {"vigor": 2},
    ),
    Escolha(
        "Arquipélago de Lúmen",
        "Ilhas misteriosas protegidas por espíritos ancestrais.",
        {"sorte": 2, "mana": 1},
    ),
]

ORIGENS = [
    Escolha(
        "Filho de um Artífice",
        "Você renasce em uma família que domina a tecnologia arcana.",
        {"mana": 1, "vigor": 1},
    ),
    Escolha(
        "Herdeiro de Guilda",
        "Uma guilda influente o adota como protegido especial do deus Gem.",
        {"carisma": 2},
    ),
    Escolha(
        "Caçador Errante",
        "Você desperta em uma caravana que atravessa territórios selvagens.",
        {"vigor": 1, "sorte": 1},
    ),
]

PODERES = [
    Escolha(
        "Forja Estelar",
        "Capaz de invocar armas moldadas com energia celeste.",
        {"vigor": 1, "mana": 2},
    ),
    Escolha(
        "Eco do Tempo",
        "Permite antecipar possibilidades futuras e evitá-las ou provocá-las.",
        {"sorte": 2},
    ),
    Escolha(
        "Lira do Coração",
        "Música encantada que inspira aliados e confunde inimigos.",
        {"carisma": 2, "mana": 1},
    ),
]

LEGADOS = [
    Escolha(
        "Guardião Celeste",
        "Você carrega uma promessa de proteger os indefesos em nome de Gem.",
        {"carisma": 1, "vigor": 1},
    ),
    Escolha(
        "Sábio Errante",
        "O desejo insaciável por conhecimento o guia por bibliotecas vivas.",
        {"mana": 1, "sorte": 1},
    ),
    Escolha(
        "Desafiante do Destino",
        "Você promete confrontar as engrenagens do mundo e vencê-las.",
        {"vigor": 1, "sorte": 1},
    ),
]

EVENTOS = [
    Evento(
        "Festival da Reencarnação",
        "O povo celebra sua chegada e o deus Gem oferece um desafio surpresa.",
        [
            ("gloria", "Exibir sua Forja Estelar em um duelo amistoso", "gloria"),
            ("caridade", "Distribuir bênçãos nas feiras com a Lira do Coração", "mistico"),
            ("humildade", "Ajudar discretamente nas barracas comunitárias", "cicatriz"),
        ],
    ),
    Evento(
        "Biblioteca Serpentina",
        "Um labirinto de pergaminhos vivos promete segredos antigos.",
        [
            ("estudo", "Mergulhar nos manuscritos brilhantes", "mistico"),
            ("atalho", "Seguir um espírito guia até uma sala proibida", "gloria"),
            ("retirada", "Recuar ao sentir uma presença hostil", "cicatriz"),
        ],
    ),
    Evento(
        "Provação do Crepúsculo",
        "Um titã elemental desperta ameaçando o povoado que o acolheu.",
        [
            ("combate", "Atacar o titã de frente com coragem", "gloria"),
            ("estrategia", "Coordenar uma retirada ordenada", "cicatriz"),
            ("selo", "Canalizar mana para selar a criatura", "mistico"),
        ],
    ),
]


INTRODUCAO = wrap(
    "Um acidente improvável interrompe sua vida no mundo original. No vazio"
    " entre realidades, você encontra Gem, o deus que gerencia reencarnações."
    " Ele sorri e oferece uma nova chance de viver em um reino fantástico."
)


SAUDACAO_DEUS = wrap(
    "Saudações, viajante perdido. Eu sou Gem, o tecelão de destinos."
    " Escolha sabiamente onde renascer, quais poderes dominar e que legado"
    " pretende construir. Cada decisão moldará a história que iremos contar."
)


def introducao() -> None:
    print("=" * 88)
    print("BEM-VINDO AO SIMULADOR DE ISEKAI DE GEM".center(88))
    print("=" * 88)
    print(INTRODUCAO)
    print()
    print(SAUDACAO_DEUS)


def preparar_personagem() -> Personagem:
    nome = solicitar_nome()
    mundo = apresentar_opcoes("Escolha seu novo mundo", MUNDOS)
    origem = apresentar_opcoes("Qual será sua nova origem?", ORIGENS)
    poder = apresentar_opcoes("Qual bênção deseja receber?", PODERES)
    legado = apresentar_opcoes("Qual legado pretende construir?", LEGADOS)
    personagem = Personagem(nome, mundo, origem, poder, legado)
    personagem.aplicar_escolhas()
    return personagem


def simular_aventura(personagem: Personagem) -> None:
    random.seed()  # garante resultados variados por execução
    print("\nGem ergue o cetro prateado e os fios do destino começam a brilhar...")
    for evento in EVENTOS:
        print(evento.apresentar())
        narrativa = personagem.resolver_evento(evento)
        print(narrativa)
    print("\n" + personagem.epilogo())


def jogar() -> None:
    introducao()
    personagem = preparar_personagem()
    simular_aventura(personagem)
    print("\nObrigado por compartilhar sua jornada com Gem. Até a próxima reencarnação!")


if __name__ == "__main__":
    jogar()
