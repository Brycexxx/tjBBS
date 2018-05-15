"""initial migration

Revision ID: f89ec9b438af
Revises: ed6351ac8239
Create Date: 2018-05-14 16:50:12.069029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f89ec9b438af'
down_revision = 'ed6351ac8239'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collections',
    sa.Column('collecting_user_id', sa.Integer(), nullable=False),
    sa.Column('collected_idle_item_id', sa.Integer(), nullable=False),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['collected_idle_item_id'], ['idle_items.id'], ),
    sa.ForeignKeyConstraint(['collecting_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('collecting_user_id', 'collected_idle_item_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('collections')
    # ### end Alembic commands ###