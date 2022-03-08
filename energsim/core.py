from typing import List
import matplotlib.pyplot as plt
import numpy as np
from PyInquirer import prompt
from examples import custom_style_3
from energsim.utils import ValidarHorario, ValidarRacionaisPositivos
from energsim.interfaces import Interface, InterfaceRes

# TODO arrumar bug Key
class Consumidor:
    """Algo que consome energia"""

    def __init__(self, nome, potencia, interface=None):
        self.nome = nome
        self.potencia = potencia
        self.interface = interface if interface is not None else Interface(self)

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
        cadastro = list(filter(lambda x: x["name"] not in kwargs, cls.cadastro))
        respostas = {**prompt(cadastro, style=custom_style_3), **kwargs}
        return cls(**respostas)

    def __repr__(self) -> str:
        return self.__class__.__name__ + ":" + str(self.__dict__)


class Eletrodomestico(Consumidor):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia)
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
    def __init__(
        self, nome, taxa, eletrodomesticos: List[Eletrodomestico] = None, interface=None
    ):
        self.nome = nome
        self.taxa = taxa
        self.eletrodomesticos = eletrodomesticos if eletrodomesticos is not None else []
        self.interface = interface if interface is not None else InterfaceRes(self)

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
