from energsim import *
from energsim.eletros import *

res = Residencia.cadastrar()
res.eletrodomesticos.append(TV.cadastrar())
res.eletrodomesticos.append(Eletrodomestico.cadastrar())
res.interface.interagir()
