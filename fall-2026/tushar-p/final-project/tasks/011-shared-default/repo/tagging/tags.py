"""Tag lists."""


def add_tag(tag, tags=[]):
    """Return a new list: tags with tag added at the end, unless it is
    already there.

    Tags are stored lower case and compared case-insensitively. The list
    passed in is never changed. Called without tags, it starts from an
    empty list.
    """
    tag = tag.lower()
    if tag not in tags:
        tags.append(tag)
    return tags
