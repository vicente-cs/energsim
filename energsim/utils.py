from pydoc import doc
from prompt_toolkit.validation import Validator, ValidationError
import os


def clear():
    os.system("cls||clear")


class ValidarNumero(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except:
            raise ValidationError(message="Digite um valor válido")


class ValidarHorario(Validator):
    pass

    def validate(self, document):
        try:
            val = float(document.text)
            if not (0 <= val <= 24):
                raise ValidationError(message="Digite um valor no período válido")
        except:
            raise ValidationError(message="Digite um valor válido")


class ValidarRacionaisPositivos(Validator):
    def validate(self, document):
        try:
            val = float(document.text)
            if val < 0:
                raise ValidationError(message="Digite um valor positivo")
        except:
            raise ValidationError(message="Digite um valor válido")
