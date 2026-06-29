from __future__ import annotations

import argparse

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    parse_args()
    sample = np.random.randn(5)
    print(f"mean={sample.mean():.3f}")


if __name__ == "__main__":
    main()
