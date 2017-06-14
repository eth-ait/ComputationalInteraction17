import numpy as np
#import pylab
import scipy.signal as sig
import scipy.interpolate as interpolate

#sg coefficient computation
def savitzky_golay(window_size=None,order=2):
    if window_size is None:
        window_size = order + 2

    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window size is too small for the polynomial")

    # A second order polynomial has 3 coefficients
    order_range = range(order+1)
    half_window = (window_size-1)//2
    B = np.mat(
        [ [k**i for i in order_range] for k in range(-half_window, half_window+1)] )


    M = np.linalg.pinv(B)
    return M
    

# savitzky-golay polynomial estimator, with optional derivatives
def sg_filter(size, deriv=0, order=4):
    if size%2==0:
        print "Size for Savitzky-Golay must be odd. Adjusting..."
        size = size + 1            
    if order<deriv+1:
        order = deriv+1
    
    sgolay = savitzky_golay(size, order)
    diff = np.ravel(sgolay[deriv, :]) 
    return diff
    

    
    
def get_velocity(t, x, sr=60, filter_len=15):
    """Return the smoothed interpolated trajectory, plus its first and second derivative"""
    #interpolator = interpolate.interp1d(t, x, kind='cubic', fill_value=x[0])
    ts = np.arange(np.min(t), np.max(t), 1.0/sr)
    #x_regular = interpolator(ts)
    x_regular = interpolate.griddata(t, x, ts, method='linear')
    f0 = sg_filter(filter_len, 0, 3)
    f1 = sg_filter(filter_len, 1, 3)
    f2 = sg_filter(filter_len, 2, 3)    
    
    x_pad = np.hstack((np.array([x[0]]*filter_len), x_regular))
    x_0 = sig.lfilter(f0, 1, x_pad)[filter_len:]
    x_1 = sig.lfilter(f1, 1, x_pad)[filter_len:]
    x_2 = sig.lfilter(f2, 1, x_pad)[filter_len:]       
    return ts, x_regular, x_0, x_1, x_2
    
