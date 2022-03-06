from typing import List
import matplotlib.pyplot as plt
import numpy as np
from PyInquirer import prompt
from examples import custom_style_3
from energsim.utils import ValidarNumero


# TODO Implementar algo com composição/agregação
class Consumidor:
    """Algo que consome energia"""

    def __init__(self, nome, potencia):
        self.nome = nome
        self.potencia = potencia

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

    # Nesse caso, o consumo não é diretamente definido
    @property
    def consumo(self):
        """Consumo em kwH"""
        return 0

    _tabela_cadastro = [
        {"type": "input", "name": "nome", "message": "Nome da entidade"},
        {"type": "input", "name": "potencia", "message": "Potência"},
    ]

    @classmethod
    def cadastrar(self):
        respostas = prompt(self._tabela_cadastro, style=custom_style_3)
        return self(**respostas)

    def __repr__(self) -> str:
        return self.__class__.__name__ + ":" + str(self.__dict__)


class Eletrodomestico(Consumidor):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia)
        self.h_diario = h_diario

    @property
    def consumo(self):
        return self.h_diario * self.potencia / 1000

    _tabela_cadastro = [
        {"type": "input", "name": "nome", "message": "Nome do eletrodoméstico"},
        {
            "type": "input",
            "name": "potencia",
            "message": "Potência (Watts)",
            "filter": lambda val: float(val),
            "validate": ValidarNumero,
        },
        {
            "type": "input",
            "name": "h_diario",
            "message": "Uso diário (Horas)",
            "filter": lambda val: float(val),
            "validate": ValidarNumero,
        },
    ]


class Residencia(Consumidor):
    def __init__(self, nome, taxa, eletrodomesticos: List[Eletrodomestico] = []):
        self.nome = nome
        self.taxa = taxa
        self.eletrodomesticos = eletrodomesticos

    def simular(self, t_dias, taxa=None):
        if taxa == None:
            taxa = self.taxa

        return super().simular(t_dias, taxa)

    def grafico(self, t_dias, taxa=None):
        if taxa == None:
            taxa = self.taxa
        return super().grafico(t_dias, taxa)

    def get_eletro_prompt(self):
        eletro_sel = [
            {
                "type": "list",
                "name": "eletros",
                "message": "Selecione um eletrodoméstico",
                "choices": [
                    {"name": eletro.nome, "value": eletro}
                    for eletro in self.eletrodomesticos
                ],
            }
        ]
        return prompt(eletro_sel, style=custom_style_3)["eletros"]

    def get_acao_prompt(self):
        acoes = [
            {
                "type": "list",
                "name": "acao",
                "message": "Selecione uma ação",
                "choices": [
                    {"name": "Adicionar eletrodoméstico", "value": "add_eletro"},
                    {"name": "Remover eletrodoméstico", "value": "del_eletro"},
                    {"name": "Consultar eletrodoméstico", "value": "con_eletro"},
                    {"name": "Simular conta", "value": "sim_conta"},
                    {"name": "Sair", "value": "sair"},
                ],
            }
        ]

        return prompt(acoes, style=custom_style_3)["acao"]

    def interagir(self):
        acao = self.get_acao_prompt()

        if acao == "con_eletro":
            pass

        elif acao == "del_eletro":
            eletro = self.get_eletro_prompt()
            self.eletrodomesticos.remove(eletro)

        if acao != "sair":
            self.interagir()

    @property
    def consumo(self):
        _consumo = 0
        if len(self.eletrodomesticos) > 0:
            for eletro in self.eletrodomesticos:
                _consumo += eletro.consumo

        return _consumo

    _tabela_cadastro = [
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
