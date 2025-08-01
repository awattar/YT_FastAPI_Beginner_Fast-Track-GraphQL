"""Make author field required with validation constraint

Revision ID: c6eddb176806
Revises: 6a53c76dbe2c
Create Date: 2025-07-30 18:37:26.972796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6eddb176806'
down_revision = '6a53c76dbe2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # First, update existing NULL author values to a default value
    op.execute("UPDATE post SET author = 'Unknown Author' WHERE author IS NULL")
    
    # Then make the column NOT NULL
    op.alter_column('post', 'author',
               existing_type=sa.VARCHAR(),
               nullable=False)
    
    # Add check constraint for non-empty author
    op.create_check_constraint('author_not_empty', 'post', 'length(trim(author)) > 0')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Remove check constraint first
    op.drop_constraint('author_not_empty', 'post', type_='check')
    
    # Then make the column nullable
    op.alter_column('post', 'author',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
