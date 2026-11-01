"""Claude judge: payloads, prompt contract, CLI backend, strict validator, retry.

Public entry points:

* ``judge.judge.CliJudge`` — the ``ports.Judge`` adapter for the pipeline;
  ``judge.judge.build_judge`` wires it from ``[model]`` settings.
* ``judge.judge.probe_model`` — one tiny real call for ``jsa doctor --probe-model``.
* ``judge.validator.validate_reply`` — the CONTRACT §8 validator.
"""
