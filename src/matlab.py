# -*- coding: utf-8 -*-
"""matlab.py

MATLAB emulation functions.

This file contains a number of functions that emulate some of the
functionality of MATLAB.  The intent of these functions is to
provide a simple interface to the python control systems library
(python-control) for people who are familiar with the MATLAB Control
Systems Toolbox (tm).  Most of the functions are just calls to
python-control functions defined elsewhere.  Use 'from
control.matlab import \*' in python to include all of the functions
defined here.  Functions that are defined in other libraries that
have the same names as their MATLAB equivalents are automatically
imported here.

"""

"""Copyright (c) 2009 by California Institute of Technology
All rights reserved.

Copyright (c) 2011 by Eike Welk

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the California Institute of Technology nor
   the names of its contributors may be used to endorse or promote
   products derived from this software without specific prior
   written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CALTECH
OR THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.

Author: Richard M. Murray
Date: 29 May 09
Revised: Kevin K. Chen, Dec 10

$Id$

"""

# Libraries that we make use of 
import scipy as sp              # SciPy library (used all over)
import numpy as np              # NumPy library
from scipy.signal.ltisys import _default_response_times
from copy import deepcopy
import warnings

# Import MATLAB-like functions that are defined in other packages
from scipy.signal import zpk2ss, ss2zpk, tf2zpk, zpk2tf
from scipy import linspace, logspace

# Control system library
import ctrlutil
import freqplot
import timeresp
from statesp import StateSpace, _rss_generate, _convertToStateSpace
from xferfcn import TransferFunction, _convertToTransferFunction
from lti import Lti #base class of StateSpace, TransferFunction
from exception import ControlArgument

# Import MATLAB-like functions that can be used as-is
from ctrlutil import unwrap
from freqplot import nyquist, gangof4
from nichols import nichols
from bdalg import series, parallel, negate, feedback
from pzmap import pzmap
from statefbk import ctrb, obsv, gram, place, lqr
from delay import pade
from modelsimp import hsvd, balred, modred
from mateqn import lyap, dlyap, dare, care

__doc__ += """
The control.matlab module defines functions that are roughly the
equivalents of those in the MATLAB Control Toolbox.  Items marked by a 
``*`` are currently implemented; those marked with a ``-`` are not planned
for implementation.

==  ==========================  ================================================
**Creating linear models.**
--------------------------------------------------------------------------------
\*  :func:`tf`                  create transfer function (TF) models
\   zpk                         create zero/pole/gain (ZPK) models.
\*  :func:`ss`                  create state-space (SS) models
\   dss                         create descriptor state-space models
\   delayss                     create state-space models with delayed terms
\   frd                         create frequency response data (FRD) models
\   lti/exp                     create pure continuous-time delays (TF and ZPK 
                                only)
\   filt                        specify digital filters
\-  lti/set                     set/modify properties of LTI models
\-  setdelaymodel               specify internal delay model (state space only)
\
**Data extraction**
--------------------------------------------------------------------------------
\   lti/tfdata                  extract numerators and denominators
\   lti/zpkdata                 extract zero/pole/gain data
\   lti/ssdata                  extract state-space matrices
\   lti/dssdata                 descriptor version of SSDATA
\   frd/frdata                  extract frequency response data
\   lti/get                     access values of LTI model properties
\   ss/getDelayModel            access internal delay model (state space only)
\ 
**Conversions**
--------------------------------------------------------------------------------
\*  :func:`tf`                  conversion to transfer function
\   zpk                         conversion to zero/pole/gain
\*  :func:`ss`                  conversion to state space
\   frd                         conversion to frequency data
\   c2d                         continuous to discrete conversion
\   d2c                         discrete to continuous conversion
\   d2d                         resample discrete-time model
\   upsample                    upsample discrete-time LTI systems
\*  :func:`ss2tf`               state space to transfer function
\   ss2zpk                      transfer function to zero-pole-gain
\*  :func:`tf2ss`               transfer function to state space
\   tf2zpk                      transfer function to zero-pole-gain
\   zpk2ss                      zero-pole-gain to state space
\   zpk2tf                      zero-pole-gain to transfer function
\
**System interconnections**
--------------------------------------------------------------------------------
\   append                      group LTI models by appending inputs and outputs
\*  :func:`parallel`            connect LTI models in parallel 
                                (see also overloaded +)
\*  :func:`series`              connect LTI models in series 
                                (see also overloaded \*)
\*  :func:`feedback`            connect lti models with a feedback loop
\   lti/lft                     generalized feedback interconnection
\   lti/connect                 arbitrary interconnection of lti models
\   sumblk                      specify summing junction (for use with connect)
\   strseq                      builds sequence of indexed strings 
                                (for I/O naming)
\
**System gain and dynamics**
--------------------------------------------------------------------------------
\*  :func:`dcgain`              steady-state (D.C.) gain
\   lti/bandwidth               system bandwidth
\   lti/norm                    h2 and Hinfinity norms of LTI models
\*  :func:`pole`                system poles
\*  :func:`zero`                system (transmission) zeros
\   lti/order                   model order (number of states)
\*  :func:`pzmap`               pole-zero map (TF only)
\   lti/iopzmap                 input/output pole-zero map
\   damp                        natural frequency and damping of system poles
\   esort                       sort continuous poles by real part
\   dsort                       sort discrete poles by magnitude
\   lti/stabsep                 stable/unstable decomposition
\   lti/modsep                  region-based modal decomposition
\
**Time-domain analysis**
--------------------------------------------------------------------------------
\*  :func:`step`                step response
\   stepinfo                    step response characteristics (rise time, ...)
\*  :func:`impulse`             impulse response
\*  :func:`initial`             free response with initial conditions
\*  :func:`lsim`                response to user-defined input signal
\   lsiminfo                    linear response characteristics
\   gensig                      generate input signal for LSIM
\   covar                       covariance of response to white noise
\
**Frequency-domain analysis**
--------------------------------------------------------------------------------
\*  :func:`bode`                Bode plot of the frequency response
\   lti/bodemag                 Bode magnitude diagram only
\   sigma                       singular value frequency plot
\*  :func:`nyquist`             Nyquist plot
\*  :func:`nichols`             Nichols plot
\*  :func:`margin`              gain and phase margins
\   lti/allmargin               all crossover frequencies and related gain/phase 
                                margins
\*  :func:`freqresp`            frequency response over a frequency grid
\*  :func:`evalfr`              evaluate frequency response at given frequency
\
**Model simplification**
--------------------------------------------------------------------------------
\   minreal                     minimal realization and pole/zero cancellation
\   ss/sminreal                 structurally minimal realization (state space)
\*  :func:`lti/hsvd`            hankel singular values (state contributions)
\*  :func:`lti/balred`          reduced-order approximations of LTI models
\*  :func:`ss/modred`           model order reduction
\
**Compensator design**
--------------------------------------------------------------------------------
\*  :func:`rlocus`              evans root locus
\*  :func:`place`               pole placement
\   estim                       form estimator given estimator gain
\   reg                         form regulator given state-feedback and 
                                estimator gains
\
**LQR/LQG design**
--------------------------------------------------------------------------------
\   ss/lqg                      single-step LQG design
\*  :func:`lqr`                 linear-Quadratic (LQ) state-feedback regulator
\   dlqr                        discrete-time LQ state-feedback regulator
\   lqry                        lq regulator with output weighting
\   lqrd                        discrete LQ regulator for continuous plant
\   ss/lqi                      linear-Quadratic-Integral (LQI) controller
\   ss/kalman                   Kalman state estimator
\   ss/kalmd                    discrete Kalman estimator for continuous plant
\   ss/lqgreg                   build LQG regulator from LQ gain and Kalman 
                                estimator
\   ss/lqgtrack                 build LQG servo-controller
\   augstate                    augment output by appending states
\
**State-space (SS) models**
--------------------------------------------------------------------------------
\*  :func:`rss`                 random stable continuous-time state-space models
\*  :func:`drss`                random stable discrete-time state-space models
\   ss2ss                       state coordinate transformation
\   canon                       canonical forms of state-space models
\*  :func:`ctrb`                controllability matrix
\*  :func:`obsv`                observability matrix
\*  :func:`gram`                controllability and observability gramians
\   ss/prescale                 optimal scaling of state-space models.  
\   balreal                     gramian-based input/output balancing
\   ss/xperm                    reorder states.   
\
**Frequency response data (FRD) models**
--------------------------------------------------------------------------------
\   frd/chgunits                change frequency vector units
\   frd/fcat                    merge frequency responses
\   frd/fselect                 select frequency range or subgrid
\   frd/fnorm                   peak gain as a function of frequency
\   frd/abs                     entrywise magnitude of the frequency response
\   frd/real                    real part of the frequency response
\   frd/imag                    imaginary part of the frequency response
\   frd/interp                  interpolate frequency response data
\   mag2db                      convert magnitude to decibels (dB)
\   db2mag                      convert decibels (dB) to magnitude
\
**Time delays**
--------------------------------------------------------------------------------
\   lti/hasdelay                true for models with time delays
\   lti/totaldelay              total delay between each input/output pair
\   lti/delay2z                 replace delays by poles at z=0 or FRD phase 
                                shift
\*  :func:`pade`                pade approximation of time delays
\
**Model dimensions and characteristics**
--------------------------------------------------------------------------------
\   class                       model type ('tf', 'zpk', 'ss', or 'frd')
\   isa                         test if model is of given type
\   tf/size                     model sizes
\   lti/ndims                   number of dimensions
\   lti/isempty                 true for empty models
\   lti/isct                    true for continuous-time models
\   lti/isdt                    true for discrete-time models
\   lti/isproper                true for proper models
\   lti/issiso                  true for single-input/single-output models
\   lti/isstable                true for models with stable dynamics
\   lti/reshape                 reshape array of linear models
\
**Overloaded arithmetic operations**
--------------------------------------------------------------------------------
\*  \+ and -                    add and subtract systems (parallel connection)
\*  \*                          multiply systems (series connection)
\   /                           right divide -- sys1/sys2 means sys1\*inv(sys2)
\-   \\                         left divide -- sys1\\sys2 means inv(sys1)\*sys2
\   ^                           powers of a given system
\   '                           pertransposition
\   .'                          transposition of input/output map
\   .\*                         element-by-element multiplication
\   [..]                        concatenate models along inputs or outputs
\   lti/stack                   stack models/arrays along some array dimension
\   lti/inv                     inverse of an LTI system
\   lti/conj                    complex conjugation of model coefficients
\
**Matrix equation solvers and linear algebra**
--------------------------------------------------------------------------------
\*  lyap, dlyap                 solve Lyapunov equations
\   lyapchol, dlyapchol         square-root Lyapunov solvers
\*  care, dare                  solve algebraic Riccati equations
\   gcare, gdare                generalized Riccati solvers
\   bdschur                     block diagonalization of a square matrix
\
**Additional functions**
--------------------------------------------------------------------------------
\*  :func:`gangof4`             generate the Gang of 4 sensitivity plots
\*  :func:`linspace`            generate a set of numbers that are linearly 
                                spaced
\*  :func:`logspace`            generate a set of numbers that are 
                                logarithmically spaced
\*  :func:`unwrap`              unwrap a phase angle to give a continuous curve
==  ==========================  ================================================
"""

def ss(*args):
    """
    Create a state space system.

    Parameters
    ----------
    A: numpy matrix or matrix-like object
    B: numpy matrix or matrix-like object
    C: numpy matrix or matrix-like object
    D: numpy matrix or matrix-like object
    sys: StateSpace or TransferFunction object
    ss accepts a set of `A`, `B`, `C`, `D` matrices or `sys`.

    Returns
    -------
    out: StateSpace object

    Raises
    ------
    ValueError
        if matrix sizes are not self-consistent

    See Also
    --------
    tf
    ss2tf
    tf2ss

    Examples
    --------
    >>> sys = ss(A, B, C, D) # Create a StateSpace object from these matrices.
    >>> sys = ss(sys1) # Convert a TransferFunction to a StateSpace object.

    """ 

    if len(args) == 4:
        return StateSpace(args[0], args[1], args[2], args[3])
    elif len(args) == 1:
        sys = args[0]
        if isinstance(sys, StateSpace):
            return deepcopy(sys)
        elif isinstance(sys, TransferFunction):
            return tf2ss(sys)
        else:
            raise TypeError("ss(sys): sys must be a StateSpace or \
TransferFunction object.  It is %s." % type(sys))
    else:
        raise ValueError("Needs 1 or 4 arguments; received %i." % len(args))

def tf(*args): 
    """
    Create a transfer function system.

    Parameters
    ----------
    num: vector, or list of lists of vectors
    den: vector, or list of lists of vectors
    sys: StateSpace or TransferFunction object
    tf accepts a `num` and `den`, or `sys``.

    Returns
    -------
    out: TransferFunction object

    Raises
    ------
    ValueError
        if `num` and `den` have invalid or unequal dimensions
    TypeError
        if `num` or `den` are of incorrect type

    See Also
    --------
    ss
    ss2tf
    tf2ss

    Notes
    --------
    `num`[`i`][`j`] is the vector of polynomial coefficients of the transfer
    function  numerator from the (`j`+1)st output to the (`i`+1)st input.
    `den`[`i`][`j`] works the same way.

    Examples
    --------
    >>> num = [[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]]
    >>> den = [[[9., 8., 7.], [6., 5., 4.]], [[3., 2., 1.], [-1., -2., -3.]]]
    >>> sys = tf(num, den)
    The transfer function from the 2nd input to the 1st output is
        (3s + 4) / (6s^2 + 5s + 4).
    >>> sys = tf(sys1) # Convert a StateSpace to a TransferFunction object.

    """

    if len(args) == 2:
       return TransferFunction(args[0], args[1])
    elif len(args) == 1:
        sys = args[0]
        if isinstance(sys, StateSpace):
            return ss2tf(sys)
        elif isinstance(sys, TransferFunction):
            return deepcopy(sys)
        else:
            raise TypeError("tf(sys): sys must be a StateSpace or \
TransferFunction object.  It is %s." % type(sys)) 
    else:
        raise ValueError("Needs 1 or 2 arguments; received %i." % len(args))

def ss2tf(*args):
    """
    Transform a state space system to a transfer function.
    
    Parameters
    ----------
    A: numpy matrix or matrix-like object
    B: numpy matrix or matrix-like object
    C: numpy matrix or matrix-like object
    D: numpy matrix or matrix-like object
    sys: StateSpace object
    ss accepts a set of `A`, `B`, `C`, `D` matrices, or `sys`.

    Returns
    -------
    out: TransferFunction object

    Raises
    ------
    ValueError
        if matrix sizes are not self-consistent, or if an invalid number of
        arguments is passed in
    TypeError
        if `sys` is not a StateSpace object

    See Also
    --------
    tf
    ss
    tf2ss

    Examples
    --------
    >>> sys = ss2tf(A, B, C, D)
    >>> sys = ss2tf(sys1) # Convert a StateSpace to a TransferFunction object.

    """

    if len(args) == 4:
        # Assume we were given the A, B, C, D matrix
        return _convertToTransferFunction(StateSpace(args[0], args[1], args[2],
            args[3]))
    elif len(args) == 1:
        sys = args[0]
        if isinstance(sys, StateSpace):
            return _convertToTransferFunction(sys)
        else:
            raise TypeError("ss2tf(sys): sys must be a StateSpace object.  It \
is %s." % type(sys))
    else:
        raise ValueError("Needs 1 or 4 arguments; received %i." % len(args))

def tf2ss(*args):
    """
    Transform a transfer function to a state space system.

    Parameters
    ----------
    num: vector, or list of lists of vectors
    den: vector, or list of lists of vectors
    sys: TransferFunction object
    tf2ss accepts `num` and `den`, or `sys`.

    Returns
    -------
    out: StateSpace object

    Raises
    ------
    ValueError
        if `num` and `den` have invalid or unequal dimensions, or if an invalid
        number of arguments is passed in
    TypeError
        if `num` or `den` are of incorrect type, or if sys is not a
        TransferFunction object

    See Also
    --------
    ss
    tf
    ss2tf

    Notes
    --------
    `num`[`i`][`j`] is the vector of polynomial coefficients of the transfer
    function numerator from the (`j`+1)st output to the (`i`+1)st input.
    `den`[`i`][`j`] works the same way.

    Examples
    --------
    >>> num = [[[1., 2.], [3., 4.]], [[5., 6.], [7., 8.]]]
    >>> den = [[[9., 8., 7.], [6., 5., 4.]], [[3., 2., 1.], [-1., -2., -3.]]]
    >>> sys = tf2ss(num, den)
    >>> sys = tf2ss(sys1) # Convert a TransferFunction to a StateSpace object.

    """

    if len(args) == 2:
        # Assume we were given the num, den
        return _convertToStateSpace(TransferFunction(args[0], args[1]))
    elif len(args) == 1:
        sys = args[0]
        if not isinstance(sys, TransferFunction):
            raise TypeError("tf2ss(sys): sys must be a TransferFunction \
object.")
        return _convertToStateSpace(sys)
    else:
        raise ValueError("Needs 1 or 2 arguments; received %i." % len(args))

def rss(states=1, inputs=1, outputs=1):
    """
    Create a stable continuous random state space object.
    
    Parameters
    ----------
    states: integer
    inputs: integer
    outputs: integer

    Returns
    -------
    sys: StateSpace object

    Raises
    ------
    ValueError
        if any input is not a positive integer

    See Also
    --------
    drss
    
    Notes
    -----
    If the number of states, inputs, or outputs is not specified, then the
    missing numbers are assumed to be 1.  The poles of the returned system will
    always have a negative real part.
     
    """
    
    return _rss_generate(states, inputs, outputs, 'c')
    
def drss(states=1, inputs=1, outputs=1):
    """
    Create a stable discrete random state space object.
    
    Parameters
    ----------
    states: integer
    inputs: integer
    outputs: integer

    Returns
    -------
    sys: StateSpace object

    Raises
    ------
    ValueError
        if any input is not a positive integer

    See Also
    --------
    rss
    
    Notes
    -----
    If the number of states, inputs, or outputs is not specified, then the
    missing numbers are assumed to be 1.  The poles of the returned system will
    always have a magnitude less than 1.
     
    """
    
    return _rss_generate(states, inputs, outputs, 'd')
    
def pole(sys):
    """
    Return system poles.

    Parameters
    ----------
    sys: StateSpace or TransferFunction object

    Returns
    -------
    poles: ndarray

    Raises
    ------
    NotImplementedError
        when called on a TransferFunction object

    See Also
    --------
    zero

    Notes
    -----
    This function is a wrapper for StateSpace.pole and TransferFunction.pole.

    """

    return sys.pole()
    
def zero(sys):
    """
    Return system zeros.

    Parameters
    ----------
    sys: StateSpace or TransferFunction object

    Returns
    -------
    zeros: ndarray

    Raises
    ------
    NotImplementedError
        when called on a TransferFunction object or a MIMO StateSpace object

    See Also
    --------
    pole

    Notes
    -----
    This function is a wrapper for StateSpace.zero and TransferFunction.zero.

    """

    return sys.zero()

def evalfr(sys, omega):
    """
    Evaluate the transfer function of an LTI system at an angular frequency.

    Parameters
    ----------
    sys: StateSpace or TransferFunction object
    omega: scalar

    Returns
    -------
    fresp: ndarray

    See Also
    --------
    freqresp
    bode

    Notes
    -----
    This function is a wrapper for StateSpace.evalfr and
    TransferFunction.evalfr.

    Examples
    --------
    >>> sys = rss(3, 2, 2)
    >>> evalfr(sys, 1.)
    array([[  4.09376126 -6.2171555j ,  23.71332080-35.24245284j],
           [  0.83405186 -1.82896006j,   8.10962251-12.66640309j]])
    This is the transfer function matrix evaluated at s = i.

    """

    return sys.evalfr(omega)

def freqresp(sys, omega): 
    """
    Frequency response of an LTI system at multiple angular frequencies.

    Parameters
    ----------
    sys: StateSpace or TransferFunction object
    omega: list or ndarray

    Returns
    -------
    mag: ndarray
    phase: ndarray
    omega: list, tuple, or ndarray

    See Also
    --------
    evalfr
    bode

    Notes
    -----
    This function is a wrapper for StateSpace.freqresp and
    TransferFunction.freqresp.  The output omega is a sorted version of the
    input omega.

    Examples
    --------
    >>> sys = rss(3, 2, 2)
    >>> mag, phase, omega = freqresp(sys, [0.1, 1., 10.])
    >>> mag[0, 1, :]
    array([ 55.43747231,  42.47766549,   1.97225895])
    >>> phase[1, 0, :]
    array([-0.12611087, -1.14294316,  2.5764547 ])
    This is the magnitude of the frequency response from the 2nd input to the
    1st output, and the phase (in radians) of the frequency response from the
    1st input to the 2nd output, for s = 0.1i, i, 10i.

    """

    return sys.freqresp(omega)

# Bode plots
def bode(*args, **keywords):
    """Bode plot of the frequency response

    Examples
    --------
    >>> bode(sys)
    >>> bode(sys, w)
    >>> bode(sys1, sys2, ..., sysN)
    >>> bode(sys1, sys2, ..., sysN, w)
    >>> bode(sys1, 'plotstyle1', ..., sysN, 'plotstyleN')
    """

    # If the first argument is a list, then assume python-control calling format
    if (getattr(args[0], '__iter__', False)):
        return freqplot.bode(*args, **keywords)

    # Otherwise, run through the arguments and collect up arguments
    syslist = []; plotstyle=[]; omega=None;
    i = 0; 
    while i < len(args):
        # Check to see if this is a system of some sort
        if (ctrlutil.issys(args[i])): 
            # Append the system to our list of systems
            syslist.append(args[i])
            i += 1

            # See if the next object is a plotsytle (string)
            if (i < len(args) and isinstance(args[i], str)):
                plotstyle.append(args[i])
                i += 1

            # Go on to the next argument
            continue

        # See if this is a frequency list
        elif (isinstance(args[i], (list, np.ndarray))):
            omega = args[i]
            i += 1
            break

        else:
            raise ControlArgument("unrecognized argument type")

    # Check to make sure that we processed all arguments
    if (i < len(args)):
        raise ControlArgument("not all arguments processed")

    # Check to make sure we got the same number of plotstyles as systems
    if (len(plotstyle) != 0 and len(syslist) != len(plotstyle)):
        raise ControlArgument("number of systems and plotstyles should be equal")

    # Warn about unimplemented plotstyles
    #! TODO: remove this when plot styles are implemented in bode()
    if (len(plotstyle) != 0):
        print("Warning (matabl.bode): plot styles not implemented");

    # Call the bode command
    return freqplot.bode(syslist, omega, **keywords)

# Nichols chart grid
def ngrid():
    """Nichols chart grid.

    Examples
    --------
    >>> ngrid()
    """
    from nichols import nichols_grid
    nichols_grid()

# Root locus plot
def rlocus(sys, klist = None, **keywords):
    """Root locus plot

    Parameters
    ----------
    sys: StateSpace or TransferFunction object
    klist: optional list of gains

    Returns
    -------
    rlist: list of roots for each gain
    klist: list of gains used to compute roots
    """
    from rlocus import RootLocus
    if (klist == None):
        #! TODO: update with a smart cacluation of the gains
        klist = logspace(-3, 3)

    rlist = RootLocus(sys, klist, **keywords)
    return rlist, klist
    

def margin(*args):
    """Calculate gain and phase margins and associated crossover frequencies

    Usage:
    gm, pm, wg, wp = margin(sys)
    gm, pm, wg, wp = margin(mag,phase,w)
    
    Parameters
    ----------
    sys : linsys
        Linear SISO system
    mag, phase, w : array_like
        Input magnitude, phase (in deg.), and frequencies (rad/sec) from bode
        frequency response data

    Returns
    -------
    gm, pm, wg, wp : float
        Gain margin gm, phase margin pm (in deg), and associated crossover
        frequencies wg and wp (in rad/sec) of SISO open-loop. If more than
        one crossover frequency is detected, returns the lowest corresponding
        margin. 
    """
    if len(args) == 1:
        sys = args[0]
        margins = freqplot.margin(sys)
    elif len(args) == 3:
        margins = freqplot.margin(args)
    else: 
        raise ValueError("Margin needs 1 or 3 arguments; received %i." 
            % len(args))
            
    return margins[0], margins[1], margins[3], margins[4]


def dcgain(*args):
    '''
    Compute the gain of the system in steady state.

    The function takes either 1, 2, 3, or 4 parameters:

    Parameters
    ----------
    A, B, C, D: array-like
        A linear system in state space form.
    Z, P, k: array-like, array-like, number
        A linear system in zero, pole, gain form.
    num, den: array-like
        A linear system in transfer function form.
    sys: Lti (StateSpace or TransferFunction)
        A linear system object.

    Returns
    -------
    gain: matrix
        The gain of each output versus each input:
        :math:`y = gain \cdot u`
    
    Notes
    -----
    This function is only useful for systems with invertible system 
    matrix ``A``. 
    
    All systems are first converted to state space form. The function then 
    computes:
    
    .. math:: gain = - C \cdot A^{-1} \cdot B + D
    '''
    #Convert the parameters to state space form
    if len(args) == 4:
        A, B, C, D = args
        sys = ss(A, B, C, D)
    elif len(args) == 3:
        Z, P, k = args
        A, B, C, D = zpk2ss(Z, P, k)
        sys = ss(A, B, C, D)
    elif len(args) == 2:
        num, den = args
        sys = tf2ss(num, den)
    elif len(args) == 1:
        sys, = args
        sys = ss(sys)
    else:
        raise ValueError("Function ``dcgain`` needs either 1, 2, 3 or 4 "
                         "arguments.")
    #gain = - C * A**-1 * B + D
    gain = sys.D - sys.C * sys.A.I * sys.B
    return gain

# Simulation routines 
# Call corresponding functions in timeresp, with arguments transposed

def step(sys, T=None, X0=0., input=0, output=0, **keywords):
    T, yout = timeresp.StepResponse(sys, T, X0, input, output, 
                                   transpose = True, **keywords)
    return T, yout

def impulse(sys, T=None, X0=0., input=0, output=0, **keywords):
    T, yout = timeresp.ImpulseResponse(sys, T, X0, input, output, 
                                   transpose = True, **keywords)
    return T, yout

def initial(sys, T=None, X0=0., input=0, output=0, **keywords):
    T, yout = timeresp.InitialResponse(sys, T, X0, input, output, 
                                   transpose = True, **keywords)
    return T, yout

def lsim(sys, U=0., T=None, X0=0., **keywords):
    T, yout, xout = timeresp.ForcedResponse(sys, T, U, X0,
                                             transpose = True, **keywords)
    return T, yout, xout
