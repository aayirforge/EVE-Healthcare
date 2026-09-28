def test_create_centre(client, auth_headers):
    response = client.post(
        "/centres/",
        headers=auth_headers,
        json={
            "name": "Fortis Diagnostics",
            "location": "Bannerghatta Road, Bangalore",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Fortis Diagnostics"
    assert data["location"] == "Bannerghatta Road, Bangalore"
    assert data["available_tests"] == []


def test_create_centre_unauthorized(client):
    response = client.post(
        "/centres/",
        json={
            "name": "Unauthorized Centre",
            "location": "Some Location",
        },
    )
    assert response.status_code == 401


def test_get_centre_details(client, test_setup):
    centre_id = test_setup["centre"].id
    response = client.get(f"/centres/{centre_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == centre_id
    assert len(data["available_tests"]) == 1
    assert data["available_tests"][0]["name"] == "Complete Blood Count"
    assert float(data["available_tests"][0]["price"]) == 400.00


def test_get_centre_not_found(client):
    response = client.get("/centres/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Diagnostic centre not found"


def test_list_centres_pagination(client, auth_headers):
    for i in range(5):
        client.post(
            "/centres/",
            headers=auth_headers,
            json={"name": f"Centre {i}", "location": f"City {i}"},
        )
    response = client.get("/centres/?page=1&size=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 5
    assert data["pages"] == 2


def test_create_diagnostic_test(client, auth_headers):
    response = client.post(
        "/tests/",
        headers=auth_headers,
        json={
            "name": "Lipid Profile",
            "description": "Cholesterol and triglyceride screening",
            "price": "750.50",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lipid Profile"
    assert float(data["price"]) == 750.50


def test_create_diagnostic_test_negative_price(client, auth_headers):
    response = client.post(
        "/tests/",
        headers=auth_headers,
        json={
            "name": "Invalid Test",
            "price": "-10.00",
        },
    )
    assert response.status_code == 422


def test_list_tests_pagination(client, auth_headers):
    for i in range(4):
        client.post(
            "/tests/",
            headers=auth_headers,
            json={"name": f"Test {i}", "price": f"{(i+1)*100}.00"},
        )
    response = client.get("/tests/?page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 4


def test_get_test_not_found(client):
    response = client.get("/tests/99999")
    assert response.status_code == 404


def test_add_test_to_centre(client, auth_headers, test_centre, test_diagnostic):
    response = client.post(
        f"/centres/{test_centre.id}/tests",
        headers=auth_headers,
        json={
            "test_id": test_diagnostic.id,
            "custom_price": "420.00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["available_tests"]) == 1
    assert float(data["available_tests"][0]["price"]) == 420.00


def test_add_test_to_centre_duplicate(client, auth_headers, test_setup):
    centre_id = test_setup["centre"].id
    test_id = test_setup["test"].id
    response = client.post(
        f"/centres/{centre_id}/tests",
        headers=auth_headers,
        json={"test_id": test_id},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Test is already associated with this centre"


def test_remove_test_from_centre(client, auth_headers, test_setup):
    centre_id = test_setup["centre"].id
    test_id = test_setup["test"].id
    response = client.delete(
        f"/centres/{centre_id}/tests/{test_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    detail_res = client.get(f"/centres/{centre_id}")
    assert len(detail_res.json()["available_tests"]) == 0
