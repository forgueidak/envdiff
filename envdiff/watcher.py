"""Watch .env files for changes and re-run comparison automatically."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Sequence

from envdiff.comparator import DiffResult, compare_envs
from envdiff.parser import parse_env_file


CallbackFn = Callable[[DiffResult], None]


class EnvWatcher:
    """Poll a pair of .env files and invoke *callback* when a diff changes.

    Parameters
    ----------
    base_path:
        Path to the base .env file.
    target_path:
        Path to the target .env file.
    callback:
        Function called with the latest :class:`~envdiff.comparator.DiffResult`
        whenever a change is detected.
    interval:
        Polling interval in seconds (default 2).
    mask_secrets:
        Passed through to :func:`~envdiff.comparator.compare_envs`.
    """

    def __init__(
        self,
        base_path: str | Path,
        target_path: str | Path,
        callback: CallbackFn,
        interval: float = 2.0,
        mask_secrets: bool = False,
    ) -> None:
        self.base_path = Path(base_path)
        self.target_path = Path(target_path)
        self.callback = callback
        self.interval = interval
        self.mask_secrets = mask_secrets
        self._last_mtimes: tuple[float, float] = (0.0, 0.0)
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, max_iterations: int | None = None) -> None:
        """Begin polling.  Blocks until :meth:`stop` is called or *max_iterations* reached."""
        self._running = True
        iterations = 0
        while self._running:
            if self._files_changed():
                result = self._run_compare()
                self.callback(result)
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            time.sleep(self.interval)

    def stop(self) -> None:
        """Signal the polling loop to stop after the current iteration."""
        self._running = False

    def snapshot(self) -> DiffResult:
        """Return a single diff result without starting the watch loop."""
        return self._run_compare()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _current_mtimes(self) -> tuple[float, float]:
        return (
            self.base_path.stat().st_mtime,
            self.target_path.stat().st_mtime,
        )

    def _files_changed(self) -> bool:
        current = self._current_mtimes()
        if current != self._last_mtimes:
            self._last_mtimes = current
            return True
        return False

    def _run_compare(self) -> DiffResult:
        base = parse_env_file(self.base_path)
        target = parse_env_file(self.target_path)
        return compare_envs(base, target, mask_secrets=self.mask_secrets)
