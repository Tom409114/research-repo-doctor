# Unseeded ML Demo Repo

This intentionally incomplete example is used by the Research Repo Doctor demo.

## Install

```bash
python -m pip install -e .
```

## Usage

```bash
python scripts/train.py --seed 42
```

## Reproducibility

The command above should produce repeatable toy output once the seed is wired
into the random number generators.
