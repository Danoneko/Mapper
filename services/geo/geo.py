from dataclasses import dataclass
from typing import Dict, List

from dal.entities import Node, GeoBroker, Location
from services.geo.entities import GeoService, Category


@dataclass
class OSMConfiguration:
    categories_to_amenities_map: Dict[str, Category]


class OSMService(GeoService):

    def __init__(self, categories: Dict[str, Category], geo_broker: GeoBroker):
        super().__init__(categories=categories, geo_broker=geo_broker)

    def get_nodes_for_category(self, category: str, user_location: Location) -> List[Node]:
        category_nodes: List[Node] = []
        for amenity in self.osm_categories_map[category].amenities:
            category_nodes.extend(self.geo_broker.get_nodes_by_amenity(amenity, user_location))

        return category_nodes
