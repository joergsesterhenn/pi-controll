from unittest.mock import MagicMock, patch
from chickenpi.images import get_latest_image, get_new_image


def test_get_latest_image(tmp_path):
    assert get_latest_image(tmp_path) == {"error": "No captures found"}


@patch("chickenpi.images.os.makedirs")
@patch("chickenpi.images.subprocess.run")
@patch("chickenpi.images.datetime")
def test_get_new_image(
    mock_datetime,
    mock_run,
    mock_makedirs,
    tmp_path,
):
    fake_now = MagicMock()

    def fake_strftime(fmt):
        if fmt == "%Y/%m/%d":
            return "2025/08/26"
        if fmt == "%Y-%m-%d-%H-%M-%S":
            return "2025-08-26-00-05-00"
        raise ValueError(f"Unexpected format: {fmt}")

    fake_now.strftime.side_effect = fake_strftime
    mock_datetime.now.return_value = fake_now
    base_dir = tmp_path / "captures"

    result = get_new_image(directory=str(base_dir))

    expected_folder = f"{base_dir}/2025/08/26"
    expected_filename = f"{expected_folder}/2025-08-26-00-05-00_capture.jpg"
    mock_makedirs.assert_called_once_with(expected_folder, exist_ok=True)
    mock_run.assert_called_once_with(["fswebcam", "-r", "1280x960", expected_filename])
    assert result == expected_filename
