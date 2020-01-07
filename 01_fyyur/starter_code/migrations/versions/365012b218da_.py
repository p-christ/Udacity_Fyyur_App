"""empty message

Revision ID: 365012b218da
Revises: d8373a546198
Create Date: 2020-01-06 10:18:40.766532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '365012b218da'
down_revision = 'd8373a546198'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('start_time', sa.Date(), nullable=False))
    op.drop_column('show', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('date', sa.DATE(), autoincrement=False, nullable=False))
    op.drop_column('show', 'start_time')
    # ### end Alembic commands ###