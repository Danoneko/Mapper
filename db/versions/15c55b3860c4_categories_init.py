"""categories_init

Revision ID: 15c55b3860c4
Revises: 99749d91db60
Create Date: 2024-06-16 16:33:36.266489

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '15c55b3860c4'
down_revision: Union[str, None] = '99749d91db60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    category = sa.table(
        "category",
        sa.column("id", sa.UUID),
        sa.Column("name", sa.VARCHAR),
        sa.Column("slug", sa.VARCHAR(10)),
    )

    op.bulk_insert(category, [
        {
            "id": "2D13902C-DEC0-4D5E-97F1-F7A8B0353112",
            "name": "Питание",
            "slug": "food",
        },
        {
            "id": "4A2117A2-FD26-41B0-9CF0-86729C8338F4",
            "name": "Образование",
            "slug": "education",
        },
        {
            "id": "F41B6869-526E-4BA7-A256-2E6DA6414B3D",
            "name": "Транспорт",
            "slug": "transport",
        },
        {
            "id": "AAD2939F-F3A4-44BB-B8B5-A32274982D93",
            "name": "Финансы",
            "slug": "finance",
        },
        {
            "id": "E3EA83AF-84DE-4B42-9A8E-2350F8D5DC78",
            "name": "Здоровье",
            "slug": "health",
        },
        {
            "id": "CF16D416-5D73-49B3-9064-FE87EB97EF14",
            "name": "Развлечение",
            "slug": "entertainment",
        },
        {
            "id": "BB1DA6DD-E389-4782-86CA-5CCAF2C769EA",
            "name": "Общественное",
            "slug": "public",
        },
        {
            "id": "3A8841C5-1EC8-4F66-A985-39EF528F7892",
            "name": "Другое",
            "slug": "Other",
        },
    ])


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM category"))