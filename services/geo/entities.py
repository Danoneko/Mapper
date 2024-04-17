from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict

from dal.entities import Node, Location, GeoBroker


@dataclass
class Category:
    name: str
    amenities: List[str]


class GeoService(ABC):
    def __init__(self, categories: Dict[str, Category], geo_broker: GeoBroker) -> None:
        self.osm_categories_map = categories
        self.geo_broker = geo_broker

    @abstractmethod
    def get_nodes_for_category(self, category: str, user_location: Location) -> List[Node]: ...
