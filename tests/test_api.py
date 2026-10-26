def test_list_students(client):
    response = client.get("/students")

    assert response.status_code == 200
    assert response.json() == []


def test_create_student(client):
    response = client.post(
        "/students",
        json={
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rahul Sharma"
    assert data["email"] == "rahul@example.com"
    assert "id" in data


def test_get_student(client):
    created = client.post(
        "/students",
        json={
            "name": "Priya Sharma",
            "email": "priya@example.com",
        },
    )
    student_id = created.json()["id"]

    response = client.get(f"/students/{student_id}")

    assert response.status_code == 200
    assert response.json()["id"] == student_id


def test_update_student(client):
    created = client.post(
        "/students",
        json={
            "name": "Aman Kumar",
            "email": "aman@example.com",
        },
    )
    student_id = created.json()["id"]

    response = client.put(
        f"/students/{student_id}",
        json={
            "name": "Aman Singh",
            "email": "aman.singh@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Aman Singh"


def test_delete_student_as_normal_user(client):
    created = client.post(
        "/students",
        json={
            "name": "Neha Verma",
            "email": "neha@example.com",
        },
    )
    student_id = created.json()["id"]

    response = client.delete(f"/students/{student_id}")

    assert response.status_code == 403


def test_create_student_with_invalid_name(client):
    response = client.post(
        "/students",
        json={
            "name": "A",
            "email": "valid@example.com",
        },
    )

    assert response.status_code == 422


def test_get_missing_student(client):
    response = client.get("/students/999999")

    assert response.status_code == 404