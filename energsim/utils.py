from prompt_toolkit.validation import Validator, ValidationError

#TODO Implementar validação horário
class ValidarNumero(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except:
            raise ValidationError(message="Digite um valor válido")
    
class ValidarHorario(Validator):
    pass