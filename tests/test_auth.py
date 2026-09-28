def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "securepassword",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["full_name"] == "New User"
    assert data["token"]["token_type"] == "bearer"
    assert len(data["token"]["access_token"]) > 0


def test_signup_duplicate_email(client, test_user):
    response = client.post(
        "/auth/signup",
        json={
            "email": test_user.email,
            "password": "anotherpassword",
            "full_name": "Duplicate User",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_signup_invalid_email(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "not-an-email",
            "password": "validpassword",
            "full_name": "Invalid Email",
        },
    )
    assert response.status_code == 422


def test_signup_short_password(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "shortpw@example.com",
            "password": "123",
            "full_name": "Short Password",
        },
    )
    assert response.status_code == 422


def test_login_success(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "somepassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_get_me_success(client, auth_headers, test_user):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_me_unauthorized_missing_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.payload"},
    )
    assert response.status_code == 401
