import filter
import derivative_estimator
import realtime_tremor
from sensation.sensation import *
import numpy as np

# threaded version

class Finger:
        def __init__(self, sg_taps):
            self.sg_taps = sg_taps
            self.reset()
            
        def update(self, dt, x, y, z):
            """Update the finger with a new x,y,z position"""
            # if finger just reappeared, re-initialise everything first
            if self.stale:
                self.reset()            
            self.interpolator.add_packet(np.array([x,y,z]), dt)            
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
            self.update(dt, self.true_xyz[0], self.true_xyz[1], self.true_xyz[2])
            self.d_seq = []
            self.active=False
            
        def tick(self):
            pass
            
        def reset(self):
            """Reset the phase tracker state"""
            sr = 140.0
            self.interpolator = filter.TimeInterpolator(fs=sr)
            self.xyz = [0,0,0]
            self.true_xyz=[0,0,0]
            self.state = 0
            self.active = True
            
            self.diffs = [[realtime_tremor.FilterBuffer(b=derivative_estimator.sg_filter(self.sg_taps, i, order=3)) for i in range(4)] for j in range(3)]
            
            self.ds = np.zeros((3,4))
            self.last_ds = np.zeros((3,4))
            
            self.stale = False
            
        def set_stale(self):
            """Indicate the finger should be reset on the next update"""
            self.stale = True
            self.target = 0
            self.active = False
            
        def get_position(self):
            """Get the current registered position"""
            return self.xyz


W = 480
H = 800

REAL_W_MM = 48.24
REAL_H_MM = 80.4
            
            
class FingerTracker:
    def __init__(self, port, sg_taps):
        self.sd = Sensation(port, False) 
        self.xdim = REAL_W_MM * 100.0 # 0.01mm units
        self.ydim = REAL_H_MM * 100.0 
        self.fingers = {}
        self.sg_taps = sg_taps
        self.last_finger = time.clock()
        
    def start(self):
        self.sd.start()
        
    def stop(self):
        self.sd.close()        
        
    def update(self, pos=None):         
        finger_positions = {}
        
        if pos:
            rawfingers = [[1, pos[0]*self.xdim, pos[1]*self.ydim, pos[2]*2500, 1, 1, 1, 1]]
        else:
            rawfingers = self.sd.fingers   
        
        dt = time.clock() - self.last_finger
        self.last_finger = time.clock()
        
        
        for i in range(len(rawfingers)):
            # create fingers
            if not self.fingers.has_key(i):
                    self.fingers[i] = Finger(self.sg_taps)
                                                    
            if rawfingers[i]:
                self.fingers[i].state = rawfingers[i][0]
                if rawfingers[i][0] != 0: 
                    x = rawfingers[i][1] / self.xdim
                    y = rawfingers[i][2] / self.ydim
                    z = rawfingers[i][3] # note unscaled value here
                    
                    if z>32768:
                        z = - (65536-z)
                    z = (z+105) / 2500.0
                    # tuple: (x, y, z, state, x-slope, y-slope)
                    finger_positions[i] = (x, y, z, rawfingers[i][0], rawfingers[i][5], rawfingers[i][6])                                        
                    self.fingers[i].update(dt, x,y,z)
                    
                else:
                    # clear interpolator
                    #self.fingers[i].set_stale()                    
                    self.fingers[i].stale_update(dt)
            else:
                self.fingers[i].stale_update(dt)
            self.fingers[i].tick()
        
        self.finger_positions = finger_positions
        
