import sys, json, numpy as np, time
from fractions import Fraction
from scipy.optimize import minimize, linprog
from word import parse_line, check, wiring

def constraints(local):
    I=[];J=[];K=[]
    for i,L in enumerate(local):
        for a,b in zip(L,L[1:]):
            I.append(i);J.append(a);K.append(b)
    return np.array(I),np.array(J),np.array(K)

def times(word,n):
    T=np.zeros((n,n)); pos=list(range(n))
    for t,g in enumerate(word):
        a,b=pos[g],pos[g+1]; T[a,b]=T[b,a]=t; pos[g],pos[g+1]=b,a
    return T

def init(word,n,rng,iters=30,noise=0.0):
    T=times(word,n); T=(T-T.mean())/T.std()
    th=np.pi/2-np.pi*(np.arange(n)+0.5)/n + noise*rng.standard_normal(n)/n
    th=np.sort(th)[::-1]; m=np.tan(th); m=np.clip(m,-30,30)
    iu=np.triu_indices(n,1)
    for _ in range(iters):
        # b_j - b_i = t_ij (m_i - m_j)
        A=np.zeros((len(iu[0])+1,n)); r=np.zeros(len(iu[0])+1)
        A[np.arange(len(iu[0])),iu[1]]=1; A[np.arange(len(iu[0])),iu[0]]=-1
        r[:-1]=T[iu]*(m[iu[0]]-m[iu[1]]); A[-1,:]=1
        b=np.linalg.lstsq(A,r,rcond=None)[0]
        # fixed b: t_ij m_i - t_ij m_j = b_j-b_i
        A=np.zeros((len(iu[0])+1,n)); A[np.arange(len(iu[0])),iu[0]]=T[iu]; A[np.arange(len(iu[0])),iu[1]]=-T[iu]
        r[:-1]=b[iu[1]]-b[iu[0]]; A[-1,:]=0; A[-1,n//2]=1; r[-1]=m[n//2]
        m2=np.linalg.lstsq(A,r,rcond=None)[0]
        if np.all(np.diff(m2)<0): m=m2
        else: break
    return m,b

def xs(m,b,i,j): return (b[j]-b[i])/(m[i]-m[j])

def loss(z,n,I,J,K,mu):
    m=z[:n]; b=z[n:]
    dj=m[I]-m[J]; dk=m[I]-m[K]
    xj=(b[J]-b[I])/dj; xk=(b[K]-b[I])/dk
    g=xk-xj; v=np.maximum(mu-g,0)
    # slope order
    ds=m[:-1]-m[1:]; vs=np.maximum(1e-3-ds,0)
    L=np.sum(v**2)+100*np.sum(vs**2)
    gz=np.zeros(2*n)
    c=-2*v  # dL/dg
    # g = xk - xj
    np.add.at(gz,n+K, c/dk); np.add.at(gz,n+I,-c/dk)
    np.add.at(gz,I,-c*xk/dk); np.add.at(gz,K,c*xk/dk)
    np.add.at(gz,n+J,-c/dj); np.add.at(gz,n+I,c/dj)
    np.add.at(gz,I,c*xj/dj); np.add.at(gz,J,-c*xj/dj)
    cs=-200*vs; gz[:n-1]+=cs; gz[1:n]-=cs
    return L,gz

def margin(m,b,I,J,K):
    return np.min(xs(m,b,I,K)-xs(m,b,I,J))

def lp_b(m,I,J,K,bound=10.0):
    # variables b (n), delta ; maximize delta s.t. x_ik - x_ij >= delta
    n=len(m); R=len(I)
    A=np.zeros((R,n+1)); dj=m[I]-m[J]; dk=m[I]-m[K]
    r=np.arange(R)
    # -(x_ik - x_ij) + delta <= 0 ; x_ik = (b_K-b_I)/dk
    np.add.at(A,(r,K),-1/dk); np.add.at(A,(r,I),1/dk)
    np.add.at(A,(r,J),1/dj); np.add.at(A,(r,I),-1/dj)
    A[:,n]=1
    c=np.zeros(n+1); c[n]=-1
    res=linprog(c,A_ub=A,b_ub=np.zeros(R),bounds=[(-bound,bound)]*n+[(None,1)],method='highs')
    return res.x[:n],res.x[n]

def run(word,n,seed=0,mu=1e-2,noise=0.0,verbose=True):
    ok,local=check(word,n); assert ok
    I,J,K=constraints(local)
    rng=np.random.default_rng(seed)
    m,b=init(word,n,rng,noise=noise)
    z=np.concatenate([m,b])
    best=None
    for mu_ in [mu, mu/3, mu/10]:
        res=minimize(loss,z,args=(n,I,J,K,mu_),jac=True,method='L-BFGS-B',options={'maxiter':20000,'maxfun':40000})
        z=res.x
        mg=margin(z[:n],z[n:],I,J,K)
        nviol=int(np.sum((xs(z[:n],z[n:],I,K)-xs(z[:n],z[n:],I,J))<=0))
        if verbose: print(f'mu={mu_:.1e} loss={res.fun:.3e} margin={mg:.3e} violations={nviol}/{len(I)}',flush=True)
        if nviol==0: break
    m=z[:n]; b2,delta=lp_b(m,I,J,K)
    if verbose: print('LP delta',delta)
    return z[:n],z[n:],b2,delta,nviol

if __name__=='__main__':
    n=int(sys.argv[1]); f=sys.argv[2]; idx=int(sys.argv[3]) if len(sys.argv)>3 else 0
    lines=open(f).read().splitlines()
    w=parse_line(lines[idx])
    t=time.time(); out=run(w,n); print('time',time.time()-t)
