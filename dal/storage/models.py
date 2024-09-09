from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.UUID, primary_key=True)
    chat_id = sa.Column(sa.Integer, nullable=False)
    status = sa.Column(sa.VARCHAR(15), nullable=False)

    search_distance = sa.Column(sa.Integer, nullable=False)
    recent_latitude = sa.Column(sa.REAL, nullable=True)
    recent_longitude = sa.Column(sa.REAL, nullable=True)


class Destination(Base):
    __tablename__ = 'destination'

    id = sa.Column(sa.UUID, primary_key=True)
    name = sa.Column(sa.VARCHAR(255), nullable=False)
    latitude = sa.Column(sa.REAL, nullable=False)
    longitude = sa.Column(sa.REAL, nullable=False)

    user_id = sa.Column(sa.UUID, sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    message_id = sa.Column(sa.Integer, nullable=False)
    map_message_id = sa.Column(sa.Integer, nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = sa.Column(sa.UUID, primary_key=True)
    name = sa.Column(sa.VARCHAR(255), nullable=False)
    slug = sa.Column(sa.VARCHAR(20), nullable=False)


class OSMType(Base):
    __tablename__ = 'osm_type'

    id = sa.Column(sa.UUID, primary_key=True)
    name = sa.Column(sa.VARCHAR(255), nullable=False)
    type = sa.Column(sa.VARCHAR(255), nullable=False)

    category_id = sa.Column(sa.ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
