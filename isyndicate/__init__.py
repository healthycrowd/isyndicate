import uuid
from pathlib import Path
from random import randint
import feedparser
import rssadd
from rssadd.source_type import SourceType
from fnum import FnumMetadata, FnumMax
from imeta import ImageMetadata
import sociallimits

from .exceptions import SyndicateException


__version__ = "1.0.0"


class TagSettings:
    def __init__(self, caption_limit=None, tag_limit=None, tag_element=None):
        self.caption_limit = caption_limit
        self.tag_limit = tag_limit
        self.tag_element = tag_element


for name, platform in sociallimits.all_platforms.items():
    settings = TagSettings(platform.caption_limit, platform.tag_limit)
    if name == "TUMBLR":
        settings.tag_element = "title"
    setattr(TagSettings, name, settings)


def add_image(
    image_url,
    from_source=None,
    to_source=None,
    image_dir=None,
    tag_settings=None,
):
    title = Path(image_url).stem
    # This should always be treated as a new item even if an image id has been reused
    guid = str(uuid.uuid4())
    link = image_url
    description = " "

    tagstr = ""
    if image_dir:
        metadata = ImageMetadata.from_image(str(Path(image_dir) / Path(image_url).name))
        tags = (tag for tag in metadata.tags if ":" not in tag)
        for n, tag in enumerate(tags):
            addedtag = tagstr + ("" if n == 0 else " ")
            addedtag += f"#{tag}"
            if (
                tag_settings
                and tag_settings.caption_limit is not None
                and len(addedtag) > tag_settings.caption_limit
            ):
                break
            tagstr = addedtag
            if (
                tag_settings
                and tag_settings.tag_limit is not None
                and n + 1 >= tag_settings.tag_limit
            ):
                break
    if tagstr == "":
        tagstr = " "

    addedtag = None
    tag_element = tag_settings.tag_element if tag_settings else None
    if tag_element is None:
        tag_element = "description"
    if tag_element in ("guid", "link"):
        raise SyndicateException(f"Tags cannot be in {tag_element} element")
    if tag_element == "title":
        title = tagstr
    elif tag_element == "description":
        description = tagstr
    else:
        addedtag = f"<{tag_element}>{tagstr}</{tag_element}>"

    tags = [
        f"<title>{title}</title>",
        f"<guid>{guid}</guid>",
        f"<link>{link}</link>",
        f"<description>{description}</description>",
    ]
    if addedtag:
        tags.append(addedtag)

    return rssadd.add_item(
        from_source=from_source,
        to_source=to_source,
        tags=tags,
        max_items=10,
    )


def _last_from_feed(feed):
    if feed is None:
        return None
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
    try:
        filename = next(
            name for name in metadata.order if name.startswith(f"{image_id}.")
        )
    except StopIteration:
        raise SyndicateException("Unable to determine image suffix")
    return f"{base_url}{filename}"


def _find_max(max_id, image_dir):
    if max_id is not None:
        return max_id
    if image_dir is None:
        return None
    try:
        metadata = FnumMetadata.from_file(image_dir)
        max_id = metadata.max
    except FileNotFoundError:
        try:
            max_id = FnumMax.from_file(image_dir).value
        except FileNotFoundError:
            pass
    return max_id


def add_image_seq(
    base_url,
    from_source=None,
    to_source=None,
    image_dir=None,
    suffix=None,
    max_id=None,
    tag_settings=None,
):
    last_id = _last_from_feed(from_source)

    image_id = 1 if last_id is None else last_id + 1

    max_id = _find_max(max_id, image_dir)
    if max_id is not None and image_id >= max_id:
        # Do nothing if we can
        if SourceType.to_source(to_source) == SourceType.FILE:
            return
        # Avoid adding to the feed
        return rssadd.add_element(
            from_source=from_source,
            to_source=to_source,
            max_items=10,
        )

    image_url = _image_url_from_id(base_url, image_id, image_dir, suffix)
    return add_image(
        image_url,
        from_source,
        to_source,
        image_dir,
        tag_settings,
    )


def add_image_random(
    base_url,
    from_source=None,
    to_source=None,
    image_dir=None,
    suffix=None,
    max_id=None,
    tag_settings=None,
):
    max_id = _find_max(max_id, image_dir)
    if max_id is None:
        raise SyndicateException("Unable to determine max_id for random selection")

    last_id = _last_from_feed(from_source)

    image_id = randint(1, max_id)
    if image_id == last_id:
        image_id -= 1
    if image_id == 0:
        image_id = max_id

    image_url = _image_url_from_id(base_url, image_id, image_dir, suffix)
    return add_image(
        image_url,
        from_source,
        to_source,
        image_dir,
        tag_settings,
    )
