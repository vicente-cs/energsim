from energsim import Eletrodomestico
from energsim.utils import ValidarNumero


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
            "validate": ValidarNumero,
        },
    ]
