#!/usr/bin/env python3
"""
make_heatmap.py

Fetches your real GitHub contribution calendar via the GraphQL API and
renders it as an SVG heatmap (GitHub's classic green squares, themeable),
matching the reference README's contrib-heatmap.svg.

Requires a GitHub personal access token with no special scopes
(read:user is enough) passed via the GITHUB_TOKEN env var -- this is
provided automatically inside GitHub Actions, so no setup is needed there.

Usage:
    GITHUB_TOKEN=xxxx python scripts/make_heatmap.py <github-username> -o contrib-heatmap.svg
"""

import argparse
import datetime
import os
import sys

import requests

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

BG = "#0d1117"
EMPTY = "#161b22"
SCALE = ["#0e4429", "#006d32", "#26a641", "#39d353"]  # low -> high, GitHub-green


def fetch_weeks(username: str, token: str) -> list:
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": username}},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def color_for(count: int, max_count: int) -> str:
    if count == 0:
        return EMPTY
    if max_count == 0:
        return SCALE[0]
    ratio = count / max_count
    idx = min(int(ratio * len(SCALE)), len(SCALE) - 1)
    return SCALE[idx]


def render_svg(weeks: list, cell: int = 11, gap: int = 3) -> str:
    all_days = [d for w in weeks for d in w["contributionDays"]]
    max_count = max((d["contributionCount"] for d in all_days), default=0)

    n_weeks = len(weeks)
    width = n_weeks * (cell + gap) + gap + 40
    height = 7 * (cell + gap) + gap + 20

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">',
        f'<rect width="100%" height="100%" fill="{BG}" rx="8"/>',
    ]

    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            dow = datetime.date.fromisoformat(day["date"]).weekday()  # Mon=0..Sun=6
            # GitHub calendars run Sun-Sat; convert so Sunday is row 0
            row = (dow + 1) % 7
            x = 30 + wi * (cell + gap)
            y = 10 + row * (cell + gap)
            color = color_for(day["contributionCount"], max_count)
            svg.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}">'
                f'<title>{day["date"]}: {day["contributionCount"]} contributions</title>'
                f'</rect>'
            )

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("-o", "--output", default="contrib-heatmap.svg")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Set GITHUB_TOKEN env var (a plain PAT with read:user scope works).", file=sys.stderr)
        sys.exit(1)

    weeks = fetch_weeks(args.username, token)
    svg = render_svg(weeks)

    with open(args.output, "w") as f:
        f.write(svg)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
