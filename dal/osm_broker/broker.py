import logging
from typing import List

import overpy
from overpy import Node as OverpyNode

from .models import Location, Node, PartialNodeInfo


class OpenMapsBroker:
    def __init__(self):
        self.api = overpy.Overpass()
        self.logger = logging.getLogger('open_maps_broker')

    def convert_api_node(self, api_node: OverpyNode) -> Node:
        if api_node.tags.get("name") is None or api_node.lat == 0.0 or api_node.lon == 0.0:
            raise PartialNodeInfo("Partial NodeInfo", api_node)

        return Node(name=api_node.tags.get("name"), latitude=api_node.lat, longitude=api_node.lon)

    def get_nodes(self, osm_type: str, osm_name: str, user_location: Location) -> List[Node]:
        query = f"""[out:json];
        node
        [{osm_type}={osm_name}](around:{user_location.search_distance},{user_location.latitude}, {user_location.longitude});
        out body;
        """

        response = self.api.query(query)

        nodes = []

        for api_node in response.nodes:
            try:
                node = self.convert_api_node(api_node)
                nodes.append(node)
            except PartialNodeInfo as e:
                self.logger.warning(f"Skipping partial node: {e.node}")
                continue

        return nodes

    def get_street(self, street: str, house_number: int, user_location: Location):
        query = f"""[out:json];
        area
        ["addr:street"~"{street}"]["addr:housenumber"="{house_number}"](around:10000,{user_location.latitude},{user_location.longitude});
        out center;
        """

        response = self.api.query(query)

        try:
            longitude = response.ways[0].center_lon
            latitude = response.ways[0].center_lat

            return Node(name='', latitude=latitude, longitude=longitude)
        except IndexError as e:
            self.logger.error(e)
            raise IndexError
