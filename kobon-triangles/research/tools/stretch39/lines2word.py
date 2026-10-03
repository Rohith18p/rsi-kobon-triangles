import json, sys
from fractions import Fraction
def word_from_lines(L):
    # L: list of (m,b) floats/fractions; wires labelled by order at x=-inf (bottom=largest slope)
    n=len(L); order=sorted(range(n), key=lambda i:-L[i][0])
    M=[L[i] for i in order]
    ev=[]
    for i in range(n):
        for j in range(i+1,n):
            x=(M[j][1]-M[i][1])/(M[i][0]-M[j][0]); ev.append((x,i,j))
    ev.sort()
    pos=list(range(n)); where=list(range(n)); w=[]
    pending=ev[:]
    # process in x order; for exact ties need adjacency: handle by repeated scan
    while pending:
        x0=pending[0][0]; grp=[e for e in pending if e[0]==x0]; pending=[e for e in pending if e[0]!=x0]
        while grp:
            for e in grp:
                _,i,j=e
                if abs(where[i]-where[j])==1:
                    g=min(where[i],where[j]); w.append(g)
                    pos[g],pos[g+1]=pos[g+1],pos[g]; where[pos[g]]=g; where[pos[g+1]]=g+1
                    grp.remove(e); break
            else: raise Exception('non-simple tie')
    return w
if __name__=='__main__':
    d=json.load(open(sys.argv[1])); L=[(Fraction(a),Fraction(b)) for a,b in d['lines']]
    print(' '.join(map(str,word_from_lines(L))))
