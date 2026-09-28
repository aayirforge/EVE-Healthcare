from datetime import datetime, timedelta, timezone

from app.models.payment import Payment


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


def test_webhook_success(client, auth_headers, test_setup, db):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    payload = {
        "event_id": "evt_webhook_success_001",
        "booking_id": booking_id,
        "payment_status": "SUCCESS",
        "provider_payment_id": "prov_tx_12345",
    }
    response = client.post("/payments/webhook/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["event_id"] == "evt_webhook_success_001"
    assert data["booking_id"] == booking_id
    assert data["booking_status"] == "CONFIRMED"

    payments = db.query(Payment).filter(Payment.booking_id == booking_id).all()
    assert len(payments) == 1
    assert payments[0].status == "SUCCESS"
    assert payments[0].provider_payment_id == "prov_tx_12345"


def test_webhook_failure(client, auth_headers, test_setup, db):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    payload = {
        "event_id": "evt_webhook_failed_001",
        "booking_id": booking_id,
        "payment_status": "FAILED",
        "provider_payment_id": "prov_tx_failed",
    }
    response = client.post("/payments/webhook/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["booking_status"] == "FAILED"

    payments = db.query(Payment).filter(Payment.booking_id == booking_id).all()
    assert len(payments) == 1
    assert payments[0].status == "FAILED"


def test_webhook_idempotency_duplicate_event(client, auth_headers, test_setup, db):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    payload = {
        "event_id": "evt_idempotent_test_001",
        "booking_id": booking_id,
        "payment_status": "SUCCESS",
        "provider_payment_id": "prov_tx_repeat",
    }

    first_res = client.post("/payments/webhook/", json=payload)
    assert first_res.status_code == 200
    assert first_res.json()["status"] == "processed"

    second_res = client.post("/payments/webhook/", json=payload)
    assert second_res.status_code == 200
    assert second_res.json()["status"] == "ignored"
    assert second_res.json()["message"] == "Duplicate event already processed"

    third_res = client.post("/payments/webhook/", json=payload)
    assert third_res.status_code == 200
    assert third_res.json()["status"] == "ignored"

    payments = db.query(Payment).filter(Payment.booking_id == booking_id).all()
    assert len(payments) == 1


def test_webhook_nonexistent_booking(client):
    payload = {
        "event_id": "evt_nonexistent_001",
        "booking_id": 99999,
        "payment_status": "SUCCESS",
    }
    response = client.post("/payments/webhook/", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_webhook_invalid_payload(client):
    payload = {
        "booking_id": 1,
        "payment_status": "INVALID_STATUS",
    }
    response = client.post("/payments/webhook/", json=payload)
    assert response.status_code == 422


def test_webhook_preserves_confirmed_booking_state(client, auth_headers, test_setup, db):
    booking_id = create_pending_booking(client, auth_headers, test_setup)
    first_payload = {
        "event_id": "evt_first_success",
        "booking_id": booking_id,
        "payment_status": "SUCCESS",
    }
    client.post("/payments/webhook/", json=first_payload)

    second_payload = {
        "event_id": "evt_second_different_event_failed",
        "booking_id": booking_id,
        "payment_status": "FAILED",
    }
    second_res = client.post("/payments/webhook/", json=second_payload)
    assert second_res.status_code == 200

    booking_res = client.get(f"/bookings/{booking_id}", headers=auth_headers)
    assert booking_res.json()["status"] == "CONFIRMED"


def test_webhook_concurrent_requests(client, auth_headers, test_setup, db):
    from concurrent.futures import ThreadPoolExecutor

    booking_id = create_pending_booking(client, auth_headers, test_setup)
    payload = {
        "event_id": "evt_concurrent_001",
        "booking_id": booking_id,
        "payment_status": "SUCCESS",
        "provider_payment_id": "prov_concurrent_123",
    }

    def send_webhook():
        return client.post("/payments/webhook/", json=payload)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_webhook) for _ in range(5)]
        responses = [f.result() for f in futures]

    for r in responses:
        assert r.status_code == 200

    processed_count = sum(1 for r in responses if r.json()["status"] == "processed")
    ignored_count = sum(1 for r in responses if r.json()["status"] == "ignored")

    assert processed_count == 1
    assert ignored_count == 4

    payments = db.query(Payment).filter(Payment.booking_id == booking_id).all()
    assert len(payments) == 1

