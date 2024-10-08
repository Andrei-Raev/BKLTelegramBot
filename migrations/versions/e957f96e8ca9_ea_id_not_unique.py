"""ea id not unique

Revision ID: e957f96e8ca9
Revises: 75ff5834ca9a
Create Date: 2024-08-27 19:08:21.002909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'e957f96e8ca9'
down_revision: Union[str, None] = '75ff5834ca9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ea_id', table_name='users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ea_id', 'users', ['ea_id'], unique=True)
    # ### end Alembic commands ###
