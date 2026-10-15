"""Writes the SYNTHETIC test set: incidents.json, evidence.json, labels.json.

Every lot, part, number and date below is invented for testing. None of it
comes from a real factory, supplier or person.

labels.json holds the outcome a careful quality engineer *should* reach.
The labels were written by the same author as the rules, so agreement
between them is weak evidence; the two cases marked known_limitation are
where the rules are expected to get it wrong.

Run: python data/build_synthetic.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
OPENED = "2026-09-01T08:00:00"
COLLECTED = "2026-09-01T13:00:00"
DECIDED = "2026-09-02T09:00:00"

INSPECTION_SPEC = {"defects_found": {"max": 0}, "bore_mean_mm": {"min": 11.95, "max": 12.05}}

evidence, incidents, labels = [], [], {}


def ev(eid, kind, lot, fields, spec=None, at=COLLECTED):
    record = {"id": eid, "kind": kind, "lot": lot, "collected_at": at, "fields": fields}
    if spec:
        record["spec"] = spec
    evidence.append(record)


def claim(cid, text, eid, field, value):
    return {"id": cid, "text": text, "evidence_id": eid, "field": field, "op": "eq", "value": value}


def inc(iid, severity, lot, description, action, claims, expected, why,
        known_limitation=False, opened=OPENED, decided=DECIDED):
    incidents.append({
        "id": iid, "severity": severity, "lot": lot, "opened_at": opened,
        "description": description,
        "proposed_action": {"type": action, "decided_at": decided, "claims": claims},
    })
    labels[iid] = {"expected": expected, "why": why, "known_limitation": known_limitation}


def good_inspection(eid, lot, **overrides):
    fields = {"sample_size": 50, "defects_found": 0, "bore_mean_mm": 12.01}
    fields.update(overrides)
    ev(eid, "inspection", lot, fields, INSPECTION_SPEC)


A, N, H = "ACCEPT FOR REVIEW", "NEEDS MORE EVIDENCE", "HUMAN REVIEW REQUIRED"

# INC-001: clean release.
good_inspection("E-001", "L-1001")
ev("E-002", "containment", "L-1001", {"units_quarantined": 800, "units_in_lot": 800})
inc("INC-001", "major", "L-1001", "Burr on bore edge of housing, lot of 800.", "release_lot",
    [claim("C1", "Inspection of 50 samples found 0 defects", "E-001", "defects_found", 0),
     claim("C2", "All 800 units were quarantined", "E-002", "units_quarantined", 800)],
    A, "Required evidence cited, values match, within spec, timing valid.")

# INC-002: cites containment record that does not exist.
good_inspection("E-003", "L-1002")
inc("INC-002", "major", "L-1002", "Scratch on mating face, lot of 500.", "release_lot",
    [claim("C1", "Inspection found 0 defects", "E-003", "defects_found", 0),
     claim("C2", "All units contained", "E-999", "units_quarantined", 500)],
    N, "Containment record E-999 is missing.")

# INC-003: claim contradicts the record.
ev("E-004", "inspection", "L-1003", {"sample_size": 50, "defects_found": 3, "bore_mean_mm": 12.00}, INSPECTION_SPEC)
inc("INC-003", "minor", "L-1003", "Cosmetic flash on bracket.", "rework_lot",
    [claim("C1", "Inspection found no defects", "E-004", "defects_found", 0)],
    H, "Claim says 0 defects; record says 3.")

# INC-004: release with no containment evidence.
good_inspection("E-005", "L-1004")
inc("INC-004", "major", "L-1004", "Wrong torque on fastener, lot of 300.", "release_lot",
    [claim("C1", "Inspection found 0 defects", "E-005", "defects_found", 0)],
    N, "Release requires containment evidence.")

# INC-005: values quoted correctly but out of spec.
good_inspection("E-006", "L-1005", bore_mean_mm=12.08)
ev("E-007", "containment", "L-1005", {"units_quarantined": 600, "units_in_lot": 600})
inc("INC-005", "major", "L-1005", "Bore diameter drift, lot of 600.", "release_lot",
    [claim("C1", "Bore mean measured at 12.08 mm", "E-006", "bore_mean_mm", 12.08),
     claim("C2", "All 600 units quarantined", "E-007", "units_quarantined", 600)],
    H, "Bore mean 12.08 is above the 12.05 limit.")

# INC-006: everything checks out, but severity is critical.
good_inspection("E-008", "L-1006")
ev("E-009", "containment", "L-1006", {"units_quarantined": 200, "units_in_lot": 200})
inc("INC-006", "critical", "L-1006", "Crack found on load-bearing bracket, lot of 200.", "release_lot",
    [claim("C1", "Inspection found 0 defects", "E-008", "defects_found", 0),
     claim("C2", "All 200 units quarantined", "E-009", "units_quarantined", 200)],
    H, "Critical incidents are never released without a named human decision.")

# INC-007: inspection predates the incident.
ev("E-010", "inspection", "L-1007", {"sample_size": 50, "defects_found": 0, "bore_mean_mm": 12.00},
   INSPECTION_SPEC, at="2026-08-28T10:00:00")
ev("E-011", "containment", "L-1007", {"units_quarantined": 400, "units_in_lot": 400})
inc("INC-007", "major", "L-1007", "Porosity in casting, lot of 400.", "release_lot",
    [claim("C1", "Inspection found 0 defects", "E-010", "defects_found", 0),
     claim("C2", "All 400 units quarantined", "E-011", "units_quarantined", 400)],
    N, "Inspection is from before the incident; it cannot show the problem is gone.")

# INC-008: evidence is for a different lot.
good_inspection("E-012", "L-2002")
ev("E-013", "containment", "L-1008", {"units_quarantined": 350, "units_in_lot": 350})
inc("INC-008", "major", "L-1008", "Thread damage, lot of 350.", "release_lot",
    [claim("C1", "Inspection found 0 defects", "E-012", "defects_found", 0),
     claim("C2", "All 350 units quarantined", "E-013", "units_quarantined", 350)],
    H, "Inspection record belongs to lot L-2002.")

# INC-009: clean close.
ev("E-014", "root_cause", "L-1009", {"cause_code": "FIXTURE-WEAR"})
ev("E-015", "verification", "L-1009", {"post_fix_sample": 30, "defects_found": 0}, {"defects_found": {"max": 0}})
inc("INC-009", "major", "L-1009", "Recurring burr traced to fixture.", "close_incident",
    [claim("C1", "Root cause is fixture wear", "E-014", "cause_code", "FIXTURE-WEAR"),
     claim("C2", "30 parts after fixture change, 0 defects", "E-015", "defects_found", 0)],
    A, "Root cause and verification cited and consistent.")

# INC-010: scrapping a bad lot (spec gate does not apply to scrap).
ev("E-016", "inspection", "L-1010", {"sample_size": 50, "defects_found": 12, "bore_mean_mm": 12.20}, INSPECTION_SPEC)
inc("INC-010", "major", "L-1010", "Gross oversize bore, lot of 150.", "scrap_lot",
    [claim("C1", "12 of 50 samples defective", "E-016", "defects_found", 12)],
    A, "Out-of-spec evidence supports scrapping.")

# INC-011: two failures with different outcomes; both must be recorded.
ev("E-017", "root_cause", "L-1011", {"cause_code": "TOOL-OFFSET"})
inc("INC-011", "major", "L-1011", "Hole position shift.", "close_incident",
    [claim("C1", "Root cause was operator error", "E-017", "cause_code", "OPERATOR")],
    H, "Claimed cause contradicts record, and no verification is cited.")

# INC-012: malformed input (unknown action type).
inc("INC-012", "major", "L-1012", "Paint run.", "ship_anyway",
    [claim("C1", "Looks fine", "E-001", "defects_found", 0)],
    H, "Unrecognised action; cannot be checked, so escalate.")

# INC-013: evidence dated after the decision it supposedly supported.
good_inspection("E-018", "L-1013")
ev("E-019", "containment", "L-1013", {"units_quarantined": 250, "units_in_lot": 250}, at="2026-09-03T15:00:00")
inc("INC-013", "major", "L-1013", "Missing chamfer, lot of 250.", "release_lot",
    [claim("C1", "Inspection found 0 defects", "E-018", "defects_found", 0),
     claim("C2", "All 250 units quarantined", "E-019", "units_quarantined", 250)],
    H, "Containment record was created after the release decision.")

# INC-014: claim names a field the record does not have.
good_inspection("E-020", "L-1014")
inc("INC-014", "minor", "L-1014", "Surface hardness concern.", "rework_lot",
    [claim("C1", "Hardness was 45 HRC", "E-020", "hardness_hrc", 45)],
    N, "Inspection record has no hardness measurement.")

# INC-015: no evidence cited at all.
inc("INC-015", "minor", "L-1015", "Label misprint.", "rework_lot", [],
    N, "Nothing cited.")

# INC-016 (known limitation): the number is quoted correctly, the sentence misleads.
good_inspection("E-021", "L-1016")
ev("E-022", "containment", "L-1016", {"units_quarantined": 400})
inc("INC-016", "major", "L-1016", "Weld spatter on brackets, lot of 1,200.", "release_lot",
    [claim("C1", "Inspection found 0 defects", "E-021", "defects_found", 0),
     claim("C2", "All suspect units are contained", "E-022", "units_quarantined", 400)],
    H, "Only 400 of 1,200 units are contained; the lot size is only in free text, "
       "so no rule compares them.", known_limitation=True)

# INC-017 (known limitation): defects found, but the record carries no spec for defects.
ev("E-023", "inspection", "L-1017", {"sample_size": 50, "defects_found": 2, "bore_mean_mm": 12.00},
   {"bore_mean_mm": {"min": 11.95, "max": 12.05}})
ev("E-024", "containment", "L-1017", {"units_quarantined": 700, "units_in_lot": 700})
inc("INC-017", "major", "L-1017", "Edge crack on stamping, lot of 700.", "release_lot",
    [claim("C1", "Inspection of 50 samples passed", "E-023", "sample_size", 50),
     claim("C2", "All 700 units quarantined", "E-024", "units_quarantined", 700)],
    H, "Inspection found 2 defects; the claim cites only sample size and the record "
       "has no defect limit, so no rule fires.", known_limitation=True)


def write(name, obj):
    with open(HERE / name, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    write("incidents.json", incidents)
    write("evidence.json", evidence)
    write("labels.json", labels)
    print(f"wrote {len(incidents)} incidents, {len(evidence)} evidence records")
