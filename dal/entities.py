from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List


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

    search_distance: int = 100


class GeoBroker(ABC):
    @abstractmethod
    def get_nodes_by_amenity(self, amenity: str, user_location: Location) -> List[Node]: ...

