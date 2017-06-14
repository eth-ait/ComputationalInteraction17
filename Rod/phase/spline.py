import math, numpy


class CardinalSpline(object):
    """Represent a spline going through a series of points. Evaluable
    at any (fractional) point from 0...len(pts)"""
    
    def __init__(self, pts, tension = -0.5, continuity=0.0, bias=0.0):
        """Create a new spline. Default is with 0.5 tension (Catmull-Rom)"""
        self.pts = pts
        self.tension = tension
        self.continuity = continuity
        self.bias = bias
                
    def __call__(self, t):
        """Evaluate the spline at t (in range 0...len(pts)), floating point"""
        p0 = int(math.floor(t))
        p1 = p0+1
        s = t-p0 # fractional part
        
        # clip range
        if p0<0: 
            p0 = 0
        if p1>=len(self.pts):
            p1 = len(self.pts)-1
        
        # compute basis function
        s3 = s**3
        s2 = s**2
        
        h1 = 2*s3 -3 * s2 + 1
        h2 = -2*s3 + 3*s2
        h3  = s3 - 2*s2 + s
        h4 = s3 - s2
        
        # compute tangent vectors
        pm = p0-1
        pp = p1+1
        
        
        
        p = self.pts
        # 0 at ends
        if pm<0:
            t1x,t1y = 0,0
        else:
            shape1 = (1-self.tension)*(1-self.continuity)*(1+self.bias)*0.5
            shape2 = (1-self.tension)*(1+self.continuity)*(1-self.bias)*0.5
            
            t1x = shape1 * (p[p0][0] - p[pm][0]) + shape2 * (p[p1][0] - p[p0][0])
            t1y = shape1 * (p[p0][1] - p[pm][1]) + shape2 * (p[p1][1] - p[p0][1])
                
        if pp>=len(self.pts):
            t2x,t2y = 0,0
        else:                
            shape3 = (1-self.tension)*(1+self.continuity)*(1+self.bias)*0.5
            shape4 = (1-self.tension)*(1-self.continuity)*(1-self.bias)*0.5
            
            t2x = shape3 * (p[p1][0] - p[p0][0]) + shape4 * (p[pp][0] - p[p1][0])
            t2y = shape3 * (p[p1][1] - p[p0][1]) + shape4 * (p[pp][1] - p[p1][1])
            
                    
        # interpolate points
        px = p[p0][0] * h1 + p[p1][0]* h2 + t1x*h3 + t2x*h4
        py = p[p0][1] * h1 + p[p1][1]* h2 + t1y*h3 + t2y*h4
        
        return (px, py)
        
            
        
    def __len__(self):
        return len(self.pts)
    

