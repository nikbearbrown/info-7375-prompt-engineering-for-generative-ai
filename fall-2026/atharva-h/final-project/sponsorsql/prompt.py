"""Builds the exact text sent to the model. The same text goes to every adapter."""

from .config import FIELDS, SOURCE_SHA256

SCHEMA = ", ".join(["sheet_row INTEGER"] + [f"{name} TEXT" for name in FIELDS])


def build(contract_text, question, output_shape="", feedback=""):
    parts = [
        contract_text.strip(),
        "",
        "## Table",
        f"lca({SCHEMA})",
        f"Source workbook SHA-256: {SOURCE_SHA256}",
        "",
        "## Question",
        question.strip(),
    ]
    if output_shape:
        parts += ["", "## Output shape for `sql`", output_shape.strip()]
    if feedback:
        parts += ["", "## Your previous reply was rejected", feedback.strip()]
    parts += ["", "Reply with only the JSON object, no other text."]
    return "\n".join(parts) + "\n"
