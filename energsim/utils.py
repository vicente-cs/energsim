from curses.ascii import isdigit
from prompt_toolkit.validation import Validator, ValidationError

class ValidarNumero(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except:
            raise ValidationError(message="Digite um valor válido")