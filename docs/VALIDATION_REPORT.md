# VeriRAG v0.1.0 Validation Report

Validated on 6 October 2026.

## Automated validation

- Test suite: 9/9 passing
- Statement coverage: 86%
- Python syntax/bytecode compilation: passing
- Clean-checkout test discovery: passing through `tests/conftest.py`

## End-to-end acceptance test

A sample policy document containing the sentence:

> Enterprise support provides 24/7 phone, chat, and email support with a one-hour target response time for priority-one incidents.

was ingested and queried through the real CLI/service stack.

### Supported answer

Answer: `Enterprise support targets a one-hour response time for priority-one incidents.`

- Result: PASS
- Risk score: 0.1875
- Supported claim ratio: 1.0
- Claim support score: 0.5469
- CLI exit code with `--fail-on-risk`: 0

### Contradictory answer

Answer: `Enterprise support targets a ten-minute response time for priority-one incidents.`

- Result: FAIL
- Risk score: 0.8500
- Supported claim ratio: 0.0
- Claim support score: 0.1721
- Reason includes: `numeric_fact_mismatch_penalty`
- CLI exit code with `--fail-on-risk`: 2

## Release note

During release validation, the first implementation was found to compare a claim against an entire retrieved chunk. This diluted lexical support and could reject a correct sentence embedded inside a larger chunk. The verifier was changed to score sentence-level evidence candidates while preserving chunk-level provenance. A numeric factual-anchor penalty was also added so highly similar text with changed quantities does not pass merely because most words overlap. A regression test now covers both behaviors.

## Environment limitation

The local execution environment used for this validation has no outbound package network access. Therefore Ruff and mypy could not be installed locally. Their commands remain enforced in GitHub Actions on Python 3.11 and 3.12 after publication.
