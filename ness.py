
import numpy as np
import sympy as sy


# cohn approximation of insertion loss
def insertion_loss(g, bw, fo, qu):
    db = 4.343 * fo / (qu * bw) * sum(g[1:-1])
    return db


### for plotting

# return function fn(f, qu) which calculates the S11 group delay at f
# for lossy bandpass filters shorted at resonator n
def fn_groupdelay_tdqu(g, bw, fo, n):
    f, w, wo, dw, wp, qu = sy.symbols("f w wo dw wp qu")
    xin = lowpass_xin(g, wp, n)
    WP = wo / dw * (w / wo - wo / w) - wo * sy.I / (qu * dw)
    phi = -2 * sy.atan(xin / g[0])
    GD = -sy.diff(WP, w) * sy.simplify(sy.diff(phi, wp)).subs(wp, WP)
    GD = GD.subs(dw, 2 * sy.pi * bw)  # sy.pi required
    GD = GD.subs(wo, 2 * np.pi * fo)  # np.pi required
    GD = GD.subs(w, 2 * np.pi * f)
    return sy.lambdify([ f, qu ], abs(GD), 'numpy')


# return function fn(f, qu) which calculates the Ness S11 values
# for lossy bandpass filters shorted at resonator n
def fn_groupdelay_maqu(g, bw, fo, n):
    f, w, wo, dw, wp, qu = sy.symbols("f w wo dw wp qu")
    xin = lowpass_xin(g, wp, n)
    WP = wo / dw * (w / wo - wo / w) - wo * sy.I / (qu * dw)
    xin = xin.subs(wp, WP)
    s11 = (xin * sy.I - g[0]) / (xin * sy.I + g[0])
    s11 = s11.subs(wo, 2 * sy.pi * fo)
    s11 = s11.subs(dw, 2 * sy.pi * bw)
    s11 = s11.subs(w, 2 * np.pi * f)
    return sy.lambdify([ f, qu ], s11, 'numpy')


#######################
# miscellaneous
#######################

def db(x):
    with np.errstate(divide='ignore'):
        return 20 * np.log10(abs(x))


# calculate group delay at f using fn(f,qu)
# (used by nodal_delay_transmission and nodal_delay_bandwidth)
def groupdelay(fn, f, qu):
    df = 1
    a = np.angle(fn(f - df / 2, qu))
    b = np.angle(fn(f + df / 2, qu))
    d = np.unwrap(np.array([a, b]).T)
    td = -np.diff(d).flatten() / (2 * np.pi * df)
    return td[0] if np.isscalar(f) else td


# denormalize qk coefficients
def denormalize_qk(qk, bw, fo):
    ql = fo / bw
    QK = np.array(qk) * ql
    QK[1:-1] = np.array(qk[1:-1]) / ql
    return QK


# calculate lowpass prototype g values from qk coefficients
def prototype_qk(qk, g0=1):
    g = np.zeros(len(qk)+1)
    g[0] = g0
    g[1] = qk[0] / g[0]
    for i in range(1, len(g)-2):
        g[i+1] = 1 / (qk[i]**2 * g[i])
    g[-1] = qk[-1] / g[-2]
    return g


# calculate qk coefficients from lowpass prototype g values
def coupling_g(g):
    g = np.array(g)
    qk = g[:-1] * g[1:]
    qk[1:-1] = 1 / np.sqrt(g[1:-2] * g[2:-1])
    return qk


def chebyshev(n, ripple):
    """
    From page 99 of Microwave Filters, Impedance-Maching 
    Networks, and Coupling Structures, by Matthaei, Young,
    and Jones
    """
    beta = np.log(1 / np.tanh(ripple / (40 / np.log(10))))
    gamma = np.sinh(beta / (2 * n))
    k = np.array([ n for n in range(1, n + 1) ])
    A = np.sin((2 * k - 1) * np.pi / (2 * n))
    B = gamma**2 + np.sin(k * np.pi / n)**2
    g = np.ones(n + 2)
    g[1] = 2 * A[0] / gamma
    for i in range(2, n + 1):
        g[i] = 4.0 * A[i-2] * A[i-1] / (B[i-2] * g[i-1])
    if n % 2 == 0:
        g[n+1] = 1 / np.tanh(beta / 4)**2
    return g


#######################
# time domain
#######################

# return the time domain of gamma values at frequencies f
def timedomain(f, gm):
    gm = np.concatenate(([0], gm))
    N = len(gm)
    window = np.kaiser(N, 14) # kaiser gives nicer peaks and dips
    td = np.fft.ifft(gm * window, N * 2 - 1) # ensure odd
    td = db(td[:N])
    df = f[1] - f[0]
    taxis = np.linspace(0, 1 / df / 2, N)
    return taxis, td


# calculate the frequency span needed for a given time domain period
def range_timedomain(fo, period, n):
    df = 1 / (2 * period)
    df = fo / np.ceil(fo / df)
    span = (n - 1) * df
    return np.linspace(fo - span / 2, fo + span / 2, n)


#######################
# nodal
#######################

# compute the components of a top-coupled nodal filter
def nodal_filter(qk, bw, fo):
    N = len(qk) - 1
    QL = fo / bw
    Q = np.array(qk[::N]) * QL
    K = np.array(qk[1:-1]) / QL

    # nodal resonators
    wo = 2 * np.pi * fo
    RE = 1
    L0 = RE / (wo * Q)
    L0 = np.concatenate((L0[0] * np.ones(N-1), L0[1:]))
    CM = 1 / (wo**2 * L0)

    # coupling capacitors
    Z = 1 / (wo * np.sqrt(CM[:-1] * CM[1:]))
    CK = K / (wo * Z)
    CK = np.insert(np.zeros(2), 1, CK)
    C0 = CM - CK[:-1] - CK[1:]
    return L0, C0, CK[1:-1]


# return a function fn(f, qu) for calculating the S11 of a nodal filter
def fn_nodal_reflection(qk, bw, fo, re=1):
    lp, cp, cs = nodal_filter(qk, bw, fo)
    f, w, qu = sy.symbols('f w qu')
    zin = re
    for i in reversed(range(len(lp))):
        zin = 1 / (sy.I * w * cp[i] + 
                   1 / (sy.I * w * lp[i]) +
                   1 / (w * lp[i] * qu) +
                   1 / zin
                  )
        if i > 0: zin += 1 / (sy.I * w * cs[i-1])           
    s11 = (zin - re) / (zin + re)
    s11 = s11.subs(w, 2 * np.pi * f)    
    return sy.lambdify([f, qu], s11, 'numpy')


# return a function fn(f, qu) for calculating the S21 of a nodal filter
def fn_nodal_transmission(qk, fo, bw, re=1):
    lp, cp, cs = nodal_filter(qk, fo, bw)
    f, w, qu = sy.symbols('f w qu')
    vin = 1
    zin = re
    n = len(lp) - 1
    for i in range(n):
        a = 1 / (sy.I * w * cp[i] + 
                 1 / (sy.I * w * lp[i]) +
                 1 / (w * lp[i] * qu)
                )
        vin = vin * a / (a + zin)
        zin = 1 / (1 / a + 1 / zin)
        zin += 1 / (sy.I * w * cs[i])
    a = 1 / (1 / re + 
             sy.I * w * cp[n] + 
             1 / (sy.I * w * lp[n]) +
             1 / (w * lp[i] * qu)
            )
    s21 = 2 * vin * a / (zin + a)
    s21 = s21.subs(w, 2 * np.pi * f)    
    return sy.lambdify([f, qu], s21, 'numpy')


# calculate the insertion loss of a filter at fo
def nodal_insertionloss(qk, bw, fo, qu):
    fn = fn_nodal_transmission(qk, bw, fo)
    return db(fn(fo, np.inf)) - db(fn(fo, qu))


# calculate the transmission group delay of a filter at fo
def nodal_delay_transmission(qk, bw, fo, qu):
    fn = fn_nodal_transmission(qk, bw, fo)
    return groupdelay(fn, fo, qu)


### approximations

# calculate the (approximate) minimum return loss of a filter
def nodal_returnloss(qk, bw, fo, qu, steps=1000):
    fn = fn_nodal_reflection(qk, bw, fo)
    f = np.linspace(fo - 2 * bw, fo + 2 * bw, steps)
    ma = -db(fn(f, qu))
    a = (np.diff(np.sign(np.diff(ma))) > 0).nonzero()[0] + 1
    return np.median(ma[a]) if a.size else -db(fn(fo, qu))


# approximate the group delay bandwidth of a filter
def nodal_delay_bandwidth(qk, bw, fo, qu, steps=1000):
    fn = fn_nodal_transmission(qk, bw, fo)
    ###
    f = np.linspace(fo - 2 * bw, fo + 2 * bw, steps)
    td = groupdelay(fn, f, qu)
    a = np.diff(np.sign(np.diff(td))).nonzero()[0] + 1
    f1 = f[a[0]]
    f2 = f[a[-1]]
    ###
    # from scipy.optimize import minimize
    # res = minimize(lambda x: -groupdelay(fn, x, qu), f1, method='Nelder-Mead')
    # f1 = res.x[0] if res.success else np.nan
    # res = minimize(lambda x: -groupdelay(fn, x, qu), f2, method='Nelder-Mead')
    # f2 = res.x[0] if res.success else np.nan
    return f2 - f1


# approximate the 3db bandwidth of a filter
def nodal_bandwidth(qk, bw, fo, qu, cutoff=3.0103, steps=1000):
    fn = fn_nodal_transmission(qk, bw, fo)
    f = np.linspace(fo - 2 * bw, fo + 2 * bw, steps)
    ma = db(fn(f, qu))
    mamax = np.max(ma)
    a = (np.diff(np.sign(np.diff(abs(mamax - ma - cutoff)))) > 0).nonzero()[0] + 1
    f1 = f[a[0]]
    f2 = f[a[-1]]
    ###
    # from scipy.optimize import minimize
    # res = minimize(lambda x: -db(fn(x, qu)), fo, method='Nelder-Mead')
    # mamax = -res.fun if res.success else np.nan
    # res = minimize(lambda x: abs(mamax - db(fn(x, qu)) - cutoff), f1, method='Nelder-Mead')
    # f1 = res.x[0] if res.success else np.nan
    # res = minimize(lambda x: abs(mamax - db(fn(x, qu)) - cutoff), f2, method='Nelder-Mead')
    # f2 = res.x[0] if res.success else np.nan
    return f2 - f1

#######################
# lossless groupdelay
#######################

# for a lossless bandpass filter, calculate Ness group delay values using g
def groupdelay_g(g, bw):
    dw = 2 * np.pi * bw
    td = [ 4 / dw * 
           sum(g[i%2+1:i:2]) * (g[0])**((-1)**i)
           for i in range(2, len(g)) ]
    return td


# for a lossless bandpass filter, calculate Ness group delay values using qk
def groupdelay_qk(qk, bw):
    qk = np.array(qk)
    QB = qk[0] / bw 
    KB = qk[1:-1] * bw
    TD = np.zeros(len(qk)+1)
    for i in range(2, len(TD)):
        TD[i] = TD[i-2] + 2 / np.pi * (
                QB * np.prod(KB[0:i-2:2]**2) / 
                np.prod(KB[1:i-2:2]**2))**((-1)**i)
    return TD[2:]


#######################
# lossy groupdelay
#######################

# calculate the Ness S11 values at fo for a filter with a given QU
def groupdelay_maqu(g, bw, fo, qu):
    w, wo, dw, wp = sy.symbols("w wo dw wp")
    ma = []
    for n in range(1, len(g)-1):
        xin = lowpass_xin(g, wp, n)
        WP = wo / dw * (w / wo - wo / w) - wo * sy.I / (qu * dw)
        xin = xin.subs(wp, WP)
        s11 = (xin * sy.I - g[0]) / (xin * sy.I + g[0])
        s11 = s11.subs(wo, 2 * sy.pi * fo)
        s11 = s11.subs(dw, 2 * sy.pi * bw)
        fn = sy.lambdify(w, s11, 'numpy')
        ma.append(abs(fn(2 * np.pi * fo)))
    return np.array(ma)


# calculate the Ness group delays at fo for a filter with a given QU
def groupdelay_tdqu(g, bw, fo, qu):
    w, wo, dw, wp = sy.symbols("w wo dw wp")
    td = []
    for n in range(1, len(g)-1):
        xin = lowpass_xin(g, wp, n)
        phi = -2 * sy.atan(xin / g[0])
        WP = wo / dw * (w / wo - wo / w) - wo * sy.I / (qu * dw)
        GD = -sy.diff(WP, w) * sy.simplify(sy.diff(phi, wp)).subs(wp, WP)
        GD = GD.subs(w, wo)
        GD = GD.subs(wo, 2 * sy.pi * fo)
        GD = GD.subs(dw, 2 * sy.pi * bw)
        td.append(float(GD.evalf()))
    return np.array(td)


#######################
# reverse
#######################

# calculate QE and QU from the Ness group delay and return loss at QE 
def qequ_groupdelay(fo, td1, ma1):
    wo = 2 * np.pi * fo
    qequ = (1 - abs(ma1)) / (1 + abs(ma1))
    qe = wo * td1 / 4 * (1 - qequ**2)
    qu = qe / qequ if qequ else np.inf
    return qe, qu


# calculate QE, QU, and K12 from TD1, TD2, and the RL at QE
def k12_groupdelay(fo, td1, td2, ma1):
    qe, qu = qequ_groupdelay(fo, td1, ma1)
    if np.isinf(qu): qu = 1e99
    wo = 2 * np.pi * fo
    k12 = np.sqrt(
        -1/qu**2 + 2/(qe*td2*wo) + 
        np.sqrt(-8*qe*td2*wo + 4*qu**2 + td2**2*wo**2)/
        (qe*qu*td2*wo))
    return k12

###

# for a given QE / QU find the reflection coefficient at QE
def reflection_qequ(qk, bw, fo, qu):
    N = len(qk) - 1
    QK = denormalize_qk(qk, bw, fo)
    qe = QK[::N]
    return (1 - qe / qu) / (1 + qe / qu)


# for a lossless bandpass filter, calculate qk from Ness group delay values at fo
def qk_groupdelayfo(td, fo):
    wo = 2 * np.pi * fo
    q = wo * td[0] / 4
    td = np.concatenate((np.zeros(2), td))
    k = 4 / wo / np.sqrt((td[2:-1] - td[:-3]) * (td[3:] - td[1:-2]))
    qk = np.concatenate(([q], k, [q]))
    return qk


#######################
# lowpass
#######################

# reactance of a low pass filter grounded at resonator n
def lowpass_xin(g, wp, n):
    xin = 0
    for i in reversed(range(1, n+1)):
        G = wp * g[i]
        if i % 2:
            xin = 1 / (-G + 1 / xin) if xin else -1 / G
        else:
            xin += G
    return xin


# impedance of a low pass filter grounded at resonator n
def lowpass_zin(g, wp, qu, n):
    zin = 0
    for i in reversed(range(1, n+1)):
        G = wp * g[i] * sy.I
        if i % 2:
            zin = 1 / (G + 1 / zin) if zin else 1 / G
        else:
            zin += G + wp * g[i] / qu
    return zin


# return function fn(f, qu) which calculates the Ness S11 values
# for lossy lowpass filters shorted at resonator n
def fn_lowpass_reflection(g, fo, n):
    f, w, wo, wp, qu = sy.symbols("f w wo wp qu")
    xin = lowpass_zin(g, wp, qu, n)
    xin = xin.subs(wp, w / wo)
    xin = xin.subs(wo, 2 * sy.pi * fo)
    xin = xin.subs(w, 2 * sy.pi * f)
    s11 = (xin - g[0]) / (xin + g[0])
    return sy.lambdify([ f, qu ], s11, 'numpy')


def fn_lowpass_transmission(g, fo):
    f, wp, qu = sy.symbols("f wp qu")
    vin = 1
    zin = g[0]
    for i in range(1, len(g)-1):
        G = wp * g[i] * sy.I
        if i % 2:
            a = 1 / G
            vin = vin * a / (a + zin)
            zin = 1 / (1 / a + 1 / zin)
        else:
            zin += G + wp * g[i] / qu
    s21 = 2 * vin * g[-1] / (zin + g[-1])
    s21 = s21.subs(wp, f / fo)
    return sy.lambdify([f, qu], s21, 'numpy')
                       

### approximations

def lowpass_groupdelay(g, fo, qu, steps=1000):
    fp = []
    td = []
    for n in range(2, len(g)-1):
        fn = fn_lowpass_reflection(g, fo, n)
        ###
        f = np.linspace(0, 2 * fo, steps)
        tdqu = groupdelay(fn, f, qu)
        a = np.argmax(tdqu)
        fmax = f[a]
        peak = tdqu[a]
        # from scipy.optimize import minimize
        # res = minimize(lambda x: -groupdelay(fn, x, qu), fmax, method='Nelder-Mead')
        # fmax = res.x[0] if res.success else np.nan
        # peak = -res.fun if res.success else np.nan
        fp.append(fmax)
        td.append(peak)
    return fp, td


def lowpass_bandwidth(g, fo, qu, steps=1000):
    fn = fn_lowpass_transmission(g, fo)
    f = np.linspace(0, 2 * fo, steps)
    tdqu = groupdelay(fn, f, qu)
    a = np.argmax(tdqu)
    fmax = f[a]
    peak = tdqu[a]
    ###
    # from scipy.optimize import minimize
    # res = minimize(lambda x: -groupdelay(fn, x, qu), fmax, method='Nelder-Mead')
    # fmax = res.x[0] if res.success else np.nan
    # peak = -res.fun if res.success else np.nan
    return fmax, peak


