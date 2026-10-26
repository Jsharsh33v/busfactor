"""Find the files in a Git repository that only one person knows."""

import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Check if your team could keep going without one person.")
console = Console()

AUTHOR_MARKER = "@@author@@"


def read_history(repo: Path) -> dict[str, Counter]:
    """Count how many commits each author made to each tracked file."""
    log = subprocess.run(
        ["git", "-C", str(repo), "log", "--no-merges", "--name-only",
         f"--format={AUTHOR_MARKER}%aN"],
        capture_output=True, text=True, check=True,
    ).stdout
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    history = parse_log(log)
    return {path: history[path] for path in tracked if path in history}


def parse_log(log: str) -> dict[str, Counter]:
    """Turn git log output into commit counts per file and author."""
    history: dict[str, Counter] = defaultdict(Counter)
    author = None
    for line in log.splitlines():
        if line.startswith(AUTHOR_MARKER):
            author = line.removeprefix(AUTHOR_MARKER).strip()
        elif line.strip() and author:
            history[line.strip()][author] += 1
    return history


def orphaned(history: dict[str, Counter], gone: set[str]) -> list[str]:
    """Return the files that nobody would know if these people left."""
    return [path for path, authors in history.items() if set(authors) <= gone]


def bus_factor(history: dict[str, Counter]) -> list[str]:
    """Remove people one by one until more than half the files have nobody left."""
    people = {name for authors in history.values() for name in authors}
    gone: set[str] = set()
    order: list[str] = []
    while len(orphaned(history, gone)) <= len(history) / 2:
        person = max(sorted(people - gone), key=lambda name: len(orphaned(history, gone | {name})))
        gone.add(person)
        order.append(person)
    return order


def get_history(repo: Path) -> dict[str, Counter]:
    """Read the history or stop with a clear message."""
    try:
        history = read_history(repo)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(f"[red]{repo} is not a Git repository.[/red]")
        raise typer.Exit(1)
    if not history:
        console.print("[red]No files with commits were found.[/red]")
        raise typer.Exit(1)
    return history


@app.command()
def scan(repo: Path = typer.Argument(Path("."), help="Path to a Git repository.")):
    """Show the bus factor and the files only one person knows."""
    history = get_history(repo)
    order = bus_factor(history)
    console.print(f"\n[bold]Bus factor: {len(order)}[/bold]")
    console.print(f"If {', '.join(order)} left, most of the {len(history)} files "
                  "would have nobody who worked on them.\n")
    table = Table(title="Files only one person knows")
    table.add_column("File")
    table.add_column("Only person")
    for path, authors in sorted(history.items()):
        if len(authors) == 1:
            table.add_row(path, next(iter(authors)))
    console.print(table)


@app.command()
def leave(
    person: str = typer.Argument(..., help="Author name as Git shows it."),
    repo: Path = typer.Argument(Path("."), help="Path to a Git repository."),
):
    """Show which files nobody would know if this person left."""
    history = get_history(repo)
    lost = orphaned(history, {person})
    console.print(f"\nIf [bold]{person}[/bold] left, {len(lost)} of "
                  f"{len(history)} files would have nobody who worked on them.")
    for path in lost:
        console.print(f"  - {path}")
    if lost:
        console.print("[yellow]Always Be Leaving: share these files with a teammate![/yellow]")
    else:
        console.print("[green]The team could keep going without them.[/green]")