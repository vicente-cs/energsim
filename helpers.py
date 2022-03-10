from PyInquirer import prompt
from energsim import Residencia
from typing import List
from examples import custom_style_3
from energsim.utils import clear
from pickle import load, dump
from os import path


def carregar(fnome, default):
    if path.exists(fnome):
        try:
            file = open(fnome, "rb")
            data = load(file)
        except:
            print("Algo deu errado")
    else:
        file = open(fnome, "wb")
        data = default
        dump(data, file)
    return data


class ResContainer:
    def __init__(self, residencias: List[Residencia] = None):
        self.residencias = residencias if residencias is not None else []
        self._acoes = [
            {"name": "Adicionar residência", "value": self._adicionar_acao},
            {"name": "Remover residência", "value": self._remover_acao},
            {"name": "Consultar residência", "value": self._consultar_acao},
            {"name": "Sair", "value": "sair"},
        ]
        self.template = [
            {
                "type": "list",
                "name": "acao",
                "message": "Selecione uma ação",
                "choices": [],
            }
        ]

    def _residencia_prompt(self):
        pergunta = [
            {
                "type": "list",
                "message": "Selecione uma residência",
                "name": "residencia",
                "choices": [
                    {"name": residencia.nome, "value": residencia}
                    for residencia in self.residencias
                ],
            }
        ]
        return prompt(pergunta, style=custom_style_3)["residencia"]

    @property
    def tabela(self):
        _tabela = self.template
        # Acessa as escolhas da tabela de ações
        _tabela[0]["choices"] = self._acoes
        return _tabela

    def _adicionar_acao(self):
        res = Residencia.cadastrar()
        self.residencias.append(res)
        res.interagir()

    def _remover_acao(self):
        if len(self.residencias) > 0:
            residencia = self._residencia_prompt()
            self.residencias.remove(residencia)
        else:
            print("Nenhuma residência encontrada")

    def _consultar_acao(self):
        if len(self.residencias) > 0:
            residencia = self._residencia_prompt()
            residencia.interagir()
        else:
            print("Nenhuma residência encontrada")

    def interagir(self):
        clear()
        acao = prompt(self.tabela, style=custom_style_3)["acao"]
        if acao != "sair":
            acao()
            self.interagir()
