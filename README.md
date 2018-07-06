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

```
python -m injectrange diff samples/guard-permissive.json samples/guard-strict.json
```

```
diff
base guard: permissive
head guard: strict

class                   base leaked  head leaked  change
--------------------------------------------------------
Instruction override              3            0  closed
Role confusion                    3            0  closed
Delimiter escape                  4            4  same
Encoding smuggling                4            0  closed
Tool coercion                     4            0  closed
Exfiltration framing              4            0  closed
--------------------------------------------------------
classes opened: 0
classes closed: 5
```


## Reading the matrix

The matrix figure below is built from the two runs above, with the real leaked
over total counts baked into each cell.

![Breach matrix, six classes by two guard configs. Each cell shows leaked over
total probes. The permissive guard breaches all six classes; the strict guard
closes five and leaves delimiter escape open](docs/assets/breach-matrix.svg)

Read a `run` matrix one row per class. A class is `closed` when every probe in
it was blocked, and `BREACH` when at least one leaked. A single leaked probe is
enough to mark the class breached, because the class is a promise about a family
of technique and a partial promise is a broken one. The trailing count of
breached classes is what determines the exit code.

Read a `diff` by the change column. `closed` means fewer probes leaked in the
head than in the base, an improvement. `opened` means more leaked, a regression,
and it is the case CI is meant to catch. `same` means the leak count did not
move. The two totals at the foot, classes opened and classes closed, summarise
the direction of the change.


## Output format

Every report is line-oriented, deterministic, and safe to commit or diff in git.
The fields are contracts.

The `run` matrix carries these fields:

| Field | Meaning |
| --- | --- |
| `guard` | The name from the guard config. |
| `corpus` | The corpus version string. |
| `digest` | The canonical sha256 digest of the loaded corpus. |
| `class` | The breach class title, one row per class, in fixed taxonomy order. |
| `total` | Number of probes in that class. |
| `blocked` | Probes the guard blocked. |
| `leaked` | Probes that passed the guard. |
| `status` | `closed` if none leaked, `BREACH` if at least one did. |
| `breached classes: N of M` | Count of breached classes over total classes. |

The `diff` table carries these fields:

| Field | Meaning |
| --- | --- |
| `base guard` / `head guard` | The two guard names being compared. |
| `class` | Breach class title, in fixed taxonomy order. |
| `base leaked` | Probes that leaked under the base guard. |
| `head leaked` | Probes that leaked under the head guard. |
| `change` | `opened`, `closed`, or `same`, from comparing the two leak counts. |
| `classes opened` | Count of classes where more probes leaked in the head. |
| `classes closed` | Count of classes where fewer probes leaked in the head. |

If the two runs in a diff were built from corpora with different digests, the
diff prints a warning that the comparison is not like for like, since the leak
counts are then measured against different probe sets.


## Exit codes

| Code | Name | Meaning |
| --- | --- | --- |
| 0 | clean | No class breached, or a pure informational command such as `version`. |
| 1 | findings | At least one class breached in the run or the head of a diff. |
| 2 | usage | Usage or input error, including a corpus digest that fails the pin. |

A pin mismatch is an input error, not a finding, so it exits 2 rather than 1:

```
python -m injectrange run samples/guard-strict.json --pin 0000000000000000000000000000000000000000000000000000000000000000
```

```
error: corpus digest 236cbebaab82a1a00f5ab0643dce0db33dd8ef5c08f2a77e8bf69ea467a0a470 does not match pin 0000000000000000000000000000000000000000000000000000000000000000
```


## Regression use in CI

The point of running injectrange in CI is not to prove a guard is good. It is to
catch the moment a guard silently gets weaker. Commit a guard config alongside
your code, run it against the pinned corpus on every change, and let the exit
code fail the build when a class breaches that used to close.

Because the corpus is pinned, a red build has exactly two possible causes: the
guard changed, or the corpus pin was changed on purpose. Both are things a
reviewer should see. A run that used to report `breached classes: 0 of 6` and
now reports a non-zero count is a guard that lost coverage, and the matrix names
the class that opened.

For a change-over-change view, keep the previous guard config in the repository
and run `diff` between it and the new one. Any class in the `opened` column is a
regression to explain before merging. The diff output is deterministic text, so
it reviews cleanly in a pull request.


## Limitations

The honest boundaries of this tool are load-bearing, not fine print.

- The reference guard is a case-insensitive substring matcher. It is a
  reproducible target for regression testing, not a production filter, and it
  does not model semantics, paraphrase, or multi-turn context.
- The corpus is a small set of synthetic skeletons, four probes per class. It is
  not a survey of real attacks, and passing it does not certify a real defence.
- Results describe only the declared guard config against this corpus. They say
  nothing about any model's behaviour, because no model is involved.
- Passing the range is not a security guarantee. It means the rules you wrote
  cover the probes in this corpus, which is a much narrower claim than being
  safe against prompt injection.
- The delimiter escape class is left open in the strict sample on purpose, so
  the diff has real movement to show. It is not a claim that the class is
  unclosable.


## Design decisions

**Test a local guard, not a live model.** Calling a model would make every run
non-deterministic, slow, and dependent on network access and credentials, and
the result would blur two questions: did the model behave, and did the filter
work. injectrange answers only the second, deliberately. A guard you declare in
a file is reproducible, reviewable in a diff, and fully under your control, which
is exactly what a regression range needs. The cost is that the tool says nothing
about a model, and the limitations section states that plainly.

**Report per class, not one score.** A single headline number hides which
family of technique regressed. A guard could lose all of one class and gain a
probe in another and net to the same score, while its actual coverage shifted.
The per-class matrix makes a regression legible: the failing row names the class
that opened, and the diff names the direction of every change. The cost is a
wider report, which is why the output is a compact fixed-width table rather than
prose.

**Pin the corpus by a canonical digest, not the raw bytes.** Hashing the raw
file would make the pin brittle: reformatting the JSON or reordering entries
would break it for no real reason. Hashing a canonical, order-independent form
ties the pin to the meaning of the corpus, so it moves only when the content
moves, which is the only time a pin should move.


## Repository layout

```
injectrange/
  README.md                    this document
  CHANGELOG.md                 release notes, starting at 0.1.0
  LICENSE                      MIT license
  pyproject.toml               package metadata, entry point, Python 3.11+
  .gitignore                   ignored paths
  docs/
    assets/
      logo.svg                 wordmark, blocked and breaching probe states
      breach-matrix.svg        matrix figure built from the two sample runs
  samples/
    README.md                  notes on the sample fixtures
    corpus.json                the 24-probe pinned corpus, four per class
    guard-permissive.json      two-rule guard, breaches every class
    guard-strict.json          twenty-rule guard, closes five classes
  src/
    injectrange/
      __init__.py              package version
      __main__.py              enables python -m injectrange
      cli.py                   argument parsing, subcommands, PINNED_DIGEST
      classes.py               the six breach classes, in fixed order
      corpus.py                load, canonical digest, integrity checks
      guard.py                 the reference substring guard
      harness.py               run the corpus against a guard, per-class tally
      report.py                render the matrix, diff, and corpus summary
  tests/
    test_injectrange.py        26 stdlib unittest cases
```


## Glossary

| Term | Meaning |
| --- | --- |
| Probe | One corpus entry: an id, a breach class, and a short skeleton of text. |
| Breach class | One family of injection technique. There are six, in fixed order. |
| Corpus | The versioned, pinned set of probes the guard is evaluated against. |
| Guard | A user-declared config of blocking substring rules, the tested target. |
| Blocked | A probe caught by at least one guard rule. |
| Leaked | A probe not caught by any guard rule. |
| Breach | A class with at least one leaked probe. |
| Closed | A class with no leaked probes. |
| Digest | The canonical, order-independent sha256 that pins the corpus. |
| Pin | The expected digest checked on every run against the corpus. |
| Matrix | The per-class report for a single run. |
| Diff | The per-class change report between two runs. |


## Verification

The suite is standard-library `unittest`, no third-party test runner. Run it
from the project root:

```
python -m unittest discover -s tests -v
```

The final lines of that run in this session were:

```
----------------------------------------------------------------------
Ran 26 tests in 0.009s

OK
```

The 26 tests cover the taxonomy order and lookups, corpus loading and shape,
digest stability and order independence, rejection of an unknown class and a
duplicate id, case-insensitive guard matching and bad-config rejection, the
harness tallies and their ordering, deterministic rendering of the matrix and
diff, and every CLI subcommand with its exit code including the pin mismatch and
the no-command case. The timing figure is from an unspecified machine and is
indicative, not a guarantee.


## Roadmap

These are directions, not dated promises.

- Optional JSON output for the matrix and diff, for machine consumption in CI.
- A way to declare more than one corpus version and pin each independently.
- A per-probe verbose mode that names which rule blocked each probe, for
  debugging a guard config.


## License

MIT, see [LICENSE](LICENSE).

<!-- draft note 287 -->
