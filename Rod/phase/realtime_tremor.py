import filter
import scipy.signal
import numpy as np
#import pylab



def bandpass_fir(f1, f2, sr, n=81):
    
    #Lowpass filter
    a = scipy.signal.firwin(n, cutoff = f1/sr, window = 'blackmanharris')
    #Highpass filter with spectral inversion
    b = - scipy.signal.firwin(n, cutoff = f2/sr, window = 'blackmanharris'); b[n/2] = b[n/2] + 1
    #Combine into a bandpass filter
    d = - (a+b); d[n/2] = d[n/2] + 1
    return d

    

def mfreqz(b,a=1,sr=60):
    """Plot the frequency response of a FIR or IIR filter"""
    w,h = scipy.signal.freqz(b,a)
    h_dB = 20 * np.log10 (np.abs(h))
    pylab.subplot(211)
    pylab.plot(w/max(w)*sr,h_dB)
    pylab.ylim(-150, 5)
    pylab.ylabel('Magnitude (db)')
    pylab.xlabel(r'Frequency (Hz)')
    pylab.title(r'Frequency response')
    pylab.subplot(212)
    h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)))
    pylab.plot(w/max(w)*sr,h_Phase)
    pylab.ylabel('Phase (radians)')
    pylab.xlabel(r'Frequency (Hz)')
    pylab.title(r'Phase response')
    pylab.subplots_adjust(hspace=0.5)  
    
    
def create_filters(band=(8,24), sr=120.0, taps=31, hilbert_taps=31):
    """Create the bandpass and Hilbert transform filters"""
    
    b = bandpass_fir(band[0], band[1], sr, taps)
    h = scipy.signal.remez(hilbert_taps, [0.0, 0.5], [1], type='hilbert', maxiter=512)
    return b,h
    
class FilterBuffer:
    def __init__(self, b):
        """Apply an FIR filter to an incoming signal, using
        a contiguous ring buffer"""
        self.b = b[::-1]
        self.len = len(b)
        self.buffer = np.zeros(self.len*2)
        self.ptr = 0
        self.out = 0
        
    def new_sample(self, x):                
        """Add a new sample to the ring buffer and filter it;
        returns the new filter output"""
        self.buffer[self.ptr] = x
        self.buffer[self.ptr+self.len] = x        
        self.ptr = (self.ptr+1) % self.len
        out = np.sum(self.b * self.buffer[self.ptr:self.ptr+self.len])
        self.out = out
        return out
        
    def get_buffer(self):
        """Return the (unfiltered) samples in the delay buffer"""
        return self.buffer[self.ptr:self.ptr+self.len]
        

class SurrogateFilterBuffer:
    def __init__(self, b):
        """Apply an FIR filter to an incoming signal, using
        a contiguous ring buffer, but shuffling elements randomly
        to eliminate time structure."""
        self.b = b[::-1]
        
        # generate randomized permutations of the filter coefficients
        self.bs = [np.random.permutation(b) for i in range(100)]
        
        self.len = len(b)
        self.buffer = np.zeros(self.len*2)
        self.ptr = 0
        self.out = 0
        
    def new_sample(self, x):                
        """Add a new sample to the ring buffer and filter it;
        returns the new filter output"""
        self.buffer[self.ptr] = x
        self.buffer[self.ptr+self.len] = x        
        self.ptr = (self.ptr+1) % self.len        
        # randomly choose a permutation
        b = self.bs[np.random.randint(0,len(self.bs))]  
        out = np.sum(b * self.buffer[self.ptr:self.ptr+self.len])
        self.out = out
        return out
        
    
        
class DelayBuffer:
    def __init__(self, delay):
        """Delay a signal by an integer number of samples"""
        self.len = delay
        self.buffer = np.zeros(self.len*2)
        self.ptr = 0
        
    def new_sample(self, x):                
        """Insert a new sample into the delay buffer, and retutn the 
        sample inserted len steps ago."""
        self.buffer[self.ptr] = x
        self.buffer[self.ptr+self.len] = x        
        self.ptr = (self.ptr+1) % self.len
        return self.buffer[self.ptr]
                
    def get_buffer(self):
        """Return the delayed samples (in order)"""
        return self.buffer[self.ptr:self.ptr+self.len]
    


class PLVMonitor:
    def __init__(self, n, decay = 0.99):
        """Create an object to monitor phase locking, using 
        a PLV leaky integrator"""
        self.phase_locks = np.zeros((n,n), dtype=np.complex)
        self.phases = np.zeros((n,1))
        self.decay = decay        
        
    def new_phase(self,i,phi):
        """Set the phase of phasor i"""
        self.phases[i,0] = phi
        
    def update(self):
        """Update the monitor (should be called once a sample)"""        
        self.phase_locks += (np.exp(1j*(self.phases-self.phases.transpose())))
        self.phase_locks *= self.decay
        
        
        
    
class PhaseTransformer:
    def __init__(self, taps=31, band=(8,24), sr=120.0, surrogate=False):    
        """Phase transform a signal, using a bandpass filter and a Hilbert
        transform. sr gives the sampling rate; taps gives the FIR filter length (for both the
        BPF filter and the Hilbert transformer); band=(low,high) gives the passband of the filter in Hz"""
        self.b, self.h = create_filters(band=band, taps=taps, hilbert_taps=taps, sr=sr)
        
        if surrogate:   
            # use shuffling filter if required
            self.bandpass = SurrogateFilterBuffer(self.b)                
        else:
            self.bandpass = FilterBuffer(self.b)                
        self.hilbert = FilterBuffer(self.h)
        self.delay = DelayBuffer(len(self.h)/2)
        self.unwrap= filter.Unwrap()
        

        
    def new_sample(self, x):
        """Filter a new sample, and return the new unwrapped phase angle"""
        f = self.bandpass.new_sample(x)
        h = self.hilbert.new_sample(f)
        # apply compensating delay
        d = self.delay.new_sample(f)
        phi = np.arctan2(h,d)
        u_phi = self.unwrap.new_sample(phi)        
        return u_phi, phi
        
if __name__=='__main__':
    # p = PhaseTransformer(taps=51)    
    # t = [p.new_sample(np.sin(i/6.0))[1] for i in range(2000)]
    
    # pylab.plot(t)           
    
    
    # t1 = [p.new_sample(np.sin(i/6.0))[0] for i in range(2000)]
    # t2 = [p.new_sample(np.sin(i/13.0))[0] for i in range(2000)]
    
    # plv = PLVMonitor(2)
    # for i in range(len(t1)):
        # plv.new_phase(0,t1[i])
        # plv.new_phase(1,t2[i])
        # plv.update()
    # print plv.phase_locks
    SG_TAPS = 61
    
    import derivative_estimator, pylab
    
    b0 = derivative_estimator.sg_filter(SG_TAPS, 0)
    b1 = derivative_estimator.sg_filter(SG_TAPS, 1)
    b2 = derivative_estimator.sg_filter(SG_TAPS, 2)
    b3 = derivative_estimator.sg_filter(SG_TAPS, 3)
    
    t = np.arange(0,30,0.01)
    f = np.abs(np.sin(t))**20
    #pylab.plot(t,f)
    
    pylab.plot(t,scipy.signal.lfilter(b0,1,f))
    pylab.plot(t,scipy.signal.lfilter(b1,1, f*10))
    pylab.plot(t,scipy.signal.lfilter(b2, 1, f*100))
    pylab.plot(t,scipy.signal.lfilter(b3, 1, f*5000))
    

        
    pylab.show()
