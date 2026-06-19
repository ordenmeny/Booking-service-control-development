"""add booking status

Revision ID: d50d06262e5e
Revises: a0c5196fecb6
Create Date: 2026-06-19 12:04:02.718292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd50d06262e5e'
down_revision: Union[str, Sequence[str], None] = 'a0c5196fecb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


status_enum = sa.Enum(
    "pending",
    "confirmed",
    "failed",
    name="status_enum",
)

def upgrade() -> None:
    status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'booking',
        sa.Column(
        'status', status_enum,
                  sa.Enum('PENDING', 'CONFIRMED', 'FAILED', name='status_enum'),
                  server_default='pending',
                  nullable=False),)
    



def downgrade() -> None:
    op.drop_column('booking', 'status')
    status_enum.drop(op.get_bind(), checkfirst=True)

