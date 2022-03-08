from threading import local
from examples import custom_style_3
from PyInquirer import prompt
from energsim.utils import ValidarHorario, ValidarNumero, ValidarRacionaisPositivos
from inspect import getargspec


class Interface:
    def __init__(self, obj, template=None):
        self.obj = obj

        self.template = (
            template
            if template is not None
            else [
                {
                    "type": "list",
                    "name": "acao",
                    "message": "Selecione uma ação",
                    "choices": [],
                }
            ]
        )

        self._acoes = [
            {"name": "Simular custo/consumo", "value": self.simular},
            {"name": "Visualizar gráfico", "value": self.grafico},
            {"name": "Sair", "value": "sair"},
        ]

    @property
    def tabela(self):
        _tabela = self.template
        # Acessa as escolhas da tabela de ações
        _tabela[0]["choices"] = self._acoes
        return _tabela

    def prompt_dias(self):
        pergunta = [
            {
                "type": "input",
                "name": "t_dias",
                "message": "Período (Dias)",
                "filter": lambda val: float(val),
                "validate": ValidarRacionaisPositivos,
            }
        ]

        return prompt(pergunta, style=custom_style_3)["t_dias"]

    def prompt_taxa(self):
        pergunta = [
            {
                "type": "input",
                "name": "taxa",
                "message": "Taxa (R$/kWh)",
                "filter": lambda val: float(val),
                "validate": ValidarHorario,
            }
        ]

        return prompt(pergunta, style=custom_style_3)["taxa"]

    def simular(self, t_dias=None, taxa=None):
        if taxa == None:
            taxa = self.prompt_taxa()

        if t_dias == None:
            t_dias = self.prompt_dias()

        resposta = self.obj.simular(taxa, t_dias)
        consumo = resposta["consumo"]
        custo = resposta["custo"]
        print(f"Consumo: {consumo} kWh")
        print(f"Custo: {custo} R$")

    def grafico(self, t_dias=None, taxa=None):
        if t_dias == None:
            t_dias = self.prompt_dias()

        if taxa == None:
            taxa = self.prompt_taxa()

        self.obj.grafico(t_dias, taxa)

    def interagir(self, t_dias=None, taxa=None):
        acao = prompt(self.tabela, style=custom_style_3)["acao"]
        if acao != "sair":
            acao_args = getargspec(acao).args

            interagir_locals = locals().copy()
            interagir_locals.pop("self")

            val_locals = {k: v for k, v in interagir_locals.items() if k in acao_args}

            # Executa a ação
            acao(**val_locals)

            self.interagir(**val_locals)


class InterfaceRes(Interface):
    def __init__(self, obj, template=None):
        super().__init__(obj, template)
        # self._acoes.insert(
        #     0, {"name": "Adicionar eletrodoméstico", "value": self.adicionar}
        # )

        self._acoes.insert(
            0, {"name": "Remover eletrodoméstico", "value": self.remover}
        )

        self._acoes.insert(
            0, {"name": "Consultar eletrodoméstico", "value": self.consultar}
        )

    def prompt_eletros(self):
        pergunta = [
            {
                "type": "list",
                "name": "eletros",
                "message": "Selecione um eletrodoméstico",
                "choices": [
                    {"name": eletro.nome, "value": eletro}
                    for eletro in self.obj.eletrodomesticos
                ],
            }
        ]
        return prompt(pergunta, style=custom_style_3)["eletros"]

    def adicionar(self, eletro=None):
        pass

    def remover(self, eletro=None):
        if eletro == None:
            eletro = self.prompt_eletros()

        self.obj.eletrodomesticos.remove(eletro)

    def consultar(self, t_dias=None, taxa=None, eletro=None):
        if eletro == None:
            eletro = self.prompt_eletros()

        eletro.interface.interagir(t_dias, taxa)

    def interagir(self, t_dias=None, taxa=None):
        if taxa == None:
            taxa = self.obj.taxa

        return super().interagir(t_dias, taxa)
