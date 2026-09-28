from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0c53065b9ca6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('diagnostic_centres',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostic_centres_id'), 'diagnostic_centres', ['id'], unique=False)
    op.create_index(op.f('ix_diagnostic_centres_name'), 'diagnostic_centres', ['name'], unique=False)
    op.create_table('diagnostic_tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('price >= 0', name='chk_test_price_positive'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostic_tests_id'), 'diagnostic_tests', ['id'], unique=False)
    op.create_index(op.f('ix_diagnostic_tests_name'), 'diagnostic_tests', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('bookings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('centre_id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=False),
    sa.Column('appointment_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('PENDING', 'CONFIRMED', 'FAILED', 'CANCELLED')", name='chk_booking_status_valid'),
    sa.CheckConstraint('amount >= 0', name='chk_booking_amount_positive'),
    sa.ForeignKeyConstraint(['centre_id'], ['diagnostic_centres.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['test_id'], ['diagnostic_tests.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_centre_id'), 'bookings', ['centre_id'], unique=False)
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'], unique=False)
    op.create_index(op.f('ix_bookings_test_id'), 'bookings', ['test_id'], unique=False)
    op.create_index(op.f('ix_bookings_user_id'), 'bookings', ['user_id'], unique=False)
    op.create_table('centre_tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('centre_id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=False),
    sa.Column('custom_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('custom_price >= 0', name='chk_centre_test_price_positive'),
    sa.ForeignKeyConstraint(['centre_id'], ['diagnostic_centres.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['test_id'], ['diagnostic_tests.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('centre_id', 'test_id', name='uq_centre_test')
    )
    op.create_index(op.f('ix_centre_tests_centre_id'), 'centre_tests', ['centre_id'], unique=False)
    op.create_index(op.f('ix_centre_tests_id'), 'centre_tests', ['id'], unique=False)
    op.create_index(op.f('ix_centre_tests_test_id'), 'centre_tests', ['test_id'], unique=False)
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('provider_payment_id', sa.String(length=100), nullable=True),
    sa.Column('idempotency_key', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('SUCCESS', 'FAILED')", name='chk_payment_status_valid'),
    sa.CheckConstraint('amount >= 0', name='chk_payment_amount_positive'),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_booking_id'), 'payments', ['booking_id'], unique=False)
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_idempotency_key'), 'payments', ['idempotency_key'], unique=True)
    op.create_index(op.f('ix_payments_status'), 'payments', ['status'], unique=False)
    op.create_table('webhook_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.String(length=100), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('payment_status', sa.String(length=30), nullable=False),
    sa.Column('provider_payment_id', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_events_booking_id'), 'webhook_events', ['booking_id'], unique=False)
    op.create_index(op.f('ix_webhook_events_event_id'), 'webhook_events', ['event_id'], unique=True)
    op.create_index(op.f('ix_webhook_events_id'), 'webhook_events', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_webhook_events_id'), table_name='webhook_events')
    op.drop_index(op.f('ix_webhook_events_event_id'), table_name='webhook_events')
    op.drop_index(op.f('ix_webhook_events_booking_id'), table_name='webhook_events')
    op.drop_table('webhook_events')
    op.drop_index(op.f('ix_payments_status'), table_name='payments')
    op.drop_index(op.f('ix_payments_idempotency_key'), table_name='payments')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_booking_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_centre_tests_test_id'), table_name='centre_tests')
    op.drop_index(op.f('ix_centre_tests_id'), table_name='centre_tests')
    op.drop_index(op.f('ix_centre_tests_centre_id'), table_name='centre_tests')
    op.drop_table('centre_tests')
    op.drop_index(op.f('ix_bookings_user_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_test_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_status'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_centre_id'), table_name='bookings')
    op.drop_table('bookings')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_diagnostic_tests_name'), table_name='diagnostic_tests')
    op.drop_index(op.f('ix_diagnostic_tests_id'), table_name='diagnostic_tests')
    op.drop_table('diagnostic_tests')
    op.drop_index(op.f('ix_diagnostic_centres_name'), table_name='diagnostic_centres')
    op.drop_index(op.f('ix_diagnostic_centres_id'), table_name='diagnostic_centres')
    op.drop_table('diagnostic_centres')
