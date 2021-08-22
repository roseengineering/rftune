

# rftune

Python 3 script for tuning, specifically narrow-band, bandpass filters.
The script requires the numpy and sympy library.

# Overview

The script has tables for low pass prototype filters, coupled
filters, and predistorted filters.  Use this script to predict
the properties of a filter you are designing.  It calculates
the insertion loss, the transmission delay, minimum
return loss, as well as the various Ness group delays for the
given filter.

# Example

To predict the properties of a 6 pole Chebyshev filter of 0.01 dB ripple centered at 2.3 GHz
with a bandwidth of 26.9 Mhz and an unloaded resonator Q of 1400, run:


```
$ rftune --cheb .01 -n 6 -f 2.3e9 -b 26.9e6 -u 1400
---------------------------------------
       6 Pole Chebyshev 0.01 dB        
---------------------------------------
Design Bandwidth    =         26.9000 MHz
Center Frequency    =       2300.0000 MHz
Delay Bandwidth     =         25.4070 MHz
3dB Bandwidth       =         25.1610 MHz
Transmission Delay  =         53.5805 ns
Minimum Return Loss =         27.8575 dB
Insertion Loss      =          2.4136 dB
Unloaded QU         =       1400.0000
Filter Loaded QL    =         85.5019
Normalized Qo       =         16.3739
Normalized and Denormalized Qi and Kij
  q1      0.937000   |   Q1     80.115242
  k12     0.809000   |   K12     0.009462
  k23     0.550000   |   K23     0.006433
  k34     0.518000   |   K34     0.006058
  k45     0.550000   |   K45     0.006433
  k56     0.809000   |   K56     0.009462
  q6      0.937000   |   Q6     80.115242
Lossless Ness Group Delay and Return Loss
  1              22.175 ns   0.000 dB   |   6              22.175 ns   0.000 dB
  1 2            38.591 ns   0.000 dB   |   6 5            38.591 ns   0.000 dB
  1 2 3          70.153 ns   0.000 dB   |   6 5 4          70.153 ns   0.000 dB
  1 2 3 4        82.098 ns   0.000 dB   |   6 5 4 3        82.098 ns   0.000 dB
  1 2 3 4 5     112.710 ns   0.000 dB   |   6 5 4 3 2     112.710 ns   0.000 dB
  1 2 3 4 5 6   102.207 ns   0.000 dB   |   6 5 4 3 2 1   102.207 ns   0.000 dB
Ness Group Delay and Return Loss (QU=1400.0)
  1              22.248 ns   0.995 dB   |   6              22.248 ns   0.995 dB
  1 2            38.314 ns   1.726 dB   |   6 5            38.314 ns   1.726 dB
  1 2 3          70.692 ns   3.153 dB   |   6 5 4          70.692 ns   3.153 dB
  1 2 3 4        80.965 ns   3.664 dB   |   6 5 4 3        80.965 ns   3.664 dB
  1 2 3 4 5     114.448 ns   5.078 dB   |   6 5 4 3 2     114.448 ns   5.078 dB
  1 2 3 4 5 6   100.422 ns   4.555 dB   |   6 5 4 3 2 1   100.422 ns   4.555 dB
```


If your VNA is 50 ohms but your filter terminates in 100 ohms, the script
will adjust its predictions for this.


```
$ rftune --cheb .01 -n 6 -f 2.3e9 -b 26.9e6 -u 1400 --re 100
---------------------------------------
       6 Pole Chebyshev 0.01 dB        
---------------------------------------
Design Bandwidth    =         26.9000 MHz
Center Frequency    =       2300.0000 MHz
Delay Bandwidth     =         25.4070 MHz
3dB Bandwidth       =         25.1610 MHz
Transmission Delay  =         53.5805 ns
Minimum Return Loss =         27.8575 dB
Insertion Loss      =          2.4136 dB
Unloaded QU         =       1400.0000
Filter Loaded QL    =         85.5019
Normalized Qo       =         16.3739
Normalized and Denormalized Qi and Kij
  q1      0.937000   |   Q1     80.115242
  k12     0.809000   |   K12     0.009462
  k23     0.550000   |   K23     0.006433
  k34     0.518000   |   K34     0.006058
  k45     0.550000   |   K45     0.006433
  k56     0.809000   |   K56     0.009462
  q6      0.937000   |   Q6     80.115242
Lossless Ness Group Delay and Return Loss
  1              22.175 ns   0.000 dB   |   6              22.175 ns   0.000 dB
  1 2            38.591 ns   0.000 dB   |   6 5            38.591 ns   0.000 dB
  1 2 3          70.153 ns   0.000 dB   |   6 5 4          70.153 ns   0.000 dB
  1 2 3 4        82.098 ns   0.000 dB   |   6 5 4 3        82.098 ns   0.000 dB
  1 2 3 4 5     112.710 ns   0.000 dB   |   6 5 4 3 2     112.710 ns   0.000 dB
  1 2 3 4 5 6   102.207 ns   0.000 dB   |   6 5 4 3 2 1   102.207 ns   0.000 dB
Ness Group Delay and Return Loss (QU=1400.0)
  1              22.248 ns   0.995 dB   |   6              22.248 ns   0.995 dB
  1 2            38.314 ns   1.726 dB   |   6 5            38.314 ns   1.726 dB
  1 2 3          70.692 ns   3.153 dB   |   6 5 4          70.692 ns   3.153 dB
  1 2 3 4        80.965 ns   3.664 dB   |   6 5 4 3        80.965 ns   3.664 dB
  1 2 3 4 5     114.448 ns   5.078 dB   |   6 5 4 3 2     114.448 ns   5.078 dB
  1 2 3 4 5 6   100.422 ns   4.555 dB   |   6 5 4 3 2 1   100.422 ns   4.555 dB
Filter Termination and Line Impedance Mismatch Results (QU=1400.0)
  1              11.097 ns   0.497 dB   |   6              11.097 ns   0.497 dB
  1 2            78.973 ns   3.487 dB   |   6 5            78.973 ns   3.487 dB
  1 2 3          34.485 ns   1.564 dB   |   6 5 4          34.485 ns   1.564 dB
  1 2 3 4       187.293 ns   7.686 dB   |   6 5 4 3       187.293 ns   7.686 dB
  1 2 3 4 5      53.684 ns   2.486 dB   |   6 5 4 3 2      53.684 ns   2.486 dB
  1 2 3 4 5 6   254.579 ns   9.841 dB   |   6 5 4 3 2 1   254.579 ns   9.841 dB
  Line Impedance                   50.0000 ohm
  Termination Resistance          100.0000 ohm
  Transmission Delay               47.4849 ns
  Insertion Loss                    3.7509 dB
  Empirical QE1                   40.0576
  Empirical QE6                   40.0576
```


# Usage


```
$ rftune -h
usage: rftune [-h] [-l] [-p] [-g] [-u QU] [-n NUMBER] [-f FREQUENCY]
              [-b BANDWIDTH] [--zo ZO] [--re RE] [--butterworth] [--bessel]
              [--legendre] [--chebyshev CHEBYSHEV] [--gaussian GAUSSIAN]
              [--linear-phase LINEAR_PHASE] [--validate]

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
  --butterworth
  --bessel
  --legendre
  --chebyshev CHEBYSHEV
  --gaussian GAUSSIAN
  --linear-phase LINEAR_PHASE
  --validate
```


# Tables

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


The following predistorted coupled filter coefficients from Zverev are supported.


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



