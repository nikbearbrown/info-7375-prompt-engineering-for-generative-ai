"""Separate authorization flag (CONTRACT.md, Out). Never changes the relevance verdict."""

E_VERIFY_UNKNOWN = "unknown"


def authorization_flag(resume):
    # Keyed on visa.type only: free text such as "work authorized" in current_status
    # is deliberately ignored, because F-1 STEM OPT still needs future sponsorship.
    if resume["visa"]["type"].strip().upper() == "F-1":
        return "NEEDS_SPONSORSHIP"
    return "UNKNOWN"
