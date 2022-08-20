

# rftune

Python 3 script for tuning, specifically narrow-band, bandpass filters.
The script requires the numpy and sympy library.

## Overview

The script has tables for low pass prototype filters, coupled
filters, and predistorted filters.  Use this script to predict
the properties of a filter you are designing.  It calculates
the insertion loss, the transmission delay, minimum
return loss, as well as the various Ness [1][2] group delays 
and associated return losses for the
given filter.

## Installation

To build the rftune executable, run:

```
sh build.sh
```

## Example

To predict the properties of a 6 pole Chebyshev filter of 0.01 dB ripple centered at 2.3 GHz
with a ripple bandwidth of 26.9 Mhz and an unloaded resonator Q of 1400, run the following.


```
$ rftune -g --cheb .01 -n 6 -f 2.3e9 -b 26.9e6 -u 1400
---------------------------------------
       6 Pole Chebyshev 0.01 dB        
---------------------------------------
Normalized Lowpass Coefficients gi
  g0      1.000000
  g1      0.781350
  g2      1.360010
  g3      1.689670
  g4      1.535020
  g5      1.497030
  g6      0.709840
  g7      1.100750
Center Frequency    =      2300.00000 MHz
Design Bandwidth    =        26.90000 MHz
Delay Bandwidth     =        30.55070 MHz
3dB Bandwidth       =        30.56146 MHz
Transmission Delay  =          44.699 ns
Minimum Return Loss =          27.598 dB
Insertion Loss      =           2.004 dB
Loaded QL           =          85.502
Unloaded QU         =        1400.000
Normalized q0       =          16.374
Normalized and Denormalized qi, kij, and Coupling Bandwidths
  q1      0.781350   |   Q1     66.806877   |   BW1     21.01832 MHz
  k12     0.970077   |   K12     0.011346   |   BW12    26.09507 MHz
  k23     0.659672   |   K23     0.007715   |   BW23    17.74517 MHz
  k34     0.620929   |   K34     0.007262   |   BW34    16.70299 MHz
  k45     0.659672   |   K45     0.007715   |   BW45    17.74516 MHz
  k56     0.970073   |   K56     0.011346   |   BW56    26.09497 MHz
  q6      0.781356   |   Q6     66.807423   |   BW6     21.01849 MHz
Lossless Ness Group Delay and Return Loss
  1              18.492 ns   0.000 dB   |   6              18.492 ns   0.000 dB
  1 2            32.186 ns   0.000 dB   |   6 5            32.186 ns   0.000 dB
  1 2 3          58.480 ns   0.000 dB   |   6 5 4          58.480 ns   0.000 dB
  1 2 3 4        68.514 ns   0.000 dB   |   6 5 4 3        68.514 ns   0.000 dB
  1 2 3 4 5      93.909 ns   0.000 dB   |   6 5 4 3 2      93.909 ns   0.000 dB
  1 2 3 4 5 6    85.313 ns   0.000 dB   |   6 5 4 3 2 1    85.313 ns   0.000 dB
Ness Group Delay and Return Loss (QU=1400.0)
  1              18.534 ns   0.830 dB   |   6              18.534 ns   0.830 dB
  1 2            32.025 ns   1.440 dB   |   6 5            32.025 ns   1.440 dB
  1 2 3          58.789 ns   2.626 dB   |   6 5 4          58.789 ns   2.626 dB
  1 2 3 4        67.860 ns   3.062 dB   |   6 5 4 3        67.860 ns   3.062 dB
  1 2 3 4 5      94.893 ns   4.224 dB   |   6 5 4 3 2      94.894 ns   4.224 dB
  1 2 3 4 5 6    84.287 ns   3.809 dB   |   6 5 4 3 2 1    84.287 ns   3.809 dB
```


This filter is an example from Ness's paper.

![](res/ness.png)

If your VNA is 50 ohms but your filter terminates in 100 ohms, the script
can adjust its predictions for this.


```
$ rftune -g --cheb .01 -n 6 -f 2.3e9 -b 26.9e6 -u 1400 --re 100
---------------------------------------
       6 Pole Chebyshev 0.01 dB        
---------------------------------------
Normalized Lowpass Coefficients gi
  g0      1.000000
  g1      0.781350
  g2      1.360010
  g3      1.689670
  g4      1.535020
  g5      1.497030
  g6      0.709840
  g7      1.100750
Center Frequency    =      2300.00000 MHz
Design Bandwidth    =        26.90000 MHz
Delay Bandwidth     =        30.55070 MHz
3dB Bandwidth       =        30.56146 MHz
Transmission Delay  =          44.699 ns
Minimum Return Loss =          27.598 dB
Insertion Loss      =           2.004 dB
Loaded QL           =          85.502
Unloaded QU         =        1400.000
Normalized q0       =          16.374
Normalized and Denormalized qi, kij, and Coupling Bandwidths
  q1      0.781350   |   Q1     66.806877   |   BW1     21.01832 MHz
  k12     0.970077   |   K12     0.011346   |   BW12    26.09507 MHz
  k23     0.659672   |   K23     0.007715   |   BW23    17.74517 MHz
  k34     0.620929   |   K34     0.007262   |   BW34    16.70299 MHz
  k45     0.659672   |   K45     0.007715   |   BW45    17.74516 MHz
  k56     0.970073   |   K56     0.011346   |   BW56    26.09497 MHz
  q6      0.781356   |   Q6     66.807423   |   BW6     21.01849 MHz
Lossless Ness Group Delay and Return Loss
  1              18.492 ns   0.000 dB   |   6              18.492 ns   0.000 dB
  1 2            32.186 ns   0.000 dB   |   6 5            32.186 ns   0.000 dB
  1 2 3          58.480 ns   0.000 dB   |   6 5 4          58.480 ns   0.000 dB
  1 2 3 4        68.514 ns   0.000 dB   |   6 5 4 3        68.514 ns   0.000 dB
  1 2 3 4 5      93.909 ns   0.000 dB   |   6 5 4 3 2      93.909 ns   0.000 dB
  1 2 3 4 5 6    85.313 ns   0.000 dB   |   6 5 4 3 2 1    85.313 ns   0.000 dB
Ness Group Delay and Return Loss (QU=1400.0)
  1              18.534 ns   0.830 dB   |   6              18.534 ns   0.830 dB
  1 2            32.025 ns   1.440 dB   |   6 5            32.025 ns   1.440 dB
  1 2 3          58.789 ns   2.626 dB   |   6 5 4          58.789 ns   2.626 dB
  1 2 3 4        67.860 ns   3.062 dB   |   6 5 4 3        67.860 ns   3.062 dB
  1 2 3 4 5      94.893 ns   4.224 dB   |   6 5 4 3 2      94.894 ns   4.224 dB
  1 2 3 4 5 6    84.287 ns   3.809 dB   |   6 5 4 3 2 1    84.287 ns   3.809 dB
Filter Termination and Line Impedance Mismatch Results (QU=1400.0)
  1               9.251 ns   0.415 dB   |   6               9.251 ns   0.415 dB
  1 2            65.403 ns   2.901 dB   |   6 5            65.403 ns   2.901 dB
  1 2 3          28.896 ns   1.306 dB   |   6 5 4          28.896 ns   1.306 dB
  1 2 3 4       149.828 ns   6.326 dB   |   6 5 4 3       149.828 ns   6.326 dB
  1 2 3 4 5      45.394 ns   2.081 dB   |   6 5 4 3 2      45.394 ns   2.081 dB
  1 2 3 4 5 6   197.528 ns   8.025 dB   |   6 5 4 3 2 1   197.527 ns   8.025 dB
  Line Impedance                    50.000 ohm
  Termination Resistance           100.000 ohm
  Transmission Delay                39.218 ns
  Insertion Loss                     3.403 dB
  Empirical QE1                     33.403
  Empirical QE6                     33.404
```


Delay Bandwidth is the bandwidth determined from the group-delay response
of S21, that is, the width that separates the two group delay peaks in the S21 response.
For some filter types, like Bessel and Gaussian,
there are no twin group delay peaks in S21
so the predicted delay bandwidth value will be wrong.

# Calculating QE, QU and K12 from Measurements

Say you measure a return loss and a Ness group delay of
.830 dB and 18.534 ns for the first resonantor of the above
filter.  To calculate this resonator's QE and QU use:


```
$ rftune -f 2.3e9 --qequ .830 18.534
QU =    1399.337
QE =      66.808
```


Next, say, you measure a Ness group delay of 32.025 ns for the second resonator.
To find k12 use:


```
$ rftune -f 2.3e9 --k12 .830 18.534 32.025
QU  =    1399.337
QE  =      66.808
K12 =    0.011346
```


# Usage


```
$ rftune -h
usage: rftune [-h] [-l] [-p] [-g] [-u QU] [-n NUMBER] [-f FREQUENCY]
              [-b BANDWIDTH] [--zo ZO] [--re RE] [--butterworth] [--bessel]
              [--legendre] [--chebyshev CHEBYSHEV] [--gaussian GAUSSIAN]
              [--linear-phase LINEAR_PHASE] [--max-ripple MAX_RIPPLE]
              [--max-swr MAX_SWR] [--max-rc MAX_RC] [--validate] [--lowpass]
              [--qequ <RL1dB)> <TD1(ns)>] [--k12 <RL1(dB)> <TD1(ns)> <TD2(ns>]

optional arguments:
  -h, --help            show this help message and exit
  -l, --list
  -p, --predistorted    use Zverev's predistorted filters (default: False)
  -g, --g               use lowpass prototype table (default: False)
  -u QU, --qu QU        unloaded quality factor (default: inf)
  -n NUMBER, --number NUMBER
                        number of filter poles (default: None)
  -f FREQUENCY, --frequency FREQUENCY
                        center frequency (default: None)
  -b BANDWIDTH, --bandwidth BANDWIDTH
                        bandwidth (default: None)
  --zo ZO               line impedance (default: 50.0)
  --re RE               filter impedance (default: 50.0)
  --butterworth         use a Butterworth filter (default: False)
  --bessel              use a Bessel filter (default: False)
  --legendre            use a Lengendre filter (default: False)
  --chebyshev CHEBYSHEV
                        use a Chebyshev filter (default: None)
  --gaussian GAUSSIAN   use a Gaussian filter (default: None)
  --linear-phase LINEAR_PHASE
                        use a Linear phase filter (default: None)
  --max-ripple MAX_RIPPLE
                        use Chebyshev filter of given ripple (default: None)
  --max-swr MAX_SWR     use Chebyshev filter of given SWR (default: None)
  --max-rc MAX_RC       use Chebyshev filter of given reflection coefficient
                        (default: None)
  --validate            validate results against k12 (default: False)
  --lowpass             predicted lowpass characteristics (default: False)
  --qequ <RL1(dB)> <TD1(ns)>
                        calculate QE and QU using resonator 1 group delay and
                        return loss (default: None)
  --k12 <RL1(dB)> <TD1(ns)> <TD2(ns)>
                        calculate k12 using resonator 1 and 2 group delay and
                        return loss (default: None)
```


## Tables

The following lowpass prototype filter coefficients are supported.
Note the bandwidth for these lowpass prototype Chebyshev filters is the ripple bandwidth.
The bandwidth for the coupled Chebyshev filters below are 3dB bandwidth.


```
$ rftune -g --list
Butterworth
Chebyshev 0.01 dB
Chebyshev 0.1 dB
Chebyshev 0.25 dB
Chebyshev 0.5 dB
Chebyshev 1.0 dB
Bessel
Linear Phase 0.05 Deg
Linear Phase 0.5 Deg
Legendre
Gaussian
Gaussian 6 dB
Gaussian 12 dB
```


The following coupled filter coefficients are supported.


```
$ rftune --list
Butterworth
Chebyshev 0.01 dB
Chebyshev 0.1 dB
Chebyshev 0.5 dB
Chebyshev 1.0 dB
Bessel
Linear Phase 0.05 Deg
Linear Phase 0.5 Deg
Gaussian 6 dB
Gaussian 12 dB
```


The following predistorted coupled filter coefficients from Zverev [3] are supported.


```
$ rftune -p --list
Butterworth
Chebyshev 0.01 dB
Chebyshev 0.1 dB
Chebyshev 0.5 dB
Bessel
Linear Phase 0.05 Deg
Linear Phase 0.5 Deg
Gaussian
Gaussian 6 dB
Gaussian 12 dB
Legendre
```


## Footnotes

[1] "A Unified Approach to the Design, Measurement, and Tuning 
of Coupled-Resonator Filter", John B. Ness, IEEE MTT Vol 46, No 4, April 1998

[2] See "Microwave Filters for Communication Systems: Fundamental Application",
Cameron, Mansour, Kaudsia, pp 610-615.   Also "Modern RF and Microwave
Filter Design", Pramanick, Bhartia, pp 346-349.

[3] "Handbook of Filter Synthesis", Anatol I. Zverev, 1967


