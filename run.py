from helpers import ResContainer
from pickle import dump
from helpers import carregar

container_path = "saves/container.pickle"

container = carregar(container_path, ResContainer())
container.interagir()

dump(container, open(container_path, "wb"))
