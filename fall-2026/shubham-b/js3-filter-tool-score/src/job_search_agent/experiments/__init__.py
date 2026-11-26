"""Experiment harnesses: sampling (Ch. 1), prompt experiment (Ch. 2), surfaces (Ch. 3).

``experiments.cli.register`` adds the ``jsa exp`` command group. The harnesses score
first replies only and never retry; all runtime outputs go under
``data/experiments/`` through the injected writer.
"""
