
import numpy as np
import argparse, json, sys, re

from coupled import COUPLED
from zverev import ZVEREV
from lowpass import LOWPASS

from ness import (
    prototype_qk, denormalize_qk, coupling_g, db, chebyshev,   # helpers
    nodal_delay_transmission, nodal_insertionloss,             # measurements at fo
    nodal_returnloss, nodal_delay_bandwidth, nodal_bandwidth,  # approximations
    lowpass_groupdelay, lowpass_bandwidth,                     # approximations
    groupdelay_maqu, groupdelay_tdqu,   # lossy
    groupdelay_qk,                      # lossless
    qequ_groupdelay, k12_groupdelay,    # validation
    fn_nodal_transmission, groupdelay,  # when re != zo
)


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=
             argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-p", "--predistorted", action="store_true", 
                        help="use Zverev's predistorted filters")
    parser.add_argument("-g", "--g", action="store_true", 
                        help="use lowpass prototype table")
    parser.add_argument("-u", "--qu", type=float, default=np.inf, 
                        help='unloaded quality factor')
    parser.add_argument("-n", "--number", type=int, default=None,
                        help="number of filter poles")
    parser.add_argument("-f", "--frequency", type=float, help='center frequency')
    parser.add_argument("-b", "--bandwidth", type=float, help='bandwidth')
    parser.add_argument("--zo", type=float, default=50.0, help='line impedance')
    parser.add_argument("--re", type=float, default=50.0, help='filter impedance')
    parser.add_argument("--butterworth", action="store_true", help='use a Butterworth filter')
    parser.add_argument("--bessel", action="store_true", help='use a Bessel filter')
    parser.add_argument("--legendre", action="store_true", help='use a Lengendre filter')
    parser.add_argument("--chebyshev", type=float, help='use a Chebyshev filter')
    parser.add_argument("--gaussian", type=float, help='use a Gaussian filter')
    parser.add_argument("--linear-phase", type=float, help='use a Linear phase filter')
    parser.add_argument("--max-ripple", type=float, help='use Chebyshev filter of given ripple')
    parser.add_argument("--max-swr", type=float, help='use Chebyshev filter of given SWR')
    parser.add_argument("--max-rc", type=float, help='use Chebyshev filter of given reflection coefficient')
    parser.add_argument("--validate", action='store_true', help='validate results against k12')
    parser.add_argument("--lowpass", action='store_true', help='predicted lowpass characteristics')
    parser.add_argument("--qequ", nargs=2, metavar=('<RL1(dB)>', '<TD1(ns)>',), type=float,
                        help='calculate QE and QU using resonator 1 group delay and return loss')
    parser.add_argument("--k12", nargs=3, metavar=('<RL1(dB)>', '<TD1(ns)>', '<TD2(ns)>'), type=float,
                        help='calculate k12 using resonator 1 and 2 group delay and return loss')
    return parser.parse_args()


def list_qk(qk, bw, fo):
    QK = denormalize_qk(qk, bw, fo)
    for i in range(len(QK)):
        name1, name2, name3 = f'k{i}{i+1}', f'K{i}{i+1}', f'BW{i}{i+1}'
        if i == 0: name1, name2, name3 = 'q1', 'Q1', 'BW1'
        if i == len(QK)-1: name1, name2, name3 = f'q{i}', f'Q{i}', f'BW{i}'
        print('  {:4s} {:11.6f}   |   {:4s} {:11.6f}   |   {:4s} {:11.5f} MHz'
              .format(name1, qk[i], name2, QK[i], name3, qk[i] * bw / 1e6))


def list_g(g):
    for i in range(len(g)):
        print('  {:4s} {:11.6f}'.format(f'g{i}', g[i]))


def list_groupdelays(TD1, TD2, MA1, MA2):
    N = len(TD1)
    width = len(' '.join([ str(i) for i in range(1, N+1) ]))
    for n in range(N):
        res1 = ' '.join([ str(i) for i in range(1, n+2) ])
        res2 = ' '.join([ str(i) for i in range(N, N-n-1, -1) ])
        print('  {} {:9.3f} ns {:7.3f} dB   |   {} {:9.3f} ns {:7.3f} dB'.format(
              res1.ljust(width), TD1[n] * 1e9, db(1/MA1[n]),
              res2.ljust(width), TD2[n] * 1e9, db(1/MA2[n])))


def find_filter(table, name, value=None):
    name = name.lower()
    for key, data in table.items():
        m = re.search('[\d\.]+', key)
        if name == key.lower() or (
           name in key.lower() and m and float(m.group(0)) == value):
            return key, data



def main():
    bw = args.bandwidth
    fo = args.frequency
    qu = args.qu

    if (args.qequ or args.k12) and not fo: 
        print("Center frequency not set.")
        return

    if args.qequ:
        ma1 = 10**(-args.qequ[0] / 20)
        td1 = args.qequ[1] * 1e-9
        qe, qu = qequ_groupdelay(fo, td1, ma1)
        print('QU = {:11.3f}'.format(qu))
        print('QE = {:11.3f}'.format(qe))
        return

    if args.k12:
        ma1 = 10**(-args.k12[0] / 20)
        td1 = args.k12[1] * 1e-9
        td2 = args.k12[2] * 1e-9
        qe, qu = qequ_groupdelay(fo, td1, ma1)
        k12 = k12_groupdelay(fo, td1, td2, ma1)
        print('QU  = {:11.3f}'.format(qu))
        print('QE  = {:11.3f}'.format(qe))
        print('K12 = {:11.6f}'.format(k12))
        return

    if args.g:
        table = LOWPASS
    elif args.predistorted:
        table = ZVEREV
    else:
        table = COUPLED

    if args.list:
        for name in table:
            print(name)
        return

    if not args.number:
        print("Number of poles not set.")
        return

    # pull tables
    if args.butterworth:
        res = find_filter(table, 'BUTTERWORTH')
    elif args.bessel:
        res = find_filter(table, 'BESSEL')
    elif args.legendre:
        res = find_filter(table, 'LEGENDRE')
    elif args.chebyshev:
        res = find_filter(table, 'CHEBYSHEV', args.chebyshev) 
    elif args.gaussian:
        res = find_filter(table, 'GAUSSIAN', args.gaussian) 
    elif args.linear_phase:
        res = find_filter(table, 'LINEAR PHASE', args.linear_phase) 
    elif args.max_ripple or args.max_swr or args.max_rc:
        args.g = True
        if args.max_swr:
            swr = args.max_swr
            rc = (swr - 1) / (swr + 1)
            ripple = -10 * np.log10(1 - rc**2)
        if args.max_rc:
            rc = args.max_rc
            ripple = -10 * np.log10(1 - rc**2)
        if args.max_ripple:
            ripple = args.max_ripple
        res = ('Chebyshev {:.4g} dB'.format(ripple), 
               [chebyshev(args.number, ripple)]) 
    else:
        print('No filter type specified.')
        return

    # collect data
    name, values = res
    data = []
    for row in values:
        d = {}
        d['name'] = name
        if args.g:
            if args.predistorted:
                print('No predistorted lowpass prototypes.')
                return
            g = row
            d['g'] = g
            d['qk'] = coupling_g(g)
            n = len(g) - 2
        else:
            if args.predistorted:
                d['qo'] = row[0]
                row = row[2:]
            qk = row[:1] + row[2:] + row[1:2] 
            d['qk'] = qk
            d['g'] = prototype_qk(qk)
            n = len(qk) - 1
        if args.number is None or args.number == n:
            data.append(d)

    # analyze filters
    count = 0
    for d in data:
        name = d.get('name')
        qo = d.get('qo')
        qk = d['qk']
        g = d['g']
        N = len(g) - 2

        if count: print()
        count += 1
        print('---------------------------------------')
        print('{:^39}'.format('{} Pole {}'.format(N, name)))
        print('---------------------------------------')

        print('Normalized Lowpass Coefficients gi')
        list_g(g)

        if qo:
            print('Predistored Q0      = {:>15}'.format(str(qo)))
        if fo:
            print('Center Frequency    = {:15.5f} MHz'.format(fo / 1e6))
        if args.lowpass:
            fp, td = lowpass_groupdelay(g, fo, qu)
            print('Ness Group Delay of Low Pass Filter (QU={})'.format(qu))
            for i in range(len(fp)):
                print('  TD{}  {:11.3f} ns     peak at {:11.5f} MHz '
                      .format(i+2, td[i] * 1e9, fp[i] / 1e6))
            fpeak, tdpeak = lowpass_bandwidth(g, fo, qu)
            print('Group Delay Peak Of Terminated Low Pass Filter (QU={})'.format(qu))
            print('       {:11.3f} ns     peak at {:11.5f} MHz '
                  .format(tdpeak * 1e9, fpeak / 1e6))
            continue

        if bw:
            print('Design Bandwidth    = {:15.5f} MHz'.format(bw / 1e6))
        if bw and fo:
            bwtd = nodal_delay_bandwidth(qk, bw, fo, qu) # step
            print('Delay Bandwidth     = {:15.5f} MHz'.format(bwtd / 1e6))
            bwdb = nodal_bandwidth(qk, bw, fo, qu) # step
            print('3dB Bandwidth       = {:15.5f} MHz'.format(bwdb / 1e6))
            td = nodal_delay_transmission(qk, bw, fo, qu)
            print('Transmission Delay  = {:15.3f} ns'.format(td * 1e9))
            rl = nodal_returnloss(qk, bw, fo, qu) # step
            print('Minimum Return Loss = {:15.3f} dB'.format(rl))
            il = nodal_insertionloss(qk, bw, fo, qu) # step
            print('Insertion Loss      = {:15.3f} dB'.format(il))
            print('Loaded QL           = {:15.3f}'.format(fo / bw))
            print('Unloaded QU         = {:15.3f}'.format(qu))
            print('Normalized Q0       = {:15.3f}'.format(qu / (fo / bw)))
            print('Normalized and Denormalized qi, kij, and Coupling Bandwidths')
            list_qk(qk, bw, fo)

        if bw:
            print('Lossless Ness Group Delay and Return Loss')
            TD1 = groupdelay_qk(qk, bw)
            TD2 = groupdelay_qk(qk[::-1], bw)
            MA = np.ones(len(TD1))
            list_groupdelays(TD1, TD2, MA, MA)

        if bw and fo and not np.isinf(qu):
            print('Ness Group Delay and Return Loss (QU={})'.format(qu))
            MA1 = groupdelay_maqu(g, bw, fo, qu)
            TD1 = groupdelay_tdqu(g, bw, fo, qu)
            MA2 = groupdelay_maqu(g[::-1], bw, fo, qu)
            TD2 = groupdelay_tdqu(g[::-1], bw, fo, qu)
            list_groupdelays(TD1, TD2, MA1, MA2)

            if args.re != args.zo:
                print('Filter Termination and Line Impedance Mismatch Results (QU={})'.format(qu))

                gcopy = g.copy()
                gcopy[0] *= args.zo / args.re
                MA1 = groupdelay_maqu(gcopy, bw, fo, qu)
                TD1 = groupdelay_tdqu(gcopy, bw, fo, qu)
                gcopy = g[::-1]
                gcopy[0] *= args.zo / args.re
                MA2 = groupdelay_maqu(gcopy, bw, fo, qu)
                TD2 = groupdelay_tdqu(gcopy, bw, fo, qu)
                list_groupdelays(TD1, TD2, MA1, MA2)

                QE1 = fo / bw * qk[0] * args.zo / args.re
                QE2 = fo / bw * qk[-1] * args.zo / args.re
                print('  Line Impedance           {:15.3f} ohm'.format(args.zo))
                print('  Termination Resistance   {:15.3f} ohm'.format(args.re))
                fn = fn_nodal_transmission(qk, bw, fo, re=args.zo/args.re)
                td = groupdelay(fn, fo, qu)
                print('  Transmission Delay       {:15.3f} ns'.format(td * 1e9))
                il = -db(fn(fo, qu))
                print('  Insertion Loss           {:15.3f} dB'.format(il))
                print('  Empirical QE{}            {:15.3f}'.format(1, QE1))
                print('  Empirical QE{}            {:15.3f}'.format(N, QE2))

            if args.validate:
                print('Validation')
                qe1, qu1 = qequ_groupdelay(fo, TD1[0], MA1[0])
                qe2, qu2 = qequ_groupdelay(fo, TD2[0], MA2[0])
                print('  QU{}={:14.6f}'.format(1, qu1))
                print('  QU{}={:14.6f}'.format(N, qu2))
                print('  QE{}={:14.6f}'.format(1, qe1))
                print('  QE{}={:14.6f}'.format(N, qe2))
                k12 = k12_groupdelay(fo, TD1[0], TD1[1], MA1[0])
                print('  K12={:14.6f}'.format(k12))
                k12 = k12_groupdelay(fo, TD2[0], TD2[1], MA2[0])
                print('  K{}{}={:14.6f}'.format(N-1, N, k12))

    
if __name__ == '__main__':
    args = parse_args()
    try:
        main()
    except KeyboardInterrupt:
        pass


