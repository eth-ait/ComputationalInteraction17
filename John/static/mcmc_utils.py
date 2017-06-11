import numpy as np
# plot the Box plot of the log-probability (very slow)
def logp_trace(mcmc, model, n_samples=1000):
    db = mcmc
    logp = np.empty(n_samples, np.double)

    #loop over all samples
    for i_sample in xrange(n_samples):
        #set the value of all stochastic to their 'i_sample' value
        for stochastic in model.stochastics:
            try:
                value = db.trace(stochastic.__name__)[i_sample]
                stochastic.value = value

            except KeyError:
                print "No trace available for %s. " % stochastic.__name__

        #get logp
        logp[i_sample] = model.logp
    return logp
