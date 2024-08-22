from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6683faa91b65'
down_revision = '85c43fee74c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Изменяем кодировку всей таблицы на utf8mb4
    op.execute('ALTER TABLE support_log CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_bin')

    # Если требуется, можно также изменить кодировку для конкретных столбцов таким образом:
    # op.execute('ALTER TABLE support_log MODIFY emoji VARCHAR(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin')
    # op.execute('ALTER TABLE support_log MODIFY message VARCHAR(16384) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin')


def downgrade() -> None:
    # Возвращаем предыдущую кодировку, если нужна поддержка отката
    op.execute('ALTER TABLE support_log CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci')

    # Восстанавливаем изменения в конкретных столбцах (если они были изменены)
    # op.execute('ALTER TABLE support_log MODIFY emoji VARCHAR(5) CHARACTER SET utf8 COLLATE utf8_general_ci')
    # op.execute('ALTER TABLE support_log MODIFY message VARCHAR(16384) CHARACTER SET utf8 COLLATE utf8_general_ci')
