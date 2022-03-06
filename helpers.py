from typing import List
import matplotlib.pyplot as plt
import numpy as np


class Consumidor:
    """Algo que consome energia"""

    def __init__(self, nome: str, potencia: float):
        self.nome = nome
        self.potencia = potencia

    def simular(self, t_dias: float, taxa_kwh: float):
        """Simula o consumo de um período de t_dias"""
        return {
            "consumo": self.consumo * t_dias,
            "custo": self.consumo * t_dias * taxa_kwh,
        }

    # Nesse caso, o consumo não é diretamente definido
    @property
    def consumo(self):
        """Consumo em kwH"""
        return 0

    # TODO: Implementar stats
    def grafico(self, t_dias: float, taxa_kwh: float):
        plt.style.use("fivethirtyeight")

        plt.title(f"{self.nome}: relação custo/consumo")
        plt.xlabel("Dias")

        sim = self.simular(t_dias, taxa_kwh)

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

    @classmethod
    def cadastrar(self):
        nome = input("Nome da entidade: ")
        potencia = float(input("Potência da entidade (Watts): "))
        return self(nome, potencia)

    def __repr__(self) -> str:
        return self.__class__.__name__ + ":" + str(self.__dict__)


class Eletrodomestico(Consumidor):
    def __init__(self, nome: str, potencia: float, h_diario: float):
        super().__init__(nome, potencia)
        self.h_diario = h_diario

    @property
    def consumo(self):
        return self.h_diario * self.potencia / 1000

    @classmethod
    def cadastrar(self):
        nome = input("Nome do eletrodoméstico: ")
        potencia = float(input("Potência do eletrodoméstico (Watts): "))
        h_diario = float(input("Tempo de uso diário (Horas): "))
        return self(nome, potencia, h_diario)


class Residencia(Consumidor):
    def __init__(
        self, nome: str, taxa_kwh: float, eletrodomesticos: List[Eletrodomestico] = []
    ):
        self.nome = nome
        self.taxa_kwh = taxa_kwh
        self.eletrodomesticos = eletrodomesticos

    def simular(self, t_dias: float, taxa_kwh: float = None):
        if taxa_kwh == None:
            taxa_kwh = self.taxa_kwh

        return super().simular(t_dias, taxa_kwh)

    @property
    def consumo(self):
        _consumo = 0
        if len(self.eletrodomesticos) > 0:
            for eletro in self.eletrodomesticos:
                _consumo += eletro.consumo

        return _consumo

    @classmethod
    def cadastrar(self):
        nome = input("Nome da residência: ")
        taxa_kwh = float(input("Taxa de energia: "))
        return self(nome, taxa_kwh)
