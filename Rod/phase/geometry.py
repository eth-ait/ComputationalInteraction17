import math
from vector import *

def to_degrees(x):
    return (x/math.pi) * 180.0

def to_radians(x):
    return (x/180.0)*math.pi
    

def inside_triangle(pt, tri):
    v0 = vsub(tri[2],tri[0])
    v1 = vsub(tri[1],tri[0])
    v2 = vsub(pt,tri[0])
    dot00 = vdot(v0, v0)
    dot01 = vdot(v0, v1)
    dot02 = vdot(v0, v2)
    dot11 = vdot(v1, v1)
    dot12 = vdot(v1, v2)
    
    invDenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * invDenom
    v = (dot00 * dot12 - dot01 * dot02) * invDenom
    return (u > 0) and (v > 0) and (u + v < 1)
    
    

    

def get_normal(start, end, width):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    
    av = ((start[0]+end[0])/2,(start[1]+end[1])/2)
    m = math.sqrt(dx*dx+dy*dy)
    if m>0:
            perp = (-dy/m,dx/m)                                    
            pt = []                                           
            pt.append((end[0]+perp[0]*width, end[1]+perp[1]*width))                
            pt.append((start[0]+perp[0]*width, start[1]+perp[1]*width))     
            pt.append((av[0]+perp[0]*width, av[1]+perp[1]*width))     
            return pt
    return None
        

def normal(start, end):
    dx = start[0] - end[0]
    dy = start[1] - end[1]    
    av = ((start[0]+end[0])/2,(start[1]+end[1])/2)
    m = math.sqrt(dx*dx+dy*dy)
    if m>0:
            perp = (-dy/m,dx/m)                                    
            return perp
    return None

         
def length(start, end):
    return math.sqrt((start[0]-end[0])*(start[0]-end[0])+(start[1]-end[1])*(start[1]-end[1]))
    
    
    
def dot(v1,v2):
    return (v1[0]*v2[0],  v1[1]*v2[1])
    
def normalize(v):
    m = length((0,0),v)
    return (v[0]/m, v[1]/m)
    
    
def sub(a,b):
    return (b[0]-a[0], b[1]-a[1])
    
def add(a,b):
    return (a[0]+b[0], a[1]+b[1])
    
def mul(v, a):
    return (v[0]*a, v[1]*a)

# no length means double length
def extend(start, end, l=None):
    if l==None:
        l = length(start, end)        
    vec = add(mul(normalize(sub(start, end)), l), end)
    return vec
    
    
    
def fix_angle(a):
        while a>math.pi:
            a = a - math.pi * 2
        while a<-math.pi:
            a = a + math.pi * 2
        return a
            
        
def shortest_angle(a1, a2):
        dif = a2-a1                    
        return fix_angle(dif)
    
# interesection point of two lines
def full_line_intersect(p1, p2, p3, p4):
    denom = (p4[1]-p3[1])*(p2[0]-p1[0]) - (p4[0]-p3[0])*(p2[1]-p1[1])        
    if denom==0:
        return []
        
    ua_nom =(p4[0]-p3[0])*(p1[1]-p3[1]) - (p4[1]-p3[1])*(p1[0]-p3[0])
    ub_nom =(p2[0]-p1[0])*(p1[1]-p3[1]) - (p2[1]-p1[1])*(p1[0]-p3[0])
    
    #return none if coincident
    if ua_nom == 0:            
        return []
    if ub_nom == 0:
        return []
    
    
    ua = ua_nom / denom
    ub = ub_nom / denom
    
    
    x = p1[0]+ua*(p2[0]-p1[0])
    y = p1[1]+ua*(p2[1]-p1[1])
    return [(x,y)]
    

# line circle intersection (points are line p1->p2, circle centered p3, p4 on radius)  
def line_circle_intersect(p1, p2, p3, p4):
    r = sqrt((p3[0]-p4[0])*(p3[0]-p4[0])+(p3[1]-p4[1])*(p3[1]-p4[1]))
    
    a = (p2[0]-p1[0])*(p2[0]-p1[0])+(p2[1]-p1[1])*(p2[1]-p1[1])
    b = 2 * ((p2[0]-p1[0])*(p1[0]-p3[0])+(p2[1]-p1[1])*(p1[1]-p3[1]))
    c = p3[0]*p3[0] + p3[1]*p3[1] + p1[0]*p1[0]+p1[1]*p1[1] - 2 * (p3[0]*p1[0]+p3[1]*p1[1]) - r*r
    det = b*b-4*a*c
    if det<0:
        return []
        
    if det==0:
        u = -b/(2*a)
        x = p1[0]+u*(p2[0]-p1[0])
        y = p1[1]+u*(p2[1]-p1[1])
        return [self.point(x,y)]
        
    if det>0:
          u = (-b + sqrt(b*b - 4*a*c )) / (2*a)
          x1 = p1[0]+u*(p2[0]-p1[0])
          y1 = p1[1]+u*(p2[1]-p1[1])
          u = (-b - sqrt(b*b - 4*a*c )) / (2*a);
          x2 = p1[0]+u*(p2[0]-p1[0])
          y2 = p1[1]+u*(p2[1]-p1[1])
          return [(x1,y1), (x2,y2)]
                                  

# return intersection of circles
def circle_circle_intersect(p1, p2, p3, p4):
        r0 = sqrt((p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1]))
        r1 = sqrt((p3[0]-p4[0])*(p3[0]-p4[0]) + (p3[1]-p4[1])*(p3[1]-p4[1]))
        d = sqrt((p1[0]-p3[0])*(p1[0]-p3[0])+(p1[1]-p3[1])*(p1[1]-p3[1]))
        
        if d>r0+r1:
            return []
            
        if d<r0-r1:
            return []
            
        a = (r0*r0 - r1*r1 + d*d) / (2*d)
        x2 = p1[0] + (p3[0]-p1[0])*(a/d)
        y2 = p1[1] + (p3[1]-p1[1])*(a/d)
        
        
        h = sqrt((r0*r0) - (a*a))
        rx = -(p3[1]-p1[1]) * (h/d)
        ry = (p3[0]-p1[0]) * (h/d)
        
        xa = x2+rx
        xb = x2-rx
        ya = y2+ry
        yb = y2-ry
        
        if xa==xb and ya==yb:
            return [(xa,ya)]
        else:
            return[(xa,ya), (xb,yb)]

    
# determine if two line _segments_ intersect
def line_intersect(a1,a2,b1,b2):
    x11,y11 = float(a1[0]), float(a1[1])
    x12, y12 = float(a2[0]), float(a2[1])
    x21, y21 = float(b1[0]), float(b1[1])
    x22, y22 = float(b2[0]), float(b2[1])

    num_s = ((x22 - x21)*(y21 - y11) - (x21 - x11)*(y22 - y21))
    den_s =((x22 - x21)*(y12 - y11) - (x12 - x11)*(y22 - y21)) 
    
    
    num_t = ((x12 - x11)*(y21 - y11) - (x21 - x11)*(y12 - y11))
    den_t = ((x22 - x21)*(y12 - y11) - (x12 - x11)*(y22 - y21))    
    
    if den_s>0:
        s = num_s / den_s
    else:
        s = -1
        
    if den_t>0:
        t =  num_t / den_t
    else:
        t = -1
    
    return s>=0 and s<=1 and t>=0 and t<=1
    
 
# determine if a point is inside a polygon by
# testing parity of intersection count of a vertical ray
# with the polygon edges
def inside_polygon(pt, pts):

    inside = False
    j = len(pts)-1
    for i in range(len(pts)):
        if (pts[i][1]<pt[1] and pts[j][1]>=pt[1]) or (pts[j][1]<pt[1] and pts[i][1]>=pt[1]):
            a =pts[i][0]
            b = pt[1]-pts[i][1]
            c = float((pts[j][1]-pts[i][1]))            
            d = float((pts[j][0]-pts[i][0]))
            if a+(b/c)*d<pt[0]:
                inside = not inside
        j = i
    return inside
                
        
    
    test_line = [pt, vadd(pt, (1e6,0))]
    intersections = 0
    for i in range(len(pts)-1):
        line = [pts[i], pts[i+1]]
        if line_intersect(test_line[0], test_line[1], line[0], line[1]):
            intersections = intersections + 1
        
    return (intersections%2)==1
    
    
# determine if there is a line of sight between
# pt1 and pt2, with the given polygons
# optionally fail if the points are further apart than max_distance
def line_of_sight(pt1, pt2, polys, max_distance=None):
    if max_distance!=None:
        if vdistance(pt1,pt2)>max_distance:
            return False
    for poly in polys:
        for i in range(len(poly)-1):
            a = poly[i]
            b = poly[i+1]
            if line_intersect(pt1, pt2, a, b):
                return False
            if line_intersect(pt1, pt2, b, a):
                return False
    return True
                

 
   # evaluate a bezier curve defined by a,b,c,d at point t (0--1).
def bezier_evaluate(a,b,c,d,t):
        x0,y0 = a[0], a[1]
        x1,y1 = b[0], b[1]
        x2,y2 = c[0], c[1]
        x3,y3 = d[0], d[1]

        cx = 3 * (x1 - x0)
        bx = 3 * (x2 - x1) - cx
        ax = x3 - x0 - cx - bx

        cy = 3 * (y1 - y0)
        by = 3 * (y2 - y1) - cy
        ay = y3 - y0 - cy - by
        
        xt = ax*t*t*t + bx*t*t + cx*t + x0
        yt = ay*t*t*t + by*t*t + cy*t + y0
        
        return (xt,yt)

             
if __name__=="__main__":
     
    print inside_triangle((0,0), [(0,200), (-100, -100), (100, -100)])
 