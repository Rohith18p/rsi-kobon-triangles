import sys, numpy as np, time
from scipy.optimize import minimize
from word import parse_line, check
from stretch import constraints, init, xs, lp_b, times

def unpack(z,n):
    u=z[:n+1]; b=z[n+1:]
    w=np.exp(u-u.max()); w/=w.sum()
    th=np.pi/2-np.pi*np.cumsum(w)[:n]
    return u,w,th,np.tan(th),b

def loss(z,n,I,J,K,mu,wreg):
    u,w,th,m,b=unpack(z,n)
    dj=m[I]-m[J]; dk=m[I]-m[K]
    xj=(b[J]-b[I])/dj; xk=(b[K]-b[I])/dk
    g=xk-xj; v=np.maximum(mu-g,0)
    L=np.sum(v**2)+wreg*np.sum(b**2)
    gm=np.zeros(n); gb=2*wreg*b
    c=-2*v
    np.add.at(gb,K, c/dk); np.add.at(gb,I,-c/dk)
    np.add.at(gm,I,-c*xk/dk); np.add.at(gm,K,c*xk/dk)
    np.add.at(gb,J,-c/dj); np.add.at(gb,I,c/dj)
    np.add.at(gm,I,c*xj/dj); np.add.at(gm,J,-c*xj/dj)
    gth=gm/np.cos(th)**2
    # th_i = pi/2 - pi*sum_{k<=i} w_k -> dL/dw_k = -pi * sum_{i>=k} gth_i
    gw=np.zeros(n+1); gw[:n]=-np.pi*np.cumsum(gth[::-1])[::-1]
    gu=w*(gw-np.dot(w,gw))
    return L,np.concatenate([gu,gb])

def run(word,n,seed=0,mu=1e-2,tries=8,verbose=False):
    ok,local=check(word,n); assert ok
    I,J,K=constraints(local)
    rng=np.random.default_rng(seed)
    best=(1e99,None)
    for t in range(tries):
        m,b=init(word,n,rng,noise=0.5*t)
        th=np.arctan(m)
        # recover u from th: w_k increments
        c=(np.pi/2-th)/np.pi; w=np.diff(np.concatenate([[0],c,[1]])); w=np.maximum(w,1e-6)
        u=np.log(w)+0.05*t*rng.standard_normal(n+1)
        z=np.concatenate([u,b/np.std(b)*1.0])
        for mu_ in [mu,mu/10]:
            res=minimize(loss,z,args=(n,I,J,K,mu_,1e-6),jac=True,method='L-BFGS-B',options={'maxiter':30000,'maxfun':60000})
            z=res.x
        _,_,_,m,b=unpack(z,n)
        g=xs(m,b,I,K)-xs(m,b,I,J); nv=int(np.sum(g<=0))
        if verbose: print(f' try{t} loss={res.fun:.3e} viol={nv}/{len(I)} minmargin={g.min():.2e}',flush=True)
        if nv<best[0]: best=(nv,(m,b))
        if nv==0: break
    m,b=best[1]
    b2,delta=lp_b(m,I,J,K)
    return best[0],m,b2,delta

if __name__=='__main__':
    n=int(sys.argv[1]); f=sys.argv[2]; idxs=[int(a) for a in sys.argv[3].split(',')]
    lines=open(f).read().splitlines()
    for idx in idxs:
        t=time.time(); nv,m,b,d=run(parse_line(lines[idx]),n,verbose=True)
        print(f'idx {idx}: viol={nv} LPdelta={d:.3e} time={time.time()-t:.1f}s',flush=True)
