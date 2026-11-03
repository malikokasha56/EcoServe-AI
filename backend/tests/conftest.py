"""Shared fixtures and the evidence recorder.

Every test calls evidence.check(input, expected, observed, ok). After the run, the recorded rows are written to
docs/testing/ as the test evidence table (Markdown and CSV) and the requirements traceability matrix.
"""
import csv
import os
import sys
from datetime import datetime

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)

from tests.requirements_catalogue import REQUIREMENTS  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(BACKEND), "docs", "testing")
RECORDS = []


def pytest_configure(config):
    config.addinivalue_line("markers", "req(*ids): requirement IDs a test provides evidence for")


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    from config import Config
    from app import create_app
    from bootstrap import ensure_ready

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp_path_factory.mktemp("db") / "test.db").replace("\\", "/")
        JWT_SECRET_KEY = "test-secret-key-with-enough-length-0123456789"
        INSTANCE_DIR = str(tmp_path_factory.mktemp("instance"))

    application = create_app(TestConfig)
    with application.app_context():
        ensure_ready(log=lambda *_: None)
    return application


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def token(client):
    r = client.post("/api/auth/login", json={"email": "manager@restaurant.com", "password": "password123"})
    return r.get_json()["token"]


@pytest.fixture(scope="session")
def auth(token):
    return {"Authorization": f"Bearer {token}"}


class Evidence:
    def __init__(self):
        self.rows = []

    def check(self, input, expected, observed, ok):
        self.rows.append({"input": str(input), "expected": str(expected), "observed": str(observed), "ok": bool(ok)})
        assert ok, f"Input: {input} | expected: {expected} | observed: {observed}"


@pytest.fixture
def evidence(request):
    e = Evidence()
    request.node._evidence = e
    return e


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" or (rep.when == "setup" and rep.outcome != "passed"):
        reqs = [r for m in item.iter_markers("req") for r in m.args]
        doc = (item.function.__doc__ or item.name).strip().splitlines()[0]
        e = getattr(item, "_evidence", None)
        RECORDS.append({
            "test": item.nodeid.split("::")[-1],
            "file": os.path.basename(str(item.fspath)),
            "title": doc,
            "reqs": reqs,
            "rows": e.rows if e else [],
            "outcome": rep.outcome,
            "seconds": round(rep.duration, 2),
            "skip_reason": str(rep.longrepr[-1]) if rep.skipped and isinstance(rep.longrepr, tuple) else "",
        })


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def pytest_sessionfinish(session, exitstatus):
    if not RECORDS or os.environ.get("ECOSERVE_NO_EVIDENCE"):
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    status = {"passed": "Pass", "failed": "Fail", "skipped": "Skipped"}

    # Number the tests T-01, T-02, ... in run order; each recorded check is a numbered row.
    rows = []
    for n, rec in enumerate(RECORDS, start=1):
        rec["id"] = f"T-{n:02d}"
        checks = rec["rows"] or [{"input": "-", "expected": "-", "observed": rec["skip_reason"] or "-", "ok": None}]
        for k, c in enumerate(checks, start=1):
            rows.append({
                "Test ID": rec["id"] if len(checks) == 1 else f"{rec['id']}.{k}",
                "Requirement": ", ".join(rec["reqs"]),
                "Test": rec["title"],
                "Input": c["input"],
                "Expected result": c["expected"],
                "Observed result": c["observed"],
                "Result": status[rec["outcome"]] if c["ok"] is not False else "Fail",
            })

    with open(os.path.join(OUT_DIR, "test_evidence.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    passed = sum(r["outcome"] == "passed" for r in RECORDS)
    failed = sum(r["outcome"] == "failed" for r in RECORDS)
    skipped = sum(r["outcome"] == "skipped" for r in RECORDS)
    lines = [
        "# Test Evidence",
        "",
        f"Generated automatically by the test suite (`python -m pytest`) on {stamp}.",
        f"{len(RECORDS)} tests, {len(rows)} recorded checks: {passed} passed, {failed} failed, {skipped} skipped.",
        "",
        "| Test ID | Requirement | Test | Input | Expected result | Observed result | Result |",
        "|---|---|---|---|---|---|---|",
    ]
    lines += ["| " + " | ".join(_cell(r[k]) for k in rows[0]) + " |" for r in rows]
    with open(os.path.join(OUT_DIR, "test_evidence.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    trace = [
        "# Requirements Traceability",
        "",
        f"Generated automatically by the test suite on {stamp}. Each requirement lists the tests that provide evidence for it.",
        "",
        "| Requirement | Type | Description | Tests | Status |",
        "|---|---|---|---|---|",
    ]
    uncovered = []
    for rid, (kind, text) in REQUIREMENTS.items():
        tests = [r for r in RECORDS if rid in r["reqs"]]
        if not tests:
            uncovered.append(rid)
            state = "NOT COVERED"
        elif any(r["outcome"] == "failed" for r in tests):
            state = "Failing"
        elif all(r["outcome"] == "skipped" for r in tests):
            state = "Skipped"
        else:
            state = f"Pass ({sum(r['outcome'] == 'passed' for r in tests)}/{len(tests)})"
        trace.append(f"| {rid} | {kind} | {_cell(text)} | {', '.join(r['id'] for r in tests) or '-'} | {state} |")
    trace += ["", f"Requirements covered: {len(REQUIREMENTS) - len(uncovered)} of {len(REQUIREMENTS)}."]
    with open(os.path.join(OUT_DIR, "traceability.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(trace) + "\n")

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if reporter:
        reporter.write_line(f"\nEvidence written to {OUT_DIR} "
                            f"({len(rows)} checks, requirements covered {len(REQUIREMENTS) - len(uncovered)}/{len(REQUIREMENTS)}"
                            f"{', uncovered: ' + ', '.join(uncovered) if uncovered else ''})")
