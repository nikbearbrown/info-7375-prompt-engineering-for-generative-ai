"""Fixed facts about the source file and the agent's budgets."""

from dataclasses import dataclass

SOURCE_FILE = "LCA_Disclosure_Data_FY2026_Q3.xlsx"
SOURCE_URL = "https://www.dol.gov//media/LCA_Disclosure_Data_FY2026_Q3.xlsx"
SOURCE_SHA256 = "f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3"
SOURCE_BYTES = 251850891
EXPECTED_ROWS = 437496

# The 18 public fields kept. Contact, attorney, preparer, address, phone and
# email columns are never loaded.
FIELDS = (
    "CASE_NUMBER", "CASE_STATUS", "DECISION_DATE", "VISA_CLASS", "JOB_TITLE",
    "SOC_CODE", "SOC_TITLE", "TOTAL_WORKER_POSITIONS", "EMPLOYER_NAME",
    "TRADE_NAME_DBA", "EMPLOYER_FEIN", "WORKSITE_CITY", "WORKSITE_STATE",
    "WAGE_RATE_OF_PAY_FROM", "WAGE_RATE_OF_PAY_TO", "WAGE_UNIT_OF_PAY",
    "PW_WAGE_LEVEL", "TOTAL_WORKSITE_LOCATIONS",
)

# Columns shown as "matching rows" evidence.
ROW_EVIDENCE_COLUMNS = (
    "sheet_row", "CASE_NUMBER", "CASE_STATUS", "VISA_CLASS", "EMPLOYER_NAME",
    "JOB_TITLE", "WORKSITE_CITY", "WORKSITE_STATE",
)


@dataclass(frozen=True)
class Budget:
    max_proposals: int = 2          # model proposals per question
    max_denials: int = 2            # policy denials before the loop stops
    statement_seconds: float = 10.0  # wall clock per SQL statement
    display_rows: int = 200         # evidence rows kept for display
    answer_rows: int = 5000         # answer rows kept for scoring
    question_seconds: float = 60.0  # wall clock per question
