from unittest.mock import MagicMock, patch

from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
import pytest

from chickenpi.auth.auth import FirebaseUser, verify_firebase_token
from chickenpi.door.door_driver import DoorState
from chickenpi.light.light_driver import Light, LightState
from chickenpi.temperature.temperature import Temperature


@pytest.fixture(scope="function")
def client():
    patch("chickenpi.auth.auth.init_auth")
    from chickenpi.chicken import app

    def override_verify() -> FirebaseUser:
        return FirebaseUser(uid="42", name="testuser")

    app.dependency_overrides[verify_firebase_token] = override_verify
    return TestClient(app)


@patch("chickenpi.chicken.coop_door_state")
def test_door_state(mock_door: MagicMock, client):
    door_return_value = DoorState.OPENING
    mock_door.return_value = door_return_value
    response: JSONResponse = client.get("/door/state")
    assert response.status_code == 200
    assert response.json() == {"status": DoorState.OPENING}


@patch("chickenpi.chicken.open_door")
def test_chicken_door_up(mock_door: MagicMock, client):
    door_return_value = DoorState.OPENING
    mock_door.return_value = door_return_value
    response: JSONResponse = client.post("/door?direction=up")
    assert response.status_code == 200
    assert response.json() == {"status": DoorState.OPENING}


@patch("chickenpi.chicken.close_door")
def test_chicken_door_down(mock_door: MagicMock, client):
    door_return_value = DoorState.CLOSING
    mock_door.return_value = door_return_value
    response: Response = client.post("/door?direction=down")
    assert response.status_code == 200
    assert response.json() == {"status": DoorState.CLOSING}


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


@patch("chickenpi.chicken.get_readings")
def test_read_temperature(mock_temperature: MagicMock, client):
    mock_temperature.return_value = Temperature(inside=10, outside=10)
    response: Response = client.get("/temperature")
    assert response.status_code == 200
    assert (
        str(response.content, encoding="UTF-8")
        == Temperature(inside=10, outside=10).model_dump_json()
    )


@patch("chickenpi.chicken.coop_door_state")
@patch("chickenpi.chicken.reset_door_state")
@patch("chickenpi.chicken.open_door")
def test_door_error_and_reset(
    mock_open_door: MagicMock,
    mock_reset_door: MagicMock,
    mock_coop_door_state: MagicMock,
    client,
):
    # Simulate error state
    mock_coop_door_state.return_value = DoorState.ERROR
    mock_reset_door.return_value = DoorState.UNDEFINED  # Reset returns undefined

    # Try to open door when in error state - should fail
    response = client.post("/door?direction=up")
    assert response.status_code == 400
    assert response.json() == {"detail": "Door in error state, reset required"}
    mock_open_door.assert_not_called()

    # Reset the door
    response = client.post("/door/reset")
    assert response.status_code == 200
    assert response.json() == {"status": DoorState.UNDEFINED}
    mock_reset_door.assert_called_once()

    # After reset, open door should now work
    mock_coop_door_state.return_value = DoorState.CLOSED  # Simulate reset worked
    mock_open_door.return_value = DoorState.OPENING
    response = client.post("/door?direction=up")
    assert response.status_code == 200
    assert response.json() == {"status": DoorState.OPENING}
    mock_open_door.assert_called_once()


@patch("chickenpi.chicken.get_readings", side_effect=Exception("Sensor Read Error"))
def test_read_temperature_sensor_unresponsive(mock_temperature: MagicMock, client):
    response: Response = client.get("/temperature")
    assert response.status_code == 200
    assert response.json() == {"inside": None, "outside": None}
