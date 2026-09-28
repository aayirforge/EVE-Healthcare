from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.diagnostic_test import DiagnosticTest


def test_create_booking_success(client, auth_headers, test_setup):
    centre = test_setup["centre"]
    test = test_setup["test"]
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    response = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_time": future_time,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["centre_id"] == centre.id
    assert data["test_id"] == test.id
    assert data["status"] == "PENDING"
    assert float(data["amount"]) == 400.00
    assert data["centre_name"] == centre.name
    assert data["test_name"] == test.name


def test_create_booking_unauthorized(client, test_setup):
    centre = test_setup["centre"]
    test = test_setup["test"]
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    response = client.post(
        "/bookings/",
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_time": future_time,
        },
    )
    assert response.status_code == 401


def test_create_booking_past_time(client, auth_headers, test_setup):
    centre = test_setup["centre"]
    test = test_setup["test"]
    past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    response = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": centre.id,
            "test_id": test.id,
            "appointment_time": past_time,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Appointment date/time must be in the future"


def test_create_booking_invalid_centre(client, auth_headers, test_setup):
    test = test_setup["test"]
    future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": 99999,
            "test_id": test.id,
            "appointment_time": future_time,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Diagnostic centre not found"


def test_create_booking_invalid_test(client, auth_headers, test_setup):
    centre = test_setup["centre"]
    future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": centre.id,
            "test_id": 99999,
            "appointment_time": future_time,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Diagnostic test not found"


def test_create_booking_test_not_offered(client, auth_headers, test_setup, db):
    centre = test_setup["centre"]
    unoffered_test = DiagnosticTest(
        name="Unlinked Test",
        price=Decimal("1500.00"),
    )
    db.add(unoffered_test)
    db.commit()
    db.refresh(unoffered_test)

    future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    response = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": centre.id,
            "test_id": unoffered_test.id,
            "appointment_time": future_time,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Test is not offered by the selected diagnostic centre"


def test_get_booking_by_id(client, auth_headers, test_setup):
    future_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    create_res = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": test_setup["centre"].id,
            "test_id": test_setup["test"].id,
            "appointment_time": future_time,
        },
    )
    booking_id = create_res.json()["id"]

    get_res = client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == booking_id


def test_get_booking_unauthorized_access(
    client, auth_headers, second_auth_headers, test_setup
):
    future_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    create_res = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": test_setup["centre"].id,
            "test_id": test_setup["test"].id,
            "appointment_time": future_time,
        },
    )
    booking_id = create_res.json()["id"]

    other_res = client.get(f"/bookings/{booking_id}", headers=second_auth_headers)
    assert other_res.status_code == 403
    assert other_res.json()["detail"] == "Not authorized to access this booking"


def test_get_booking_not_found(client, auth_headers):
    response = client.get("/bookings/99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_list_user_bookings(client, auth_headers, second_auth_headers, test_setup):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    for _ in range(3):
        client.post(
            "/bookings/",
            headers=auth_headers,
            json={
                "centre_id": test_setup["centre"].id,
                "test_id": test_setup["test"].id,
                "appointment_time": future_time,
            },
        )
    client.post(
        "/bookings/",
        headers=second_auth_headers,
        json={
            "centre_id": test_setup["centre"].id,
            "test_id": test_setup["test"].id,
            "appointment_time": future_time,
        },
    )

    res = client.get("/bookings/", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_cancel_booking_success(client, auth_headers, test_setup):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_res = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": test_setup["centre"].id,
            "test_id": test_setup["test"].id,
            "appointment_time": future_time,
        },
    )
    booking_id = create_res.json()["id"]

    cancel_res = client.post(f"/bookings/{booking_id}/cancel", headers=auth_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"


def test_cancel_booking_already_cancelled(client, auth_headers, test_setup):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_res = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": test_setup["centre"].id,
            "test_id": test_setup["test"].id,
            "appointment_time": future_time,
        },
    )
    booking_id = create_res.json()["id"]
    client.post(f"/bookings/{booking_id}/cancel", headers=auth_headers)

    second_cancel = client.post(f"/bookings/{booking_id}/cancel", headers=auth_headers)
    assert second_cancel.status_code == 400
    assert "Cannot cancel booking with status 'CANCELLED'" in second_cancel.json()["detail"]


def test_cancel_booking_unauthorized_user(
    client, auth_headers, second_auth_headers, test_setup
):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_res = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": test_setup["centre"].id,
            "test_id": test_setup["test"].id,
            "appointment_time": future_time,
        },
    )
    booking_id = create_res.json()["id"]

    other_cancel = client.post(
        f"/bookings/{booking_id}/cancel", headers=second_auth_headers
    )
    assert other_cancel.status_code == 403
