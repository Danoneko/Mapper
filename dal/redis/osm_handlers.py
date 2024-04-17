import json

from redis import Redis

from dal.entities import Location, Node


class OSMRedisHelper:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set_location_info(self, chat_id: int, location: Location):
        return self.redis.set(str(chat_id), json.dumps({
            "latitude": location.latitude,
            "longitude": location.longitude,

            "search_distance": location.search_distance,
        }))

    def get_location_by_chat_id(self, chat_id: int) -> Location:
        location_data = self.redis.get(str(chat_id))
        if location_data:
            return Location(**json.loads(location_data))

    async def set_user_choice(self, chat_instance: str, choice: Node):
        return self.redis.set(chat_instance, json.dumps({
            "name": choice.name,
            "latitude": choice.latitude,
            "longitude": choice.longitude,
        }))
