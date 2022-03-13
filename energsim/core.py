from typing import List, Type
import matplotlib.pyplot as plt
import numpy as np
from PyInquirer import prompt
from energsim.utils import ValidarHorario, ValidarRacionaisPositivos, clear
from inspect import getfullargspec
from examples import custom_style_3


prompt_style = custom_style_3

# TODO: Adicionar nome às consultas


class Consumidor:
    """Algo que consome energia"""

    def __init__(self, nome):
        self.nome = nome
        self.template = [
            {
                "type": "list",
                "name": "acao",
                "message": "Selecione uma ação",
                "choices": [],
            }
        ]

        self._acoes = [
            {"name": "Simular custo/consumo", "value": self._simular_acao},
            {"name": "Visualizar gráfico", "value": self._grafico_acao},
            {"name": "Sair", "value": "sair"},
        ]

    categoria = "Consumidor"

    # Nesse caso, o consumo não é diretamente definido
    @property
    def consumo(self) -> float:
        """Consumo em kwH"""
        return 0

    def simular(self, t_dias, taxa):
        """Simula o consumo de um período de t_dias"""
        return {
            "consumo": self.consumo * t_dias,
            "custo": self.consumo * t_dias * taxa,
        }

    def grafico(self, t_dias, taxa):
        plt.style.use("fivethirtyeight")

        plt.title(f"{self.nome}: relação custo/consumo")
        plt.xlabel("Dias")

        sim = self.simular(t_dias, taxa)

        x1 = np.array([0, t_dias])
        y1 = np.array([0, sim["custo"]])

        x2 = np.array([0, t_dias])
        y2 = np.array([0, sim["consumo"]])

        plt.plot(x1, y1, label="Custo (R$)")
        plt.plot(x2, y2, label="Consumo (kwH)")

        plt.legend()

        plt.grid(True)

        plt.tight_layout()
        plt.show()

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da entidade",
            "validate": lambda x: x != "",
        },
        {
            "type": "input",
            "name": "potencia",
            "message": "Potência (Watts)",
            "filter": lambda val: float(val),
            "validate": ValidarRacionaisPositivos,
        },
    ]

    @classmethod
    def cadastrar(cls, **kwargs):
        clear()
        cadastro = list(filter(lambda x: x["name"] not in kwargs, cls.cadastro))
        respostas = {**prompt(cadastro, style=prompt_style), **kwargs}
        return cls(**respostas)

    @property
    def tabela(self):
        _tabela = self.template
        # Acessa as escolhas da tabela de ações
        _tabela[0]["choices"] = self._acoes
        return _tabela

    # Nenhuma descrição interessante para Consumidor
    @property
    def _descricao(self):
        return ""

    def _prompt_dias(self):
        pergunta = [
            {
                "type": "input",
                "name": "t_dias",
                "message": "Período (Dias)",
                "filter": lambda val: float(val),
                "validate": ValidarRacionaisPositivos,
            }
        ]

        return prompt(pergunta, style=prompt_style)["t_dias"]

    def _prompt_taxa(self):
        pergunta = [
            {
                "type": "input",
                "name": "taxa",
                "message": "Taxa (R$/kWh)",
                "filter": lambda val: float(val),
                "validate": ValidarHorario,
            }
        ]

        return prompt(pergunta, style=prompt_style).get("taxa", "")

    def _simular_acao(self, t_dias=None, taxa=None):
        if taxa == None:
            taxa = self._prompt_taxa()

        if t_dias == None:
            t_dias = self._prompt_dias()

        resposta = self.simular(t_dias, taxa)
        consumo = resposta["consumo"]
        custo = resposta["custo"]
        print(f"Consumo: {consumo:.2f} kWh")
        print(f"Custo: {custo:.2f} R$")
        input()

    def _grafico_acao(self, t_dias=None, taxa=None):
        if t_dias == None:
            t_dias = self._prompt_dias()

        if taxa == None:
            taxa = self._prompt_taxa()

        self.grafico(t_dias, taxa)

    def interagir(self, t_dias=None, taxa=None):
        clear()
        # Imprime as informações sobre o Consumidor
        print(self)
        print()

        acao = prompt(self.tabela, style=prompt_style)["acao"]
        if acao != "sair":
            acao_args = getfullargspec(acao).args

            interagir_locals = locals().copy()
            interagir_locals.pop("self")

            val_locals = {k: v for k, v in interagir_locals.items() if k in acao_args}

            # Executa a ação
            acao(**val_locals)

            self.interagir(**val_locals)

    def __str__(self) -> str:
        return f"{self.categoria} {self.nome}\n{self._descricao}"


class Eletrodomestico(Consumidor):
    def __init__(self, nome: str, potencia: float, h_diario: float):
        super().__init__(nome)
        self.potencia = potencia
        self.h_diario = h_diario

    categoria = "Eletrodoméstico"

    @property
    def consumo(self):
        return self.h_diario * self.potencia / 1000

    @property
    def _descricao(self):
        return f"{self.potencia}W {self.consumo}kWh/dia"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome do eletrodoméstico",
            "validate": lambda x: x != "",
        },
        {
            "type": "input",
            "name": "potencia",
            "message": "Potência (Watts)",
            "filter": lambda val: float(val),
            "validate": ValidarRacionaisPositivos,
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class Residencia(Consumidor):
    def __init__(self, nome, taxa, eletrodomesticos: List[Eletrodomestico] = None):
        super().__init__(nome)
        self.taxa = taxa
        self.eletrodomesticos = eletrodomesticos if eletrodomesticos is not None else []
        self._eletro_selecao = [TV, Eletrodomestico]
        self._acoes.insert(
            0,
            {"name": "Consultar eletrodoméstico", "value": self._consultar_eletro_acao},
        )
        self._acoes.insert(
            0, {"name": "Remover eletrodoméstico", "value": self._remover_eletro_acao}
        )
        self._acoes.insert(
            0,
            {"name": "Adicionar eletrodoméstico", "value": self._adicionar_eletro_acao},
        )

    categoria = "Residência"

    @property
    def consumo(self):
        _consumo = 0
        if len(self.eletrodomesticos) > 0:
            for eletro in self.eletrodomesticos:
                _consumo += eletro.consumo

        return _consumo

    @property
    def _descricao(self):
        return f"{len(self.eletrodomesticos)} aparelhos {self.consumo}kWh/dia"

    def simular(self, t_dias, taxa=None):
        if taxa == None:
            taxa = self.taxa

        return super().simular(t_dias, taxa)

    def grafico(self, t_dias, taxa=None):
        if taxa == None:
            taxa = self.taxa
        return super().grafico(t_dias, taxa)

    def _prompt_eletro(self):
        if len(self.eletrodomesticos) > 0:
            pergunta = [
                {
                    "type": "list",
                    "name": "eletro",
                    "message": "Selecione um eletrodoméstico",
                    "choices": [
                        {"name": f"{eletro.categoria} {eletro.nome}", "value": eletro}
                        for eletro in self.eletrodomesticos
                    ],
                }
            ]
            return prompt(pergunta, style=prompt_style)["eletro"]
        else:
            return None

    def _adicionar_eletro_acao(self, **kwargs):
        pergunta = [
            {
                "type": "list",
                "name": "eletro",
                "message": "Selecione um eletrodoméstico",
                "choices": [
                    {"name": eletro.categoria, "value": eletro}
                    for eletro in self._eletro_selecao
                ],
            }
        ]
        eletro = prompt(pergunta, style=prompt_style)["eletro"]

        self.eletrodomesticos.append(eletro.cadastrar(**kwargs))

    def _remover_eletro_acao(self):
        eletro = self._prompt_eletro()
        if eletro != None:
            self.eletrodomesticos.remove(eletro)

    def _consultar_eletro_acao(self, t_dias=None, taxa=None):
        eletro = self._prompt_eletro()
        if eletro != None:
            print(
                f"""{eletro.nome} {eletro.potencia}W
    Consumo de {eletro.consumo} kWh/dia
    {eletro.h_diario} horas diárias de uso"""
            )

            eletro.interagir(t_dias, taxa)

    def interagir(self, t_dias=None, taxa=None):
        if taxa == None:
            taxa = self.taxa

        return super().interagir(t_dias, taxa)

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da residência",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "taxa",
            "message": "Classificação da residência",
            "choices": [
                {"name": "Normal", "value": 0.53224},
                {"name": "Baixa Renda até 30kWh", "value": 0.16121},
                {"name": "Baixa Renda de 31 a 100kWh", "value": 0.27636},
                {"name": "Residencial Baixa Renda de 101 a 220kWh", "value": 0.41454},
                {"name": "Residencial Baixa Renda acima de 220kWh", "value": 0.4606},
            ],
        },
    ]


class TV(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class LavaRoupa(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class Geladeira(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class Fogao(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class ArCondicionado(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class Radio(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class Abajur(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]


class Fogao(Eletrodomestico):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia, h_diario)

    categoria = "Televisão"

    cadastro = [
        {
            "type": "input",
            "name": "nome",
            "message": "Nome da TV (ex: LG Sala)",
            "validate": lambda x: x != "",
        },
        {
            "type": "list",
            "name": "potencia",
            "message": "Modelo da TV",
            "choices": [
                {"name": 'Plasma 42"', "value": 320},
                {"name": 'Plasma 50"', "value": 380},
                {"name": 'LCD 32"', "value": 120},
                {"name": 'LCD 40"', "value": 200},
                {"name": 'LCD 42"', "value": 250},
                {"name": 'LCD 46"', "value": 280},
                {"name": 'LCD 52"', "value": 310},
                {"name": 'LED 32"', "value": 100},
                {"name": 'LED 40"', "value": 130},
                {"name": 'LED 46"', "value": 150},
            ],
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarHorario,
        },
    ]
