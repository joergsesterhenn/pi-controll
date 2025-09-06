from unittest.mock import MagicMock, patch

from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
import pytest

from chickenpi.auth.auth import FirebaseUser, verify_firebase_token
from chickenpi.door.door_driver import Door, DoorState
from chickenpi.light.light_driver import Light, LightState


@pytest.fixture(scope="function")
def client():
    patch("chickenpi.auth.auth.init_auth")
    from chickenpi.chicken import app

    def override_verify() -> FirebaseUser:
        return FirebaseUser(uid="42", name="testuser")

    app.dependency_overrides[verify_firebase_token] = override_verify
    return TestClient(app)


@patch("chickenpi.chicken.open_door")
def test_chicken_door_up(mock_door: MagicMock, client):
    door_return_value = DoorState.OPENING
    mock_door.return_value = door_return_value
    response: JSONResponse = client.post("/door?direction=up")
    assert response.status_code == 200
    assert (
        str(response.content, encoding="UTF-8")
        == Door(status=DoorState.OPENING).model_dump_json()
    )


@patch("chickenpi.chicken.close_door")
def test_chicken_door_down(mock_door: MagicMock, client):
    door_return_value = DoorState.CLOSING
    mock_door.return_value = door_return_value
    response: Response = client.post("/door?direction=down")
    assert response.status_code == 200
    assert (
        str(response.content, encoding="UTF-8")
        == Door(status=DoorState.CLOSING).model_dump_json()
    )


@patch("chickenpi.chicken.get_new_image")
def test_chicken_capture_image_none_returned(mock_capture: MagicMock, client):
    mock_capture.return_value = ""
    response: Response = client.post("/image")
    assert response.status_code == 404
    assert response.json() == {"detail": "No image available"}


@patch("chickenpi.chicken.get_new_image")
def test_chicken_capture_image(mock_capture: MagicMock, client):
    mock_capture.return_value = "image"
    response: Response = client.post("/image")
    assert response.status_code == 200
    assert response.json() == {"status": "image captured", "filename": "image"}


@patch("chickenpi.chicken.get_latest_image")
def test_chicken_latest_image(mock_capture: MagicMock, client):
    image = "tests/data/2020/01/01/2025-08-26-00-05-00_capture.jpg"
    mock_capture.return_value = image
    response: Response = client.get("/image")
    assert response.status_code == 200
    assert list(response.content) == []


@patch("chickenpi.chicken.toggle")
def test_light_toggle(mock_light: MagicMock, client):
    mock_light.return_value = LightState.ON
    response: Response = client.post("/light")
    assert response.status_code == 200
    assert (
        str(response.content, encoding="UTF-8")
        == Light(status=LightState.ON).model_dump_json()
    )


@patch("chickenpi.chicken.state")
def test_light_state(mock_light: MagicMock, client):
    mock_light.return_value = LightState.OFF
    response: Response = client.get("/light/state")
    assert response.status_code == 200
    assert (
        str(response.content, encoding="UTF-8")
        == Light(status=LightState.OFF).model_dump_json()
    )
