from unittest.mock import MagicMock, patch

from fastapi import Response
from fastapi.responses import FileResponse
from fastapi.testclient import TestClient

from chickenpi.auth.auth import FirebaseUser, verify_firebase_token


def override_verify() -> FirebaseUser:
    return FirebaseUser(uid="42", name="testuser")


@patch("chickenpi.auth.auth.init_auth")
@patch("chickenpi.door.door.open_door")
def test_chicken_door_up(mock_door: MagicMock, mock_auth: MagicMock):
    from chickenpi.chicken import app

    door_return_value = {"status": "OPENING"}
    mock_door.return_value = door_return_value
    app.dependency_overrides[verify_firebase_token] = override_verify
    client = TestClient(app)
    response: Response = client.post("/door?direction=up")
    assert response.status_code == 200
    assert response.json() == door_return_value


@patch("chickenpi.auth.auth.init_auth")
@patch("chickenpi.door.door.close_door")
def test_chicken_door_down(mock_door: MagicMock, mock_auth: MagicMock):
    from chickenpi.chicken import app

    door_return_value = {"status": "CLOSING"}
    mock_door.return_value = door_return_value
    app.dependency_overrides[verify_firebase_token] = override_verify
    client = TestClient(app)
    response: Response = client.post("/door?direction=down")
    assert response.status_code == 200
    assert response.json() == door_return_value


@patch("chickenpi.auth.auth.init_auth")
@patch("chickenpi.chicken.get_new_image")
def test_chicken_capture_image_none_returned(
    mock_capture: MagicMock, mock_auth: MagicMock
):
    from chickenpi.chicken import app

    mock_capture.return_value = ""
    app.dependency_overrides[verify_firebase_token] = override_verify
    client = TestClient(app)
    response: Response = client.post("/capture")
    assert response.status_code == 200
    assert response.json() == {"error": "No captures found"}


@patch("chickenpi.auth.auth.init_auth")
@patch("chickenpi.chicken.get_new_image")
def test_chicken_capture_image(mock_capture: MagicMock, mock_auth: MagicMock):
    from chickenpi.chicken import app

    mock_capture.return_value = "image"
    app.dependency_overrides[verify_firebase_token] = override_verify
    client = TestClient(app)
    response: Response = client.post("/capture")
    assert response.status_code == 200
    assert response.json() == {"status": "image captured", "filename": "image"}


@patch("chickenpi.auth.auth.init_auth")
@patch("chickenpi.chicken.get_latest_image")
def test_chicken_latest_image(mock_capture: MagicMock, mock_auth: MagicMock):
    from chickenpi.chicken import app

    image = "tests/data/2020/01/01/2025-08-26-00-05-00_capture.jpg"
    mock_capture.return_value = image
    app.dependency_overrides[verify_firebase_token] = override_verify
    client = TestClient(app)
    response: Response = client.get("/latest-image")
    assert response.status_code == 200
    assert list(response.content) == []
