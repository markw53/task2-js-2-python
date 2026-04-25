# Environment Interface

## Observation space

- Source JavaScript repository files under `/source`
- `prompt.txt`
- Shell output from build, test, grep, and file inspection commands

## Action space

- Read files
- Search code
- Create and edit files under `/target`
- Run shell commands (`pip install`, `python3 -m pytest`, etc.)
- Install Python dependencies

## Episode start

- Container starts with the source JavaScript repository at `/source`
- An empty `/target` directory is provided for the translation
- The target behavioral test suite is delivered via `test_patch.diff` and applied after the agent submits its work
- The agent receives only `prompt.txt`

## Deterministic verifier

- Apply `test_patch.diff` to inject behavioral tests into `/target/tests/`
- Run `cd /target && pip install -e .` to verify package installation
- Run `cd /target && MDFORGE_BIN='python3 -m mdforge' python3 -m pytest /target/tests/test_mdforge_behavioral.py --rootdir=/target/tests -v --tb=short --no-header -rA --color=no -p no:cacheprovider` to verify functional equivalence
- Count passing and failing tests

## Success condition

- `pip install -e .` succeeds with no errors
- All behavioral tests pass: `42 passed, 0 failed`
- No test files were modified by the agent (tests are injected post-submission)