"""Brain loader.

Reads finance-domain "instruction" markdown files committed under
``.github/instructions/<name>.instructions.md`` at the repository root, strips
the optional YAML frontmatter, and returns the prose so agents can splice it
into their system prompts.

Example
-------
>>> from stonk_sage.brain import load_brain
>>> docs = load_brain("equity-research", "risk-portfolio")
>>> sorted(docs.keys())
['equity-research', 'risk-portfolio']
>>> docs["equity-research"].startswith("---")
False
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["BrainFileNotFound", "load_brain"]


class BrainFileNotFound(FileNotFoundError):
    """Raised when a requested brain instruction file cannot be located."""


_INSTRUCTIONS_SUBPATH = Path(".github") / "instructions"
_brain_dir_cache: Path | None = None


def _find_brain_dir() -> Path:
    """Walk up from this file to find the repo's `.github/instructions/` dir."""
    global _brain_dir_cache
    if _brain_dir_cache is not None:
        return _brain_dir_cache

    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        candidate = parent / _INSTRUCTIONS_SUBPATH
        if candidate.is_dir():
            _brain_dir_cache = candidate
            return candidate

    raise BrainFileNotFound(
        f"Could not locate '{_INSTRUCTIONS_SUBPATH.as_posix()}' walking up from {here}"
    )


def _strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block delimited by `---` lines.

    Defensive: only strips when the file *starts* with `---` on its own line
    and a closing `---` exists. Otherwise returns the input unchanged.
    """
    if not text.startswith("---"):
        return text

    # Normalize to detect the opening fence as a standalone line.
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text

    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            remainder = "".join(lines[idx + 1 :])
            return remainder.lstrip("\r\n")

    # No closing fence — leave content alone rather than silently nuke it.
    return text


def load_brain(*names: str) -> dict[str, str]:
    """Load one or more brain instruction files by short name.

    Each ``name`` resolves to ``.github/instructions/<name>.instructions.md``
    relative to the repository root. YAML frontmatter (if present) is stripped
    so the returned strings contain just the prose content suitable for
    splicing into LLM prompts.

    Parameters
    ----------
    *names:
        Short names of the instruction files, e.g. ``"equity-research"``.

    Returns
    -------
    dict[str, str]
        Mapping ``{name: file_contents}`` preserving call order.

    Raises
    ------
    BrainFileNotFound
        If any requested file (or the instructions directory itself) is
        missing.

    Example
    -------
    >>> brain = load_brain("equity-research", "risk-portfolio")
    >>> set(brain) == {"equity-research", "risk-portfolio"}
    True
    """
    brain_dir = _find_brain_dir()
    result: dict[str, str] = {}
    for name in names:
        path = brain_dir / f"{name}.instructions.md"
        if not path.is_file():
            raise BrainFileNotFound(
                f"Brain file '{name}' not found at {path}. "
                f"Expected '<name>.instructions.md' under {brain_dir}."
            )
        text = path.read_text(encoding="utf-8")
        result[name] = _strip_frontmatter(text)
    return result
