from ytfetcher_gui.utils import extract_video_id


def test_extract_video_id_from_plain_id():
    assert extract_video_id("abc123DEF") == "abc123DEF"


def test_extract_video_id_from_watch_url():
    url = "https://www.youtube.com/watch?v=abcdEFG1234&t=10s"
    assert extract_video_id(url) == "abcdEFG1234"


def test_extract_video_id_from_youtu_short():
    url = "https://youtu.be/abcdEFG1234?si=xyz"
    assert extract_video_id(url) == "abcdEFG1234"


def test_extract_video_id_from_embed_url():
    url = "https://www.youtube.com/embed/abcdEFG1234?start=10"
    assert extract_video_id(url) == "abcdEFG1234"


def test_extract_video_id_invalid():
    assert extract_video_id("https://www.youtube.com/watch") is None

