from __future__ import division

import time
import filter
import derivative_estimator
import realtime_tremor
import numpy as np

REAL_W_MM = 48.24
REAL_H_MM = 80.4

class TrackerObject(object):
        def __init__(self, sg_taps):
            self.sg_taps = sg_taps
            self.reset()
            
        def update(self, dt, x, y):
            """Update the object with a new position"""
            # if object just reappeared, re-initialise everything first
            if self.stale:
                self.reset()            
            self.interpolator.add_packet(np.array([x, y]), dt)            
            self.last_ds = np.array(self.ds)
            self.active = True
            packets = self.interpolator.get_packets()            
            
            d_seq = []
            for p in packets:                            
                for axis, derivs in enumerate(self.diffs):
                    for deriv,df in enumerate(derivs):
                        self.ds[axis, deriv] = df.new_sample(p[axis])
                d_seq.append(np.array(self.ds))
                
            if packets:
                self.xyz = packets[-1] 
                self.true_xyz = np.array(packets[-1])
            self.d_seq = d_seq                                                         
            
        def stale_update(self, dt):
            """Tick, but no new samples"""
            self.update(dt, self.true_xy[0], self.true_xy[1])
            self.d_seq = []
            self.active=False
            
        def tick(self):
            pass
            
        def reset(self):
            """Reset the phase tracker state"""
            sr = 140.0
            self.interpolator = filter.TimeInterpolator(fs=sr)
            self.xy = [0, 0]
            self.true_xy=[0, 0]
            self.state = 0
            self.active = True
            
            self.diffs = [[realtime_tremor.FilterBuffer(b=derivative_estimator.sg_filter(self.sg_taps, i, order=3)) for i in range(4)] for j in range(2)]
            
            self.ds = np.zeros((2,4))
            self.last_ds = np.zeros((2,4))
            
            self.stale = False
            
        def set_stale(self):
            """Indicate the object should be reset on the next update"""
            self.stale = True
            self.target = 0
            self.active = False
            
        def get_position(self):
            """Get the current registered position"""
            return self.xyz

class Tracker(object):
    def __init__(self, w, h, sg_taps=15):
        self.xdim = w
        self.ydim = h 
        self.the_object = TrackerObject(sg_taps)
        self.sg_taps = sg_taps
        self.last_object = time.clock()
        
    def start(self):
        self.sd.start()
        
    def stop(self):
        self.sd.close()        
        
    def update(self, pos):         
        rawobject = pos
        
        dt = time.clock() - self.last_object
        self.last_object = time.clock()
        
        self.the_object.state = True
        x = rawobject[0] / self.xdim
        y = rawobject[1] / self.ydim
        self.the_object.update(dt, x, y)

        self.the_object.tick()
