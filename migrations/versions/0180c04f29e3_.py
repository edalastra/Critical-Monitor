"""empty message

Revision ID: 0180c04f29e3
Revises: a6e92cc50a6a
Create Date: 2021-11-12 16:35:05.029345

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0180c04f29e3'
down_revision = 'a6e92cc50a6a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('occurrence_config_id_fkey', 'occurrence', type_='foreignkey')
    op.create_foreign_key(None, 'occurrence', 'config', ['config_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'occurrence', type_='foreignkey')
    op.create_foreign_key('occurrence_config_id_fkey', 'occurrence', 'config', ['config_id'], ['id'])
    # ### end Alembic commands ###