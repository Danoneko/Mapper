import json
from redis import Redis
from dal.entities import Location, Node

class OSMRedisHelper:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.loc_prefix = "location_"
        self.choice_prefix = "choice_"

    async def set_location_info(self, chat_id: int, location: Location):
        return self.redis.set(self.loc_prefix + str(chat_id), json.dumps({
            "latitude": location.latitude,
            "longitude": location.longitude,
            "live_period": location.live_period,
        }))

    def get_location_by_chat_id(self, chat_id: int) -> Location:
        location_data = self.redis.get(self.loc_prefix + str(chat_id))
        if location_data:
            data = json.loads(location_data)
            return Location(
                latitude=data["latitude"],
                longitude=data["longitude"],
                live_period=data.get("live_period")
            )
        
    def delete_location_by_chat_id(self, chat_id: int):
        return self.redis.delete(self.loc_prefix + str(chat_id))

    async def set_user_choice(self, chat_id: int, choice: Node):
        return self.redis.set(self.choice_prefix + str(chat_id), json.dumps({
            "name": choice.name,
            "latitude": choice.latitude,
            "longitude": choice.longitude,
        }))

    def get_choice_by_chat_id(self, chat_id: int) -> Node:
        choice_data = self.redis.get(self.choice_prefix + str(chat_id))
        if choice_data:
            data = json.loads(choice_data)
            return Node(
                name=data["name"],
                latitude=data["latitude"],
                longitude=data["longitude"]
            )
        
    def delete_choice_by_chat_id(self, chat_id: int):
        return self.redis.delete(self.choice_prefix + str(chat_id))
