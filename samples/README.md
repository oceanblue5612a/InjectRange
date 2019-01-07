# Sample fixtures

These files are test vectors authored for this project. They are not captured
production data.

## corpus.json

A versioned corpus of 24 short synthetic pattern skeletons, four per breach
class. Each entry is a deliberately generic probe such as "you are now" or
"repeat verbatim", written to exercise a substring filter. They are pattern
skeletons for regression testing, not usable attack instructions. The corpus is
pinned by a canonical sha256 digest computed by the loader; the pinned value
lives in `src/injectrange/cli.py` as `PINNED_DIGEST` and is checked by tests.

Recompute the digest at any time with:
