from typing import List


class Consumidor:
    def __init__(self, nome, potencia):
        self.nome = nome
        self.potencia = potencia
        self._consumo = 0

    def calcular(self, t_horas, taxa):
        return self.potencia * t_horas

    # TODO: Implementar stats
    def stats(self):
        pass

    @property
    def consumo(self):
        return self._consumo

    @classmethod
    def cadastrar(self):
        nome = input("Digite o nome da entidade: ")
        potencia = float(input("Digite a potência da entidade (Watts): "))
        return self(nome, potencia)


class Eletrodomestico(Consumidor):
    def __init__(self, nome, potencia, h_diario):
        super().__init__(nome, potencia)
        self.h_diario = h_diario

    @property
    def consumo(self):
        return self.h_diario * self.potencia

    @classmethod
    def cadastrar(self):
        nome = input("Digite o nome do eletrodoméstico: ")
        potencia = float(input("Digite a potência do eletrodoméstico (Watts): "))
        h_diario = float(input("Digite o tempo de uso diário (Horas): "))
        return self(nome, potencia, h_diario)


class Residencia(Consumidor):
    def __init__(self, nome, taxa, eletrodomesticos: List[Eletrodomestico] = []):
        self.nome = nome
        self.taxa = taxa
        self.eletrodomesticos = eletrodomesticos

    @property
    def consumo(self):
        _consumo = 0
        if len(self.eletrodomesticos) > 0:
            for eletro in self.eletrodomesticos:
                _consumo += eletro.consumo

        return _consumo

    @classmethod
    def cadastrar(self):
        nome = input("Digite o nome da residência: ")
        return self(nome)
