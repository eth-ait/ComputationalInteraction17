import math, random

def msize(a):
    return (len(a), len(a[0]))
    
def vpromote(a):
    try:
        x = iter(a[0])
    except:
        return [a]
    return a
        
    
# def mmul(a,b):
    # asize = msize(vpromote(a))
    # bsize = msize(vpromote(b))
    # if asize[1]!=bsize[0]:
        # raise Exception("Matrices not of same size.")
    
   
def vzeros(n):
    return [0 for i in range(n)]
    
def vones(n):
    return [1 for i in range(n)]
    
def vrandom(n, generator=random.random):
    return [generator() for i in range(n)]

def vrandom_uniform(n, start=0, end=1):
    return [random.randrange(start,end) for i in range(n)]
    
def vrandom_gaussian(n, mean=0, std=1):
    return [random.gauss(mean,std) for i in range(n)]
    
def vsum(a):
    return sum(a)
       
def voperator(a, op):
    return [op(x) for x in a]
        
def vaverage(a,b):
    return [(a[i]+b[i])/2 for i in range(len(a))]

def vadd(a,b):
    return [a[i]+b[i] for i in range(len(a))]

def vsub(a,b):
    return [b[i]-a[i] for i in range(len(a))]
    
def vscale(v, a):
    return [x*a for x in v]
    
def vector_split(segment,t):
    return [vscale(vadd(segment[i],segment[i+1]), t) for i in range(len(segment)-1)]
    
def vdistance(a,b):
    return math.sqrt(sum([(a[i]-b[i])*(a[i]-b[i]) for i in range(len(a))]))

def vlength(a):
    return math.sqrt(sum([(a[i])*(a[i]) for i in range(len(a))]))
    
def vnormalize(a):
    l = vlength(a)
    if l>0:
        return [x/l for x in a]
    else:
        return [0 for x in a]
    
def vdot(a, b):
    return sum([a[i]*b[i] for i in range(len(a))])
    
def vdotproduct(a, b):
    return vdot(vnormalize(a),vnormalize(b))
        
def vnegate(a):
    return [-x for x in a]
    
def vcross3(a, b):    
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    

    