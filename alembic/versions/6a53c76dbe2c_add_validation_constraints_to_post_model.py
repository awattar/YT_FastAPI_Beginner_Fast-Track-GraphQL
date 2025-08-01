"""Add validation constraints to Post model

Revision ID: 6a53c76dbe2c
Revises: 0f62ca6e975a
Create Date: 2025-07-30 11:49:13.280992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a53c76dbe2c'
down_revision = '0f62ca6e975a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Add string length constraints
    op.alter_column('post', 'title',
               existing_type=sa.VARCHAR(),
               type_=sa.VARCHAR(length=200),
               nullable=False)
    op.alter_column('post', 'content',
               existing_type=sa.VARCHAR(),
               type_=sa.VARCHAR(length=10000),
               nullable=False)
    op.alter_column('post', 'author',
               existing_type=sa.VARCHAR(),
               type_=sa.VARCHAR(length=100))
    
    # Add check constraints for non-empty strings
    op.create_check_constraint('title_not_empty', 'post', 'length(trim(title)) > 0')
    op.create_check_constraint('content_not_empty', 'post', 'length(trim(content)) > 0')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop check constraints first
    op.drop_constraint('title_not_empty', 'post', type_='check')
    op.drop_constraint('content_not_empty', 'post', type_='check')
    
    # Revert string length constraints
    op.alter_column('post', 'title',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.VARCHAR(),
               nullable=True)
    op.alter_column('post', 'content', 
               existing_type=sa.VARCHAR(length=10000),
               type_=sa.VARCHAR(),
               nullable=True)
    op.alter_column('post', 'author',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.VARCHAR())
    # ### end Alembic commands ###
