from tempfile import TemporaryDirectory
from pathlib import Path
import pytest
import feedparser
from imeta import ImageMetadata
from fnum import FnumMetadata, FnumMax

from isyndicate import add_image, add_image_random, add_image_seq, TagSettings
from isyndicate.exceptions import SyndicateException


BASE_URL = "https://invalid/"


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
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    topath = Path(tempdir.name) / "to"
    frompath.write_bytes(add_image("/1.jpg"))
    add_image_seq(
        BASE_URL, from_source=str(frompath), to_source=str(topath), suffix=".jpg"
    )
    items = feedparser.parse(topath.read_text())["items"]
    assert len(items) == 2, items
    assert items[1]["link"] == "/1.jpg"
    item = items[0]
    assert item["title"] == "2"
    assert item["guid"]
    assert item["link"] == f"{BASE_URL}2.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_seq_success_image_dir():
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    topath = Path(tempdir.name) / "to"
    frompath.write_bytes(add_image("/1.jpg"))
    (Path(tempdir.name) / "2.jpg").write_text("")
    metadata = ImageMetadata(
        {
            "$version": "1.0",
            "tags": [],
        }
    )
    metadata.to_image(str(Path(tempdir.name) / "2.jpg"))
    metadata = FnumMetadata({})
    metadata.order = ["1.jpg", "2.jpg"]
    metadata.to_file(tempdir.name)
    add_image_seq(
        BASE_URL,
        from_source=str(frompath),
        to_source=str(topath),
        image_dir=tempdir.name,
    )
    items = feedparser.parse(topath.read_text())["items"]
    assert len(items) == 2, items
    assert items[1]["link"] == "/1.jpg"
    item = items[0]
    assert item["title"] == "2"
    assert item["guid"]
    assert item["link"] == f"{BASE_URL}2.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_seq_success_suffix_and_dir():
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    topath = Path(tempdir.name) / "to"
    frompath.write_bytes(add_image("/1.jpg"))
    (Path(tempdir.name) / "2.png").write_text("")
    metadata = ImageMetadata(
        {
            "$version": "1.0",
            "tags": [],
        }
    )
    metadata.to_image(str(Path(tempdir.name) / "2.png"))
    metadata = FnumMetadata({})
    metadata.order = ["1.jpg", "2.jpg"]
    metadata.to_file(tempdir.name)
    add_image_seq(
        BASE_URL,
        from_source=str(frompath),
        to_source=str(topath),
        image_dir=tempdir.name,
        suffix=".png",
    )
    items = feedparser.parse(topath.read_text())["items"]
    assert len(items) == 2, items
    assert items[1]["link"] == "/1.jpg"
    item = items[0]
    assert item["title"] == "2"
    assert item["guid"]
    assert item["link"] == f"{BASE_URL}2.png"
    assert item["published"]
    assert item["description"] == ""


def test_add_seq_success_new_feed():
    feed = add_image_seq(BASE_URL, suffix=".jpg")
    items = feedparser.parse(feed)["items"]
    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "1"
    assert item["guid"]
    assert item["link"] == f"{BASE_URL}1.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_seq_success_over_max_explicit_no_write():
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    topath = Path(tempdir.name) / "to"
    frompath.write_bytes(add_image("/5.jpg"))
    add_image_seq(
        BASE_URL,
        from_source=str(frompath),
        to_source=str(topath),
        suffix=".jpg",
        max_id=5,
    )
    assert not topath.exists()


def test_add_seq_success_over_max_explicit_to_string():
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    frompath.write_bytes(add_image("/5.jpg"))
    feed = add_image_seq(BASE_URL, from_source=str(frompath), suffix=".jpg", max_id=5)
    items = feedparser.parse(feed)["items"]

    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "5"
    assert item["guid"]
    assert item["link"] == "/5.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_seq_success_over_max_fnum_meta():
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    frompath.write_bytes(add_image("/5.jpg"))
    metadata = FnumMetadata({})
    metadata.max = 5
    metadata.to_file(tempdir.name)
    feed = add_image_seq(
        BASE_URL, from_source=str(frompath), suffix=".jpg", image_dir=tempdir.name
    )
    items = feedparser.parse(feed)["items"]

    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "5"
    assert item["guid"]
    assert item["link"] == "/5.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_seq_success_over_max_fnum_max():
    tempdir = TemporaryDirectory()
    frompath = Path(tempdir.name) / "from"
    frompath.write_bytes(add_image("/5.jpg"))
    metadata = FnumMax(5)
    metadata.to_file(tempdir.name)
    feed = add_image_seq(
        BASE_URL, from_source=str(frompath), suffix=".jpg", image_dir=tempdir.name
    )
    items = feedparser.parse(feed)["items"]

    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "5"
    assert item["guid"]
    assert item["link"] == "/5.jpg"
    assert item["published"]
    assert item["description"] == ""


def test_add_seq_success_tag_settings():
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

    feed = add_image_seq(
        BASE_URL,
        suffix=".jpg",
        tag_settings=TagSettings(tag_limit=10),
        image_dir=tempdir.name,
    )
    items = feedparser.parse(feed)["items"]
    assert len(items) == 1, items
    item = items[0]
    assert item["title"] == "1"
    assert item["guid"]
    assert item["link"] == f"{BASE_URL}1.jpg"
    assert item["published"]
    assert item["description"] == " ".join(f"#test{n}" for n in range(10))


def test_add_seq_fail_no_suffix():
    with pytest.raises(SyndicateException):
        add_image_seq(BASE_URL)


def test_add_random_success_with_max():
    pass


def test_add_random_success_with_dir():
    pass


def test_add_random_success_max_and_dir():
    pass


def test_add_random_fail_no_suffix():
    pass


def test_add_random_fail_no_max():
    pass


def test_add_random_success_new_feed():
    pass


def test_add_random_success_max_one():
    pass


def test_add_random_success_tag_settings():
    pass
