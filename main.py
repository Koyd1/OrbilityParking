"""Basic counter script for the Sigmoid2025 project."""

from __future__ import annotations

import argparse
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print a simple incrementing counter.")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number to count up to (inclusive). Defaults to 5.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between counter ticks in seconds. Defaults to 0.5.",
    )
    return parser.parse_args()


def run_counter(limit: int, delay: float) -> None:
    """Print numbers from 1 to `limit`, waiting `delay` seconds between each."""
    for value in range(1, limit + 1):
        print(f"Count: {value}")
        time.sleep(delay)


def main() -> None:
    args = parse_args()
    run_counter(limit=args.limit, delay=args.delay)


if __name__ == "__main__":
    main()
