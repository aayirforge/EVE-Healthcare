from datetime import datetime, timedelta, timezone


def create_pending_booking(client, auth_headers, test_setup):
    future_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post(
        "/bookings/",
        headers=auth_headers,
        json={
            "centre_id": test_setup["centre"].id,
            "test_id": test_setup["test"].id,
            "appointment_time": future_time,
        },
    )
    return response.json()["id"]


def test_payment_success(client, auth_headers, test_setup):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": booking_id,
            "status": "SUCCESS",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == booking_id
    assert data["status"] == "SUCCESS"
    assert data["booking_status"] == "CONFIRMED"
    assert float(data["amount"]) == 400.00

    booking_res = client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert booking_res.json()["status"] == "CONFIRMED"


def test_payment_failure(client, auth_headers, test_setup):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": booking_id,
            "status": "FAILED",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == booking_id
    assert data["status"] == "FAILED"
    assert data["booking_status"] == "FAILED"

    booking_res = client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert booking_res.json()["status"] == "FAILED"


def test_payment_unauthorized_user(
    client, auth_headers, second_auth_headers, test_setup
):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    response = client.post(
        "/payments/",
        headers=second_auth_headers,
        json={
            "booking_id": booking_id,
            "status": "SUCCESS",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to pay for this booking"


def test_payment_nonexistent_booking(client, auth_headers):
    response = client.post(
        "/payments/",
        headers=auth_headers,
        json={
            "booking_id": 99999,
            "status": "SUCCESS",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_payment_invalid_state_transition(client, auth_headers, test_setup):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    first_res = client.post(
        "/payments/",
        headers=auth_headers,
        json={"booking_id": booking_id, "status": "SUCCESS"},
    )
    assert first_res.status_code == 200

    second_res = client.post(
        "/payments/",
        headers=auth_headers,
        json={"booking_id": booking_id, "status": "SUCCESS"},
    )
    assert second_res.status_code == 400
    assert "Cannot process payment for booking with status 'CONFIRMED'" in second_res.json()["detail"]


def test_payment_cancelled_booking(client, auth_headers, test_setup):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    client.post(f"/bookings/{booking_id}/cancel", headers=auth_headers)

    response = client.post(
        "/payments/",
        headers=auth_headers,
        json={"booking_id": booking_id, "status": "SUCCESS"},
    )
    assert response.status_code == 400
    assert "Cannot process payment for booking with status 'CANCELLED'" in response.json()["detail"]


def test_payment_missing_token(client, auth_headers, test_setup):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    response = client.post(
        "/payments/",
        json={"booking_id": booking_id, "status": "SUCCESS"},
    )
    assert response.status_code == 401
