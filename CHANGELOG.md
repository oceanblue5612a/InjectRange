# Changelog

All notable changes to InjectRange are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Rule wording is being reviewed for the next patch.

## [1.0.0] - 2026-06-02

### Added

- Stable contract: exit codes 0, 1 and 2, and the written corpus contract in
  `docs/FORMAT.md`.
- The guard comparison prints a per-class breach delta between two guards.

## [0.9.0] - 2025-07-01

### Added

- Corpus pinning: every run records the corpus hash, and a mismatch is a usage
  error rather than a silent comparison.
- `--corpus` accepts a pinned hash alongside the corpus file.

## [0.8.0] - 2024-06-04

### Added

- The sixth breach class: exfiltration framing, with a worked sample probe.
- Per-class pass rates in the JSON report.

## [0.7.0] - 2023-04-25

### Added

- Guard configuration files with per-class sensitivity.
- A real comparison of the strict and permissive sample guards.

## [0.6.0] - 2022-02-15

### Added

- JSON report with fixed keys, including per-probe outcomes.
- `harness` and `report` subcommands.

## [0.5.0] - 2020-12-22

### Added
