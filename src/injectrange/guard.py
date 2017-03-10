"""A configurable reference guard built from rules the user declares.

The guard is deliberately simple and fully local: it holds a list of rules, and
each rule is a lowercase substring that, if present in a probe, blocks that
probe. This is not a production filter. It is a reference target so a regression
range has something concrete and reproducible to evaluate. Because the guard is
declared in a config file the user controls, the corpus tests the guard, not any
model.
