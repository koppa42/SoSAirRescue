from .aircraft import Aircraft
from .map import Map


class Scene:
    def __init__(self) -> None:
        self.aircraft: list[Aircraft] = []
        self.money: int = 0
        self.map: Map = Map()
