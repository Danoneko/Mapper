import logging
from typing import List

import overpy
from overpy import Node

from dal.entities import GeoBroker, Location, Node
from .entities import PartialNodeInfo


class OpenMapsBroker(GeoBroker):
    def __init__(self):
        self.api = overpy.Overpass()
        self.logger = logging.getLogger('open_maps_broker')

    def convert_api_node(self, api_node: overpy.Node) -> Node:
        if api_node.tags.get("name") is None or api_node.lat == 0.0 or api_node.lon == 0.0:
            self.logger.warning(f'Partial NodeInfo, node: {api_node}')
            raise PartialNodeInfo

        return Node(name=api_node.tags.get("name"), latitude=api_node.lat, longitude=api_node.lon)

    def get_nodes_by_amenity(self, amenity: str, user_location: Location) -> List[Node]:
        query = f"""[out:json];
        node
        [amenity={amenity}](around:{user_location.search_distance},{user_location.latitude}, {user_location.longitude});
        out body;
        """

        response = self.api.query(query)

        nodes = []

        for api_node in response.nodes:
            try:
                node = self.convert_api_node(api_node)
                nodes.append(node)
            except PartialNodeInfo:
                continue

        return nodes
