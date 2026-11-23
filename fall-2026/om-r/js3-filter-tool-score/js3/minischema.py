"""A deliberately small JSON Schema checker (stdlib only) for the subset the
MCP tool server declares: type (incl. lists and "null"), enum, required,
properties, additionalProperties: false, items, minLength, oneOf.

Anything outside that subset raises, so a schema can't silently claim more
than this checker enforces. Returns a list of error strings ([] = valid).
"""
SUPPORTED = {"type", "enum", "required", "properties", "additionalProperties", "items",
             "minLength", "oneOf", "description", "title"}
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _is_type(v, t):
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _TYPES[t])


def errors(value, schema, path="$"):
    unknown = set(schema) - SUPPORTED
    if unknown:
        raise ValueError(f"schema keyword(s) not supported by minischema at {path}: {sorted(unknown)}")
    errs = []
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, t) for t in types):
            return [f"{path}: expected {types}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        errs.append(f"{path}: shorter than {schema['minLength']}")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing required {k!r}")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                errs += errors(v, props[k], f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: unexpected key {k!r}")
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            errs += errors(v, schema["items"], f"{path}[{i}]")
    if "oneOf" in schema:
        n = sum(1 for s in schema["oneOf"] if not errors(value, s, path))
        if n != 1:
            errs.append(f"{path}: must match exactly one of oneOf, matched {n}")
    return errs
