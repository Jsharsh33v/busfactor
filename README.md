# busfactor

`busfactor` is a command-line tool that reads a Git repository's history and
finds the files that only one person has ever worked on. It also shows the
team's **bus factor**: how many people would have to leave before more than
half of the files have nobody left who worked on them.

The idea comes from "Always Be Leaving" in the "Leading at Scale" chapter of
*Software Engineering at Google*. A good leader builds a team that can keep
going without them, so no one person should be the only one who knows a part
of the code.

## Installation

```bash
git clone https://github.com/Jsharsh33v/busfactor.git
cd busfactor
uv sync
```

## Usage

Show the bus factor and the files only one person knows:

```bash
uv run busfactor scan /path/to/repo
```

See what the team would lose if one person left:

```bash
uv run busfactor leave "Jane Doe" /path/to/repo
```

## Running the tests

```bash
uv run pytest
```