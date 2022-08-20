# utility functions to generate
# the jupyter notebooks here

import ness
import numpy as np
import matplotlib.pyplot as plt
from lowpass import LOWPASS
from zverev import ZVEREV
from coupled import COUPLED

def timespantofreqspan(timespan, points):
    df = 1 / (2 * timespan)
    freqspan = (points - 1) * df
    return freqspan


def gtobandpasstd(f, g, beta=None, dc=None):
    dc = -1 if dc is None else dc
    beta = 14 if beta is None else beta
    g = np.concatenate(([dc], g)) # at dc filter is open so no return loss
    n = len(g)
    window = np.kaiser(n, beta)  # beta at 14 gives nicest peaks and dips
    td = abs(np.fft.ifft(g * window, n * 2)[:n])
    taxis = np.linspace(0, 1 / (f[1] - f[0]) / 2, n)
    return taxis, td


def draw(qk, bw, fo, qu=np.inf, re=1):
    n = len(qk) - 1
    f = np.linspace(fo - 2 * bw, fo + 2 * bw, 10000)
    fig = plt.figure(figsize=(16,3))
    a1 = fig.add_subplot(131)
    plt.xlabel('Frequency (GHz) vs Magnitude (dB)')
    plt.ylabel('Qu={:.0f}'.format(qu))
    a2 = fig.add_subplot(132)
    plt.xlabel('Frequency (GHz) vs Group Delay (ns)')
    a3 = fig.add_subplot(133)
    plt.xlabel('Time (ns) vs Magnitude (dB)')
    a1.set_ylim(-40, 5)
    
    ######### reflection #############
    fn = ness.fn_nodal_reflection(qk, bw, fo, re=re)
    ma = abs(fn(f, qu))
    #print(fn(1e-99, qu))
    ma = 20 * np.log10(ma)
    a1.plot(f/1e9, ma, label="S11")

    # return loss
    a = (np.diff(np.sign(np.diff(ma))) < 0).nonzero()[0] + 1    # max
    a1.plot(f[a]/1e9, ma[a], "o", color='b')

    # time domain
    points = 401
    freqspan = timespantofreqspan(26e-9 * n, points)
    faxis = np.linspace(fo - freqspan / 2, fo + freqspan / 2, points)
    
    gm = fn(faxis, qu)
    taxis, td = gtobandpasstd(faxis, gm)
    td = np.log(td)
    a3.plot(taxis * 1e9, td, label="S11")
    
    ######## transmission ##############
    fn = ness.fn_nodal_transmission(qk, bw, fo, re=re)
    td = ness.groupdelay(fn, f, qu)
    ma = abs(fn(f, qu))
    ma = 20 * np.log10(ma)
    a1.plot(f / 1e9, ma, label="S21", color='m')
    a2.plot(f / 1e9, td * 1e9, label="S21", color='m')
    
    # bandwidth
    db = ma - np.max(ma)
    a = (np.diff(np.sign(np.diff(abs(db + 3.01)))) > 0).nonzero()[0] + 1   # min
    a = [a[-1], a[0]]
    a1.plot(f[a] / 1e9, ma[a], "o", color='m')       
    
    # delay bandwidth
    a = np.diff(np.sign(np.diff(td))).nonzero()[0] + 1
    a = [a[-1], a[0]]
    a2.plot(f[a] / 1e9, td[a] * 1e9, "o", color='m')
        
    print('-----------------------------------------')
    bwdb = ness.nodal_bandwidth(qk, bw, fo, qu) # step
    print('3dB Bandwidth       = {:15.5f} MHz'.format(bwdb / 1e6))
    bwtd = ness.nodal_delay_bandwidth(qk, bw, fo, qu) # step
    print('Delay Bandwidth     = {:15.5f} MHz'.format(bwtd / 1e6))
    td = ness.nodal_delay_transmission(qk, bw, fo, qu)
    print('Transmission Delay  = {:15.5f} ns'.format(td * 1e9))
    rl = ness.nodal_returnloss(qk, bw, fo, qu) # step
    print('Minimum Return Loss = {:15.3f} dB'.format(rl))
    il = ness.nodal_insertionloss(qk, bw, fo, qu) # step
    print('Insertion Loss      = {:15.3f} dB'.format(il))
    print(qk)
    a1.legend()
    a2.legend()
    a3.legend()
    plt.show()
