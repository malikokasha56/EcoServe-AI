"""Renders captured terminal output (start-up checklist, test run) as images for the report."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))


def render(src, out, title, cmd):
    with open(os.path.join(HERE, src), encoding="utf-8", errors="replace") as f:
        lines = [cmd, ""] + [line.rstrip("\n") for line in f]
    lines = [line.split("Downloads" + os.sep)[-1] if "Downloads" + os.sep in line else line for line in lines]
    h = 0.6 + 0.24 * len(lines)
    fig = plt.figure(figsize=(10, h))
    fig.patch.set_facecolor("#0c0c0c")
    fig.text(0.01, 1 - 0.18 / h, title, color="#9ca3af", family="monospace", fontsize=9, va="top")
    for i, line in enumerate(lines):
        color = "#93c5fd" if line.startswith(">") else ("#86efac" if "[OK]" in line or "passed" in line else "#e5e5e5")
        fig.text(0.02, 1 - (0.5 + 0.24 * i) / h, line, color=color, family="monospace", fontsize=9.5, va="top")
    fig.savefig(os.path.join(HERE, "figures", out), dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("wrote", out)


render("start_run.txt", "term_start.png", "EcoServe AI (START.bat)", "> START.bat")
render("test_run.txt", "term_tests.png", "Windows PowerShell", "> python -m pytest tests -q")
