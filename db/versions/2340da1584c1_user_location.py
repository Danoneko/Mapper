"""user_location

Revision ID: 2340da1584c1
Revises: 279d9bf847f2
Create Date: 2024-06-17 03:17:50.099113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2340da1584c1'
down_revision: Union[str, None] = '279d9bf847f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('recent_latitude', sa.REAL, nullable=True))
    op.add_column('user', sa.Column('recent_longitude', sa.REAL, nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'recent_latitude')
    op.drop_column('user', 'recent_longitude')
