import uuid
from pathlib import Path
from random import randint
import feedparser
import rssadd
from fnum import FnumMetadata, FnumMax
from imeta import ImageMetadata

from .exceptions import SyndicateException


__version__ = "0.1.0"


def add_image(image_url, from_source=None, to_source=None):
    title = Path(image_url).stem
    # This should always be treated as a new item even if an image id has been reused
    guid = str(uuid.uuid4())
    link = image_url
    description = " "

    return rssadd.add_item(
        from_source=from_source,
        to_source=to_source,
        tags=[
            f"<title>{title}</title>",
            f"<guid>{guid}</guid>",
            f"<link>{link}</link>",
            f"<description>{description}</description>",
        ],
        max_items=10,
    )


def _last_from_feed(feed):
    parsed_feed = feedparser.parse(feed)
    try:
        if parsed_feed.status < 200 or parsed_feed.status > 299:
            raise SyndicateException(
                f"HTTP status {parsed_feed.status} while requesting feed {feed}"
            )
    except AttributeError:
        pass

    items = parsed_feed["items"]
    if len(items) == 0:
        return None

    last_item = items[0]
    last_id = int(last_item["title"])
    return last_id


def _image_url_from_id(base_url, image_id, image_dir, suffix):
    if not suffix and not image_dir:
        raise SyndicateException("Unable to determine image suffix")
    if suffix:
        return f"{base_url}{image_id}{suffix}"

    metadata = FnumMetadata.from_file(image_dir)
    filename = next(name for name in metadata.order if name.startswith(f"{image_id}."))
    if not filename:
        raise SyndicateException("Unable to determine image suffix")
    return f"{base_url}{filename}"


def add_image_seq(
    base_url, from_source=None, to_source=None, image_dir=None, max_id=None, suffix=None
):
    last_id = _last_from_feed(from_source)

    image_id = 1 if last_id is None else last_id + 1

    if not max_id and image_dir:
        try:
            metadata = FnumMetadata.from_file(image_dir)
            max_id = metadata.max
        except FileNotFoundError:
            try:
                max_id = FnumMax.from_file(image_dir).value
            except FileNotFoundError:
                pass
    if max_id is not None and image_id >= max_id:
        return rssadd.add_element(
            from_source=from_source,
            to_source=to_source,
            max_items=10,
        )

    image_url = _image_url_from_id(base_url, image_id, image_dir, suffix)
    return schedule(image_url, from_source, to_source)


def add_image_random(
    base_url, from_source=None, to_source=None, image_dir=None, max_id=None, suffix=None
):
    last_id = _last_from_feed(from_source)

    image_id = randint(1, max_id)
    if image_id == last_id:
        image_id -= 1
    if image_id == 0:
        image_id = max_id

    image_url = _image_url_from_id(base_url, image_id, image_dir, suffix)
    return schedule(image_url, from_source, to_source)
