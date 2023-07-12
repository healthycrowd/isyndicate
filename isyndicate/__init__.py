import uuid
from pathlib import Path
from random import randint
import feedparser
import rssadd
from fnum import FnumMetadata

from .exceptions import ScheduleException


__version__ = "0.1.0"


def schedule(image_url, feed=None):
    title = Path(image_url).stem
    # This should always be treated as a new item even if an image id has been reused
    guid = str(uuid.uuid4())
    link = image_url
    description = " "

    return rssadd.add_item(
        from_source=feed,
        tags=[
            f"<title>{title}</title>",
            f"<guid>{guid}</guid>",
            f"<link>{link}</link>",
            f"<description>{description}</description>",
        ],
    )


def _last_from_feed(feed):
    parsed_feed = feedparser.parse(feed)
    try:
        if parsed_feed.status < 200 or parsed_feed.status > 299:
            raise ScheduleException(
                f"HTTP status {parsed_feed.status} while requesting feed {feed}"
            )
    except AttributeError:
        pass

    last_item = parsed_feed["items"][0]
    last_id = int(last_item["title"])
    prefix = str(Path(last_item["link"]).parents[0]) + "/"
    return (last_id, prefix)


def _image_url_from_id(prefix, image_id, suffix=None):
    if not suffix:
        # read imeta file then fnum metadata
        raise ScheduleException("Unable to determine image suffix")

    return f"{prefix}{image_id}{suffix}"


def schedule_seq(feed, suffix=None):
    (last_id, prefix) = _last_from_feed(feed)

    image_id = last_id + 1

    image_url = _image_url_from_id(prefix, image_id, suffix)
    return schedule(image_url, feed)


def schedule_random(feed, max_id, suffix=None):
    (last_id, prefix) = _last_from_feed(feed)

    image_id = randint(1, max_id)
    if image_id == last_id:
        image_id -= 1
    if image_id == 0:
        image_id = max_id

    image_url = _image_url_from_id(prefix, image_id, suffix)
    return schedule(image_url, feed)
