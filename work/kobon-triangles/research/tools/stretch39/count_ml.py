import sys, json
from fractions import Fraction
sys.path.insert(0,'/Users/rohith/My/WORK/Projects/RSI_Math/work/kobon-triangles/research/tools')
from autolab_hill_eval import count_triangles, _normalize
def to_hill(m,b,den=10**12):
    L=[]
    for mi,bi in zip(m,b):
        fm=Fraction(mi).limit_denominator(den); fb=Fraction(bi).limit_denominator(den)
        # y = fm x + fb -> fm x - y + fb = 0 ; clear denominators
        q=fm.denominator*fb.denominator//__import__('math').gcd(fm.denominator,fb.denominator)
        L.append([int(fm*q), -q, int(fb*q)])
    return L
def count_ml(m,b,den=10**12):
    L=[_normalize(tuple(l)) for l in to_hill(m,b,den)]
    return len(count_triangles(L)), L
