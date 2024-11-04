
from alembic import op
import sqlalchemy as sa

revision = 'xxxxxxxxxxxx'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, unique=True, index=True),
        sa.Column('hashed_password', sa.String),
    )
    op.create_table(
        'images',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, index=True),
        sa.Column('file_path', sa.String),
        sa.Column('upload_date', sa.DateTime),
        sa.Column('resolution', sa.String),
        sa.Column('size', sa.Float),
        sa.Column('tags', sa.String),
    )

def downgrade():
    op.drop_table('images')
    op.drop_table('users')
