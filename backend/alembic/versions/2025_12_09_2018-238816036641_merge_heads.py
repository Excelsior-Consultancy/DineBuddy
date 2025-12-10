"""Merge heads

Revision ID: 238816036641
Revises: e147a51226c7, 4aaf4ef923aa
Create Date: 2025-12-09 20:18:02.704871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '238816036641'
down_revision: Union[str, None] = ('e147a51226c7', '4aaf4ef923aa')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
