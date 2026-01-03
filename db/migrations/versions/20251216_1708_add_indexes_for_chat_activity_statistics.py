"""add indexes for chat activity statistics

Revision ID: 6cc4831a1bca
Revises: 3778fe160734
Create Date: 2025-12-16 17:08:40.269782

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6cc4831a1bca"
down_revision: Union[str, None] = "3778fe160734"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Events per day, DAU
    op.create_index(
        "idx_chats_event_statistics_date",
        "chats_event_statistics",
        ["date"],
        unique=False,
    )

    # Retention, WAU, MAU
    op.create_index(
        "idx_chats_event_statistics_chat_date",
        "chats_event_statistics",
        ["chat_id", "date"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "idx_chats_event_statistics_chat_date",
        table_name="chats_event_statistics",
    )
    op.drop_index(
        "idx_chats_event_statistics_date",
        table_name="chats_event_statistics",
    )
