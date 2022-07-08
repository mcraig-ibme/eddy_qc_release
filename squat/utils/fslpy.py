#!/usr/bin/env python
"""Python wrappers for FSL tools."""

import sys
from subprocess import check_output


def fslsplit(input, output=None, t=False, x=False, y=False, z=False):
    """Tool that takes splits 4D images and produces 3D volumes."""
    assert (input), \
        "a 3D volume file should be provided"

    cmd = "$FSLDIR/bin/fslsplit {0}".format(input)

    if output is not None:
        cmd += " {0}".format(output)
    if t is not False:
        cmd += " -t "
    if x is not False:
        cmd += " -x "
    if y is not False:
        cmd += " -y "
    if z is not False:
        cmd += " -z "
       
    print("Running " + cmd)
    sys.stdout.flush()
    jobout = check_output(cmd, shell=True)


def select_dwi_vols(data, bvals, output, b, m=False, v=False):
    """Tool that takes splits 4D images and produces 3D volumes."""
    assert (data), \
        "a 4D volume file should be provided"
    assert (bvals), \
        "a bvals file should be provided"
    assert (output), \
        "an output basename should be provided"
    assert (b), \
        "an approximate bvalue should be provided"

    cmd = "$FSLDIR/bin/select_dwi_vols {0} {1} {2} {3}".format(data, bvals, output, b)

    if m is not False:
        cmd += " -m "
    if v is not False:
        cmd += " -v "
       
    print("Running " + cmd)
    sys.stdout.flush()
    jobout = check_output(cmd, shell=True)


def slicer(input, input2=None, label=False, l=None, i=None, e=None, t=False,
           n=False, u=False, c=False,
           a=None, sample=None):
    """Tool that takes 3D images and produces 2D pictures of slices from within these files."""
    assert (input), \
        "a 3D volume file should be provided"

    cmd = "$FSLDIR/bin/slicer {0}".format(input)

    if input2 is not None:
        cmd += " {0}".format(input2)
    if label is not False:
        cmd += " -L "
    if l is not None:
        cmd += " -l {0}".format(l)
    if i is not None:
        cmd += " -i {0} {1}".format(i[0], i[1])
    if e is not None:
        cmd += " -e {0}".format(e)
    if t is not False:
        cmd += " -t "
    if n is not False:
        cmd += " -n "
    if u is not False:
        cmd += " -u "
    if c is not False:
        cmd += " -c "
    if a is not None:
        cmd += " -a {0}".format(a)
    if sample is not None:
        cmd += " -S {0} {1} {2}".format(sample[0], sample[1], sample[2])
        
    print("Running " + cmd)
    sys.stdout.flush()
    jobout = check_output(cmd, shell=True)


