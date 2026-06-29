# Making The Demo GIF

The README embeds `docs/demo.gif`, generated from `docs/demo.tape` with
[VHS](https://github.com/charmbracelet/vhs). The tape runs a focused `rrdoctor scan`
against `examples/unseeded-ml-repo` so the demo shows the seed warning plus a couple
of common repository hygiene findings.

## Windows

Open a fresh PowerShell after installing so the new PATH entries are available:

```powershell
winget install --id charmbracelet.vhs --exact
winget install --id Gyan.FFmpeg --exact
winget install --id tsl0922.ttyd --exact
vhs docs/demo.tape
```

## macOS

In `docs/demo.tape`, change:

```text
Set Shell "cmd"
```

to:

```text
Set Shell "bash"
```

Then run:

```bash
brew install charmbracelet/tap/vhs ffmpeg ttyd
vhs docs/demo.tape
```

## Linux

In `docs/demo.tape`, change `Set Shell "cmd"` to `Set Shell "bash"`. Install
`vhs`, `ffmpeg`, and `ttyd` with your package manager or from their release pages,
then run:

```bash
vhs docs/demo.tape
```

The expected output is:

```text
docs/demo.gif
```

If the command cannot find `rrdoctor`, install the project first:

```bash
python -m pip install -e ".[dev]"
```
