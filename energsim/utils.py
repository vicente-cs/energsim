from pydoc import doc
from prompt_toolkit.validation import Validator, ValidationError

# TODO Implementar validação horário
class ValidarNumero(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except:
            raise ValidationError(message="Digite um valor válido")


class ValidarHorario(Validator):
    def validate(self, document):
        message = "Digite um valor válido"
        try:
            val = float(document.text)
            if not (0 <= val <= 24):
                raise ValidationError(message=message)
        except:
            raise ValidationError(message=message)
