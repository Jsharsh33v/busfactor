"""Tests for the busfactor tool."""

from collections import Counter

from busfactor.main import AUTHOR_MARKER, bus_factor, orphaned, parse_log


def test_parse_log_counts_commits():
    """Each commit should count once per file for its author."""
    log = f"{AUTHOR_MARKER}Ana\n\nmain.py\nREADME.md\n\n{AUTHOR_MARKER}Ben\n\nmain.py\n"
    history = parse_log(log)
    assert history["main.py"] == Counter({"Ana": 1, "Ben": 1})
    assert history["README.md"] == Counter({"Ana": 1})


def test_orphaned_finds_files_only_one_person_knows():
    """A file is orphaned when all of its authors are gone."""
    history = {"a.py": Counter({"Ana": 2}), "b.py": Counter({"Ana": 1, "Ben": 1})}
    assert orphaned(history, {"Ana"}) == ["a.py"]


def test_bus_factor_is_one_when_one_person_knows_most_files():
    """One person who owns most files gives a bus factor of one."""
    history = {
        "a.py": Counter({"Ana": 3}),
        "b.py": Counter({"Ana": 1}),
        "c.py": Counter({"Ana": 1, "Ben": 1}),
    }
    assert bus_factor(history) == ["Ana"]


def test_bus_factor_is_two_when_knowledge_is_shared():
    """Files that two people know need both of them to leave."""
    history = {"a.py": Counter({"Ana": 1, "Ben": 1}), "b.py": Counter({"Ana": 1, "Ben": 1})}
    assert len(bus_factor(history)) == 2