"""Add file column

Revision ID: 218765d73188
Revises: 3291f8a19cef
Create Date: 2024-02-23 16:27:55.933783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '218765d73188'
down_revision: Union[str, None] = '3291f8a19cef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('file', sa.JSON()))


def downgrade() -> None:
    pass
