import numpy

class Fader:
    """Simulate a system which fades in and out exponentially"""
    def __init__(self, in_time, out_time, snap=0.8):
        """Create an object which fades in in in_time and out in out_time.
        Snap adjusts the curvature near the transition point. 0.63 = snappy, 0.8 = slow, 0.5 = jumpy"""
        self.snap = snap
        self.in_time = in_time
        self.out_time = out_time
        self.reset()
        
    def get(self):
        """Return the scaled state of the fader"""
        return (self.state / self.snap) * 0.9
        
        
    def reset(self):
        """Reset the fader back to starting fade in"""
        self.state = 0.0
        self.fading_in = True
        
    def update(self, dt):
        """Update the state of the fader. 
        dt should be the time since the last update in (fractional) seconds"""
        # compute new coefficeints
                
        in_coeff = numpy.exp(-dt/(self.in_time))
        out_coeff = numpy.exp(-dt/(self.out_time))        
        if self.fading_in:
            # fade in
            if self.state < self.snap:
                self.state = in_coeff * self.state + (1-in_coeff) * 1.0
            else:
                # start fading out
                self.state = self.snap 
                self.fading_in = False
        else:
            # fade out
            self.state = out_coeff * self.state 
        
        
            
    