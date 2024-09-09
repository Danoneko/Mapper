from dataclasses import dataclass


@dataclass
class Node:
    """Отражает точку на карте, как конечный найденный объект."""
    name: str

    latitude: float
    longitude: float


@dataclass
class Location:
    """Содержит базовую информацию от которых ищется объект."""
    latitude: float
    longitude: float

    search_distance: int = 300
    live_period: int = None


class PartialNodeInfo(Exception):
    def __init__(self, message, node):
        super().__init__(message)
        self.node = node

    def __str__(self):
        return "API returned a partial node info"
