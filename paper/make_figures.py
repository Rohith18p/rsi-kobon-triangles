"""Figures for the paper (run from repo root): uv run python paper/make_figures.py"""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "kobon-triangles", "deck"))
sys.path.insert(0, os.path.join(ROOT, "kobon-triangles", "src"))
import build_deck as D  # reuse the exact drawing code and palette

L = json.load(open(os.path.join(ROOT, "kobon-triangles", "n39_470", "solution.json")))["lines"]
fig, ax = plt.subplots(figsize=(6.4, 4.6), facecolor="white")
D.draw_arrangement(ax, L, highlight_line=len(L) - 1, clip=0.1, pad=0.12, focus_line=len(L) - 1)
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "paper", "fig_arrangement.png"), dpi=220, facecolor="white")

dist = [(466, 4), (467, 28), (468, 70), (469, 135), (470, 11)]
fig, ax = plt.subplots(figsize=(6.0, 3.0), facecolor="white")
xs = [a for a, _ in dist]; ys = [b for _, b in dist]
bars = ax.bar(xs, ys, width=0.62, color=D.BLUE, edgecolor="white", linewidth=2)
bars[-1].set_color(D.ORANGE)
for x, y in zip(xs, ys):
    ax.text(x, y + 3, str(y), ha="center", fontsize=10)
ax.set_xticks(xs); ax.set_yticks([])
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.set_xlabel("triangles after adding the best 39th line")
ax.set_ylabel("number of 38-line bases")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "paper", "fig_sweep.png"), dpi=220, facecolor="white")
print("ok")
