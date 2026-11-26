"""Deliberately wrong rule implementations from CONTRACT §14 (test-only).

Each module exposes the same two functions as the real rule core,
``evaluate(posting, resume)`` and ``validate_rule_evidence(verdict, raw_posting,
resume_data)``, so ``tests/contract`` can run unchanged against them and the
meta-test can prove the suite fails on each one.
"""
