from tempfile import TemporaryDirectory
from pathlib import Path
import feedparser
from imeta import ImageMetadata

from isyndicate import add_image, add_image_random, add_image_seq, TagSettings


def test_add_url_success_minimal():
    feed = add_image("/1.jpg")
    items = feedparser.parse(feed)["items"]
    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "1"
    assert item["guid"]
    assert item["link"] == "/1.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_url_success_existing():
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    topath = Path(tempdir.name) / "to"
    frompath.write_bytes(add_image("/0.jpg"))
    add_image("/1.jpg", from_source=str(frompath), to_source=str(topath))
    items = feedparser.parse(topath.read_text())["items"]
    assert len(items) == 2, items
    assert items[1]["link"] == "/0.jpg"
    item = items[0]
    assert item["title"] == "1"
    assert item["guid"]
    assert item["link"] == "/1.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_url_success_with_tags_no_limit():
    tempdir = TemporaryDirectory()
    (Path(tempdir.name) / "1.jpg").write_text("")
    metadata = ImageMetadata(
        {
            "$version": "1.0",
            "tags": [f"test{n}" for n in range(50)]
            + ["meta:tagged", "source:pinterest"],
        }
    )
    metadata.to_image(str(Path(tempdir.name) / "1.jpg"))

    feed = add_image("/1.jpg", image_dir=tempdir.name)
    items = feedparser.parse(feed)["items"]
    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "1"
    assert item["guid"]
    assert item["link"] == "/1.jpg"
    assert item["published"]
    assert item["description"] == " ".join(f"#test{n}" for n in range(50))


def test_add_url_success_with_tags_preset_limit():
    tempdir = TemporaryDirectory()
    (Path(tempdir.name) / "1.jpg").write_text("")
    metadata = ImageMetadata(
        {
            "$version": "1.0",
            "tags": [f"test{n}" for n in range(50)]
            + ["meta:tagged", "source:pinterest"],
        }
    )
    metadata.to_image(str(Path(tempdir.name) / "1.jpg"))

    feed = add_image(
        "/1.jpg", image_dir=tempdir.name, tag_settings=TagSettings.INSTAGRAM
    )
    items = feedparser.parse(feed)["items"]
    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "1"
    assert item["guid"]
    assert item["link"] == "/1.jpg"
    assert item["published"]
    assert item["description"] == " ".join(f"#test{n}" for n in range(30))


def test_add_url_success_with_tags_custom_limit():
    tempdir = TemporaryDirectory()
    (Path(tempdir.name) / "1.jpg").write_text("")
    metadata = ImageMetadata(
        {
            "$version": "1.0",
            "tags": [f"test{n}" for n in range(50)]
            + ["meta:tagged", "source:pinterest"],
        }
    )
    metadata.to_image(str(Path(tempdir.name) / "1.jpg"))

    feed = add_image(
        "/1.jpg", image_dir=tempdir.name, tag_settings=TagSettings(tag_limit=10)
    )
    items = feedparser.parse(feed)["items"]
    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "1"
    assert item["guid"]
    assert item["link"] == "/1.jpg"
    assert item["published"]
    assert item["description"] == " ".join(f"#test{n}" for n in range(10))


def test_add_seq_success_suffix():
    pass


def test_add_seq_success_image_dir():
    pass


def test_add_seq_success_suffix_and_dir():
    pass


def test_add_seq_fail_no_suffix():
    pass


def test_add_seq_success_new_feed():
    pass


def test_add_seq_success_over_max_explicit():
    pass


def test_add_seq_success_over_max_fnum():
    pass


def test_add_seq_success_tag_settings():
    pass


def test_add_random_success_with_max():
    pass


def test_add_random_success_with_dir():
    pass


def test_add_random_success_max_and_dir():
    pass


def test_add_seq_fail_no_suffix():
    pass


def test_add_random_fail_no_max():
    pass


def test_add_random_success_new_feed():
    pass


def test_add_random_success_max_one():
    pass


def test_add_random_success_tag_settings():
    pass
