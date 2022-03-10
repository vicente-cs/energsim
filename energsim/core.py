from typing import List, Type
import matplotlib.pyplot as plt
import numpy as np
from PyInquirer import prompt
from energsim.utils import ValidarHorario, ValidarRacionaisPositivos, clear
from inspect import getfullargspec
from examples import custom_style_3


prompt_style = custom_style_3


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

    # Nesse caso, o consumo não é diretamente definido
    @property
    def consumo(self):
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
        {"type": "input", "name": "nome", "message": "Nome da entidade"},
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
        print(f"Consumo: {consumo} kWh")
        print(f"Custo: {custo} R$")

    def _grafico_acao(self, t_dias=None, taxa=None):
        if t_dias == None:
            t_dias = self._prompt_dias()

        if taxa == None:
            taxa = self._prompt_taxa()

        self.grafico(t_dias, taxa)

    def interagir(self, t_dias=None, taxa=None):
        clear()
        acao = prompt(self.tabela, style=prompt_style)["acao"]
        if acao != "sair":
            acao_args = getfullargspec(acao).args

            interagir_locals = locals().copy()
            interagir_locals.pop("self")

            val_locals = {k: v for k, v in interagir_locals.items() if k in acao_args}

            # Executa a ação
            acao(**val_locals)

            self.interagir(**val_locals)

    def __repr__(self) -> str:
        return self.__class__.__name__ + ":" + str(self.__dict__)


class Eletrodomestico(Consumidor):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome)
        self.potencia = potencia
        self.h_diario = h_diario

    @property
    def consumo(self):
        return self.h_diario * self.potencia / 1000

    cadastro = [
        {"type": "input", "name": "nome", "message": "Nome do eletrodoméstico"},
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
        self._eletro_tabela = [
            {"name": "Televisão", "value": TV},
            {"name": "Personalizado", "value": Eletrodomestico},
        ]
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

    @property
    def consumo(self):
        _consumo = 0
        if len(self.eletrodomesticos) > 0:
            for eletro in self.eletrodomesticos:
                _consumo += eletro.consumo

        return _consumo

    def simular(self, t_dias, taxa=None):
        if taxa == None:
            taxa = self.taxa

        return super().simular(t_dias, taxa)

    def grafico(self, t_dias, taxa=None):
        if taxa == None:
            taxa = self.taxa
        return super().grafico(t_dias, taxa)

    def _prompt_eletro(self):
        pergunta = [
            {
                "type": "list",
                "name": "eletro",
                "message": "Selecione um eletrodoméstico",
                "choices": [
                    {"name": eletro.nome, "value": eletro}
                    for eletro in self.eletrodomesticos
                ],
            }
        ]
        return prompt(pergunta, style=prompt_style)["eletro"]

    def _adicionar_eletro_acao(self, **kwargs):
        pergunta = [
            {
                "type": "list",
                "name": "eletro",
                "message": "Selecione um eletrodoméstico",
                "choices": self._eletro_tabela,
            }
        ]
        eletro = prompt(pergunta, style=prompt_style)["eletro"]

        self.eletrodomesticos.append(eletro.cadastrar(**kwargs))

    def _remover_eletro_acao(self):
        eletro = self._prompt_eletro()

        self.eletrodomesticos.remove(eletro)

    def _consultar_eletro_acao(self, t_dias=None, taxa=None):
        eletro = self._prompt_eletro()

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
        {"type": "input", "name": "nome", "message": "Nome da residência"},
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

    cadastro = [
        {"type": "input", "name": "nome", "message": "Nome da TV (ex: TV Sala)"},
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
