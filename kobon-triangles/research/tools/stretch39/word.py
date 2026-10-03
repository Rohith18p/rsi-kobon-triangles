import sys, re
def parse_line(s):
    s = s.strip()
    if ')' in s: s = s.split(')',1)[1]
    return [int(t) for t in s.split()]
def wiring(word, n):
    pos = list(range(n))  # pos[p] = wire at position p (0=bottom at x=-inf)
    local = [[] for _ in range(n)]
    crossings = []
    for g in word:
        a, b = pos[g], pos[g+1]
        local[a].append(b); local[b].append(a)
        crossings.append((a,b))
        pos[g], pos[g+1] = b, a
    return pos, local, crossings
def check(word, n):
    pos, local, cr = wiring(word, n)
    ok = len(word) == n*(n-1)//2 and pos == list(range(n))[::-1] and len(set(frozenset(c) for c in cr)) == len(cr)
    return ok, local
if __name__ == '__main__':
    n = int(sys.argv[1]); w = parse_line(open(sys.argv[2]).readline())
    ok, local = check(w, n); print(len(w), ok)
