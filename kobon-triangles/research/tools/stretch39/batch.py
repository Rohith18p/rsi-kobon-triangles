import sys, json, numpy as np, time, os
from multiprocessing import Pool
os.environ.setdefault('OMP_NUM_THREADS','1')
from word import parse_line
from stretch2 import run
n=int(sys.argv[1]); files=sys.argv[2].split(','); tries=int(sys.argv[3]); out=sys.argv[4]
words=[]
for f in files:
    for k,l in enumerate(open(f)):
        if ')' in l: words.append((f"{os.path.basename(f)}:{k}",l))
def job(a):
    tag,l=a
    w=parse_line(l)
    t=time.time()
    nv,m,b,d=run(w,n,tries=tries)
    r=dict(tag=tag,viol=nv,delta=float(d),t=time.time()-t)
    if d>1e-7: r['m']=m.tolist(); r['b']=b.tolist(); r['word']=w
    return r
if __name__=='__main__':
    with Pool(int(os.environ.get("NP","2"))) as p, open(out,'w') as fo:
        for r in p.imap_unordered(job,words):
            fo.write(json.dumps(r)+'\n'); fo.flush()
            if r["delta"]>1e-7: print('SUCCESS',r['tag'],r['delta'],flush=True)
