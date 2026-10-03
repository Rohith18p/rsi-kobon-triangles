"""Build the Kobon-triangles slide deck (16:9 PDF) from the project's real data.

Run: uv run python deck/build_deck.py   (from kobon-triangles/)
Output: deck/kobon_deck.pdf and deck/png/slide-XX.png (previews)
"""
import json
import os
import sys
from fractions import Fraction as F

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from count import _meet, triangles  # noqa: E402
from stats import stats  # noqa: E402

# ---- palette (dataviz reference palette, light mode) ----
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
GRID = "#e4e3df"
CARD = "#f3f2ee"

W, H = 13.333, 7.5
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK, "axes.edgecolor": MUTED})


def load(path):
    return json.load(open(os.path.join(ROOT, path)))["lines"]


# ---------------------------------------------------------------- helpers
def new_slide(title, kicker=None):
    fig = plt.figure(figsize=(W, H), facecolor=SURFACE)
    if kicker:
        fig.text(0.05, 0.915, kicker.upper(), fontsize=11, color=BLUE, weight="bold")
    fig.text(0.05, 0.855, title, fontsize=26, weight="bold", color=INK)
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.83, 0.83], color=GRID, lw=1.2))
    return fig


def bullets(fig, items, x=0.05, y=0.77, w=0.9, size=15, gap=0.062, color=INK):
    for it in items:
        if it.startswith("~"):
            fig.text(x + 0.019, y + gap * 0.42, it[1:].strip(), fontsize=size, color=color, va="top")
            y -= gap * 0.58
            continue
        sub = it.startswith("  ")
        txt = it.strip()
        fig.text(x + (0.025 if sub else 0), y, ("–  " if sub else "•  ") + txt, fontsize=size - (2 if sub else 0),
                 color=INK2 if sub else color, va="top", wrap=True)
        y -= gap * (0.85 if sub else 1)
    return y


def card(fig, x, y, w, h, title, body, accent=BLUE, tsize=15, bsize=12.5):
    ax = fig.add_axes([x, y, w, h])
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04", fc=CARD, ec=GRID,
                                transform=ax.transAxes))
    ax.add_patch(FancyBboxPatch((0, 0.965), 1, 0.035, boxstyle="square,pad=0", fc=accent, ec="none",
                                transform=ax.transAxes))
    ax.text(0.05, 0.88, title, fontsize=tsize, weight="bold", color=INK, va="top", transform=ax.transAxes)
    ax.text(0.05, 0.72, body, fontsize=bsize, color=INK2, va="top", transform=ax.transAxes, linespacing=1.45,
            wrap=True)
    return ax


def hero(fig, x, y, number, label, color=INK):
    fig.text(x, y, number, fontsize=48, weight="bold", color=color)
    fig.text(x, y - 0.05, label, fontsize=13, color=INK2)


def footer(fig, n, text="Open Math Challenge · Kobon triangles · team rohith18p"):
    fig.text(0.05, 0.035, text, fontsize=9, color=MUTED)
    fig.text(0.95, 0.035, str(n), fontsize=9, color=MUTED, ha="right")


def draw_arrangement(ax, L, title=None, pad=0.08, mark_multi=True, highlight_line=None, clip=0.0, focus_line=None):
    """Lines (thin gray), triangles (blue fill), multiple points (orange dots)."""
    n = len(L)
    tris = triangles(L)
    pts = {}
    for i in range(n):
        for j in range(i + 1, n):
            X, Y, Wd = _meet(L[i], L[j])
            if Wd:
                p = (F(X, Wd), F(Y, Wd))
                pts.setdefault(p, set()).update((i, j))
    tv = []
    for i, j, k in tris:
        poly = []
        for a, b in ((i, j), (i, k), (j, k)):
            X, Y, Wd = _meet(L[a], L[b])
            poly.append((float(F(X, Wd)), float(F(Y, Wd))))
        tv.append(poly)
    src = tv if focus_line is None else [poly for poly, t in zip(tv, tris) if focus_line in t]
    xs = sorted(p[0] for poly in src for p in poly)
    ys = sorted(p[1] for poly in src for p in poly)
    lo, hi = int(clip * len(xs)), int((1 - clip) * len(xs)) - 1
    x0, x1, y0, y1 = xs[lo], xs[hi], ys[lo], ys[hi]
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    x0, x1, y0, y1 = x0 - pad * dx, x1 + pad * dx, y0 - pad * dy, y1 + pad * dy
    for poly in tv:
        ax.add_patch(Polygon(poly, closed=True, fc=BLUE, ec="none", alpha=0.28))
    for idx, (a, b, c) in enumerate(L):
        col, lw = (AQUA, 2.0) if idx == highlight_line else (INK2, 0.7)
        if abs(b) > abs(a):
            X = [x0 - dx, x1 + dx]
            Y = [(-c - a * x) / b for x in X]
        else:
            Y = [y0 - dy, y1 + dy]
            X = [(-c - b * y) / a for y in Y]
        ax.plot(X, Y, color=col, lw=lw, solid_capstyle="round", zorder=3 if idx == highlight_line else 2)
    if mark_multi:
        mp = [p for p, s in pts.items() if len(s) >= 3]
        if mp:
            ax.scatter([float(p[0]) for p in mp], [float(p[1]) for p in mp], s=46, color=ORANGE,
                       edgecolors=SURFACE, linewidths=1.5, zorder=4)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("auto")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(GRID)
    if title:
        ax.set_title(title, fontsize=12, color=INK2, loc="left")
    return len(tris)


def table(fig, x, y, w, h, header, rows, col_w=None, size=11.5, highlight_col=None):
    ax = fig.add_axes([x, y, w, h])
    ax.axis("off")
    nr, nc = len(rows) + 1, len(header)
    col_w = col_w or [1 / nc] * nc
    xs = [sum(col_w[:i]) for i in range(nc)]
    rh = 1 / nr
    for j, htxt in enumerate(header):
        ax.text(xs[j] + 0.01, 1 - rh / 2, htxt, fontsize=size, weight="bold", color=INK2, va="center")
    ax.plot([0, 1], [1 - rh, 1 - rh], color=MUTED, lw=1)
    for i, row in enumerate(rows):
        yc = 1 - rh * (i + 1.5)
        if i % 2 == 0:
            ax.add_patch(plt.Rectangle((0, yc - rh / 2), 1, rh, fc=CARD, ec="none"))
        for j, cell in enumerate(row):
            ax.text(xs[j] + 0.01, yc, str(cell), fontsize=size, color=INK, va="center",
                    weight="bold" if (highlight_col is not None and j == highlight_col) else "normal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


# ---------------------------------------------------------------- data
N18_OURS = "submissions/n18/solution.json"
R = "research/records/"
N18 = [
    ("Ours: simulated annealing", N18_OURS),
    ("Gallery: 4 triple points", R + "n18_93_ud1_18_18-1fftk1anhxxvi.json"),
    ("Gallery: 3 triple pts + 1 parallel pair", R + "n18_93_ud1_18-1_18-2bkqp8oa3yr7t.json"),
    ("Gallery: 4 parallel pairs", R + "n18_93_ud1_18-4_18-2y40uhlf5g17s.json"),
    ("Lean-verified (yhinai/openmath)", R + "n18_93_yhinai_openmath_lean.json"),
]
N39_BEST = "added/g38/n39_470_38-74kq3v76alw-grow.json"
N38_BASE = "derived/g38/38-74kq3v76alw.json"
N39_SIMPLE = "simple39/n39_470_38-2jwrwxg032wq0-grow.json"
INSERT_DIST = [(466, 4), (467, 28), (468, 70), (469, 135), (470, 11)]


def main():
    out_pdf = os.path.join(ROOT, "deck", "kobon_deck.pdf")
    png_dir = os.path.join(ROOT, "deck", "png")
    os.makedirs(png_dir, exist_ok=True)
    slides = []

    # 1 ---- title
    fig = plt.figure(figsize=(W, H), facecolor=SURFACE)
    fig.text(0.07, 0.70, "KOBON TRIANGLES", fontsize=14, color=BLUE, weight="bold")
    fig.text(0.07, 0.58, "How many triangles can n lines make?", fontsize=38, weight="bold")
    fig.text(0.07, 0.50, "Methods, results and what we are trying next  ·  n = 18 and n = 39", fontsize=18,
             color=INK2)
    hero(fig, 0.07, 0.25, "93", "n = 18 · ties the best known")
    hero(fig, 0.37, 0.25, "470", "n = 39 · official (#2 since 2 Oct)", color=BLUE)
    hero(fig, 0.67, 0.25, "481", "n = 39 · proven upper bound")
    footer(fig, 1, "Open Math Challenge · AutoLab hill alejandrozu/kobon-triangles · team rohith18p · 27 Sep 2026")
    slides.append(fig)

    # 2 ---- the problem
    fig = new_slide("The problem in one picture", "What is being counted")
    ax = fig.add_axes([0.58, 0.12, 0.37, 0.66])
    L5 = [[0, 1, 0], [1, 1, -3], [-1, 1, -3], [2, 1, 2], [-2, 1, 2]]
    k = draw_arrangement(ax, L5, pad=0.35)
    ax.set_title(f"5 lines → {k} triangles (the maximum for 5)", fontsize=12, color=INK2, loc="left")
    bullets(fig, [
        "Draw exactly n straight lines.",
        "Count the triangles they cut out: closed",
        "~3-sided regions no other line passes through.",
        "A big triangle split by a line does not count.",
        "Goal: as many as possible — the Kobon",
        "~triangle problem (still open for most n).",
        "Contest input: integers a·x + b·y + c = 0",
        "~per line, checked with exact arithmetic.",
    ], w=0.5, size=15, gap=0.058)
    footer(fig, 2)
    slides.append(fig)

    # 3 ---- vocabulary
    fig = new_slide("The pieces that matter besides the triangle count", "Vocabulary")
    items = [
        ("Crossing point", "Where two lines meet. n lines in general\nposition have n(n−1)/2 of them\n(153 for n=18, 741 for n=39)."),
        ("Simple arrangement", "No parallel lines and no point where three\nor more lines meet. Most theorems (and our\nSAT encoding) assume this."),
        ("Triple point", "Three lines through one point. Merges\ncrossings; lets one segment border two\ntriangles. Our 470 has 5 of them."),
        ("Parallel pair", "Two lines that never meet (they meet 'at\ninfinity'). Allowed by the contest; one known\n93 for n=18 uses 4 parallel pairs."),
        ("Bounded segment", "A piece of a line between two consecutive\ncrossings. Each triangle uses 3 of them;\nunused ones are 'wasted' capacity."),
        ("Upper bound (Tamura)", "Each line has at most n−2 segments, so\ntriangles ≤ ⌊n(n−2)/3⌋: 96 for n=18,\n481 for n=39 (hitting it = 'perfect')."),
    ]
    for idx, (t, b) in enumerate(items):
        cx = 0.05 + (idx % 3) * 0.305
        cy = 0.44 - (idx // 3) * 0.33
        card(fig, cx, cy, 0.285, 0.30, t, b, accent=[BLUE, ORANGE, AQUA][idx % 3], bsize=12)
    fig.text(0.05, 0.095, "Counting identity checked on every result:", fontsize=12.5, color=INK2)
    fig.text(0.05, 0.06, "3 × triangles  =  (segments used once)  +  2 × (segments shared by two triangles)",
             fontsize=13.5, color=INK, weight="bold")
    footer(fig, 3)
    slides.append(fig)

    # 4 ---- n = 18 at a glance
    fig = new_slide("n = 18: we match the best known result, 93", "n = 18 · summary")
    hero(fig, 0.05, 0.60, "93", "ours (official score)", color=BLUE)
    hero(fig, 0.30, 0.60, "93", "best known in the literature")
    hero(fig, 0.55, 0.60, "96", "proven upper bound (95 claimed, 2007 draft)")
    bullets(fig, [
        "Blanc (2011) proved: a SIMPLE arrangement of 18 lines has at most 93 triangles.",
        "So 94 would need triple points or parallel lines, and nobody has found one",
        "  (the Parpalak–Utkin gallery lists 3,016 different 93s and no 94).",
        "Leaderboard: 16 entries all at 93; ties are ranked by submission time (we are #8).",
        "Value for the competition: matching a known result earns no new-math credit;",
        "  it confirmed our end-to-end pipeline (search → exact check → official evaluation).",
    ], y=0.45, size=14.5)
    footer(fig, 4)
    slides.append(fig)

    # 5 ---- n = 18 approaches
    fig = new_slide("Five different ways people reach 93 for n = 18", "n = 18 · approaches")
    cards = [
        ("A · Annealing (ours)", "Start from random lines, nudge one line\nat a time, keep changes that don't lose\ntriangles, occasionally accept a worse one\nto escape dead ends. Found 93 in ~1 minute\non 10 cores (7 of 10 runs)."),
        ("B · Symmetric construction", "Bader (2007): design the lines with\n3-fold rotational symmetry, so you only\nchoose 6 lines and rotate them. Fewer\nchoices, cleaner structure."),
        ("C · SAT + straightening", "Savchuk (2025): describe only the ORDER\nof crossings as true/false variables,\nlet a SAT solver find a valid pattern,\nthen bend it into straight lines."),
        ("D · Exhaustive search", "Parpalak & Utkin (2026): enumerate\ncombinatorial arrangements, then fit\nlines by linear programming. Their gallery\nhas 3,016 different 93s."),
        ("E · Machine-checked proof", "A 93 whose count was proved inside the\nLean theorem prover (yhinai/openmath) —\nthe triangle count itself is formally\nverified, not just computed."),
        ("Why they all stop at 93", "Blanc (2011): simple 18-line arrangements\ncan't beat 93. Beating it needs triple\npoints or parallels — tried in thousands\nof gallery variants, never above 93."),
    ]
    for idx, (t, b) in enumerate(cards):
        cx = 0.05 + (idx % 3) * 0.305
        cy = 0.44 - (idx // 3) * 0.34
        card(fig, cx, cy, 0.285, 0.32, t, b, accent=[BLUE, ORANGE, AQUA, BLUE, ORANGE, MUTED][idx], bsize=11.5)
    footer(fig, 5)
    slides.append(fig)

    # 6 ---- n = 18 anatomy table
    fig = new_slide("Same 93 triangles, very different structures", "n = 18 · anatomy of five 93s")
    rows = []
    for name, path in N18:
        s = stats(load(path))
        rows.append([name, s["triangles"], s["crossing_points"], s["triple_points"], s["parallel_pairs"],
                     s["bounded_segments"], s["unused_segments"], s["segments_shared_by_2"],
                     s["max_coef_digits"]])
    table(fig, 0.05, 0.30, 0.9, 0.46,
          ["Solution", "Triangles", "Crossings", "Triple pts", "Parallel", "Segments", "Unused",
           "Shared", "Digits"], rows,
          col_w=[0.30, 0.09, 0.09, 0.09, 0.08, 0.09, 0.08, 0.08, 0.10], size=12, highlight_col=1)
    bullets(fig, [
        "Ours is simple: 153 crossings, 288 segments, 9 unused — the maximum a simple 18-line arrangement allows.",
        "Triple points and parallels 'spend' crossings but waste fewer segments (down to 1 unused).",
        "Digits = size of the largest integer coefficient; all fit the contest's 10^30 limit.",
    ], y=0.24, size=12.5, gap=0.05)
    footer(fig, 6)
    slides.append(fig)

    # 7 ---- n = 18 picture
    fig = new_slide("Our 93-triangle arrangement for n = 18", "n = 18 · picture")
    ax = fig.add_axes([0.05, 0.08, 0.55, 0.72])
    draw_arrangement(ax, load(N18_OURS), clip=0.0, pad=0.03)
    s = stats(load(N18_OURS))
    bullets(fig, [
        f"{s['lines']} lines, {s['triangles']} triangles (shaded)",
        f"{s['crossing_points']} crossing points, all simple",
        f"{s['bounded_segments']} bounded segments,",
        f"  {s['segments_used_once']} used, {s['unused_segments']} unused",
        "Integer coefficients ≤ 8 digits",
        "Official score 93 (AutoLab, 27 Sep)",
        "Shaded = the 93 triangles; the view",
        "  is fitted to them (lines extend further).",
    ], x=0.64, y=0.76, w=0.33, size=14)
    footer(fig, 7)
    slides.append(fig)

    # 8 ---- n = 39 summary
    fig = new_slide("n = 39: 470 triangles, officially scored", "n = 39 · summary")
    hero(fig, 0.05, 0.60, "470", "ours, official (27 Sep)", color=BLUE)
    hero(fig, 0.30, 0.60, "471", "current #1 (lavaskiller, 2 Oct)")
    hero(fig, 0.55, 0.60, "481", "proven upper bound")
    hero(fig, 0.78, 0.60, "?", "published value (OEIS)")
    bullets(fig, [
        "No 39-line arrangement was published before this event (OEIS lists a(39) as '?'); ours was #1 27 Sep – 2 Oct.",
        "The bound 481 = 39·37/3 holds for every arrangement (Felsner–Kriegel 1999);",
        "  reaching it needs a 'perfect' arrangement: every segment used by exactly one triangle.",
        "The only thing ruled out so far: a perfect arrangement with 13-fold symmetry (Savchuk 2025).",
        "Gap to close: 11 triangles between what we can draw (470) and what is provably impossible (482+).",
    ], y=0.45, size=14.5)
    footer(fig, 8)
    slides.append(fig)

    # 9 ---- how we got 470
    fig = new_slide("How we got 470", "n = 39 · method")
    steps = [
        ("1  Start", "Parpalak–Utkin gallery:\n248 different 38-line\narrangements, 450\ntriangles each (best known)"),
        ("2  Add one line", "For each, try every\nposition of a 39th line\n(angle × gap grid, scored\nincrementally in ~6 s)"),
        ("3  Exact check", "Re-count the winner with\ninteger arithmetic, then\nthe contest's own evaluator\n(two independent counters)"),
        ("4  Submit", "Official AutoLab climb:\nlocked experiment, run\non our Mac node, scored\n470 at n = 39"),
    ]
    for idx, (t, b) in enumerate(steps):
        card(fig, 0.05 + (idx % 2) * 0.235, 0.46 - (idx // 2) * 0.30, 0.22, 0.28, t, b,
             accent=[BLUE, BLUE, AQUA, ORANGE][idx], tsize=13, bsize=11)
    ax = fig.add_axes([0.57, 0.14, 0.38, 0.60])
    xs = [v for v, _ in INSERT_DIST]
    ys = [c for _, c in INSERT_DIST]
    bars = ax.bar(xs, ys, width=0.62, color=BLUE, edgecolor=SURFACE, linewidth=2)
    bars[-1].set_color(ORANGE)
    for x, y in zip(xs, ys):
        ax.text(x, y + 3, str(y), ha="center", fontsize=11, color=INK)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(x) for x in xs], fontsize=11, color=INK2)
    ax.set_yticks([])
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.set_title("Best triangles after adding one line (248 bases)", fontsize=12, color=INK2, loc="left")
    ax.set_xlabel("triangles with 39 lines", fontsize=11, color=INK2)
    fig.text(0.05, 0.11, "11 of 248 bases reach 470; none reach 471 —", fontsize=12.5, color=INK)
    fig.text(0.05, 0.075, "checked over every combinatorial position of the new line.", fontsize=12.5, color=INK2)
    footer(fig, 9)
    slides.append(fig)

    # 10 ---- anatomy of 470
    fig = new_slide("Anatomy of our 470", "n = 39 · structure")
    L39 = load(N39_BEST)
    s = stats(L39)
    sb = stats(load(N38_BASE))
    ax = fig.add_axes([0.05, 0.08, 0.50, 0.72])
    draw_arrangement(ax, L39, highlight_line=len(L39) - 1, clip=0.1, pad=0.12, focus_line=len(L39) - 1)
    rows = [
        ["Lines", sb["lines"], s["lines"]],
        ["Triangles", sb["triangles"], s["triangles"]],
        ["Crossing points", sb["crossing_points"], s["crossing_points"]],
        ["Triple points", sb["triple_points"], s["triple_points"]],
        ["Bounded segments", sb["bounded_segments"], s["bounded_segments"]],
        ["Unused segments", sb["unused_segments"], s["unused_segments"]],
        ["Shared by 2 triangles", sb["segments_shared_by_2"], s["segments_shared_by_2"]],
        ["Upper bound", sb["tamura_bound"], s["tamura_bound"]],
    ]
    table(fig, 0.58, 0.34, 0.38, 0.44, ["", "38 base", "Our 39"], rows, col_w=[0.52, 0.24, 0.24],
          size=12, highlight_col=2)
    bullets(fig, [
        "Green = the line we added (+20 triangles).",
        "Orange = triple points (inherited from the base).",
        "Picture: zoom on the new line's triangles —",
        "~the full arrangement spans many scales.",
        "Made simple (no triple points) it drops to 466–468.",
    ], x=0.58, y=0.29, size=12, gap=0.045)
    footer(fig, 10)
    slides.append(fig)

    # 11 ---- what did not work
    fig = new_slide("What we tried that did not beat 470 (and what it taught us)", "n = 39 · dead ends")
    cards = [
        ("Local search", "Remove 1 or 2 lines and put back the\nbest ones: ~4,700 moves on three 470s,\nnever above 470. The 470s are strict\nlocal optima."),
        ("Line through a crossing", "Force the new line exactly through an\nexisting crossing (makes a triple point).\nBest 469 — worse than a free line."),
        ("Symmetric SAT (3-fold)", "Solver found curved-line patterns with\n475, 477, 480 and 480 triangles — but\nnone could be straightened (best straight\nfit broke 339–477 crossing orders)."),
        ("Lesson: 'stretchability'", "Curved-line (pseudoline) patterns are\neasy to find; only a tiny, shrinking\nfraction can be drawn with straight lines\n(~99% at 19 lines, ~1% at 27; 0 of 46\nperfect 39-line patterns we tried)."),
    ]
    for idx, (t, b) in enumerate(cards):
        card(fig, 0.05 + (idx % 2) * 0.46, 0.45 - (idx // 2) * 0.35, 0.44, 0.32, t, b,
             accent=[BLUE, BLUE, ORANGE, AQUA][idx], bsize=12)
    footer(fig, 11)
    slides.append(fig)

    # 12 ---- current approach
    fig = new_slide("Last approach tried: SAT neighbourhood search", "n = 39 · SAT neighbourhood search")
    steps = [
        ("Freeze", "Take a straight 470-type\narrangement (made simple:\n466–468). Freeze all lines\nexcept 3–6 'free' ones near\nwasted segments."),
        ("Ask SAT", "Encode every crossing order\nas one bit per triple of lines\n(9,139 bits). Ask: can the free\nlines be re-threaded so at\nmost 1443 − 3T segments\nare wasted, for T = best + 1?"),
        ("Straighten", "Only the free lines move, so\nstraightening is small: pick\ntheir slopes, then solve a\nlinear program for their\npositions."),
        ("Verify", "Exact integer re-count; if\nit beats the best, it becomes\nthe new base and the target\nrises (469 → 470 → 471 …)."),
    ]
    for idx, (t, b) in enumerate(steps):
        card(fig, 0.05 + idx * 0.228, 0.36, 0.21, 0.42, t, b, accent=[MUTED, BLUE, AQUA, ORANGE][idx], tsize=14,
             bsize=11)
    bullets(fig, [
        "Why this can work where symmetric SAT failed: the answer stays close to a picture we can already",
        "  draw, so straightening is a small, well-posed problem instead of a shot in the dark.",
        "Outcome: 394 neighbourhoods (8 cores, ~3 h): 8 curved-line 469s, none straightenable; 7 local 'no' answers;",
        "  the rest timed out. A parallel 2–4-line re-insertion beam (~2,000 moves) also stopped at 470.",
    ], y=0.30, size=12.5, gap=0.05)
    footer(fig, 12)
    slides.append(fig)

    # 13 ---- bounds + next
    fig = new_slide("Where the maximum for n = 39 stands", "n = 39 · upper bound")
    ax = fig.add_axes([0.05, 0.50, 0.9, 0.22])
    ax.set_xlim(455, 485)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.plot([455, 485], [0.4, 0.4], color=GRID, lw=6, solid_capstyle="round")
    ax.plot([470, 481], [0.4, 0.4], color=ORANGE, lw=6, solid_capstyle="butt", alpha=0.35)
    for v, lab, col, yy in ((470, "470\nours", BLUE, 0.75), (471, "471\nother team (2 Oct)", MUTED, -0.05),
                            (481, "481\nproven maximum", INK, 0.75)):
        ax.scatter([v], [0.4], s=160, color=col, zorder=3, edgecolors=SURFACE, linewidths=2)
        ax.text(v, yy, lab, ha="center", va="bottom" if yy > 0.4 else "top", fontsize=12, color=col,
                weight="bold")
    ax.text(476.5, 0.05, "open: 472 – 481", ha="center", va="top", fontsize=12, color=ORANGE)
    bullets(fig, [
        "Proven: nothing can beat 481 (true for all arrangements, including triple points and parallels).",
        "Not yet known: whether 481 (or anything above 471) can actually be drawn with straight lines.",
        "Tried without success: SAT neighbourhood search (394) and 2–4-line re-insertion (~2,000 moves).",
        "  Open directions: new global constructions; straightening many more near-perfect curved-line patterns.",
    ], y=0.40, size=14)
    footer(fig, 13)
    slides.append(fig)

    # 14 ---- verification
    fig = new_slide("How every number here was checked", "Verification & credit")
    bullets(fig, [
        "Exact arithmetic everywhere: lines are integers, crossings are exact fractions — no floating point in any count.",
        "Two independent counters (ours + the contest evaluator's code) plus the counting identity on every result.",
        "Official scores come only from AutoLab's own evaluator (signed report, hill tree hash 7d3f1d91).",
        "Credit: the 38-line bases and several 93s are Parpalak & Utkin's published gallery; the symmetric 93",
        "~is Bader's; the SAT tooling is Savchuk's (kobon-cnf, LineOrder) with the Kissat solver.",
        "Ours: the search and insertion pipeline, the 39-line results, the SAT neighbourhood method.",
        "Tools: Python (numba, python-sat, SciPy/HiGHS), Kissat 4.0.4, Claude Code (Claude Opus 5.5) as the assistant.",
    ], size=13.5, gap=0.07)
    footer(fig, 14)
    slides.append(fig)

    with PdfPages(out_pdf) as pdf:
        for i, fig in enumerate(slides, 1):
            pdf.savefig(fig, facecolor=SURFACE)
            fig.savefig(os.path.join(png_dir, f"slide-{i:02d}.png"), dpi=70, facecolor=SURFACE)
            plt.close(fig)
    print("wrote", out_pdf, len(slides), "slides")


if __name__ == "__main__":
    main()
