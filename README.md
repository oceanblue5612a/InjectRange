<p align="center">
  <img src="docs/assets/banner.svg" alt="injectrange banner: probe dots against a guard bar with one probe breaching, and the six breach classes and the pinned corpus rule written beside it" width="760">
</p>

<div align="center">

<img src="docs/assets/logo.svg" width="260"
     alt="injectrange wordmark split at the inject and range morphemes, with one
     accent mark showing a single probe that breaches the guard" />

# InjectRange

</div>

| What this is | What this is not |
| --- | --- |
| A deterministic regression range for a prompt-injection guard you declare yourself. | A production filter. The reference guard is a plain substring matcher, nothing more. |
| A hash-pinned corpus of 24 short synthetic pattern skeletons, four in each of six breach classes. | A survey of real attacks. The entries are generic skeletons, not usable attack instructions. |
| A harness that tells you which named class opened, so a regression is legible. | A model test. It exercises the config you wrote, never a model, and there is no network access. |
| A tool for catching a guard that silently got weaker between two commits. | A security guarantee. Passing the range says the declared rules cover this corpus, and nothing more. |

injectrange evaluates a locally declared guard configuration against a fixed,
hash-pinned corpus and records which breach classes the guard fails to close.
The output is a per-class matrix rather than a single headline number, so a
regression shows up as a named class opening rather than a score drifting by a
point. It tests the guard you wrote, not any model, and it never reaches the
network, so the same corpus and the same guard config always produce the same
result.

The rest of this document explains why the corpus is pinned, what each breach
class asks of a filter, how integrity is enforced, and how to read the two
reports. Every command block below was captured from a real run in this
session.


## Why a pinned corpus

A guard is a moving target. You add a rule to close one class, refactor the
matcher, tighten a normaliser, and three commits later a rule you thought was
redundant turns out to have been the only thing holding a class shut. Nothing
in a green test suite necessarily notices, because the guard still loads and
still blocks the obvious cases.

injectrange exists to make that regression loud. The corpus is fixed and pinned
by a canonical digest, so the set of probes does not drift underneath you. When
the same corpus runs against two versions of your guard, any change in the
per-class result is attributable to the guard alone. If you want the corpus to
change, you change it deliberately, the digest moves, and the pin you commit
records that decision. A silent corpus edit cannot masquerade as a guard
improvement, because the loader refuses to run against a corpus that does not
match the pin.


## Install

Install into the current environment in editable mode:

```
pip install -e .
```

The project targets Python 3.11 and has no runtime dependencies beyond the
standard library. You can also run it without installing by pointing Python at
the source tree:

```
python -m injectrange version
```

```
injectrange 0.1.0
```


## Commands

The CLI has four subcommands. With no subcommand it prints usage and exits 2.

```
python -m injectrange
```

```
usage: injectrange [-h] {run,corpus,diff,version} ...

Deterministic regression range for prompt-injection defences.

positional arguments:
  {run,corpus,diff,version}
    run                 evaluate a guard against the corpus
    corpus              summarize and verify the corpus
    diff                compare two guards against the corpus
    version             print the version

options:
  -h, --help            show this help message and exit
```

| Command | Purpose | Reads | Emits |
| --- | --- | --- | --- |
| `run <guard>` | Evaluate one guard config against the pinned corpus. | guard JSON, corpus JSON | per-class breach matrix |
| `corpus` | Summarise the corpus and verify its pinned digest. | corpus JSON | per-class counts, digest |
| `diff <base> <head>` | Compare two guard configs against the corpus. | two guard JSONs, corpus JSON | per-class change table |
| `version` | Print the version and exit clean. | nothing | version string |

Every subcommand that touches the corpus accepts `--corpus` to point at a
different file, `--pin` to supply an expected digest, and `--allow-unpinned` to
skip the digest check. `corpus` also accepts `--show-digest`, which prints only
the computed digest and exits, so you can update a pin after a deliberate corpus
change.


## The six breach classes

Each corpus entry is tagged with exactly one breach class, and the harness
reports one line per class. The descriptions below say what a filter is being
asked to recognise, at the level of the family of technique. The corpus entries
themselves are deliberately short skeletons written to exercise a substring
matcher, so this section names the shape of each class rather than reproducing
any usable string.

### Instruction override

A probe in this class attempts to cancel or replace the standing instructions,
telling the assistant that the earlier guidance no longer applies. A guard
closes the class when it recognises the family of phrasings that assert prior
directions are void and that fresh ones take their place, rather than matching a
single literal sentence.

### Role confusion
