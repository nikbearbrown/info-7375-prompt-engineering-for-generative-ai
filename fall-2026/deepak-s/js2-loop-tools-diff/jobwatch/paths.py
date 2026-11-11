"""JSON Pointer (RFC 6901) building and resolution for citations."""
import re

_INDEX = re.compile(r"0|[1-9][0-9]*")


class Unresolved(Exception):
    """The pointer names nothing in the document."""


def pointer(*parts):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def resolve(doc, path):
    if not isinstance(path, str) or (path and not path.startswith("/")):
        raise Unresolved(path)
    node = doc
    for raw in path.split("/")[1:]:
        part = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if part not in node:
                raise Unresolved(path)
            node = node[part]
        elif isinstance(node, list):
            if not _INDEX.fullmatch(part) or int(part) >= len(node):
                raise Unresolved(path)
            node = node[int(part)]
        else:
            raise Unresolved(path)
    return node
