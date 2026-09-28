from app.api.dependencies import get_current_user
from app.api.routes import (
    auth_router,
    bookings_router,
    centres_router,
    payments_router,
    tests_router,
)

__all__ = [
    "get_current_user",
    "auth_router",
    "centres_router",
    "tests_router",
    "bookings_router",
    "payments_router",
]
