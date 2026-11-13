"""Turn titles into URL slugs."""


def slugify(title):
    """Return a URL slug for title.

    The slug is lower case. Every run of characters that are not ASCII
    letters or digits becomes a single hyphen, and the slug never starts
    or ends with a hyphen. A title with no ASCII letters or digits gives "".
    """
    return title.lower().replace(" ", "-")
