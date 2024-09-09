"""init

Revision ID: 99749d91db60
Revises: 
Create Date: 2024-06-16 15:34:47.632894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '99749d91db60'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("user",
                    sa.Column("id", sa.UUID, primary_key=True),
                    sa.Column("chat_id", sa.Integer, nullable=False, comment="ID чата в telegram"),
                    sa.Column("search_distance", sa.Integer, nullable=False, default=300, comment="Радиус поиска в метрах"),
                    sa.Column("status", sa.VARCHAR(15), nullable=False, comment="int представление статуса")

                    )

    op.create_table("destination",
                    sa.Column("id", sa.UUID, primary_key=True),
                    sa.Column("user_id", sa.UUID, sa.ForeignKey("user.id"), nullable=False),
                    sa.Column("latitude", sa.REAL, nullable=False),
                    sa.Column("longitude", sa.REAL, nullable=False),
                    sa.Column("name", sa.VARCHAR, nullable=False),
                    sa.Column('message_id', sa.Integer(), nullable=True),
                    sa.Column('map_message_id', sa.Integer(), nullable=True)
                    )

    op.create_table("category",
                    sa.Column("id", sa.UUID, primary_key=True),
                    sa.Column("name", sa.VARCHAR, nullable=False, comment="текст категории на русском"),
                    sa.Column("slug", sa.VARCHAR(20), nullable=False, comment="короткое название на английском"),
                    )

    op.create_table("osm_type",
                    sa.Column("id", sa.UUID, primary_key=True),
                    sa.Column("name", sa.VARCHAR, nullable=False),
                    sa.Column("type", sa.VARCHAR, nullable=False),
                    sa.Column("category_id", sa.UUID, sa.ForeignKey("category.id"), nullable=False),
                    )


def downgrade() -> None:
    op.drop_table("osm_type")
    op.drop_table("category")
    op.drop_table("destination")
    op.drop_table("user")
