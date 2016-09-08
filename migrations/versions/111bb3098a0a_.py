"""empty message

Revision ID: 111bb3098a0a
Revises: d347894495cb
Create Date: 2016-08-26 13:39:45.592545

"""

# revision identifiers, used by Alembic.
revision = '111bb3098a0a'
down_revision = 'd347894495cb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pile', 'testmitigrate')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pile', sa.Column('testmitigrate', mysql.VARCHAR(length=255), nullable=True))
    ### end Alembic commands ###
