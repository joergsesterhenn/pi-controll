from unittest.mock import MagicMock, patch
from chickenpi.image.image import get_latest_image, get_new_image


def test_get_latest_image_none_found(tmp_path):
    assert get_latest_image(tmp_path) == ""


def test_get_latest_image():
    assert (
        get_latest_image("tests/data/")
        == "tests/data/2020/01/01/2025-08-26-00-05-00_capture.jpg"
    )


@patch("chickenpi.image.image.os.makedirs")
@patch("chickenpi.image.image.subprocess.run")
@patch("chickenpi.image.image.datetime")
def test_get_new_image(
    mock_datetime: MagicMock,
    mock_run: MagicMock,
    mock_makedirs: MagicMock,
    tmp_path,
):
    fake_now = MagicMock()

    def fake_strftime(fmt):
        if fmt == "%Y/%m/%d":
            return "2025/08/26"
        if fmt == "%Y-%m-%d-%H-%M-%S":
            return "2025-08-26-00-05-00"

    fake_now.strftime.side_effect = fake_strftime
    mock_datetime.now.return_value = fake_now
    base_dir = tmp_path / "captures"
    result = get_new_image(directory=str(base_dir))
    expected_folder = f"{base_dir}/2025/08/26"
    expected_filename = f"{expected_folder}/2025-08-26-00-05-00_capture.jpg"
    mock_makedirs.assert_called_once_with(expected_folder, exist_ok=True)
    mock_run.assert_called_once_with(["fswebcam", "-r", "1280x960", expected_filename])
    assert result == expected_filename
