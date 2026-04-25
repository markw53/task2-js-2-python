"""
Local verification script for mdforge JS → Python Sycamore task.

NOT uploaded to Realm — this is for pre-flight validation only.

Checks:
  1. Golden repo installs and passes all behavioral tests
  2. Empty scaffold (source JS repo only) FAILS all tests
  3. FAIL_TO_PASS entries match actual pytest node IDs
  4. test_patch.diff applies cleanly
  5. Source JS repo runs (optional sanity check)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_REPO = ROOT / "golden_repo"
BEHAVIORAL_TESTS = ROOT / "behavioral_tests"
TASK_CONFIG = ROOT / "submission" / "task_config.json"
SOURCE_REPO = ROOT / "source_repo"
SUBMISSION_DIR = ROOT / "submission"
IGNORE_PATTERNS = shutil.ignore_patterns(
    ".git", ".pytest_cache", "__pycache__", ".DS_Store", "node_modules",
)


def _load_config() -> Dict[str, Any]:
    """Load task_config.json."""
    with TASK_CONFIG.open() as fh:
        return json.load(fh)


def _copy_dir(src: Path, dst: Path) -> None:
    """Copy a directory tree, ignoring irrelevant files."""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=IGNORE_PATTERNS)


def _inject_tests(repo_root: Path) -> int:
    """Copy behavioral test files into the repo's tests/ directory.
    Returns the number of test files injected."""
    tests_dir = repo_root / "tests"
    tests_dir.mkdir(exist_ok=True)
    count = 0
    for test_file in BEHAVIORAL_TESTS.glob("test_*.py"):
        shutil.copy2(test_file, tests_dir / test_file.name)
        count += 1
    return count


def _run_pip_install(repo_root: Path) -> Dict[str, Any]:
    """Install the Python package in editable mode."""
    process = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "command": f"{sys.executable} -m pip install -e .",
        "returncode": process.returncode,
        "stdout": process.stdout.strip(),
        "stderr": process.stderr.strip(),
    }


def _run_tests(repo_root: Path) -> Dict[str, Any]:
    """Run pytest behavioral tests against the translated Python code."""
    tests_dir = repo_root / "tests"
    test_file = tests_dir / "test_mdforge_behavioral.py"

    env = {
        **os.environ,
        "MDFORGE_BIN": f"{sys.executable} -m mdforge",
        "MDFORGE_CWD": str(repo_root),
    }

    process = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            str(test_file),
            f"--rootdir={tests_dir}",
            "-v", "--tb=short", "--no-header", "-rA",
            "--color=no", "-p", "no:cacheprovider",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )

    # Parse pytest output
    passed = 0
    failed = 0
    errors = 0
    passed_tests: List[str] = []
    failed_tests: List[str] = []

    for line in process.stdout.split("\n"):
        line_stripped = line.strip()
        if " PASSED" in line_stripped:
            passed += 1
            # Extract test node ID
            node_id = line_stripped.split(" PASSED")[0].strip()
            passed_tests.append(node_id)
        elif " FAILED" in line_stripped:
            failed += 1
            node_id = line_stripped.split(" FAILED")[0].strip()
            failed_tests.append(node_id)
        elif " ERROR" in line_stripped:
            errors += 1

    return {
        "command": "pytest (behavioral)",
        "returncode": process.returncode,
        "stdout": process.stdout.strip(),
        "stderr": process.stderr.strip(),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
    }


def _collect_pytest_node_ids(repo_root: Path) -> List[str]:
    """Collect all pytest node IDs without running tests."""
    tests_dir = repo_root / "tests"
    test_file = tests_dir / "test_mdforge_behavioral.py"

    process = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            str(test_file),
            f"--rootdir={tests_dir}",
            "--collect-only", "-q",
            "--color=no", "-p", "no:cacheprovider",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
    )

    node_ids = []
    for line in process.stdout.split("\n"):
        line = line.strip()
        if "::" in line and not line.startswith("="):
            node_ids.append(line)

    return node_ids


def verify_golden() -> Dict[str, Any]:
    """Verify the golden repo installs and passes all behavioral tests."""
    print("=" * 60)
    print("PHASE 1: Verifying golden translation")
    print("=" * 60)

    if not GOLDEN_REPO.exists():
        return {"passed": False, "reason": f"Golden repo not found at {GOLDEN_REPO}"}

    tempdir = tempfile.TemporaryDirectory()
    try:
        workspace = Path(tempdir.name) / "target"
        _copy_dir(GOLDEN_REPO, workspace)

        # Gate check: pyproject.toml or setup.py must exist
        has_pyproject = (workspace / "pyproject.toml").exists()
        has_setup = (workspace / "setup.py").exists()
        if not has_pyproject and not has_setup:
            return {
                "passed": False,
                "reason": "Neither pyproject.toml nor setup.py found in golden repo",
            }

        # Gate check: mdforge package directory must exist
        pkg_dir = workspace / "mdforge"
        if not pkg_dir.is_dir():
            return {
                "passed": False,
                "reason": "mdforge/ package directory not found in golden repo",
            }

        # Count Python source files
        py_files = list(workspace.rglob("*.py"))
        py_files = [f for f in py_files if "test" not in f.name.lower()]
        print(f"  Found {len(py_files)} Python source files")

        if len(py_files) < 10:
            return {
                "passed": False,
                "reason": f"Insufficient source files: found {len(py_files)}, expected >= 10",
            }

        # Install
        print("  Installing package...")
        install_result = _run_pip_install(workspace)
        if install_result["returncode"] != 0:
            return {
                "install": install_result,
                "passed": False,
                "reason": "pip install failed",
            }
        print("  ✓ pip install succeeded")

        # Inject behavioral tests
        injected = _inject_tests(workspace)
        print(f"  Injected {injected} behavioral test file(s)")

        if injected == 0:
            return {
                "install": install_result,
                "passed": False,
                "reason": f"No test files found in {BEHAVIORAL_TESTS}",
            }

        # Run tests
        print("  Running behavioral tests...")
        test_result = _run_tests(workspace)

        config = _load_config()
        expected = len(config.get("FAIL_TO_PASS", []))

        result = {
            "install": install_result,
            "tests": test_result,
            "passed": (
                test_result["returncode"] == 0
                and test_result["failed"] == 0
                and test_result["errors"] == 0
                and test_result["passed"] == expected
            ),
            "expected_tests": expected,
            "actual_passed": test_result["passed"],
            "actual_failed": test_result["failed"],
            "actual_errors": test_result["errors"],
            "source_files": len(py_files),
        }

        if result["passed"]:
            print(f"  ✓ PASSED: {test_result['passed']}/{expected} tests")
        else:
            print(f"  ✗ FAILED: {test_result['passed']}/{expected} passed, "
                  f"{test_result['failed']} failed, {test_result['errors']} errors")
            if test_result["failed_tests"]:
                print("  Failed tests:")
                for tid in test_result["failed_tests"]:
                    print(f"    - {tid}")

        return result
    finally:
        tempdir.cleanup()


def verify_scaffold_fails() -> Dict[str, Any]:
    """Verify that behavioral tests FAIL against an empty scaffold.

    This is the mandatory 'fail state' check: tests must not pass
    when no translation has been applied.
    """
    print()
    print("=" * 60)
    print("PHASE 2: Verifying empty scaffold FAILS")
    print("=" * 60)

    tempdir = tempfile.TemporaryDirectory()
    try:
        workspace = Path(tempdir.name) / "target"
        workspace.mkdir(parents=True)

        # Create a minimal scaffold: just pyproject.toml with click dependency
        # but NO actual mdforge code
        pyproject = workspace / "pyproject.toml"
        pyproject.write_text(
            '[project]\n'
            'name = "mdforge"\n'
            'version = "0.0.1"\n'
            'dependencies = ["click", "python-frontmatter"]\n'
            '\n'
            '[build-system]\n'
            'requires = ["setuptools"]\n'
            'build-backend = "setuptools.backends._legacy:_Backend"\n',
            encoding="utf-8",
        )

        # Create empty mdforge package so pip install doesn't fail entirely
        pkg = workspace / "mdforge"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")

        # Install (may partially succeed)
        
        # Inject behavioral tests
        injected = _inject_tests(workspace)
        print(f"  Injected {injected} behavioral test file(s)")

        # Run tests — they MUST all fail
        print("  Running behavioral tests against empty scaffold...")
        test_result = _run_tests(workspace)

        all_failed = (
            test_result["passed"] == 0
            and test_result["returncode"] != 0
        )

        result = {
            "tests": test_result,
            "scaffold_all_failed": all_failed,
            "passed": all_failed,
            "scaffold_passed_count": test_result["passed"],
        }

        if all_failed:
            print(f"  ✓ GOOD: All tests failed against empty scaffold "
                  f"({test_result['failed'] + test_result['errors']} failures)")
        else:
            print(f"  ✗ BAD: {test_result['passed']} test(s) passed against empty scaffold!")
            print("  This means your tests have false positives — they pass without a real translation.")
            if test_result["passed_tests"]:
                print("  Accidentally passing tests:")
                for tid in test_result["passed_tests"]:
                    print(f"    - {tid}")

        return result
    finally:
        tempdir.cleanup()


def verify_fail_to_pass_ids() -> Dict[str, Any]:
    """Verify that every FAIL_TO_PASS entry matches a real pytest node ID."""
    print()
    print("=" * 60)
    print("PHASE 3: Auditing FAIL_TO_PASS node IDs")
    print("=" * 60)

    if not GOLDEN_REPO.exists():
        return {"passed": False, "reason": "Golden repo not found"}

    tempdir = tempfile.TemporaryDirectory()
    try:
        workspace = Path(tempdir.name) / "target"
        _copy_dir(GOLDEN_REPO, workspace)

        # Install
        _run_pip_install(workspace)

        # Inject tests
        _inject_tests(workspace)

        # Collect node IDs
        print("  Collecting pytest node IDs...")
        collected_ids = _collect_pytest_node_ids(workspace)

        config = _load_config()
        fail_to_pass = config.get("FAIL_TO_PASS", [])

        # Normalize: collected IDs may have full paths, FAIL_TO_PASS has relative
        collected_short = set()
        for nid in collected_ids:
            # Extract the "test_file.py::Class::method" part
            parts = nid.split("/")
            short = parts[-1] if parts else nid
            collected_short.add(short)

        missing = []
        found = []
        for entry in fail_to_pass:
            if entry in collected_short:
                found.append(entry)
            else:
                missing.append(entry)

        extra_in_suite = collected_short - set(fail_to_pass)

        result = {
            "passed": len(missing) == 0 and len(extra_in_suite) == 0,
            "fail_to_pass_count": len(fail_to_pass),
            "collected_count": len(collected_short),
            "matched": len(found),
            "missing_from_suite": missing,
            "extra_in_suite": sorted(extra_in_suite),
        }

        if len(missing) == 0:
            print(f"  ✓ All {len(fail_to_pass)} FAIL_TO_PASS entries found in test suite")
        else:
            print(f"  ✗ {len(missing)} FAIL_TO_PASS entries NOT found in test suite:")
            for mid in missing:
                print(f"    - {mid}")

        if extra_in_suite:
            print(f"  ⚠ {len(extra_in_suite)} tests in suite but NOT in FAIL_TO_PASS:")
            for eid in sorted(extra_in_suite):
                print(f"    - {eid}")

        if result["passed"]:
            print(f"  ✓ Perfect match: {len(fail_to_pass)} entries ↔ {len(collected_short)} tests")

        return result
    finally:
        tempdir.cleanup()


def verify_test_patch_diff() -> Dict[str, Any]:
    """Verify that test_patch.diff exists and is non-empty."""
    print()
    print("=" * 60)
    print("PHASE 4: Checking test_patch.diff")
    print("=" * 60)

    diff_path = SUBMISSION_DIR / "test_patch.diff"

    if not diff_path.exists():
        print("  ✗ test_patch.diff not found")
        return {"passed": False, "reason": "test_patch.diff not found"}

    content = diff_path.read_text(encoding="utf-8")
    byte_count = diff_path.stat().st_size

    if byte_count == 0:
        print("  ✗ test_patch.diff is empty (0 bytes)")
        return {"passed": False, "reason": "test_patch.diff is empty"}

    # Check it looks like a valid unified diff
    has_diff_header = "diff --git" in content or "---" in content
    has_additions = "+++ " in content

    result = {
        "passed": byte_count > 0 and has_diff_header and has_additions,
        "byte_count": byte_count,
        "has_diff_header": has_diff_header,
        "has_additions": has_additions,
    }

    if result["passed"]:
        print(f"  ✓ test_patch.diff looks valid ({byte_count} bytes)")
    else:
        print(f"  ✗ test_patch.diff may be malformed ({byte_count} bytes)")

    return result


def verify_submission_files() -> Dict[str, Any]:
    """Verify all six required submission files exist."""
    print()
    print("=" * 60)
    print("PHASE 5: Checking submission artifacts")
    print("=" * 60)

    required = {
        "prompt.txt": SUBMISSION_DIR / "prompt.txt",
        "task_config.json": TASK_CONFIG,
        "golden_repo.tar.gz": SUBMISSION_DIR / "golden_repo.tar.gz",
        "test_patch.diff": SUBMISSION_DIR / "test_patch.diff",
        "Dockerfile": ROOT / "evaluations" / "Dockerfile",
        "reasoning.txt": SUBMISSION_DIR / "reasoning.txt",
    }

    results = {}
    all_present = True

    for name, filepath in required.items():
        exists = filepath.exists()
        size = filepath.stat().st_size if exists else 0
        results[name] = {"exists": exists, "size": size}
        status = f"✓ {name} ({size} bytes)" if exists else f"✗ {name} MISSING"
        print(f"  {status}")
        if not exists:
            all_present = False

    return {"passed": all_present, "files": results}


def verify_config_no_placeholders() -> Dict[str, Any]:
    """Check task_config.json for placeholder strings."""
    print()
    print("=" * 60)
    print("PHASE 6: Checking for placeholder strings in config")
    print("=" * 60)

    config = _load_config()
    config_str = json.dumps(config)

    placeholders = [
        "LEAVE_BLANK",
        "will_be_filled_in",
        "TODO",
        "FIXME",
        "PLACEHOLDER",
        "CHANGEME",
    ]

    found = []
    for ph in placeholders:
        if ph.lower() in config_str.lower():
            found.append(ph)

    result = {"passed": len(found) == 0, "found_placeholders": found}

    if result["passed"]:
        print("  ✓ No placeholder strings found")
    else:
        print(f"  ✗ Found placeholder strings: {found}")

    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Local verification for mdforge JS → Python Sycamore task."
    )
    parser.add_argument(
        "--phase",
        choices=("all", "golden", "scaffold", "ids", "diff", "files", "config"),
        default="all",
        help="Which verification phase to run (default: all).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full pytest output on failure.",
    )
    args = parser.parse_args(argv)

    results: Dict[str, Any] = {}
    overall_pass = True

    phases = {
        "golden": verify_golden,
        "scaffold": verify_scaffold_fails,
        "ids": verify_fail_to_pass_ids,
        "diff": verify_test_patch_diff,
        "files": verify_submission_files,
        "config": verify_config_no_placeholders,
    }

    if args.phase == "all":
        run_phases = list(phases.keys())
    else:
        run_phases = [args.phase]

    for phase_name in run_phases:
        try:
            phase_result = phases[phase_name]()
            results[phase_name] = phase_result
            phase_passed = phase_result.get("passed", False)
            overall_pass = overall_pass and phase_passed
        except Exception as exc:
            print(f"\n  ✗ Phase '{phase_name}' crashed: {exc}")
            results[phase_name] = {"passed": False, "error": str(exc)}
            overall_pass = False

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for phase_name in run_phases:
        phase_result = results.get(phase_name, {})
        status = "✓ PASS" if phase_result.get("passed") else "✗ FAIL"
        print(f"  {status}  {phase_name}")

    print()
    if overall_pass:
        print("🟢 ALL CHECKS PASSED — ready to push to Realm")
    else:
        print("🔴 SOME CHECKS FAILED — fix before pushing")

    # Write results to file for reference
    results_file = ROOT / "verification_results.json"
    with results_file.open("w") as fh:
        json.dump(results, fh, indent=2, default=str)
    print(f"\nDetailed results written to: {results_file}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())