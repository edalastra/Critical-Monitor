"""empty message

Revision ID: 05dc0a849478
Revises: 1626e1d1e17d
Create Date: 2021-10-19 19:52:09.684358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05dc0a849478'
down_revision = '1626e1d1e17d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('config', sa.Column('point_x1', sa.Integer(), nullable=True))
    op.add_column('config', sa.Column('point_y1', sa.Integer(), nullable=True))
    op.add_column('config', sa.Column('point_x2', sa.Integer(), nullable=True))
    op.add_column('config', sa.Column('point_y2', sa.Integer(), nullable=True))
    op.add_column('config', sa.Column('point_x3', sa.Integer(), nullable=True))
    op.add_column('config', sa.Column('point_y3', sa.Integer(), nullable=True))
    op.add_column('config', sa.Column('point_x4', sa.Integer(), nullable=True))
    op.add_column('config', sa.Column('point_y4', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('config', 'point_y4')
    op.drop_column('config', 'point_x4')
    op.drop_column('config', 'point_y3')
    op.drop_column('config', 'point_x3')
    op.drop_column('config', 'point_y2')
    op.drop_column('config', 'point_x2')
    op.drop_column('config', 'point_y1')
    op.drop_column('config', 'point_x1')
    # ### end Alembic commands ###
