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

A probe here attempts to reassign the assistant to a new persona or account, on
the theory that a renamed actor is exempt from the original constraints. Closing
the class means treating an attempt to redefine who the assistant is as
suspicious in itself, independent of the specific persona named.

### Delimiter escape

A probe in this class attempts to break out of a quoting, fencing, or wrapping
boundary so that following text is read as a fresh instruction rather than as
quoted content. A guard closes the class when it accounts for the boundary
markers a hostile input can forge, not only the ones the application itself
emits. In the strict sample this class is left open on purpose, which is
discussed below.

### Encoding smuggling

A probe here hides a directive behind an encoding or transform, so a filter that
only inspects the surface text sees nothing to block. Closing the class requires
recognising the request to decode-then-act as a signal on its own, before any
decoding happens, rather than trying to enumerate encodings.

### Tool coercion

A probe in this class attempts to force an unrequested tool or command
invocation, steering the assistant toward an action the user never asked for. A
guard closes the class by treating an unsolicited push toward a privileged
capability as something to reject, regardless of which tool is named.

### Exfiltration framing

A probe here frames a request as a reason to reveal held secrets, dressing the
disclosure up as debugging, auditing, or verification. Closing the class means
recognising that a plausible-sounding pretext for surfacing hidden state is
still a request to surface hidden state.


## Corpus pinning and integrity

The corpus is pinned by a sha256 digest, but the digest is not taken over the
raw file bytes. It is computed over a canonical form: the patterns are sorted by
id, each is reduced to its id, class, and text, and the whole is serialised with
sorted keys and no incidental whitespace. Hashing that canonical form means the
digest is stable across platforms and indifferent to how the source file is
formatted or how its entries are ordered. Reformatting the JSON or reordering
the entries does not change the digest, while changing any id, class, or text
does. A test in the suite confirms the digest is unchanged when the pattern list
is reversed.

Summarise and verify the corpus:

```
python -m injectrange corpus
```

```
corpus: 1.0.0
digest: 236cbebaab82a1a00f5ab0643dce0db33dd8ef5c08f2a77e8bf69ea467a0a470

class                   count
-----------------------------
Instruction override        4
Role confusion              4
Delimiter escape            4
Encoding smuggling          4
Tool coercion               4
Exfiltration framing        4
-----------------------------
total                      24
```

The pinned digest lives in `src/injectrange/cli.py` as `PINNED_DIGEST` and is
checked against the loaded corpus on every `run` and `diff`. Its value is:

```
236cbebaab82a1a00f5ab0643dce0db33dd8ef5c08f2a77e8bf69ea467a0a470
```

To recompute the digest after a deliberate corpus change, print it directly and
copy it into the pin:

```
python -m injectrange corpus --show-digest
```

```
236cbebaab82a1a00f5ab0643dce0db33dd8ef5c08f2a77e8bf69ea467a0a470
```


## Writing a guard config

A guard config is a JSON object with a name and a list of blocking rules. Each
rule is a substring; a probe is blocked if any rule occurs in its lowercased
text, so matching is case-insensitive. The shape is:

```json
{
  "name": "strict",
  "rules": [
    "ignore all previous",
    "you are now",
    "..."
  ]
}
```

The name is required and must be non-empty; the rules must be a list, and each
rule must be a non-empty string. Rules are lowercased when the config loads, so
the guard behaves deterministically regardless of the case you write them in. A
malformed config is a usage error, not a crash: a missing name, a non-list
`rules`, or an empty rule each raise a clear `GuardError` and exit 2.

This guard is a reference target, not a filter you should ship. It exists so the
regression range has something concrete and reproducible to evaluate. Because
you declare it, the corpus tests your declared rules, never a model.


## A real comparison of the two sample guards

Two sample guards ship in `samples/`. The permissive guard has two rules and is
meant to leave every class open, giving the diff a clear baseline. The strict
guard has twenty rules covering five of the six classes.

Run the permissive guard. It breaches every class and exits 1:

```
python -m injectrange run samples/guard-permissive.json
```

```
guard: permissive
corpus: 1.0.0
digest: 236cbebaab82a1a00f5ab0643dce0db33dd8ef5c08f2a77e8bf69ea467a0a470

class                   total blocked  leaked  status
-----------------------------------------------------
Instruction override        4       1       3  BREACH
Role confusion              4       1       3  BREACH
Delimiter escape            4       0       4  BREACH
Encoding smuggling          4       0       4  BREACH
Tool coercion               4       0       4  BREACH
Exfiltration framing        4       0       4  BREACH
-----------------------------------------------------
breached classes: 6 of 6
```

The permissive guard's two rules each catch exactly one probe in their class,
which is why instruction override and role confusion show one blocked and three
leaked while the four classes with no matching rule leak all four.

Run the strict guard. It closes five classes and leaves delimiter escape open:

```
python -m injectrange run samples/guard-strict.json
```

```
guard: strict
corpus: 1.0.0
digest: 236cbebaab82a1a00f5ab0643dce0db33dd8ef5c08f2a77e8bf69ea467a0a470

class                   total blocked  leaked  status
-----------------------------------------------------
Instruction override        4       4       0  closed
Role confusion              4       4       0  closed
Delimiter escape            4       0       4  BREACH
Encoding smuggling          4       4       0  closed
Tool coercion               4       4       0  closed
Exfiltration framing        4       4       0  closed
-----------------------------------------------------
breached classes: 1 of 6
```

Delimiter escape is left open in the strict sample on purpose, so the range
still reports a real breach and the diff below has real movement to show. It is
not a claim that the class cannot be closed.

Diff the two guards to see what changed between them:

