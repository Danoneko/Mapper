import logging
import uuid

from .models import User, Category, OSMType, Destination
from sqlalchemy.types import UUID


class Storage:
    def __init__(self, session):
        self.__session = session
        self.__logger = logging.getLogger('open_maps_broker')

    # USER METHODS

    def create_user(self, chat_id: int, status: str, search_distance=300, latitude=None, longitude=None):
        user = User(id=uuid.uuid4(), chat_id=chat_id, search_distance=search_distance, status=status,
                    recent_latitude=latitude, recent_longitude=longitude)

        self.__session.add(user)

        try:
            self.__session.commit()

            return None
        except Exception as e:
            self.__logger.error(e)
            self.__session.rollback()

            return e

    def delete_user(self, chat_id: int):
        user = self.__session.query(User).filter_by(chat_id=chat_id).first()
        self.__session.delete(user)

        try:
            self.__session.commit()

            return None
        except Exception as e:
            self.__logger.error(e)
            self.__session.rollback()

            return e

    def update_user_status(self, chat_id: int, status: str):
        user = self.__session.query(User).filter_by(chat_id=chat_id).first()

        if user:
            user.status = status
            self.__session.add(user)

            try:
                self.__session.commit()

                return None
            except Exception as e:
                self.__logger.error(e)
                self.__session.rollback()

                return e

    def update_search_distance(self, chat_id: int, search_distance: int):
        user = self.__session.query(User).filter_by(chat_id=chat_id).first()

        if user:
            user.search_distance = search_distance
            self.__session.add(user)

            try:
                self.__session.commit()

                return None
            except Exception as e:
                self.__logger.error(e)
                self.__session.rollback()

                return e

    def update_user_location(self, chat_id: int, latitude: float, longitude: float):
        user = self.__session.query(User).filter_by(chat_id=chat_id).first()

        if user:
            user.latitude = latitude
            user.longitude = longitude
            self.__session.add(user)

            try:
                self.__session.commit()
                return None

            except Exception as e:
                self.__logger.error(e)
                self.__session.rollback()

                return e

    def get_user(self, chat_id: int):
        user = self.__session.query(User).filter_by(chat_id=chat_id).first()

        if user:
            return {
                "id": user.id,
                "chat_id": user.chat_id,
                "status": user.status,
                "search_distance": user.search_distance,
                "latitude": user.recent_latitude,
                "longitude": user.recent_longitude
            }

        return None

    # CATEGORIES AND TYPES METHODS

    def get_categories(self):
        categories = self.__session.query(Category).all()

        result = []

        for category in categories:
            result.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            })

        return result

    def get_osm_types(self, category_id: UUID):
        osm_types = self.__session.query(OSMType).filter_by(category_id=category_id).all()

        result = []

        for osm_type in osm_types:
            result.append({
                'id': osm_type.id,
                'name': osm_type.name,
                'type': osm_type.type,
            })

        return result

    # DESTINATION METHODS

    def create_destination(self, user_id: UUID, name: str, latitude: float, longitude: float, message_id: int,
                           map_message_id: int):
        destination = Destination(id=uuid.uuid4(), user_id=user_id, name=name, latitude=latitude, longitude=longitude,
                                  message_id=message_id, map_message_id=map_message_id)
        self.__session.add(destination)

        try:
            self.__session.commit()

            return None
        except Exception as e:
            self.__logger.error(e)
            self.__session.rollback()

            return e

    def get_destination(self, user_id: UUID):
        destination = self.__session.query(Destination).filter_by(user_id=user_id).first()

        if destination:
            return {
                "id": destination.id,
                "name": destination.name,
                "latitude": destination.latitude,
                "longitude": destination.longitude,
                "message_id": destination.message_id,
                "map_message_id": destination.map_message_id,
            }

        return None

    def delete_destination(self, user_id: UUID):
        destination = self.__session.query(Destination).filter_by(user_id=user_id).first()
        self.__session.delete(destination)

        try:
            self.__session.commit()

            return None
        except Exception as e:
            self.__logger.error(e)
            self.__session.rollback()

            return e
