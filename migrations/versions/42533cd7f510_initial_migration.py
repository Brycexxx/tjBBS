"""initial migration

Revision ID: 42533cd7f510
Revises: a21a146cf2c0
Create Date: 2018-05-30 19:58:04.892981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42533cd7f510'
down_revision = 'a21a146cf2c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('system_messages', sa.Column('user', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('system_messages', 'user')
    # ### end Alembic commands ###