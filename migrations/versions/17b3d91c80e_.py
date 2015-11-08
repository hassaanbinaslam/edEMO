"""empty message

Revision ID: 17b3d91c80e
Revises: None
Create Date: 2015-11-05 15:25:02.597000

"""

# revision identifiers, used by Alembic.
revision = '17b3d91c80e'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['user_role.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('survey_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('survey',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('creation_date', sa.Date(), nullable=False),
    sa.Column('expiry_date', sa.Date(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('survey_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['survey_group_id'], ['survey_group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('survey_group_member',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('survey_group_id', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['survey_group_id'], ['survey_group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('survey_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('answer', sa.String(length=255), nullable=False),
    sa.Column('survey_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['survey_id'], ['survey.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('survey_data')
    op.drop_table('survey_group_member')
    op.drop_table('survey')
    op.drop_table('survey_group')
    op.drop_table('user')
    op.drop_table('user_role')
    ### end Alembic commands ###