from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]
    assert body["Chess Club"]["max_participants"] == 12


def test_signup_adds_participant(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }


def test_signup_rejects_unknown_activity(client):
    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_requires_email(client):
    # Act
    response = client.post("/activities/Chess Club/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }


def test_unregister_rejects_unknown_activity(client):
    # Act
    response = client.delete(
        "/activities/Unknown Club/participants/student@mergington.edu"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unknown_participant(client):
    # Act
    response = client.delete(
        "/activities/Chess Club/participants/student@mergington.edu"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Student is not signed up for this activity"
    )


def test_participant_can_signup_again_after_unregister(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    unregister_response = client.delete(
        f"/activities/Chess Club/participants/{email}"
    )
    signup_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert unregister_response.status_code == 200
    assert signup_response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_full_activity_currently_accepts_another_participant(client):
    # Arrange
    activity = activities["Art Club"]
    activity["participants"] = [
        f"student-{index}@mergington.edu"
        for index in range(activity["max_participants"])
    ]
    email = "extra.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Art Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activity["participants"]
