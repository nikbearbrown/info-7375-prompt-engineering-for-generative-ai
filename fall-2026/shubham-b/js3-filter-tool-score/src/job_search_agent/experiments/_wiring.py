"""Production wiring for ``jsa exp``: the real adapters, built on first use.

Nothing here runs at import time. Each dependency is a cached property or a factory
method, so a command builds only what it needs (``exp sampling table`` never loads
the résumé, ``exp surfaces run c --dry-run`` never builds a fetcher).
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable, Sequence
from functools import cached_property
from pathlib import Path

from job_search_agent.clock import SystemClock
from job_search_agent.config import AgentConfig, ConfigOverrides, load_config
from job_search_agent.experiments._calls import FirstReplyJudge
from job_search_agent.experiments._io import ExperimentContext, LocalRepoReader
from job_search_agent.experiments.prompt_experiment import HANDCHECK_RAW_REL
from job_search_agent.fsio import OutputRoot, ReadPolicy, create_output_root
from job_search_agent.http import build_fetcher_from_settings
from job_search_agent.judge.backend import child_env
from job_search_agent.judge.judge import build_backend
from job_search_agent.judge.prompt import PromptContract, load_prompt
from job_search_agent.judge.rawlog import RawReplyLog
from job_search_agent.models import Posting, RuleVerdict, VerifiedResume
from job_search_agent.ports import CommandRunner, HttpFetcher
from job_search_agent.providers.greenhouse import GreenhouseProvider
from job_search_agent.resume import load_verified_resume
from job_search_agent.rule.verdict import evaluate as rule_evaluate
from job_search_agent.sysio import SubprocessGit, SubprocessRunner


class Wiring:
    """Builds the real dependencies for one ``jsa exp`` invocation.

    Args:
        config_path: ``--config`` value.
        runner: Runs ``git`` and ``claude``; defaults to ``SubprocessRunner``.
        overrides: CLI overrides (``--data-dir``).
    """

    def __init__(
        self,
        config_path: Path,
        *,
        runner: CommandRunner | None = None,
        overrides: ConfigOverrides | None = None,
    ) -> None:
        self._config_path = config_path
        self._runner = runner
        self._overrides = overrides

    @cached_property
    def config(self) -> AgentConfig:
        """The validated configuration."""
        return load_config(self._config_path, overrides=self._overrides)

    @cached_property
    def runner(self) -> CommandRunner:
        """The command runner (injected, or ``SubprocessRunner``)."""
        return self._runner or SubprocessRunner()

    @cached_property
    def out(self) -> OutputRoot:
        """``fsio.OutputRoot`` on the data directory (created if absent)."""
        return create_output_root(self.config.data_dir)

    @cached_property
    def context(self) -> ExperimentContext:
        """Shared experiment dependencies."""
        root = self.config.project_root
        return ExperimentContext(
            writer=self.out,
            reader=LocalRepoReader(ReadPolicy(root)),
            git=SubprocessGit(root, runner=self.runner),
            clock=SystemClock(),
            data_dir=self.config.data_dir.relative_to(root.resolve()).as_posix(),
        )

    @cached_property
    def resume(self) -> VerifiedResume:
        """The verified résumé (the §12 gate)."""
        return load_verified_resume(
            self.config.resume_path,
            self.config.resume.pinned_sha256,
            project_root=self.config.project_root,
        )

    def evaluate(self) -> Callable[[Posting], RuleVerdict]:
        """The rule with the verified résumé bound."""
        resume = self.resume
        return lambda posting: rule_evaluate(posting, resume)

    @cached_property
    def handcheck_postings(self) -> Sequence[Posting]:
        """Postings of the committed hand-check raw file."""
        body = self.context.reader.read_bytes(HANDCHECK_RAW_REL)
        return GreenhouseProvider().parse(body).postings

    def postings_by_id(self) -> dict[str, Posting]:
        """Hand-check postings keyed by ID."""
        return {p.posting_id: p for p in self.handcheck_postings}

    def load_prompt(self, version: str) -> PromptContract:
        """Loads ``prompts/judge.<version>.md``."""
        return load_prompt(self.config.project_root, version)

    def judge_call(self) -> FirstReplyJudge:
        """A first-reply judge on the configured backend."""
        backend = build_backend(
            self.config.model,
            runner=self.runner,
            make_empty_dir=self.out.make_empty_dir,
            clock=SystemClock(),
        )
        return FirstReplyJudge(
            backend=backend,
            resume=self.resume,
            rawlog=RawReplyLog(self.out, repo_rel=self.config.repo_rel),
            model_requested=self.config.model.model_id,
        )

    def fetcher(self) -> HttpFetcher:
        """The allow-listed fetcher built from ``[http]``."""
        return build_fetcher_from_settings(self.config.http)

    def child_env(self) -> dict[str, str]:
        """The R1 child environment."""
        return child_env(os.environ)

    @staticmethod
    def which(name: str) -> str | None:
        """``shutil.which``."""
        return shutil.which(name)
