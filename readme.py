#!/usr/bin/python3

import os, subprocess 

def run(command, language=''):
    proc = subprocess.Popen("PYTHONPATH=. python3 " + command, shell=True, stdout=subprocess.PIPE)
    buf = proc.stdout.read().decode()
    proc.wait()
    return f"""
```{language}
$ {command}
{buf}\
```
"""

print(f"""

# rftune

Python 3 script for tuning, specifically narrow-band, bandpass filters.
The script requires the numpy and sympy library.

## Overview

The script has tables for low pass prototype filters, coupled
filters, and predistorted filters.  Use this script to predict
the properties of a filter you are designing.  It calculates
the insertion loss, the transmission delay, minimum
return loss, as well as the various Ness [1][2] group delays for the
given filter.

## Example

To predict the properties of a 6 pole Chebyshev filter of 0.01 dB ripple centered at 2.3 GHz
with a ripple bandwidth of 26.9 Mhz and an unloaded resonator Q of 1400, run:

{ run("rftune -g --cheb .01 -n 6 -f 2.3e9 -b 26.9e6 -u 1400") }

If your VNA is 50 ohms but your filter terminates in 100 ohms, the script
will adjust its predictions for this.

{ run("rftune -g --cheb .01 -n 6 -f 2.3e9 -b 26.9e6 -u 1400 --re 100") }

# Usage

{ run("rftune -h") }

## Tables

The following lowpass prototype filter coefficients are supported.
Note the bandwidth for these lowpass prototype Chebyshev filters is the ripple bandwidth.
The bandwidth for the coupled Chebyshev filters below are 3dB bandwidth.

{ run("rftune -g --list") }

The following coupled filter coefficients are supported.

{ run("rftune --list") }

The following predistorted coupled filter coefficients from Zverev [3] are supported.

{ run("rftune -p --list") }

## Footnotes

[1] "A Unified Approach to the Design, Measurement, and Tuning 
of Coupled-Resonator Filter", John B. Ness, IEEE MTT Vol 46, No 4, April 1998

[2] See "Microwave Filters for Communication Systems: Fundamental Application",
Cameron, Mansour, Kaudsia, pp 610-615.   Also "Modern RF and Microwave
Filter Design", Pramanick, Bhartia, pp 346-349.

[3] "Handbook of Filter Synthesis", Anatol I. Zverev, 1967

""")


