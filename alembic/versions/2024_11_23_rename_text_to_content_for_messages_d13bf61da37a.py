"""rename text to content for messages

Revision ID: d13bf61da37a
Revises: 28efe30d51e2
Create Date: 2024-11-23 22:43:38.759629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd13bf61da37a'
down_revision: Union[str, None] = '28efe30d51e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('message', sa.Column('content', sa.Text(), nullable=True))
    op.execute("UPDATE message SET content = text")
    op.drop_column('message', 'text')
    op.alter_column('message', 'content', nullable=False)



def downgrade() -> None:
    op.add_column('message', sa.Column('text', sa.Text(), nullable=True))
    op.execute("UPDATE message SET text = content")
    op.drop_column('message', 'content')
    op.alter_column('message', 'text', nullable=True)
