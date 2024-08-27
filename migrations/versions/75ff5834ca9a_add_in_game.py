"""add in_game

Revision ID: 75ff5834ca9a
Revises: f55e6f16c60f
Create Date: 2024-08-27 18:07:13.278892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '75ff5834ca9a'
down_revision: Union[str, None] = 'f55e6f16c60f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('in_game', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'in_game')
    # ### end Alembic commands ###
