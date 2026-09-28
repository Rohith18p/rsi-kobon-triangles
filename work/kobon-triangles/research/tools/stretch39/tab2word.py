import ast, sys, json
from word import check
def tab_to_word(tab):
    n=len(tab)
    for rev_rows in (False,True):
        for rev_labels in (False,True):
            lab=(lambda s: n-s) if rev_labels else (lambda s: s-1)   # savchuk 1..n -> my 0..n-1
            local=[None]*n
            for r,row in enumerate(tab):
                seq=[lab(x) for x in row]
                if rev_rows: seq=seq[::-1]
                local[lab(r+1)]=seq
            # simulate sweep greedily: position array, repeatedly swap adjacent pair (p,p+1) if each is the other's next
            pos=list(range(n)); nxt=[0]*n; word=[]; ok=True
            for _ in range(n*(n-1)//2):
                found=False
                for g in range(n-1):
                    a,b=pos[g],pos[g+1]
                    if nxt[a]<len(local[a]) and nxt[b]<len(local[b]) and local[a][nxt[a]]==b and local[b][nxt[b]]==a:
                        word.append(g); nxt[a]+=1; nxt[b]+=1; pos[g],pos[g+1]=b,a; found=True; break
                if not found: ok=False; break
            if ok:
                good,_=check(word,n)
                if good: return word,(rev_rows,rev_labels)
    return None,None
if __name__=='__main__':
    tabs=ast.literal_eval(open(sys.argv[1]).read())
    for k,t in enumerate(tabs):
        w,h=tab_to_word(t); print(k, len(t), h, None if w is None else len(w))
        if w: open(sys.argv[2]+f'_{k}.txt','w').write(' '.join(map(str,w))+'\n')
