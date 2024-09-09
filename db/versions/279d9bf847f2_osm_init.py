"""osm_init

Revision ID: 279d9bf847f2
Revises: 15c55b3860c4
Create Date: 2024-06-16 19:09:21.763336

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '279d9bf847f2'
down_revision: Union[str, None] = '15c55b3860c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    osm_type = sa.table(
        "osm_type",
        sa.Column("id", sa.UUID),
        sa.Column("name", sa.VARCHAR),
        sa.Column("type", sa.VARCHAR),
        sa.Column("category_id", sa.UUID, sa.ForeignKey("category.id")),
    )

    op.bulk_insert(osm_type, [
        {
            "id": uuid.uuid4(),
            "name": "bar",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "biergarten",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "cafe",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "fast_food",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "food_court",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "ice_cream",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "pub",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "restaurant",
            "type": "amenity",
            "category_id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
        },
        {
            "id": uuid.uuid4(),
            "name": "bicycle_parking",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "bicycle_rental",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "bus_station",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "car_rental",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "car_wash",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "vehicle_inspection",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "charging_station",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "fuel",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "motorcycle_parking",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "parking",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "taxi",
            "type": "amenity",
            "category_id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
        },
        {
            "id": uuid.uuid4(),
            "name": "atm",
            "type": "amenity",
            "category_id": "AAD2939F-F3A4-44BB-B8B5-A32274982D93",
        },
        {
            "id": uuid.uuid4(),
            "name": "bank",
            "type": "amenity",
            "category_id": "AAD2939F-F3A4-44BB-B8B5-A32274982D93",
        },
        {
            "id": uuid.uuid4(),
            "name": "bureau_de_change",
            "type": "amenity",
            "category_id": "AAD2939F-F3A4-44BB-B8B5-A32274982D93",
        },
        {
            "id": uuid.uuid4(),
            "name": "clinic",
            "type": "amenity",
            "category_id": "E3EA83AF-84DE-4B42-9A8E-2350F8D5DC78",
        },
        {
            "id": uuid.uuid4(),
            "name": "dentist",
            "type": "amenity",
            "category_id": "E3EA83AF-84DE-4B42-9A8E-2350F8D5DC78",
        },
        {
            "id": uuid.uuid4(),
            "name": "doctors",
            "type": "amenity",
            "category_id": "E3EA83AF-84DE-4B42-9A8E-2350F8D5DC78",
        },
        {
            "id": uuid.uuid4(),
            "name": "hospital",
            "type": "amenity",
            "category_id": "E3EA83AF-84DE-4B42-9A8E-2350F8D5DC78",
        },
        {
            "id": uuid.uuid4(),
            "name": "pharmacy",
            "type": "amenity",
            "category_id": "E3EA83AF-84DE-4B42-9A8E-2350F8D5DC78",
        },
        {
            "id": uuid.uuid4(),
            "name": "veterinary",
            "type": "amenity",
            "category_id": "E3EA83AF-84DE-4B42-9A8E-2350F8D5DC78",
        },
        {
            "id": uuid.uuid4(),
            "name": "casino",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "cinema",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "community_centre",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "conference_centre",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "events_venue",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "exhibition_centre",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "music_venue",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "nightclub",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "planetarium",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "public_bookcase",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "theatre",
            "type": "amenity",
            "category_id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
        },
        {
            "id": uuid.uuid4(),
            "name": "bbq",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "drinking_water",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "townhall",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "post_office",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "parcel_locker",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "shower",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "telephone",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "toilets",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "water_point",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "marketplace",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "place_of_worship",
            "type": "amenity",
            "category_id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
        },
        {
            "id": uuid.uuid4(),
            "name": "recycling",
            "type": "amenity",
            "category_id": "3A8841C5-1EC8-4F66-A985-39EF528F7892",
        },
        {
            "id": uuid.uuid4(),
            "name": "waste_disposal",
            "type": "amenity",
            "category_id": "3A8841C5-1EC8-4F66-A985-39EF528F7892",
        },
        {
            "id": uuid.uuid4(),
            "name": "photo_booth",
            "type": "amenity",
            "category_id": "3A8841C5-1EC8-4F66-A985-39EF528F7892",
        },
        {
            "id": uuid.uuid4(),
            "name": "grave_yard",
            "type": "amenity",
            "category_id": "3A8841C5-1EC8-4F66-A985-39EF528F7892",
        },
        {
            "id": uuid.uuid4(),
            "name": "animal_shelter",
            "type": "amenity",
            "category_id": "3A8841C5-1EC8-4F66-A985-39EF528F7892",
        },
        {
            "id": uuid.uuid4(),
            "name": "college",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },
        {
            "id": uuid.uuid4(),
            "name": "driving_school",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },
        {
            "id": uuid.uuid4(),
            "name": "kindergarten",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },
        {
            "id": uuid.uuid4(),
            "name": "language_school",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },
        {
            "id": uuid.uuid4(),
            "name": "library",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },
        {
            "id": uuid.uuid4(),
            "name": "music_school",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },
        {
            "id": uuid.uuid4(),
            "name": "school",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },
        {
            "id": uuid.uuid4(),
            "name": "university",
            "type": "amenity",
            "category_id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
        },

    ])


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM osm_type"))
