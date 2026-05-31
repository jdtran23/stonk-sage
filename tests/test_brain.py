"""Tests for stonk_sage.brain."""

from __future__ import annotations

import pytest

from stonk_sage.brain import BrainFileNotFound, load_brain


def test_load_single_strips_frontmatter() -> None:
    brain = load_brain("equity-research")
    assert set(brain) == {"equity-research"}
    content = brain["equity-research"]
    assert isinstance(content, str)
    assert content  # non-empty
    assert not content.startswith("---"), "YAML frontmatter should be stripped"


def test_load_multiple() -> None:
    brain = load_brain("equity-research", "risk-portfolio")
    assert set(brain) == {"equity-research", "risk-portfolio"}
    assert all(isinstance(v, str) and v for v in brain.values())


def test_missing_file_raises() -> None:
    with pytest.raises(BrainFileNotFound):
        load_brain("nonexistent-file-xyz")


def test_real_content_loaded() -> None:
    brain = load_brain("equity-research")
    # Sanity: the equity-research file talks about Porter's five forces.
    assert "Porter" in brain["equity-research"]
