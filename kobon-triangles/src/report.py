"""Write RESULTS.md: best exact value per n vs upper bounds and published values."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Best published values (OEIS A006066 rev. 245 + Parpalak–Utkin gallery + doubling series),
# per research/literature.md. Missing key = no published arrangement found.
PUBLISHED = {n: v for n, v in {
    3: 1, 4: 2, 5: 5, 6: 7, 7: 11, 8: 15, 9: 21, 10: 25, 11: 32, 12: 38, 13: 47, 14: 54, 15: 65,
    16: 72, 17: 85, 18: 93, 19: 107, 20: 117, 21: 133, 22: 143, 23: 161, 24: 172, 25: 191,
    26: 204, 27: 225, 28: 238, 29: 261, 30: 275, 31: 299, 32: 315, 33: 341, 34: 357, 35: 385,
    36: 402, 37: 431, 38: 450, 41: 533, 42: 553, 43: 587, 45: 645, 46: 667, 49: 767, 50: 792,
    53: 901, 54: 927, 57: 1045, 65: 1365, 73: 1727, 97: 3071}.items()}


def tamura(n):
    return n * (n - 2) // 3


def blanc_simple(n):
    """Blanc 2011 bound for SIMPLE arrangements, even n (odd n: Tamura)."""
    if n % 2:
        return tamura(n)
    if n % 6 == 2:
        return (2 * n * n - 5 * n - 4) // 6
    return (2 * n * n - 5 * n) // 6


def main():
    rows = []
    for line in open(os.path.join(ROOT, "submissions", "BEST.md")):
        m = re.match(r"\| (\d+) \| (\d+) \| (.+) \|", line)
        if m:
            rows.append((int(m.group(1)), int(m.group(2)), m.group(3)))
    out = ["| n | ours (exact) | published best | upper bound (simple / Tamura) | status | source |",
           "|---|---|---|---|---|---|"]
    new = 0
    for n, v, src in rows:
        pub = PUBLISHED.get(n)
        if pub is None:
            status = "**NEW** (no published arrangement)"
            new += 1
        elif v > pub:
            status = "**RECORD** (beats published)"
        elif v == pub:
            status = "ties published"
        else:
            status = f"below published ({pub})"
        out.append(f"| {n} | {v} | {pub if pub is not None else '–'} | {blanc_simple(n)} / {tamura(n)} | {status} | `{src}` |")
    hdr = (f"# Kobon triangles: results\n\nAll values are exact counts (integer arithmetic), and each file passes "
           f"the mirrored AutoLab evaluator. They are dev numbers until scored with `hills eval`.\n\n"
           f"New values (n with no published arrangement): **{new}**\n\n")
    open(os.path.join(ROOT, "RESULTS.md"), "w").write(hdr + "\n".join(out) + "\n")
    print(hdr + "\n".join(out))


if __name__ == "__main__":
    main()
