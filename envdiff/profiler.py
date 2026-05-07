"""Profiles .env files and produces statistics about key composition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import _is_secret
from envdiff.parser import parse_env_file


@dataclass
class EnvProfile:
    path: str
    total_keys: int
    secret_keys: List[str] = field(default_factory=list)
    plain_keys: List[str] = field(default_factory=list)
    empty_keys: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)

    @property
    def secret_count(self) -> int:
        return len(self.secret_keys)

    @property
    def plain_count(self) -> int:
        return len(self.plain_keys)

    @property
    def empty_count(self) -> int:
        return len(self.empty_keys)

    @property
    def secret_ratio(self) -> float:
        if self.total_keys == 0:
            return 0.0
        return round(self.secret_count / self.total_keys, 4)

    def as_dict(self) -> Dict:
        return {
            "path": self.path,
            "total_keys": self.total_keys,
            "secret_count": self.secret_count,
            "plain_count": self.plain_count,
            "empty_count": self.empty_count,
            "duplicate_count": len(self.duplicate_keys),
            "secret_ratio": self.secret_ratio,
            "secret_keys": self.secret_keys,
            "plain_keys": self.plain_keys,
            "empty_keys": self.empty_keys,
            "duplicate_keys": self.duplicate_keys,
        }


def profile_env(path: str) -> EnvProfile:
    """Parse *path* and return an :class:`EnvProfile` with key statistics."""
    env = parse_env_file(path)

    secret_keys: List[str] = []
    plain_keys: List[str] = []
    empty_keys: List[str] = []

    seen: Dict[str, int] = {}
    for key, value in env.items():
        seen[key] = seen.get(key, 0) + 1
        if value == "":
            empty_keys.append(key)
        if _is_secret(key):
            secret_keys.append(key)
        else:
            plain_keys.append(key)

    duplicate_keys = [k for k, count in seen.items() if count > 1]

    return EnvProfile(
        path=path,
        total_keys=len(env),
        secret_keys=sorted(secret_keys),
        plain_keys=sorted(plain_keys),
        empty_keys=sorted(empty_keys),
        duplicate_keys=sorted(duplicate_keys),
    )


def profile_many(paths: List[str]) -> List[EnvProfile]:
    """Return a profile for each path in *paths*."""
    return [profile_env(p) for p in paths]
