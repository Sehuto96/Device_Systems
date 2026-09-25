"""add authentication fields to users

Revision ID: 3fe4a0b9022f
Revises: 21ef778e543d
Create Date: 2026-09-21 22:36:19.756645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fe4a0b9022f'
down_revision: Union[str, Sequence[str], None] = '21ef778e543d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Agregar la columna como nullable primero (para no romper filas existentes)
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("hashed_password", sa.String(length=255), nullable=True)
        )

    # 2. Rellenar cualquier fila existente con un valor temporal no usable para login
    op.execute(
        "UPDATE users SET hashed_password = 'MIGRATION_PLACEHOLDER_INVALID_HASH' "
        "WHERE hashed_password IS NULL"
    )

    # 3. Ahora sí, forzar NOT NULL
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(length=255),
            nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("hashed_password")